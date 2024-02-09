import pandas as pd
from datetime import datetime, timedelta
import os
import math
import json
import warnings
from utils import str_to_datetime, datetime_to_str, haawks_id_to_str, read_news_data, save_news_data, get_indicator_info, convert_news_data_to_float, get_deviation,  get_higher_dev_expected_direction
import numpy as np

warnings.simplefilter(action='ignore', category=FutureWarning)

DEFAULT_TIME_DELTAS = {
    "1s": timedelta(seconds=1),
    "2s": timedelta(seconds=2),
    "3s": timedelta(seconds=3),
    "4s": timedelta(seconds=4),
    "5s": timedelta(seconds=5),
    "10s": timedelta(seconds=10),
    "15s": timedelta(seconds=15),
    "20s": timedelta(seconds=20),
    "25s": timedelta(seconds=25),
    "30s": timedelta(seconds=30),
    "45s": timedelta(seconds=45),
    "1m": timedelta(minutes=1),
    "2m": timedelta(minutes=2),
    "3m": timedelta(minutes=3),
    "4m": timedelta(minutes=4),
    "5m": timedelta(minutes=5),
    "10m": timedelta(minutes=10),
    "15m": timedelta(minutes=15),
}


def get_decimal_places(num: float):
    """
    Get the number of decimal places of a given float number.

    Args:
        num (float): The number to check for decimal places.

    Returns:
        int: The number of decimal places.

    Example:
        >>> get_decimal_places(123.456)
        3
    """
    # Convert the input number to a string, split it at the decimal point,
    # and retrieve the second part of the resulting list
    # (which represents the digits after the decimal point).
    decimal_digits = str(num).split(".")[1]

    # Calculate the length of the decimal digits string to determine
    # how many decimal places the original number has.
    decimal_places = len(decimal_digits)

    # Return the number of decimal places.
    return decimal_places


def get_decimal_places_from_tick_data(tick_data):
    """
    Extracts the maximum number of decimal places from the 'ask' column of a given DataFrame's sample.

    Args:
        tick_data (pd.DataFrame): DataFrame containing tick data with an 'ask' column.

    Returns:
        int: Maximum number of decimal places found in the sample of 'ask' column.
    """
    # To avoid rounding issues, we take the first 20 rows of tick data as a sample
    df = tick_data.loc[1:20]
    decimal_places_list = []

    # Loop through each item in the `ask` column of the sample
    for index, value in df['ask'].items():
        # Call the `get_decimal_places` function to get the number of decimal places in the current value
        decimal_places = get_decimal_places(value)

        # Append the number of decimal places to the `decimal_places_list`
        decimal_places_list.append(decimal_places)

    # The number of decimal places we want to use is the maximum value in `decimal_places_list`
    decimal_places = max(decimal_places_list)
    return decimal_places


def price_movement_to_pips(price_movement, decimal_places):
    """
    Convert a price movement to pips based on the number of decimal places.

    Args:
        price_movement (float): The price movement to convert.
        decimal_places (int): Number of decimal places in the price movement. Can be 5, 4, 3, or 2.

    Returns:
        float: Price movement in pips.

    Raises:
        ValueError: If the provided decimal places is not 5, 4, 3, or 2.

    Example:
        >>> price_movement_to_pips(0.0003, 5)
        3.0
    """
    match decimal_places:
        case 5:
            pips = round(price_movement / 0.0001, 1)
        case 4:
            pips = round(price_movement / 0.001, 1)
        case 3:
            pips = round(price_movement / 0.01, 1)
        case 2:
            pips = round(price_movement / 0.1, 1)
        case _:
            return ValueError("Invalid amount of decimal places (Only accepts 5, 4, 3 or 2 decimals)")

    return pips


def get_release_time_price(release_datetime, tick_df):
    """
    Retrieve the ask and bid prices at the time just before the given release datetime.

    Args:
        release_datetime (datetime): The datetime of the release event.
        tick_df (pd.DataFrame): DataFrame containing tick data with 'time', 'ask', and 'bid' columns.

    Returns:
        tuple: A tuple containing the ask and bid prices at the release time.

    Notes:
        - Assumes 'time' column values can be in one of two formats: "%Y-%m-%d %H:%M:%S.%f" or "%Y-%m-%d %H:%M:%S".

    Example:
        >>> tick_df = pd.DataFrame({"time": ["2023-08-14 12:00:00.000", "2023-08-14 12:01:00.000"], "ask": [1.2345, 1.2350], "bid": [1.2344, 1.2349]})
        >>> release_datetime = datetime(2023, 8, 14, 12, 1)
        >>> get_release_time_price(release_datetime, tick_df)
        (1.2345, 1.2344)
    """
    release_index = 0

    for index, value in tick_df['time'].items():
        try:
            timestamp = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
        except:
            timestamp = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

        if timestamp > release_datetime:
            release_index = index - 1
            break
    release_price = (tick_df.loc[release_index]['ask'], tick_df.loc[release_index]['bid'])

    return release_price


def get_prices_at_time_deltas(release_datetime, tick_df, time_deltas=DEFAULT_TIME_DELTAS):
    """
    Retrieve the ask and bid prices at specific intervals after the given release datetime.

    Args:
        release_datetime (datetime): The datetime of the release event.
        tick_df (pd.DataFrame): DataFrame containing tick data with 'time', 'ask', and 'bid' columns.
        time_deltas (dict, optional): Dictionary mapping descriptive strings to timedelta objects indicating desired time intervals after the release. Defaults to `DEFAULT_TIME_DELTAS`.

    Returns:
        dict: A dictionary mapping descriptive strings to tuples of ask and bid prices at each interval after the release.

    Notes:
        - Assumes 'time' column values can be in one of two formats: "%Y-%m-%d %H:%M:%S.%f" or "%Y-%m-%d %H:%M:%S".

    Example:
        >>> tick_df = pd.DataFrame({"time": ["2023-08-14 12:00:00.000", "2023-08-14 12:01:00.000", "2023-08-14 12:02:00.000"], "ask": [1.2345, 1.2350, 1.2355], "bid": [1.2344, 1.2349, 1.2354]})
        >>> release_datetime = datetime(2023, 8, 14, 12, 0)
        >>> time_deltas = {"1_minute": timedelta(minutes=1), "2_minutes": timedelta(minutes=2)}
        >>> get_prices_at_time_deltas(release_datetime, tick_df, time_deltas)
        {"1_minute": (1.2350, 1.2349), "2_minutes": (1.2355, 1.2354)}
    """
    prices = {}
    td_timestamps = {}

    # Calculate the timestamps for each time delta
    for td in time_deltas:
        td_timestamps[td] = release_datetime + time_deltas[td]

    # Extract the prices at each time delta
    for td in time_deltas:
        for index, value in tick_df['time'].items():
            try:
                timestamp = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
            except:
                timestamp = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

            if timestamp > (td_timestamps[td]):
                # Extract the ask and bid prices and store them in the prices dictionary
                prices[td] = (tick_df.loc[index]['ask'], tick_df.loc[index]['bid'])
                break

    return prices


def get_relative_price_movements(prices_per_time_delta, release_time_price, decimal_places):
    """
    Calculates the relative price movements based on the release time price and the prices at different time deltas.

    Args:
        prices_per_time_delta (dict): A dictionary containing the prices at different time deltas.
        release_time_price (tuple): A tuple containing the release time ask and bid prices.
        decimal_places (int): The number of decimal places to round the price movements to.

    Returns:
        price_movements (dict): A dictionary containing the relative price movements rounded to the specified decimal places.
    Example:
        >>> prices_per_time_delta = {"1m": (1.2350, 1.2349), "2m": (1.2355, 1.2354)}
        >>> release_time_price = (1.2345, 1.2344)
        >>> decimal_places = 4
        >>> get_relative_price_movements(prices_per_time_delta, release_time_price, decimal_places)
        {"1m": (0.0005, 0.0005), "2m": (0.0010, 0.0010)}

    """
    release_ask = float(release_time_price[0])
    release_bid = float(release_time_price[1])

    price_movements = {}

    for price in prices_per_time_delta:
        ask = float(prices_per_time_delta[price][0])
        bid = float(prices_per_time_delta[price][1])

        difference_ask = round(ask - release_ask, decimal_places)
        difference_bid = round(bid - release_bid, decimal_places)
        price_movements[price] = (difference_ask, difference_bid)

    return price_movements



def cross_reference_pips_with_news_data(news_data, pip_data):
    """
    Cross-references pip data with news data and stores the deviation and pips data for matching timestamps.

    Args:
        news_data (pd.DataFrame): DataFrame containing news data with 'Timestamp' and 'Deviation' columns.
        pip_data (dict): Dictionary containing pip data with timestamps as keys and pip movements as values.

    Returns:
        news_pip_data (dict): Dictionary containing matched news and pip data with timestamps as keys, and deviation and pip movements as values.
    """

    news_pip_data = {}

    for timestamp in pip_data:

        for index, row in news_data.iterrows():
            if timestamp == row['Timestamp']:
                deviation = row['Deviation']
                news_pip_data[timestamp] = {"deviation": deviation, "pips": pip_data[timestamp]}
    return news_pip_data



def get_pip_movements(price_movements, decimal_places):
    """
    Calculates the pip movements for each of the provided price movements based on the decimal places
    and returns a dictionary of the calculated pip movements.

    Args:
    - price_movements (dict): A dictionary containing the price movements for each time delta, with the keys being the
    time delta and the values being a tuple of the difference in ask and bid prices.
    - decimal_places (int): The number of decimal places for the given currency pair.

    Returns:
    - pip_movements (dict): A dictionary containing the pip movements for each time delta, with the keys being the
    time delta and the values being a tuple of the difference in ask and bid prices, expressed in pips.
    """
    pip_movements = {}

    for price_movement in price_movements:
        pm_ask = price_movement_to_pips(price_movements[price_movement][0], decimal_places)
        pm_bid = price_movement_to_pips(price_movements[price_movement][1], decimal_places)
        pip_movements[price_movement] = (pm_ask, pm_bid)

    return pip_movements



def read_tick_data(symbol, release_datetime):
    """
    Reads the tick data for a given symbol and release datetime from a CSV file.
    The function assumes a certain naming convention for the CSV files.

    Args:
        symbol (str): The trading symbol for which the tick data is to be read.
        release_datetime (datetime): The datetime of the news release event.

    Returns:
        pd.DataFrame: DataFrame containing the tick data read from the CSV file.

    Raises:
        ValueError: If the corresponding CSV file doesn't exist.

    Notes:
        - Assumes CSV files are located in "./tick_data" directory.
        - Assumes CSV files are named in the format: "{symbol}__{release_date}__{start_time}_{end_time}.csv".
    """
    release_date_hyphenated = release_datetime.strftime("%Y-%m-%d")
    start_time_hyphenated = (release_datetime - timedelta(minutes=5)).strftime('%H-%M-%S')
    end_time_hyphenated = (release_datetime + timedelta(minutes=15)).strftime('%H-%M-%S')
    for filename in os.listdir("./tick_data"):
        if filename == f"{symbol}__{release_date_hyphenated}__{start_time_hyphenated}_{end_time_hyphenated}.csv":
            tick_data = pd.read_csv(f"./tick_data/{filename}")
            return tick_data

    raise ValueError(
        f"File {symbol}__{release_date_hyphenated}__{start_time_hyphenated}_{end_time_hyphenated}.csv doesn't exist")



