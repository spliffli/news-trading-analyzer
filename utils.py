from datetime import datetime
import pandas as pd
import os
import math

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
    raise ValueError("Invalid haawks_id")

def read_news_data(haawks_id):
    # loop through all the files in the news_data directory
    for filename in os.listdir('./news_data'):
        # check if the filename starts with the haawks_id provided
        if filename.startswith(haawks_id):
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
    suffix = get_indicator_info(haawks_id_str)['suffix']
    data_str = str(data_str)
    data = float(data_str.replace(suffix, "").replace(",", ""))
    return data


def get_deviation(actual, forecast):
    return actual - forecast