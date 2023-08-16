from datetime import datetime
import pandas as pd
import os
import math
from dateutil.tz import tzoffset

def datetime_to_str(dt: datetime, microseconds=False):
    if not microseconds:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    elif microseconds:
        return dt.strftime("%Y-%m-%d %H:%M:%S:%f")


def str_to_datetime(dt_str: str):
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S:%f")


def haawks_id_to_str(haawks_id: float):
    # All haawks IDd should be 5 digits long but when they're stored as float or int inside the csv or excel files, it removes the leading zeros, so this adds them back
    return str(haawks_id).zfill(5)


def get_indicator_info(haawks_id_str):
    indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")
    for index, row in indicators.iterrows():
        if haawks_id_to_str(row['Id']) == haawks_id_str:
            cols = indicators.columns
            indicator_info = {}
            for index, value in enumerate(row.values):
                indicator_info[cols[index]] = value
            return indicator_info
    raise ValueError("Invalid haawks_id_str")

def read_news_data(haawks_id_str):
    # loop through all the files in the news_data directory
    for filename in os.listdir('./news_data'):
        # check if the filename starts with the haawks_id_str provided
        if filename.startswith(haawks_id_str):
            # if the filename matches, read the CSV file into a Pandas dataframe
            news_data = pd.read_csv(f"./news_data/{filename}")
            # return the dataframe
            return news_data


def save_news_data(haawks_id_str, news_data):
    # loop through all files in the news_data directory
    for filename in os.listdir('./news_data'):
        # if the file name starts with haawks_id_str, it means we've found the correct file
        if filename.startswith(haawks_id_str):
            # print a message indicating that we are saving to this file
            print(f"saving to: news_data/{filename}")
            # save the news data to the file
            news_data.to_csv(f"./news_data/{filename}", index=False)


def get_indicator_suffix(haawks_id):
    indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")

    for index, row in indicators.iterrows():
        if row['Id'] == int(haawks_id):
            suffix = row['suffix']
            if type(suffix) == float and math.isnan(suffix):
                suffix = ""
            return suffix

def convert_news_data_to_float(haawks_id_str: str, data_str: str):
    suffix = get_indicator_suffix(haawks_id_str)
    data_str = str(data_str)
    data = float(data_str.replace(suffix, "").replace(",", ""))
    return data


def get_deviation(actual, forecast):
    return actual - forecast


def get_higher_dev_expected_direction(symbol, inv_currency, higher_dev):
    if higher_dev == 'unknown':
        print(f"Whether a higher news deviation is bullish or bearish is unknown for the underlying currency ({inv_currency}) and the symbol {symbol}. Please manually input whether a higher deviation is bullish or bearish for {symbol}. (This affects the calculation of the correlation scores).")
        input_str = ""
        while input_str not in ['bullish', 'bearish']:
            input_str = input("Type either 'bullish' or 'bearish': ")

        return input_str

    if inv_currency in symbol:
        if symbol.startswith(inv_currency):
            underlying_currency_position = 'base'
        elif symbol.endswith(inv_currency):
            underlying_currency_position = 'quote'
        else:
            raise ValueError("Currency is in symbol but doesn't start or end with it so the symbol is invalid.")

        if underlying_currency_position == 'base' and higher_dev == 'bullish':
            print(f"A positive news deviation is bullish for {inv_currency} which is the base currency in {symbol}, so a positive deviation is also bullish for {symbol}.")
            return 'bullish'
        elif underlying_currency_position == 'base' and higher_dev == 'bearish':
            print(
                f"A positive news deviation is bearish for {inv_currency} which is the base currency in {symbol}, so a positive deviation is also bearish for {symbol}.")
            return 'bearish'
        elif underlying_currency_position == 'quote' and higher_dev == 'bullish':
            print(f"A positive news deviation is bullish for {inv_currency} which is the quote currency in {symbol}, so a positive deviation is bearish for {symbol}.")
            return 'bearish'
        elif underlying_currency_position == 'quote' and higher_dev == 'bearish':
            print(f"A positive news deviation is bearish for {inv_currency} which is the quote currency in {symbol}, so a positive deviation is bullish for {symbol}.")
            return 'bullish'
    else:
        print(f"The underlying currency for this indicator according to investing.com ({inv_currency}) is not in {symbol}. Please manually input whether a higher deviation is bullish or bearish for {symbol}. (This affects the calculation of the correlation scores).")
        input_str = ""
        while input_str not in ['bullish', 'bearish']:
            input_str = input("Type either 'bullish' or 'bearish': ")

        if input_str == "bullish":
            return "positive"
        elif input_str == "bearish":
            return "negative"


def get_day(tzinfo = tzoffset(None, 0), dt = None):
    if dt is None:
        day = datetime.now(tzinfo).today().strftime('%A')
    elif type(dt) == datetime:
        day = dt.strftime('%A')
    else:
        raise ValueError("dt must be a datetime")
    return day


def check_if_saturday():

    if get_day(tzoffset(None, -5.0 * 3600)) == 'Saturday':
        return True
    else:
        return False