def save_news_pip_data(haawks_id, symbol, pip_data: dict):
    """
    Save the news pip data for a given financial symbol to a JSON file.

    This function takes in the news pip data associated with a specific financial symbol,
    formats the filename and directory path based on various parameters including the haawks_id,
    and saves the data in a structured JSON file within the specified directory. If a file with
    the same symbol prefix exists in the target directory, it will be removed before saving the
    new data file.

    Args:
        haawks_id (str): The unique identifier associated with the Haawks platform.
        symbol (str): The ticker symbol of the financial instrument (e.g., 'AAPL' for Apple Inc.).
        pip_data (dict): A dictionary containing the pip data that needs to be saved.
                         Example:
                         {
                             '2023-08-14 09:30:00': {'value': 120.5, ...},
                             '2023-08-14 09:31:00': {'value': 120.7, ...},
                             ...
                         }

    Directory Structure:
        The JSON file will be saved in the following directory structure:
        - analysis_data/
            - {haawks_id}_{inv_id}_{name_formatted}/
                - pip_data/
                    - {symbol}__{start_date_str}_{end_date_str}.json

    Example:
        >>> haawks_id = '12345'
        >>> symbol = 'AAPL'
        >>> pip_data = {'2023-08-14 09:30:00': {'value': 120.5}, '2023-08-14 09:31:00': {'value': 120.7}}
        >>> save_news_pip_data(haawks_id, symbol, pip_data)

    Note:
        This function assumes that `get_indicator_info(haawks_id)` is a function that returns a
        dictionary containing 'inv_title' and 'inv_id' based on the given `haawks_id`.
    """
    # pip_data.to_csv(f"{symbol}")
    indicator_info = get_indicator_info(haawks_id)
    event_title = indicator_info['inv_title']
    inv_id = indicator_info['inv_id']
    start_datetime_str = list(pip_data.keys())[-1]
    end_datetime_str = list(pip_data.keys())[0]

    name_formatted = event_title.replace(" ", "_").replace(".", "")
    dir_name = f"{haawks_id}_{inv_id}_{name_formatted}"
    start_date_str = start_datetime_str.split(" ")[0]
    end_date_str = end_datetime_str.split(" ")[0]
    new_filename = f"{symbol}__{start_date_str}_{end_date_str}.json"

    if not os.path.exists(os.path.join(os.getcwd(), f"analysis_data/{dir_name}/pip_data")):
        os.makedirs(os.path.join(os.getcwd(), f"analysis_data/{dir_name}/pip_data"))

    for existing_filename in os.listdir(f"./analysis_data/{dir_name}/pip_data/"):
        if existing_filename.startswith(symbol):
            os.remove(f"./analysis_data/{dir_name}/pip_data/{existing_filename}")

    file = open(f"./analysis_data/{dir_name}/pip_data/{new_filename}", "w")
    json.dump(pip_data, file, indent=4)
    file.close()


def read_news_pip_data(haawks_id, symbol):
    """
    Read and return pip data from analysis data files based on the provided haawks_id and symbol.

    Args:
        haawks_id (str): The identifier of the haawks event.
        symbol (str): The trading symbol (e.g., 'EURUSD') for which the data should be retrieved.

    Returns:
        dict: A dictionary containing:
            - "data_exists" (bool): Indicates whether the relevant data file exists.
            - "data" (dict, optional): The pip data loaded from the file, if it exists.
            - "start" (datetime, optional): The start datetime of the pip data, if it exists.
            - "end" (datetime, optional): The end datetime of the pip data, if it exists.

    Example:
        >>> read_news_pip_data("12345", "EURUSD")
        {
            "data_exists": True,
            "data": {...},
            "start": datetime(2023, 8, 14, 12, 0),
            "end": datetime(2023, 8, 14, 12, 30)
        }
    """
    indicator_info = get_indicator_info(haawks_id)
    event_title = indicator_info['inv_title']
    inv_id = indicator_info['inv_id']

    for dir_name in os.listdir("./analysis_data"):
        if dir_name.startswith(haawks_id):
            for filename in os.listdir(f"./analysis_data/{dir_name}/pip_data/"):
                if filename.startswith(symbol):
                    file = open(f"./analysis_data/{dir_name}/pip_data/{filename}")
                    data = json.load(file)
                    file.close()
                    start_datetime = str_to_datetime(list(data.keys())[-1])
                    end_datetime = str_to_datetime(list(data.keys())[0])

                    return {
                        "data_exists": True,
                        "data": data,
                        "start": start_datetime,
                        "end": end_datetime,
                    }

    return {
        "data_exists": False
    }


from datetime import timedelta

from datetime import timedelta


from datetime import timedelta

def get_first_stoploss_hit(tick_data, release_datetime, release_price, decimal_places, stoploss, expected_direction):
    """
    Find the timestamp of the first instance when the stoploss is hit and calculate the pip movement relative
    to the expected direction and the time delta.

    Args:
        tick_data (DataFrame): Raw forex tick data with columns: 'time', 'ask', and 'bid'.
        release_datetime (datetime): Timestamp of the news release.
        release_price (tuple): Tuple containing the ask and bid prices at the time of the news release.
        decimal_places (int): Number of decimal places in the bid & ask prices.
        stoploss (float): Virtual stoploss value in pips.
        expected_direction (str): Expected direction of the price movement ('up' or 'down').

    Returns:
        tuple: A tuple containing the timestamp of the first retracement, the pip movement relative to
               the expected direction, and the time delta between the release time and the first retracement.

    Raises:
        ValueError: If the expected_direction is neither 'up' nor 'down'.
    """
    # Initialize variables to track the first retracement instance and time delta
    first_sl_hit_timestamp = None
    pip_movement_relative_to_expected_direction = None
    time_delta_at_first_sl_hit = None
    if type(release_price) == tuple:
        release_price_ask, release_price_bid = release_price

    # Iterate through tick data
    for index, row in tick_data.iterrows():
        timestamp = row['time']

        # Determine which price (bid or ask) to use based on expected_direction
        if expected_direction == 'up':
            current_price = row['bid']
            if type(release_price) == tuple:
                release_price = release_price_bid
        elif expected_direction == 'down':
            current_price = row['ask']
            if type(release_price) == tuple:
                release_price = release_price_ask
        else:
            raise ValueError("Invalid expected_direction. Use 'up' or 'down'.")

        # Calculate the price movement from the release price to the current price
        price_movement = current_price - release_price

        # Calculate the pip movement relative to the expected direction using the helper function
        pip_movement_relative_to_expected_direction = price_movement_to_pips(price_movement, decimal_places)

        # Check if the stoploss is hit in the contrary direction
        if (expected_direction == 'up' and pip_movement_relative_to_expected_direction >= stoploss) or \
                (expected_direction == 'down' and pip_movement_relative_to_expected_direction <= -stoploss):
            # Record the timestamp and time delta of the first retracement instance
            first_sl_hit_timestamp = timestamp
            time_delta_at_first_sl_hit = str_to_datetime(timestamp) - release_datetime
            break  # Exit loop once the first retracement is found

    # Return the timestamp, pip movement relative to the expected direction, and time delta
    return (
        first_sl_hit_timestamp,
        pip_movement_relative_to_expected_direction,
        time_delta_at_first_sl_hit
    )



def calc_stoploss_hits(tick_data, release_datetime, relative_price, decimal_places, stoploss, expected_direction):
    """
    Calculate the number of times the stoploss is hit, resetting it each time it's hit.

    Args:
        tick_data (DataFrame): Raw forex tick data with columns: 'time', 'ask', and 'bid'.
        release_datetime (datetime): Timestamp of the news release.
        relative_price (tuple): Tuple containing the ask and bid prices at the time of the news release.
        decimal_places (int): Number of decimal places in the bid & ask prices.
        stoploss (float): Virtual stoploss value in pips.
        expected_direction (str): Expected direction of the price movement ('up' or 'down').

    Returns:
        int: Number of times the stoploss is hit.

    Raises:
        ValueError: If the expected_direction is neither 'up' nor 'down'.
    """
    # Initialize variables to track stoploss hits and reset stoploss
    stoploss_hits = 0
    reset_stoploss = False
    release_price_ask, release_price_bid = relative_price

    # Iterate through tick data
    for index, row in tick_data.iterrows():
        timestamp = row['time']

        # Determine which price (bid or ask) to use based on expected_direction
        if expected_direction == 'up':
            current_price = row['ask']
            relative_price = release_price_ask
        elif expected_direction == 'down':
            current_price = row['bid']
            relative_price = release_price_bid
        else:
            raise ValueError("Invalid expected_direction. Use 'up' or 'down'.")

        # Calculate the price movement from the release price to the current price
        price_movement = current_price - relative_price

        # Check if the stoploss is hit in the contrary direction
        if (expected_direction == 'up' and price_movement >= stoploss) or \
                (expected_direction == 'down' and price_movement <= -stoploss):
            # Count stoploss hits
            stoploss_hits += 1

            # Reset the stoploss a given amount of pips behind the hit price
            relative_price = current_price + (stoploss if expected_direction == 'up' else -stoploss)
            reset_stoploss = True

        # Check if the stoploss is reset and the timestamp is within 15 mins after release_datetime
        if reset_stoploss and timestamp <= release_datetime + timedelta(minutes=15):
            # Continue calculating retracements with the reset stoploss
            retracement_timestamp, pip_movement, time_delta = get_first_stoploss_hit(tick_data[index:],
                                                                                     release_datetime, (
                                                                                     release_price_ask,
                                                                                     release_price_bid), decimal_places,
                                                                                     stoploss, expected_direction)

            # Update stoploss reset status based on retracement results
            reset_stoploss = False

    return stoploss_hits




def calc_continuation_score(tick_data, release_datetime, release_price, decimal_places, stoploss, expected_direction):
    """
    Calculate the continuation score, which measures how many pips the price continues after the news release.

    Args:
        tick_data (DataFrame): Raw forex tick data with columns: 'time', 'ask', and 'bid'.
        release_datetime (datetime): Timestamp of the news release.
        release_price (tuple): Tuple containing the ask and bid prices at the time of the news release.
        decimal_places (int): Number of decimal places in the bid & ask prices.
        stoploss (float): Virtual stoploss value in pips.
        expected_direction (str): Expected direction of the price movement ('up' or 'down').

    Returns:
        float: Continuation score in pips.
    """
    if type(release_price) == tuple:
        release_price_ask = release_price[0]
        release_price_bid = release_price[1]

    # Determine which price (bid or ask) to use based on expected_direction
    if expected_direction == 'up':
        virtual_entry_price = release_price_ask
    elif expected_direction == 'down':
        virtual_entry_price = release_price_bid
    else:
        raise ValueError("Invalid expected_direction. Use 'up' or 'down'.")

    # Calculate the timestamp after 5 seconds
    initial_peak_range_timestamp = release_datetime + timedelta(seconds=5)

    # Find the maximum price between the release and 5 seconds later
    virtual_entry_price = max(row['ask'] if expected_direction == 'up' else row['bid'] for index, row in tick_data.iterrows() if str_to_datetime(row['time']) <= initial_peak_range_timestamp)

    # Get the continuation timestamp, price, and time delta
    initial_peak_range_timestamp, continuation_pip_movement, time_delta_after_virtual_entry = get_first_stoploss_hit(tick_data, initial_peak_range_timestamp, virtual_entry_price, decimal_places, stoploss, expected_direction)

    # return initial_peak_range_timestamp, continuation_pip_movement, time_delta_after_virtual_entry
    return continuation_pip_movement


def fetch_stoploss(symbol):
    match symbol:
        case "USDJPY":
            return 5
        case "USDCAD":
            return 5
        case "USDSEK":
            return 75
        case "USDNOK":
            return 75
        case "USDTRY":
            return 75
        case "USDPLN":
            return 75
        case "USDRUB":
            return 75


def get_expected_direction_2(higher_dev, deviation):

    if higher_dev == "bullish":
        if deviation >= 0:
            return "positive"
    elif higher_dev == "bearish":
        if deviation >= 0:
            return "negative"
    else:
        raise ValueError("higher_dev must be 'bearish' or 'bullish'")


def mine_data_from_ticks(news_data, symbol, release_datetime):
    """
    Extract and calculate pip movements based on tick data, symbol, and a release datetime.

    Args:
        news_data (pd.DataFrame): The news data as a DataFrame, assumed to contain relevant columns.
        symbol (str): The trading symbol (e.g., 'EURUSD') for which the data should be retrieved.
        release_datetime (datetime): The datetime at which the news was released.

    Returns:
        dict: A dictionary containing the pip movements for each time delta,
        with keys being the time delta and values being a tuple of the difference in ask and bid prices,
        expressed in pips.

    Raises:
        ValueError: If the tick data is empty.

    Example:
        >>> news_data = pd.DataFrame(...)
        >>> release_datetime = datetime(2023, 8, 14, 12, 0)
        >>> mine_data_from_ticks(news_data, "EURUSD", release_datetime)
        {"1m": (0.5, 0.5), "5m": (1.0, 1.0), ...}
    """
    row_count = news_data.shape[0]
    pip_data = {}
    expected_direction = None

    for index, row in news_data.iterrows():
        if str_to_datetime(row['Timestamp']).date() == release_datetime.date():
            expected_direction = row['expected_direction']
            break


    tick_data = read_tick_data(symbol, release_datetime)

    if tick_data.shape[0] == 0:
        raise ValueError("Tick data is empty")

    prices_at_timedeltas = get_prices_at_time_deltas(release_datetime, tick_data)
    release_price = get_release_time_price(release_datetime, tick_data)
    decimal_places = get_decimal_places_from_tick_data(tick_data)

    stoploss = fetch_stoploss(symbol)

    first_stoploss_hit = get_first_stoploss_hit(tick_data, release_datetime, release_price, decimal_places, stoploss, expected_direction)
    stoploss_hits = calc_stoploss_hits(tick_data, release_datetime, release_price, decimal_places, stoploss, expected_direction)
    continuation_score = calc_continuation_score(tick_data, release_datetime, release_price, decimal_places, stoploss, expected_direction)

    relative_price_movements = get_relative_price_movements(prices_at_timedeltas, release_price, decimal_places)
    pip_movements = get_pip_movements(relative_price_movements, decimal_places)

    return {
        "first_sl_hit" : first_stoploss_hit,
        "sl_hits": stoploss_hits,
        "cont_score" : continuation_score,
        "pip_movements": pip_movements
    }


def sort_news_pip_data_by_timestamp(news_pip_data):
    """
    Sort the news pip data by timestamp in descending order.

    Args:
        news_pip_data (dict): A dictionary where the keys are timestamp strings and the values
        are dictionaries containing pip data information for those timestamps.

    Returns:
        dict: The input dictionary sorted by timestamp keys in descending order.

    Example:
        >>> news_pip_data = {"2023-08-14 12:30": {...}, "2023-08-14 12:00": {...}}
        >>> sort_news_pip_data_by_timestamp(news_pip_data)
        {"2023-08-14 12:30": {...}, "2023-08-14 12:00": {...}}
    """
    keys = list(news_pip_data.keys())
    keys.sort(reverse=True)
    sorted_dict = {i: news_pip_data[i] for i in keys}

    return sorted_dict


def load_local_news_pip_data(haawks_id_str, symbol, timestamps_to_mine, news_data):
    """
    Load locally available news pip data for a given haawks_id and trading symbol.

    Args:
        haawks_id_str (str): The identifier of the haawks event as a string.
        symbol (str): The trading symbol (e.g., 'EURUSD') for which the data should be retrieved.
        timestamps_to_mine (list): List of timestamps to mine from raw tick data.
        news_data (pd.DataFrame): DataFrame containing news data with relevant columns.

    Returns:
        dict: A dictionary containing the pip data information for each timestamp in the local data.
    """
    local_data = read_news_pip_data(haawks_id_str, symbol)

    if local_data['data_exists']:
        local_data_start = local_data['start']
        local_data_end = local_data['end']

        # Calculate the total number of rows in the news_data DataFrame.
        row_count = news_data.shape[0]

        # For each timestamp in local data, remove it from the timestamps_to_mine list.
        for timestamp in local_data['data']:
            timestamp = str_to_datetime(timestamp)
            if timestamp in timestamps_to_mine:
                timestamps_to_mine.remove(timestamp)

        # If all required timestamps are in the local data, use it directly.
        if not timestamps_to_mine:
            print(
                f"Local data exists for {len(local_data['data'].keys())}/{row_count} releases. Reading data from file...")
            return local_data['data']

    return {}



def mine_and_save_pip_data(news_data, symbol, timestamp, news_pip_data):
    """
    Mine pip data from raw tick data for a specific timestamp and save it to the news_pip_data dictionary.

    Args:
        news_data (pd.DataFrame): DataFrame containing news data with relevant columns.
        symbol (str): The trading symbol (e.g., 'EURUSD') for which the data should be mined.
        timestamp (datetime): The timestamp for which pip data should be mined.
        news_pip_data (dict): Dictionary to store pip data information for each timestamp.

    Returns:
        None
    """
    timestamp_str = datetime_to_str(timestamp)

    try:
        # Extract pip data from raw tick data.
        pip_movements_at_timedeltas = mine_data_from_ticks(news_data, symbol, timestamp)
        news_pip_data.setdefault(timestamp_str, {}).setdefault('pips', pip_movements_at_timedeltas['pip_movements'])

        # Retrieve and set the 'deviation' value for the current timestamp.
        for _, row in news_data.iterrows():
            if row['Timestamp'] == timestamp_str:
                news_pip_data[timestamp_str]['deviation'] = row.get('Deviation', None)
                break
    except ValueError:
        # Handle any ValueErrors, e.g., when tick data might be empty.
        return


def load_news_pip_movements_at_timedeltas(haawks_id_str, news_data, symbol):
    """
    Load news pip data for a given haawks_id, news data, and trading symbol.
    If local data exists, it uses that; otherwise, it mines data from raw tick data.

    Args:
        haawks_id_str (str): The identifier of the haawks event as a string.
        news_data (pd.DataFrame): The news data as a DataFrame, assumed to contain relevant columns.
        symbol (str): The trading symbol (e.g., 'EURUSD') for which the data should be retrieved.

    Returns:
        dict: A dictionary containing the pip data information for each timestamp in the news_data DataFrame.
    """
    # Fetches the details about the specific haawks event using its ID.
    indicator_info = get_indicator_info(haawks_id_str)

    higher_dev_expected_direction = get_higher_dev_expected_direction(symbol, indicator_info['inv_currency'], indicator_info['higher_dev'])

    # Initialize an empty dictionary to store pip data for each timestamp.
    news_pip_data = {}
    row_count = news_data.shape[0]  # Calculate the total number of rows in the news_data DataFrame.

    # Convert the start and end timestamps from string to datetime objects.
    start_datetime = str_to_datetime(news_data.loc[row_count - 1]['Timestamp'])
    end_datetime = str_to_datetime(news_data.loc[0]['Timestamp'])

    # Initialize a list to store all timestamps that need data extraction (i.e., mining).
    timestamps_to_mine = [str_to_datetime(ts) for _, ts in news_data["Timestamp"].items()]

    # Provide feedback about the process.
    print(f"Loading news pip data for {indicator_info['inv_title']}: {start_datetime} - {end_datetime}")

    # Load locally available news pip data
    local_data = load_local_news_pip_data(haawks_id_str, symbol, timestamps_to_mine, news_data)
    news_pip_data.update(local_data)

    # If no local data is available, provide a message indicating data will be mined.
    if not local_data:
        print("No local data exists, so it will be mined...")

    # For each timestamp in timestamps_to_mine, mine pip data from raw tick data.
    for index, timestamp in enumerate(timestamps_to_mine):
        print(f"\rMining pip data from {timestamp} ({index + 1}/{len(timestamps_to_mine)})", end="", flush=True)
        mine_and_save_pip_data(news_data, symbol, timestamp, news_pip_data)

    # Sort the news pip data by timestamp.
    news_pip_data = sort_news_pip_data_by_timestamp(news_pip_data)

    # Once all data is extracted, save it locally for future use.
    print("\nsaving mined data to file")
    save_news_pip_data(haawks_id_str, symbol, news_pip_data)

    # Return the final news pip data dictionary.
    return news_pip_data


def calc_all_deviations_for_indicator(haawks_id):
    """
    Calculate the deviations between the actual and forecast values for a given haawks_id.

    For each record in the news data associated with the specified haawks_id, this function
    calculates the deviation between the 'Actual' and 'Forecast' values. The calculated
    deviation is then stored in a new column "Deviation" in the DataFrame.

    Args:
        haawks_id (str or int): The identifier of the haawks event.

    Notes:
        - The news data is read using the function `read_news_data(haawks_id)`.
        - The function prints the progress of deviation calculation.
        - If the 'Actual' or 'Forecast' data for a record is missing or invalid, that record is skipped.
        - After calculating the deviations, it saves the updated news data using the function `save_news_data(haawks_id, news_data)`.
        - The function prints the final DataFrame with the deviations calculated after processing.

    Example:
        >>> calc_all_deviations_for_indicator("12345")
        Calculating deviation for: 2023-08-14 12:30 (1/100)
        ...
        Calculating deviation for: 2023-08-15 12:30 (100/100)
        ... (DataFrame printed here)
    """
    news_data = read_news_data(haawks_id)
    row_count = news_data.shape[0]
    news_data = news_data.loc[:, ~news_data.columns.str.contains('Unnamed')]  # Remove unnamed column

    for index, row in news_data.iterrows():
        print(f"\rCalculating deviation for: {row['Timestamp']} ({str(index + 1)}/{row_count})", end="", flush=True)
        try:
            actual = convert_news_data_to_float(haawks_id, row['Actual'])
            forecast = convert_news_data_to_float(haawks_id, row['Forecast'])
            deviation = round(get_deviation(actual, forecast), 4)
            news_data.loc[index, "Deviation"] = deviation
        except ValueError:
            print(f"\nForecast data missing from {row['Timestamp']}... Skipping")

    print(news_data)
    save_news_data(haawks_id, news_data)


def calc_all_indicator_deviations():
    """
    Calculate deviations for all indicators listed in an Excel file.

    This function reads an Excel file that contains a list of financial indicators. For each
    indicator in this list, it prints a message showing progress and then calls another function,
    `calc_all_deviations_for_indicator`, to calculate deviations for the given indicator based on
    the unique Haawks ID associated with that indicator.

    Excel File Format:
        The Excel file, named "haawks-indicator-shortlist.xlsx", is expected to contain at least
        the following columns:
        - 'Id': The unique Haawks ID for the indicator
        - 'inv_title': The title or name of the indicator

    Example Output:
        Calculating deviations for: Unemployment Rate (1/25)
        Calculating deviations for: Inflation Rate (2/25)
        ...

    Notes:
        1. This function assumes that the Excel file "haawks-indicator-shortlist.xlsx" is in the
           current working directory.
        2. `calc_all_deviations_for_indicator(haawks_id_str)` is assumed to be a pre-defined function
           that takes a Haawks ID string as an argument and calculates deviations for the indicator
           associated with that ID.

    Example Usage:
        >>> calc_all_indicator_deviations()
    """
    indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")
    # indicators = indicators.iloc[17:].reset_index()

    row_count = indicators.shape[0]

    for index, row in indicators.iterrows():
        print(f"Calculating deviations for: {row['inv_title']} ({str(index + 1)}/{row_count})")
        haawks_id_str = haawks_id_to_str(row['Id'])
        calc_all_deviations_for_indicator(haawks_id_str)


def calc_mean_deviation(news_data):
    """
    Calculate deviations for all indicators listed in a specific Excel file.

    This function reads an Excel file named "haawks-indicator-shortlist.xlsx" that contains
    information about various indicators. For each indicator in the file, this function
    calls another function `calc_all_deviations_for_indicator(haawks_id_str)` to calculate
    the deviations for that specific indicator.

    Notes:
        - The progress of the calculation is printed to the console in the format:
          "Calculating deviations for: [indicator title] ([current index]/[total indicators])"
    """
    deviations = []

    for index, value in news_data['Deviation'].items():
        deviations.append(value)

    length = len(deviations)
    average = round(sum(deviations) / length, 2)

    return average


def calc_median_deviations(news_data):
    pos_deviations = []
    neg_deviations = []
    for index, value in news_data['Deviation'].items():
        if value > 0:
            pos_deviations.append(value)
        elif value < 0:
            neg_deviations.append(value)
        elif value == 0:
            pos_deviations.append(value)
            neg_deviations.append(value)

    pos_middle_index = math.floor(len(pos_deviations) / 2)  # rounds down in case of an odd length
    neg_middle_index = math.floor(len(neg_deviations) / 2)  # rounds down in case of an odd length

    pos_mean = pos_deviations[pos_middle_index]
    neg_mean = neg_deviations[neg_middle_index]

    return {
        "positive": pos_mean,
        "negative": neg_mean
    }


def calc_quantiles(data_list: list, quantile_count=5):
    """
    Calculate quantiles for a given list of data.

    Args:
        data_list (list): A list of numerical data for which quantiles are to be calculated.
        quantile_count (int, optional): The number of equal intervals to divide the data into.
                                        Defaults to 5 (quintiles).

    Returns:
        dict: A dictionary where keys are quantile values as strings and values are the data
              points at those quantiles.

    Raises:
        ValueError: If the length of data_list is smaller than the specified quantile_count.

    Example:
        >>> data = [2, 4, 4, 4, 5, 5, 7, 9]
        >>> calc_quantiles(data)
        {'0.2': 4, '0.4': 4, '0.6': 5, '0.8': 5}

    References:
        - https://www.thoughtco.com/what-is-a-quantile-3126239
        - https://www.statisticshowto.com/quantile-definition-find-easy-steps/
    """
    a = 1 / quantile_count
    n = len(data_list)
    quantiles = {}

    if n > quantile_count - 1:
        data_list.sort()

        for x in range(quantile_count - 1):
            q = round(a * (x + 1), 4)
            i = q * (n + 1)
            index = math.floor(i)
            quantiles[str(q)] = data_list[index]

        return quantiles
    else:
        raise ValueError("Data list is smaller than the quantile count. Cannot calculate")


def calc_deviation_quantiles(news_data, quantile_count=5):
    """
    Calculate quantiles for positive, negative, and combined deviations in news data.

    Args:
        news_data (pd.DataFrame): A DataFrame containing news data. It is assumed
                                  that there is a column named 'Deviation' which
                                  contains numerical values.
        quantile_count (int, optional): The number of equal intervals to divide the deviations
                                        into. Defaults to 5 (quintiles).

    Returns:
        dict: A dictionary with keys 'positive', 'negative', and 'combined'. Each key is
              associated with a dictionary of quantiles for that category.

    Example:
        >>> news_data = pd.DataFrame({'Deviation': [0.2, -0.1, 0.3, -0.2]})
        >>> calc_deviation_quantiles(news_data)
        {
            'positive': {'0.2': 0.2, '0.4': 0.2, '0.6': 0.3, '0.8': 0.3},
            'negative': {'0.2': -0.2, '0.4': -0.2, '0.6': -0.1, '0.8': -0.1},
            'combined': {'0.2': 0.1, '0.4': 0.2, '0.6': 0.2, '0.8': 0.3}
        }

    Note:
        This should be useful in deciding which triggers_vars to screen for.
    the default of 5 quantiles are technically called 'quintiles'

    References:
        - https://www.thoughtco.com/what-is-a-quantile-3126239
        - https://www.statisticshowto.com/quantile-definition-find-easy-steps/
    """
    pos_deviations = []
    neg_deviations = []
    all_deviations = []

    for index, value in news_data['Deviation'].items():
        if value > 0:
            pos_deviations.append(value)
            all_deviations.append(value)
        elif value < 0:
            neg_deviations.append(value)
            all_deviations.append(value * -1)

        elif value == 0:
            pos_deviations.append(value)
            neg_deviations.append(value)
            all_deviations.append(value)

    try:
        pos_quantiles = calc_quantiles(pos_deviations, quantile_count)
        neg_quantiles = calc_quantiles(neg_deviations, quantile_count)
        all_dev_quantiles = calc_quantiles(all_deviations, quantile_count)

        return {
            "positive": pos_quantiles,
            "negative": neg_quantiles,
            "combined": all_dev_quantiles,
        }
    except ValueError:
        pass


def calc_and_save_trigger_levels(haawks_id_str):
    """
    Calculate the quantiles for the deviations of a specific indicator and save them to the Excel file.
    The trigger levels calculated by this function can be further manually adjusted to be rounder numbers.

    Args:
        haawks_id_str (str): The identifier for the specific indicator in string format.

    Returns:
        dict: A dictionary containing the calculated trigger levels, or None if deviations are missing.
              Keys are in the format "trigger_n" and values are the calculated quantiles for the deviations.

    Example:
        >>> calc_and_save_trigger_levels("12345")
        {'trigger_1': 0.15, 'trigger_2': 0.30, 'trigger_3': 0.50, 'trigger_4': 0.70}

    Notes:
        - This function updates an Excel file "haawks-indicator-shortlist.xlsx" with the calculated trigger levels.
        - This just gets the quantiles for the deviations and populates the news data with it.
        - The levels it outputs were be adjusted manually afterwards to be more round numbers
    """
    news_data = read_news_data(haawks_id_str)
    indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")
    for index, row in indicators.iterrows():
        if haawks_id_to_str(row['Id']) == haawks_id_str:
            title = row['inv_title']
    if 'Deviation' in news_data.columns:

        quantiles = calc_deviation_quantiles(news_data)

        if quantiles is not None:
            triggers = {}

            for count, value in enumerate(quantiles['combined']):
                triggers[str(f"trigger_{count + 1}")] = quantiles['combined'][value]

            for index, row in indicators.iterrows():
                if haawks_id_to_str(row['Id']) == haawks_id_str:
                    for trigger in triggers:
                        indicators.loc[index, trigger] = triggers[trigger]

                    # print(indicators.loc[index])
                    break

            indicators.to_excel("haawks-indicator-shortlist.xlsx", index=False)
            return triggers
    else:
        print(f"Deviations missing from {title}... Skipping")


def calc_and_save_all_trigger_levels():
    """
    Iterate through all indicators listed in the Excel file and calculate and save the trigger levels
    for each of them using the `calc_and_save_trigger_levels` function.

    This function operates on all rows of the Excel file "haawks-indicator-shortlist.xlsx".

    Example:
        >>> calc_and_save_all_trigger_levels()
        Calculating triggers_vars for indicator 1/100: GDP
        Calculating triggers_vars for indicator 2/100: Unemployment Rate
        ...

    Note:
        This function updates an Excel file "haawks-indicator-shortlist.xlsx" with the calculated trigger levels
        for each indicator.
    """
    indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")
    # indicators = indicators.loc[28:]
    row_count = indicators.shape[0]
    for index, row in indicators.iterrows():
        print(f"\rCalculating triggers_vars for indicator {str(index + 1)}/{row_count}: {row['inv_title']}")

        calc_and_save_trigger_levels(haawks_id_to_str(row['Id']))


def read_triggers(haawks_id_str):
    """
    Read the trigger levels for a specific indicator from an Excel file.

    Args:
        haawks_id_str (str): The identifier for the specific indicator in string format.

    Returns:
        dict: A dictionary containing the trigger levels for the specified indicator.
              Keys are in the format "trigger_n" and values are the respective trigger levels.

    Example:
        >>> read_triggers("12345")
        {'trigger_1': 0.15, 'trigger_2': 0.30, 'trigger_3': 0.50, 'trigger_4': 0.70}

    Note:
        This function reads from an Excel file "haawks-indicator-shortlist.xlsx".
    """

    indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")
    for index, row in indicators.iterrows():
        if haawks_id_to_str(row['Id']) == haawks_id_str:
            triggers = {}
            i = 1
            while True:
                try:
                    triggers[f"trigger_{i}"] = row[f"trigger_{i}"]
                    i += 1
                except KeyError:
                    break
            break
    return triggers


def calc_correlation_1_score(values: list, expected_direction="positive"):
    """
    Calculate the percentage of values in a list that are in the expected direction.

    Args:
        values (list): A list of numerical values for which the correlation score is calculated.
        expected_direction (str, optional): The expected direction of the correlation; either "positive" or "negative".
                                           Default is "positive".

    Returns:
        float: The correlation score, expressed as a percentage.

    Raises:
        ValueError: If the `expected_direction` is not "positive" or "negative".

    Example:
        >>> calc_correlation_1_score([0.1, -0.2, 0.3, 0.4], expected_direction="positive")
        75.0
    """
    pos_values = []
    neg_values = []
    for value in values:
        if value > 0:
            pos_values.append(value)
        else:
            neg_values.append(value)

    if expected_direction == "positive":
        correlation_1_score = round((len(pos_values) / len(values)) * 100, 1)
    elif expected_direction == "negative":
        correlation_1_score = round((len(neg_values) / len(values)) * 100, 1)
    else:
        raise ValueError("Expected direction must be positive or negative")

    return correlation_1_score


def calc_correlation_2_score(values: list, expected_direction="positive"):
    """
    Calculate a correlation score based on the sum of positive and negative values in a list.

    Args:
        values (list): A list of numerical values for which the correlation score is calculated.
        expected_direction (str, optional): The expected direction of the correlation; either "positive" or "negative".
                                           Default is "positive".

    Returns:
        float: The correlation score, expressed as a percentage.

    Raises:
        ValueError: If the `expected_direction` is not "positive" or "negative".

    Example:
        >>> calc_correlation_2_score([0.1, -0.2, 0.3, 0.4], expected_direction="positive")
        64.3
    """
    pos_values = []
    neg_values = []
    for value in values:
        if value > 0:
            pos_values.append(value)
        else:
            neg_values.append(value * -1)
    if expected_direction == "positive":
        correlation_2_score = round((sum(pos_values) / (sum(pos_values) + sum(neg_values))) * 100, 1)
    elif expected_direction == "negative":
        correlation_2_score = round((sum(neg_values) / (sum(pos_values) + sum(neg_values))) * 100, 1)
    else:
        raise ValueError("Expected direction must be positive or negative")

    return correlation_2_score

def ema(values, window_size):
    """
    Calculate the Exponential Moving Average (EMA) of a list of numerical values.

    This function computes the EMA of the given data over a specified window size.
    The EMA is calculated using exponentially decreasing weights for older observations.

    Args:
        values (list or ndarray): A list or NumPy array of numerical values for which the EMA is calculated.
        window_size (int): The size of the moving window. This is the number of observations used for calculating
                           the EMA for each point.

    Returns:
        list: A list containing the computed EMA values. The length of the returned list is equal to the length of
              the input minus the window size plus 1. If the length of the input values is less than the window size,
              the input values are returned as is.

    Note:
        - The EMA is a type of weighted moving average where more weight is given to the latest data points.
        - The weights decrease exponentially as data points become older.

    Example:
        >>> ema([1, 2, 3, 4, 5], 3)
        [1.8, 2.8, 3.8, 4.8]

    Raises:
        No specific exceptions are raised, but the function expects numerical input values and a positive integer
        window size.

    """
    if len(values) < window_size:
        return values  # Not enough data to calculate the EMA

    # Create an array of linearly spaced values between -1 and 0 (inclusive), with a length equal to the window size.
    # This will be used to create the weights for the EMA calculation.
    linspace_values = np.linspace(-1., 0., window_size)

    # Calculate the exponential of each value in the linspace_values array.
    # This will transform the linearly spaced values into a set of exponential weights,
    # where the most recent value has the highest weight and the oldest value has the lowest weight.
    weights = np.exp(linspace_values)

    # Normalize the weights by dividing each weight by the sum of all weights.
    # This ensures that the sum of the weights equals 1.
    weights /= weights.sum()

    # Calculate the EMA using a convolution operation, which combines the input values (values) and the weights.
    # The 'valid' mode means that the output EMA array has a size equal to the input size minus the window size plus 1,
    # which ensures that there is no padding with zeros and that the EMA is only calculated where the values and
    # weights fully overlap.
    ema_values = np.convolve(values, weights, mode='valid')

    # Convert the resulting EMA array to a list and return it.
    return list(ema_values)


def calc_news_pip_metrics_old(haawks_id_str, news_pip_data, triggers, symbol_higher_dev):
    """
    Calculate news pip metrics for each trigger.

    This function processes raw news pip data and calculates various metrics, such as mean,
    median, range, and correlation scores for each trigger. The calculation is based on the
    deviation of news pips at different timestamps, and whether the symbol is expected to be
    bullish or bearish for higher deviations.

    Args:
        haawks_id_str (str): A unique identifier string for the haawks indicator.
        news_pip_data (dict): A dictionary containing news pip data, where the key is the timestamp
                              and the value is a dictionary containing 'deviation' and 'pips' for the timestamp.
        triggers (dict): A dictionary containing trigger names as keys and corresponding deviation
                         values as values.
        symbol_higher_dev (str): The expected direction of higher deviations. Can be "bullish" or "bearish".

    Returns:
        news_pip_metrics (dict): A nested dictionary containing news pip metrics for each trigger.
                                 The structure is: {trigger: {time_delta: {metric_name: metric_value}}}.

                                 Here, 'trigger' is the trigger name, 'time_delta' is a specific time period
                                 after a news event, 'metric_name' is the name of the calculated metric,
                                 and 'metric_value' is the calculated value for that metric.

    Notes:
        - The 'deviation' value is used to determine how significant the news event is.
        - Metrics include median, mean, range of pips, correlation scores, and more for different time periods.

    Example:
        >>> news_pip_data = {timestamp1: {'deviation': 0.5, 'pips': {...}}, timestamp2: {...}}
        >>> triggers = {'trigger_1': 0.2, 'trigger_2': 0.5}
        >>> calc_news_pip_metrics('hawk_id', news_pip_data, triggers, 'bullish')
        {'trigger_1': {...}, 'trigger_2': {...}}

    Raises:
        ValueError: If 'symbol_higher_dev' is not "bullish" or "bearish".
    """
    print("Calculating news pip metrics...")
    news_pip_metrics = {}
    indicator_info = get_indicator_info(haawks_id_str)
    inv_currency = indicator_info['inv_currency']

    for trigger in triggers:
        news_pip_metrics[trigger] = {}

    for timestamp in news_pip_data:
        # Retrieve deviation value and check if it is negative
        deviation = news_pip_data[timestamp]['deviation']
        if deviation < 0:
            deviation = deviation * -1
            negative_dev = True
        else:
            negative_dev = False

        for index, trigger in enumerate(list(triggers.items())):
            # Check if deviation falls within the range of the current trigger
            if trigger[1] == 0:
                continue
            if index == len(triggers) - 1:
                if deviation >= trigger[1]:
                    break  # Keeps trigger at current value before continuing
            else:
                if list(triggers.items())[index + 1][1] > 0:
                    if trigger[1] <= deviation < list(triggers.items())[index + 1][1]:
                        break  # Keeps trigger at current value before continuing
                else:
                    if trigger[1] <= deviation:
                        break  # Keeps trigger at current value before continuing

        for time_delta in news_pip_data[timestamp]['pips']:
            # Retrieve ask and bid values for the given time delta
            ask = news_pip_data[timestamp]['pips'][time_delta][0]
            bid = news_pip_data[timestamp]['pips'][time_delta][1]

            if negative_dev:
                ask = ask * -1
                bid = bid * -1

            # Determine the direction of the pips (positive or negative)
            if ask < 0 and bid < 0:  # ask/bid both negative
                pips = bid
            elif ask >= 0 and bid >= 0:  # ask/bid both positive
                pips = ask
            elif ask < 0 and bid > 0:  # ask negative and bid positive (This should never happen)
                if bid > ask * -1:
                    pips = bid
                else:
                    pips = ask
            elif ask >= 0 and bid < 0:  # ask positive and bid negative
                if ask > bid * -1:
                    pips = ask
                else:
                    pips = bid

            # Add pips to the corresponding trigger and time delta
            if trigger[1] != 0:
                news_pip_metrics[trigger[0]].setdefault(time_delta, []).append(pips)

    for trigger in news_pip_metrics:
        for time_delta, values in news_pip_metrics[trigger].items():
            # Sort the list of pips values in ascending order
            values.sort()
            # Calculate the median value of the pips values
            median = values[math.floor((len(values) - 1) / 2)]
            # Calculate the mean value of the pips values, rounded to 1 decimal place
            mean = round(sum(values) / len(values), 1)
            # Calculate the range of the pips values as a tuple of the minimum and maximum values
            range = (min(values), max(values))

            if symbol_higher_dev == "bullish":
                # Calculate the correlation 1 score for positive expected direction
                correlation_1_score = calc_correlation_1_score(values, expected_direction="positive")
                # Calculate the correlation 2 score for positive expected direction
                correlation_2_score = calc_correlation_2_score(values, expected_direction="positive")
            elif symbol_higher_dev == "bearish":
                # Calculate the correlation 1 score for negative expected direction
                correlation_1_score = calc_correlation_1_score(values, expected_direction="negative")
                # Calculate the correlation 2 score for negative expected direction
                correlation_2_score = calc_correlation_2_score(values, expected_direction="negative")
            else:
                # Raise an exception if higher_dev is not "bullish" or "bearish"
                raise ValueError("higher_dev must be 'bullish' or 'bearish'")

            # Calculate the average of the two correlation scores, rounded to 1 decimal place
            correlation_3_score = round((correlation_1_score + correlation_2_score) / 2, 1)

            # Add the calculated metrics to the news_pip_metrics dictionary
            news_pip_metrics[trigger][time_delta] = {
                "median": median,
                "mean": mean,
                "range": range,
                "correlation_1": correlation_1_score,
                "correlation_2": correlation_2_score,
                "correlation_3": correlation_3_score,
                "values": values
            }

            # Calculate the EMA values for different periods (EMA5, EMA10, and EMA15) for the given time_delta and trigger
            ema5_values = ema(values, 5)
            ema10_values = ema(values, 10)
            ema15_values = ema(values, 15)

            # Create a list containing the EMA values and their corresponding suffixes for labeling purposes
            ema_values_list = [(ema5_values, 'ema5'), (ema10_values, 'ema10'), (ema15_values, 'ema15')]

            # Iterate through the list of EMA values and suffixes
            for ema_values, ema_suffix in ema_values_list:
                # Calculate the EMA-based correlation scores depending on the symbol_higher_dev value
                if symbol_higher_dev == "bullish":
                    correlation_1_ema = calc_correlation_1_score(ema_values, expected_direction="positive")
                    correlation_2_ema = calc_correlation_2_score(ema_values, expected_direction="positive")
                elif symbol_higher_dev == "bearish":
                    correlation_1_ema = calc_correlation_1_score(ema_values, expected_direction="negative")
                    correlation_2_ema = calc_correlation_2_score(ema_values, expected_direction="negative")
                else:
                    raise ValueError("higher_dev must be 'bullish' or 'bearish'")

                # Calculate the average of the two correlation scores for the current EMA period, rounding to 1 decimal place
                correlation_3_ema = round((correlation_1_ema + correlation_2_ema) / 2, 1)

                # Add the calculated correlation scores to the news_pip_metrics dictionary with the corresponding EMA suffixes
                news_pip_metrics[trigger][time_delta].update({
                    f"correlation_1_{ema_suffix}": correlation_1_ema,
                    f"correlation_2_{ema_suffix}": correlation_2_ema,
                    f"correlation_3_{ema_suffix}": correlation_3_ema,
                })

    # Return the dictionary of news_pip_metrics
    return news_pip_metrics


def calculate_relative_pips(ask, bid, negative_dev):
    """
    Calculate the 'pips' based on ask and bid values and whether the deviation is negative.
    """
    if negative_dev:
        ask, bid = ask * -1, bid * -1

    if ask < 0 and bid < 0:
        return bid
    elif ask >= 0 and bid >= 0:
        return ask
    elif ask < 0 and bid > 0:
        return bid if bid > ask * -1 else ask
    else:  # ask >= 0 and bid < 0
        return ask if ask > bid * -1 else bid


def calculate_basic_metrics(values):
    """
    Calculate the median, mean, and range of a list of 'pips' values.
    """
    values.sort()
    median = values[math.floor((len(values) - 1) / 2)]
    mean = round(sum(values) / len(values), 1)
    range_of_values = (min(values), max(values))
    return median, mean, range_of_values


def get_correlation_scores(values, symbol_higher_dev):
    """
    Calculate correlation scores based on the expected direction of the 'symbol_higher_dev'.
    """
    expected_direction = "positive" if symbol_higher_dev == "bullish" else "negative"
    correlation_1_score = calc_correlation_1_score(values, expected_direction)
    correlation_2_score = calc_correlation_2_score(values, expected_direction)
    correlation_3_score = round((correlation_1_score + correlation_2_score) / 2, 1)
    return correlation_1_score, correlation_2_score, correlation_3_score

def get_expected_direction(symbol_higher_dev):
    if symbol_higher_dev == "bullish":
        expected_direction = "positive"
    elif symbol_higher_dev == "bearish":
        expected_direction = "negative"
    else:
        raise ValueError("higher_dev must be 'bullish' or 'bearish'")

    return expected_direction


def get_c3_ema_scores(ema_values, ema_suffix, symbol_higher_dev):
    """
    Calculate EMA-based correlation scores and label them with a suffix indicating the EMA period.
    """

    expected_direction = get_expected_direction(symbol_higher_dev)

    correlation_1_ema = calc_correlation_1_score(ema_values, expected_direction)
    correlation_2_ema = calc_correlation_2_score(ema_values, expected_direction)
    correlation_3_ema = round((correlation_1_ema + correlation_2_ema) / 2, 1)

    return {
        f"correlation_1_{ema_suffix}": correlation_1_ema,
        f"correlation_2_{ema_suffix}": correlation_2_ema,
        f"correlation_3_{ema_suffix}": correlation_3_ema,
    }

# TODO: Write get_tsl_hits here


def calc_news_pip_metrics(haawks_id_str, news_pip_data, triggers, symbol_higher_dev):
    """
    Calculate news pip metrics for each trigger.

    Parameters:
    - haawks_id_str (str): Haawks ID as a string.
    - news_pip_data (dict): Dictionary containing news pip data for different timestamps.
    - triggers (list): List of triggers to consider.
    - symbol_higher_dev (str): Expected direction of the trading symbol.

    Returns:
    - news_pip_metrics (dict): Dictionary containing calculated news pip metrics for each trigger and time delta.
    """
    # Print a message indicating the start of news pip metrics calculation
    print("Calculating news pip metrics...")

    # Initialize an empty dictionary to store news pip metrics for each trigger
    news_pip_metrics = {trigger: {} for trigger in triggers}

    # Get information about the indicator using its Haawks ID
    indicator_info = get_indicator_info(haawks_id_str)

    # Iterate through each timestamp in the news pip data
    for timestamp in news_pip_data:
        # Preprocess deviation and find the trigger for the current timestamp
        deviation, negative_dev = preprocess_deviation(news_pip_data, timestamp)
        trigger = find_trigger(deviation, triggers)

        # Iterate through each time delta and calculate relative pips
        for time_delta in news_pip_data[timestamp]['pips']:
            ask, bid = news_pip_data[timestamp]['pips'][time_delta]
            pips = calculate_relative_pips(ask, bid, negative_dev)

            # If a trigger is found, store the calculated pips in the corresponding trigger's dictionary
            if trigger:
                news_pip_metrics[trigger[0]].setdefault(time_delta, []).append(pips)

    # Iterate through each trigger in the news_pip_metrics dictionary
    for trigger in news_pip_metrics:
        # Iterate through each time delta and its associated pips values
        for time_delta, values in news_pip_metrics[trigger].items():
            # Calculate basic metrics (median, mean, range) for the pips values
            median, mean, range_of_values = calculate_basic_metrics(values)

            # Get correlation scores for the pips values with respect to the expected symbol direction
            correlation_1, correlation_2, correlation_3 = get_correlation_scores(values, symbol_higher_dev)

            #first_stoploss_hit_timedelta = get_first_stoploss_hit_timedelta()

            # Store the calculated metrics in the news_pip_metrics dictionary
            news_pip_metrics[trigger][time_delta] = {
                "median": median,
                "mean": mean,
                "range": range_of_values,
                "correlation_1": correlation_1,
                "correlation_2": correlation_2,
                "correlation_3": correlation_3,
                "values": values
            }

            # Compute EMA values for various periods and their corresponding correlation scores
            c3_ema_values_list = [
                (ema(values, 5), 'ema5'),
                (ema(values, 10), 'ema10'),
                (ema(values, 15), 'ema15')
            ]

            # Iterate through the calculated EMA values and their corresponding suffixes
            for c3_ema_values, ema_suffix in c3_ema_values_list:
                # Get correlation scores for the EMA values with respect to the expected symbol direction
                c3_ema_scores = get_c3_ema_scores(c3_ema_values, ema_suffix, symbol_higher_dev)


                # Update the news_pip_metrics dictionary with the EMA correlation scores
                news_pip_metrics[trigger][time_delta].update(c3_ema_scores)



    # Return the final news_pip_metrics dictionary
    return news_pip_metrics


# Helper function to preprocess deviation values
def preprocess_deviation(news_pip_data, timestamp):
    """
    Process deviation value and check if it is negative.
    """
    deviation = news_pip_data[timestamp]['deviation']
    negative_dev = False
    if deviation < 0:
        deviation = deviation * -1
        negative_dev = True
    return deviation, negative_dev


# Helper function to find the trigger for a given deviation
def find_trigger(deviation, triggers):
    """
    Find the corresponding trigger for the given deviation value.
    """
    for index, trigger in enumerate(list(triggers.items())):
        if trigger[1] == 0:
            continue
        if index == len(triggers) - 1:
            if deviation >= trigger[1]:
                return trigger
        else:
            next_trigger = list(triggers.items())[index + 1]
            if next_trigger[1] > 0:
                if trigger[1] <= deviation < next_trigger[1]:
                    return trigger
            else:
                if trigger[1] <= deviation:
                    return trigger
    return None


# The calc_correlation_1_score, calc_correlation_2_score, ema and get_indicator_info functions
# are assumed to be previously defined or imported as they were not included in the original code.


def calc_pip_averages_and_correlation(values: list):
    """
    Calculate various statistical metrics and correlation scores for a given list of pip values.

    This function takes a list of numerical pip values (pips), sorts them in ascending order, and
    calculates several statistical metrics such as the median, mean, and range. It also computes
    correlation scores using two different correlation calculation functions, and averages these
    two scores to produce a third correlation score.

    Args:
        values (list): A list of numerical pip values. 'Pips' in this context refer to the smallest
                       price move that a given exchange rate can make based on market convention.

    Returns:
        dict: A dictionary containing the calculated statistical metrics and correlation scores.
              The keys and their corresponding values in the dictionary are as follows:
              - "median": The median of the pip values.
              - "mean": The mean of the pip values, rounded to one decimal place.
              - "range": A tuple containing the minimum and maximum pip values.
              - "correlation_1": The first correlation score, calculated using `calc_correlation_1_score`.
              - "correlation_2": The second correlation score, calculated using `calc_correlation_2_score`.
              - "correlation_3": The average of `correlation_1` and `correlation_2`.
              - "values": The sorted list of pip values.

    Example:
        >>> pip_values = [1.5, 2.3, 0.9, 1.8, 1.6]
        >>> calc_pip_averages_and_correlation(pip_values)
        {
            'median': 1.6,
            'mean': 1.6,
            'range': (0.9, 2.3),
            'correlation_1': 0.85,
            'correlation_2': 0.78,
            'correlation_3': 0.815,
            'values': [0.9, 1.5, 1.6, 1.8, 2.3]
        }
    """
    values.sort()
    median = values[math.floor((len(values) - 1) / 2)]
    mean = round(sum(values) / len(values), 1)
    range = (min(values), max(values))
    correlation_1_score = calc_correlation_1_score(values)
    correlation_2_score = calc_correlation_2_score(values)
    correlation_3_score = (correlation_1_score + correlation_2_score) / 2
    return {
        "median": median,
        "mean": mean,
        "range": range,
        "correlation_1": correlation_1_score,
        "correlation_2": correlation_2_score,
        "correlation_3": correlation_3_score,
        "values": values
    }


def calc_news_pip_metrics_2(news_pip_data, triggers):
    """
    Calculate news pip metrics based on given trigger levels and news pip data.

    This function processes news pip data, which contains price deviations at
    different timestamps, and organizes them according to the predefined trigger
    levels specified in `triggers`. For each trigger level, it computes and
    organizes pip data into positive and negative deviations, and calculates various
    statistical metrics for those deviations using an external function
    `calc_pip_averages_and_correlation`.

    Args:
        news_pip_data (dict): A dictionary where each key is a timestamp, and the value
                              is another dictionary containing 'deviation' and 'pips' data.
                              For example:
                              {
                                  'timestamp1': {'deviation': x, 'pips': {time_delta: [ask, bid], ...}},
                                  ...
                              }

        triggers (dict): A dictionary containing named trigger levels as keys and
                         corresponding numerical values as values. For example:
                         {
                             'level1': value1,
                             'level2': value2,
                             ...
                         }

    Returns:
        dict: A nested dictionary organized first by trigger levels, then by time deltas,
              and finally by the type of deviation ('positive_dev', 'negative_dev', 'combined').
              Each type of deviation contains the statistical metrics calculated by the
              `calc_pip_averages_and_correlation` function.

              For example:
              {
                  'level1': {
                      time_delta1: {
                          'positive_dev': {...},
                          'negative_dev': {...},
                          'combined': {...}
                      },
                      ...
                  },
                  ...
              }

    Raises:
        UnboundLocalError: If both positive and negative deviations do not exist
                           for a certain trigger and time_delta pair.

    Example:
        >>> news_pip_data = {'2021-01-01': {'deviation': 2, 'pips': {1: [0.1, -0.1], 2: [0.2, -0.2]}}}
        >>> triggers = {'level1': 1, 'level2': 3}
        >>> calc_news_pip_metrics_2(news_pip_data, triggers)
        {
            'level1': {
                1: {
                    'positive_dev': {...},
                    'negative_dev': {...},
                    'combined': {...}
                },
                2: {
                    ...
                }
            },
            'level2': {
                ...
            }
        }
    """
    news_pip_metrics = {}

    for trigger in triggers:
        news_pip_metrics[trigger] = {}

    for timestamp in news_pip_data:

        deviation = news_pip_data[timestamp]['deviation']

        if deviation < 0:
            negative_dev = True
            for index, trigger in enumerate(list(triggers.items())):  # Identifies appropriate trigger level

                if index == len(triggers) - 1:  # If it's the last trigger
                    if deviation <= (triggers[trigger[0]] * -1):
                        break  # Keeps trigger at current value before continuing
                else:
                    if (triggers[trigger[0]] * -1) >= deviation > (list(triggers.items())[index + 1][1] * -1):
                        break  # Keeps trigger at current value before continuing
        else:
            negative_dev = False
            for index, trigger in enumerate(list(triggers.items())):  # Identifies appropriate trigger level

                if index == len(triggers) - 1:  # If it's the last trigger
                    if deviation >= triggers[trigger[0]]:
                        break  # Keeps trigger at current value before continuing
                else:
                    if triggers[trigger[0]] <= deviation < list(triggers.items())[index + 1][1]:
                        break  # Keeps trigger at current value before continuing

        for time_delta in news_pip_data[timestamp]['pips']:

            ask = news_pip_data[timestamp]['pips'][time_delta][0]
            bid = news_pip_data[timestamp]['pips'][time_delta][1]

            # if negative_dev:
            #     ask = ask * -1
            #     bid = bid * -1

            if ask < 0 and bid < 0:  # ask/bid both negative
                pips = bid
            elif ask > 0 and bid > 0:  # ask/bid both positive
                pips = ask
            elif ask < 0 and bid > 0:  # ask negative and bid positive (This should never happen)
                if bid > ask * -1:
                    pips = bid
                else:
                    pips = ask
            elif ask > 0 and bid < 0:  # ask positive and bid negative
                if ask > bid * -1:
                    pips = ask
                else:
                    pips = bid

            # news_pip_metrics[trigger[0]].append(pips)
            if not negative_dev:
                news_pip_metrics[trigger[0]].setdefault(time_delta, {}).setdefault("positive_dev", []).append(pips)
            elif negative_dev:
                news_pip_metrics[trigger[0]].setdefault(time_delta, {}).setdefault("negative_dev", []).append(pips)

    for trigger in news_pip_metrics:

        for time_delta in news_pip_metrics[trigger]:

            try:
                pos_dev_values = news_pip_metrics[trigger][time_delta]['positive_dev']
                positive_dev_averages = calc_pip_averages_and_correlation(pos_dev_values)
            except KeyError:
                print(f"No positive deviations for {trigger}")
            try:
                neg_dev_values = news_pip_metrics[trigger][time_delta]['negative_dev']
                negative_dev_averages = calc_pip_averages_and_correlation(neg_dev_values)
            except KeyError:
                print(f"No negative deviations for {trigger}")

            try:
                for index, value in enumerate(neg_dev_values):
                    neg_dev_values[index] = value * -1

                combined_values = pos_dev_values + neg_dev_values

                combined_dev_averages = calc_pip_averages_and_correlation(combined_values)

                news_pip_metrics[trigger][time_delta]['positive_dev'] = positive_dev_averages
                news_pip_metrics[trigger][time_delta]['negative_dev'] = negative_dev_averages
                news_pip_metrics[trigger][time_delta]['combined'] = combined_dev_averages
            except UnboundLocalError:
                try:
                    news_pip_metrics[trigger][time_delta]['positive_dev'] = positive_dev_averages
                except UnboundLocalError:
                    news_pip_metrics[trigger][time_delta]['negative_dev'] = negative_dev_averages
            # breakpoint()
    return news_pip_metrics


def calc_news_pip_metrics_for_multiple_indicators(haawks_id_strs_and_symbols: list[tuple[str, str]]):
    """
    Calculate news pip metrics for multiple indicators using their Haawks ID strings and symbols.

    This function processes a list of Haawks ID strings and symbols for various financial
    indicators. For each pair of Haawks ID string and symbol, the function retrieves
    the indicator information, reads news data and trigger levels, loads the news pip data,
    and calculates the news pip metrics. It organizes the results in a dictionary,
    where the keys are formatted as "{Haawks_ID_String}_{Symbol} {Indicator_Title}",
    and the values are the corresponding news pip metrics.

    Args:
        haawks_id_strs_and_symbols (list[tuple[str, str]]): A list of tuples, where each tuple contains
                                                            two elements:
                                                            1. Haawks ID string for a financial indicator,
                                                            2. Symbol representing the financial instrument
                                                               (e.g., currency pair or stock symbol).

    Returns:
        dict: A dictionary where each key is a formatted string "{Haawks_ID_String}_{Symbol} {Indicator_Title}",
              and the value is the corresponding news pip metrics calculated for that indicator and symbol pair.

              For example:
              {
                  '1234_EURUSD Inflation': {...},
                  '5678_USDJPY Employment': {...},
                  ...
              }

    Example:
        >>> haawks_id_strs_and_symbols = [('1234', 'EURUSD'), ('5678', 'USDJPY')]
        >>> calc_news_pip_metrics_for_multiple_indicators(haawks_id_strs_and_symbols)
        {
            '1234_EURUSD Inflation': {...},
            '5678_USDJPY Employment': {...},
        }
    """
    result = {}

    for haawks_id_str_and_symbol in haawks_id_strs_and_symbols:
        haawks_id_str = haawks_id_str_and_symbol[0]
        indicator_info = get_indicator_info(haawks_id_str)
        title = indicator_info['inv_title']
        symbol = indicator_info['symbol']
        higher_dev = indicator_info['higher_dev']
        news_data = read_news_data(haawks_id_str)
        triggers = read_triggers(haawks_id_str)

        expected_directions = []

        for value in news_data['Deviation']:
            if value >= 0:
                expected_directions.append("up")
            else:
                expected_directions.append("down")

        news_data['expected_direction'] = expected_directions

        news_pip_data = load_news_pip_movements_at_timedeltas(haawks_id_str, news_data, symbol)
        news_pip_metrics = calc_news_pip_metrics(haawks_id_str, symbol, news_pip_data, triggers, higher_dev)
        result.setdefault(f"{haawks_id_str}_{symbol} {title}", news_pip_metrics)

    return result

def calc_pip_metrics_df_total_averages(pip_metrics_df: pd.DataFrame, trigger_name: str):
    """
    Calculate the total range and averages of various metrics for given pip data in a DataFrame.

    This function iterates through rows of a DataFrame containing pip metrics data, computes the
    total range and calculates the mean of various metrics including means, medians, c1_scores,
    c2_scores, c3_scores, and various Exponential Moving Averages (EMAs). The results are
    returned as a pandas Series.

    Args:
        pip_metrics_df (pd.DataFrame): A DataFrame containing pip metrics data with columns including
                                       'range', 'mean', 'median', various correlation scores (e.g., 'c1', 'c2', 'c3'),
                                       and various EMAs (e.g., 'c1_ema5', 'c2_ema5', 'c3_ema5').
        trigger_name (str): A string representing the name of the trigger for which the pip metrics
                            are calculated.

    Returns:
        pd.Series: A pandas Series containing the total range, the mean of various metrics, and
                   data points for each metric. The index of the Series represents the names of
                   these metrics.

    Example:
        >>> pip_metrics_df = pd.DataFrame({'range': [(1,5), (2,6)], 'mean': [2, 4], 'median': [2.5, 4.5], ...})
        >>> trigger_name = 'Trigger1'
        >>> calc_pip_metrics_df_total_averages(pip_metrics_df, trigger_name)
        time_delta    Total/Averages
        range            (1, 6)
        mean                3.0
        median              3.5
        ...
        data_points        100
        dtype: object

    Note:
        The function also prints the calculated total averages to the console with the format:
        "{trigger_name} total_averages:\n {total_averages}"
    """
    total_range = [0, 0]
    means = []
    medians = []
    c1_scores = []
    c2_scores = []
    c3_scores = []
    c1_ema5_scores = []
    c2_ema5_scores = []
    c3_ema5_scores = []
    c1_ema10_scores = []
    c2_ema10_scores = []
    c3_ema10_scores = []
    c1_ema15_scores = []
    c2_ema15_scores = []
    c3_ema15_scores = []
    for index, row in pip_metrics_df.iterrows():
        if row['range'][0] < total_range[0]:
            total_range[0] = row['range'][0]
        if row['range'][1] > total_range[1]:
            total_range[1] = row['range'][1]

        means.append(row['mean'])
        medians.append(row['median'])
        c1_scores.append(row['c1'])
        c2_scores.append(row['c2'])
        c3_scores.append(row['c3'])
        c1_ema5_scores.append(row['c1_ema5'])
        c2_ema5_scores.append(row['c2_ema5'])
        c3_ema5_scores.append(row['c3_ema5'])
        c1_ema10_scores.append(row['c1_ema10'])
        c2_ema10_scores.append(row['c2_ema10'])
        c3_ema10_scores.append(row['c3_ema10'])
        c1_ema15_scores.append(row['c1_ema15'])
        c2_ema15_scores.append(row['c2_ema15'])
        c3_ema15_scores.append(row['c3_ema15'])

    total_range = tuple(total_range)
    mean_mean = round(sum(means) / len(means), 1)
    mean_median = round(sum(medians) / len(medians), 1)
    mean_c1 = round(sum(c1_scores) / len(c1_scores), 1)
    mean_c2 = round(sum(c2_scores) / len(c2_scores), 1)
    mean_c3 = round(sum(c3_scores) / len(c3_scores), 1)
    mean_c1_ema5 = round(sum(c1_ema5_scores) / len(c1_ema5_scores), 1)
    mean_c2_ema5 = round(sum(c2_ema5_scores) / len(c2_ema5_scores), 1)
    mean_c3_ema5 = round(sum(c3_ema5_scores) / len(c3_ema5_scores), 1)
    mean_c1_ema10 = round(sum(c1_ema10_scores) / len(c1_ema10_scores), 1)
    mean_c2_ema10 = round(sum(c2_ema10_scores) / len(c2_ema10_scores), 1)
    mean_c3_ema10 = round(sum(c3_ema10_scores) / len(c3_ema10_scores), 1)
    mean_c1_ema15 = round(sum(c1_ema15_scores) / len(c1_ema15_scores), 1)
    mean_c2_ema15 = round(sum(c2_ema15_scores) / len(c2_ema15_scores), 1)
    mean_c3_ema15 = round(sum(c3_ema15_scores) / len(c3_ema15_scores), 1)

    data_points = pip_metrics_df.iloc[0]['data_points']

    """
    return ['Total/Averages', total_range, mean_mean, mean_median, mean_c1, mean_c2, mean_c3, mean_c1_ema5,
            mean_c2_ema5, mean_c3_ema5, mean_c1_ema10, mean_c2_ema10, mean_c3_ema10, mean_c1_ema15,
            mean_c2_ema15, mean_c3_ema15,  data_points]
    """

    total_averages = pd.Series(data={
                                    'time_delta': 'Total/Averages',
                                    'range': total_range,
                                    'mean': mean_mean,
                                    'median': mean_median,
                                    'c1': mean_c1,
                                    'c2': mean_c2,
                                    'c3': mean_c3,
                                    'c1_ema5': mean_c1_ema5,
                                    'c2_ema5': mean_c2_ema5,
                                    'c3_ema5': mean_c3_ema5,
                                    'c1_ema10': mean_c1_ema10,
                                    'c2_ema10': mean_c2_ema10,
                                    'c3_ema10': mean_c3_ema10,
                                    'c1_ema15': mean_c1_ema15,
                                    'c2_ema15': mean_c2_ema15,
                                    'c3_ema15': mean_c3_ema15,
                                    'data_points': data_points
                               },
                               index=[
                                    'time_delta', 'range', 'mean', 'median',
                                    'c1', 'c2', 'c3',
                                    'c1_ema5', 'c2_ema5', 'c3_ema5',
                                    'c1_ema10', 'c2_ema10', 'c3_ema10',
                                    'c1_ema15', 'c2_ema15', 'c3_ema15', 'data_points'
                               ])

    print(f"{trigger_name} total_averages:\n {total_averages}")
    return total_averages


def calc_lowest_ema_c3(total_averages):
    """
    Calculate the lowest EMA (Exponential Moving Average) among c3 related metrics.

    This function takes in a pandas Series of total averages and various EMAs of the c3 metric.
    It finds the lowest EMA among c3 related metrics (c3, c3_ema5, c3_ema10, c3_ema15) and
    appends this information to the input Series as 'lowest_c3_type' and 'lowest_c3_val'.

    Args:
        total_averages (pd.Series): A pandas Series containing total averages and various EMAs of
                                    the c3 metric.
                                    Example: ['c3', 'c3_ema5', 'c3_ema10', 'c3_ema15']

    Returns:
        pd.Series: The updated pandas Series containing the input total averages along with the
                   'lowest_c3_type' and 'lowest_c3_val'.

    Prints:
        The type and value of the lowest EMA c3 metric, and the updated total averages with the
        lowest EMA c3 information.
    """
    c3 = total_averages['c3']
    c3_ema5 = total_averages['c3_ema5']
    c3_ema10 = total_averages['c3_ema10']
    c3_ema15 = total_averages['c3_ema5']

    c3_keys = ["c3", "c3_ema5", "c3_ema10", "c3_ema15"]
    c3_vals = [c3, c3_ema5, c3_ema10, c3_ema15]

    lowest_c3_index = c3_vals.index(min(c3_vals))
    lowest_c3_type = c3_keys[lowest_c3_index]
    lowest_c3_val = c3_vals[lowest_c3_index]

    total_averages_and_lowest_ema_c3 = total_averages.append(pd.Series([lowest_c3_type, lowest_c3_val],
                                    index=['lowest_c3_type', 'lowest_c3_val']))

    print(f"lowest_ema_c3:\n [{lowest_c3_type}: {lowest_c3_val}]")
    print(f"total_averages_and_lowest_ema_c3:\n {total_averages_and_lowest_ema_c3}")

    return total_averages_and_lowest_ema_c3


def news_pip_trigger_data_to_df(trigger_data, trigger_name):
    """
    Convert the raw news pip trigger data into a formatted DataFrame.

    This function takes a raw data structure containing pip trigger data related to news and
    transforms it into a structured pandas DataFrame. The DataFrame includes various metrics
    and their EMAs (Exponential Moving Averages) for each time_delta in the trigger data.
    It also appends a row for the total averages and the lowest EMA c3 metric.

    Args:
        trigger_data (dict): A dictionary containing pip trigger data for various time_delta.
                             Each time_delta is associated with a dictionary containing various
                             metrics and their EMAs.

        trigger_name (str): A string representing the name of the trigger for which the pip metrics
                            are calculated.

    Returns:
        pd.DataFrame: A pandas DataFrame structured with columns representing time_delta, range, mean,
                      median, various correlation scores (e.g., 'c1', 'c2', 'c3'), various EMAs,
                      data points, lowest_c3_type, and lowest_c3_val.

    Example:
        >>> trigger_data = {'1s': {'range': (1,5), 'mean': 2, 'median': 2.5, ...}, ...}
        >>> trigger_name = 'Trigger1'
        >>> news_pip_trigger_data_to_df(trigger_data, trigger_name)
        ...
        time_delta    1s
        range         (1, 5)
        mean            2
        ...
        lowest_c3_type  c3
        lowest_c3_val   0.5
        Name: 0, dtype: object
    """
    df = pd.DataFrame(
        columns=['time_delta', 'range', 'mean', 'median',
                 'c1', 'c2', 'c3',
                 'c1_ema5', 'c2_ema5', 'c3_ema5',
                 'c1_ema10', 'c2_ema10', 'c3_ema10',
                 'c1_ema15', 'c2_ema15', 'c3_ema15',
                 'data_points', 'lowest_c3_type', 'lowest_c3_val'])
    data_points = len(trigger_data['1s']['values'])

    for time_delta in trigger_data:
        range = trigger_data[time_delta]['range']
        mean = trigger_data[time_delta]['mean']
        median = trigger_data[time_delta]['median']
        c1 = trigger_data[time_delta]['correlation_1']
        c2 = trigger_data[time_delta]['correlation_2']
        c3 = trigger_data[time_delta]['correlation_3']
        c1_ema5 = trigger_data[time_delta]['correlation_1_ema5']
        c2_ema5 = trigger_data[time_delta]['correlation_2_ema5']
        c3_ema5 = trigger_data[time_delta]['correlation_3_ema5']
        c1_ema10 = trigger_data[time_delta]['correlation_1_ema10']
        c2_ema10 = trigger_data[time_delta]['correlation_2_ema10']
        c3_ema10 = trigger_data[time_delta]['correlation_3_ema10']
        c1_ema15 = trigger_data[time_delta]['correlation_1_ema15']
        c2_ema15 = trigger_data[time_delta]['correlation_2_ema15']
        c3_ema15 = trigger_data[time_delta]['correlation_3_ema15']

        df.loc[len(df.index)] = [time_delta, range, mean, median, c1, c2, c3, c1_ema5, c2_ema5, c3_ema5,
                                 c1_ema10, c2_ema10, c3_ema10, c1_ema15, c2_ema15, c3_ema15,  data_points, None, None]

    total_averages = calc_pip_metrics_df_total_averages(df, trigger_name)

    total_averages_and_lowest_ema_c3 = calc_lowest_ema_c3(total_averages)
    df.loc[len(df.index)] = total_averages_and_lowest_ema_c3
    return df


def news_pip_metrics_to_dfs(news_pip_metrics):
    """
    Convert the news pip metrics for multiple triggers into a dictionary of DataFrames.

    This function takes in a dictionary of news pip metrics associated with various triggers
    and converts each set of pip metrics for each trigger into a structured pandas DataFrame.
    The resulting DataFrames are stored in a new dictionary where the keys are the trigger names
    and the values are the corresponding DataFrames.

    Args:
        news_pip_metrics (dict): A dictionary where the keys are trigger names and the values are
                                 dictionaries containing raw pip trigger data for each trigger.
                                 Example:
                                 {
                                     'Trigger1': {'1s': {'range': (1,5), 'mean': 2, ...}, ...},
                                     'Trigger2': {'1s': {'range': (2,6), 'mean': 3, ...}, ...},
                                     ...
                                 }

    Returns:
        dict: A dictionary where the keys are the trigger names and the values are pandas DataFrames
              structured with columns representing various metrics and their EMAs (Exponential Moving
              Averages), for each trigger.
              Example:
              {
                  'Trigger1': <pd.DataFrame ...>,
                  'Trigger2': <pd.DataFrame ...>,
                  ...
              }

    Prints:
        For each trigger name, it prints the name of the trigger followed by the corresponding
        pandas DataFrame.

    Example:
        >>> news_pip_metrics = {'Trigger1': {'1s': {'range': (1,5), 'mean': 2, ...}, ...}}
        >>> news_pip_metrics_to_dfs(news_pip_metrics)
        Trigger1:
        ...
        time_delta    1s
        range         (1, 5)
        mean            2
        ...
        Name: 0, dtype: object
    """
    dfs = {}
    for trigger in news_pip_metrics:
        if len(news_pip_metrics[trigger]) > 0:
            dfs[trigger] = news_pip_trigger_data_to_df(news_pip_metrics[trigger], trigger)
            print(str(trigger) + ": ")
            print(str(dfs[trigger]))
        else:
            continue

    return dfs

"""
news_data = read_news_data("10290")
triggers_vars = read_triggers("10290")
# mean_deviations = calc_median_deviations(news_data)
# calc_deviations_for_indicator("10000")
# calc_all_indicator_deviations()
# calc_and_save_all_trigger_levels()
# read_news_pip_data("10000", "EURUSD")
news_pip_data = load_news_pip_data_at_timedeltas("10290", news_data, "USDCAD")
news_pip_metrics = calc_news_pip_metrics(news_pip_data, triggers_vars, higher_dev="bearish")
news_pip_metrics_dfs = news_pip_metrics_to_dfs(news_pip_metrics)
"""
# news_pip_data = cross_reference_pips_with_news_data("10000", pip_data)

# calc_all_indicator_deviations()
# calc_and_save_all_trigger_levels()
"""
news_pip_metrics = calc_news_pip_metrics_for_multiple_indicators([
    ("00051", "USDSEK"),
    ("00091", "USDNOK"),
    ("10000", "EURUSD"),
    ("10010", "USDJPY"),
    ("10030", "USDJPY"),
    ("10060", "EURUSD"),
    ("10230", "EURUSD"),
    ("10260", "USDCAD"),
    ("10270", "USDCAD"),
    ("10290", "USDCAD"),
    ("30000", "BRENTCMDUSD")
])
"""
