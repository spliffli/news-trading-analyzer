import pandas as pd
from datetime import datetime, timedelta
import os
import math
import json
import warnings
from utils import str_to_datetime, datetime_to_str, haawks_id_to_str, read_news_data, save_news_data, get_indicator_info, convert_news_data_to_float, get_deviation

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
    Get the prices at specific time intervals after the release_datetime.

    Args:
        release_datetime (datetime): The datetime of a release.
        tick_df (DataFrame): A DataFrame of tick data.
        time_deltas (dict): A dictionary of time deltas to extract prices from.

    Returns:
        dict: A dictionary of prices at specific time intervals after the release datetime.

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



def get_prices_at_time_deltas_2(release_datetime, tick_df, time_deltas=DEFAULT_TIME_DELTAS):
    """
    This is meant to be an optimized version of get_prices_at_time_deltas which converts
    the time delta timestamps to strings at the beginning and searches for those instead
    of converting every timestamp in the tick datas into a datetime.
    It should speed things up (I hope).
    Update. This is faster but the results are wrong
    """
    prices = {}
    td_timestamps_strs = {}

    for td in time_deltas:
        td_timestamps_strs[td] = datetime.strftime(release_datetime + time_deltas[td], "%Y-%m-%d %H:%M:%S")

    for td in td_timestamps_strs:
        for index, value in tick_df['time'].items():
            if value.startswith(td_timestamps_strs[td]):
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
    - news_data: pandas DataFrame containing news data with Timestamp and Deviation columns.
    - pip_data: dictionary containing pip data with timestamps as keys and pip movements as values.

    Returns:
    - news_pip_data: dictionary containing matched news and pip data with timestamps as keys, and deviation and pip movements as values.
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


def mine_pip_data_from_ticks(news_data, symbol, release_datetime):
    row_count = news_data.shape[0]
    pip_data = {}

    tick_data = read_tick_data(symbol, release_datetime)

    prices = get_prices_at_time_deltas(release_datetime, tick_data)
    release_price = get_release_time_price(release_datetime, tick_data)
    decimal_places = get_decimal_places_from_tick_data(tick_data)
    relative_price_movements = get_relative_price_movements(prices, release_price, decimal_places)
    pip_movements = get_pip_movements(relative_price_movements, decimal_places)

    return pip_movements


def sort_news_pip_data_by_timestamp(news_pip_data):
    keys = list(news_pip_data.keys())
    keys.sort(reverse=True)
    sorted_dict = {i: news_pip_data[i] for i in keys}

    return sorted_dict


def load_news_pip_data(haawks_id, news_data, symbol):
    # news_data = news_data.iloc[:7]  # FOR TESTING, shortens the dataframe to be quicker
    indicator_info = get_indicator_info(haawks_id)

    news_pip_data = {}
    row_count = news_data.shape[0]
    start_datetime = str_to_datetime(news_data.loc[row_count - 1]['Timestamp'])
    end_datetime = str_to_datetime(news_data.loc[0]['Timestamp'])
    timestamps_to_mine = []

    for timestamp in news_data["Timestamp"].items():
        timestamps_to_mine.append(str_to_datetime(timestamp[1]))

    print(f"Loading news pip data for {indicator_info['inv_title']}: {start_datetime} - {end_datetime}")

    local_data = read_news_pip_data(haawks_id, symbol)
    if local_data['data_exists']:
        local_data_start = local_data['start']
        local_data_end = local_data['end']

        for timestamp in list(local_data['data'].keys()):
            timestamp = str_to_datetime(timestamp)
            if timestamp in timestamps_to_mine:
                timestamps_to_mine.remove(timestamp)

        news_pip_data = local_data['data']
        if len(timestamps_to_mine) == 0:
            print(
                f"Local data exists for {len(local_data['data'].keys())}/{row_count} releases. Reading data from file...")
            return news_pip_data
        else:
            print(
                f"Local data exists for {len(local_data['data'].keys())}/{row_count} releases. The remaining {row_count - len(local_data['data'])} will be mined from raw tick data")
    else:
        print("No local data exists, so it will be mined...")

    for index, timestamp in enumerate(timestamps_to_mine):
        print(f"\rMining pip data from {timestamp} ({index + 1}/{len(timestamps_to_mine)})", end="", flush=True)
        data = mine_pip_data_from_ticks(news_data, symbol, timestamp)
        timestamp_str = datetime_to_str(timestamp)
        news_pip_data.setdefault(timestamp_str, {}).setdefault('pips', data)

        for index, row in news_data.iterrows():
            if row['Timestamp'] == timestamp_str:
                try:
                    news_pip_data[timestamp_str]['deviation'] = row['Deviation']
                    break
                except KeyError:
                    news_pip_data[timestamp_str]['deviation'] = None

    news_pip_data = sort_news_pip_data_by_timestamp(news_pip_data)
    print("\nsaving mined data to file")
    save_news_pip_data(haawks_id, symbol, news_pip_data)

    return news_pip_data


def calc_all_deviations_for_indicator(haawks_id):
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
    indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")
    # indicators = indicators.iloc[17:].reset_index()

    row_count = indicators.shape[0]

    for index, row in indicators.iterrows():
        print(f"Calculating deviations for: {row['inv_title']} ({str(index + 1)}/{row_count})")
        haawks_id_str = haawks_id_to_str(row['Id'])
        calc_all_deviations_for_indicator(haawks_id_str)


def calc_mean_deviation(news_data):
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
    """https://www.thoughtco.com/what-is-a-quantile-3126239
    https://www.statisticshowto.com/quantile-definition-find-easy-steps/"""

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
    """This should be useful in deciding which triggers to screen for.
    the default of 5 quantiles are technically called 'quintiles'
    https://www.thoughtco.com/what-is-a-quantile-3126239
    https://www.statisticshowto.com/quantile-definition-find-easy-steps/"""
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
    """This just gets the quantiles for the deviations and populates the news data with it.
    The levels it outputs will be adjusted manually to be more round numbers"""
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
    indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")
    # indicators = indicators.loc[28:]
    row_count = indicators.shape[0]
    for index, row in indicators.iterrows():
        print(f"\rCalculating triggers for indicator {str(index + 1)}/{row_count}: {row['inv_title']}")

        calc_and_save_trigger_levels(haawks_id_to_str(row['Id']))


def read_triggers(haawks_id_str):
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


def calc_news_pip_metrics(haawks_id_str, news_pip_data, triggers, underlying_currency_higher_dev):
    """
    Calculate news pip metrics for each trigger.

    Args:
        news_pip_data (dict): A dictionary containing news pip data.
        triggers (dict): A dictionary containing trigger names and corresponding deviation values.
        underlying_currency_higher_dev (str): The expected direction of higher deviations. Can be "bullish" or "bearish".

    Returns:
        news_pip_metrics (dict): A dictionary containing news pip metrics for each trigger.

    """
    news_pip_metrics = {}
    indicator_info = get_indicator_info(haawks_id_str)
    inv_currency = indicator_info['inv_currency']

    for trigger in triggers:
        news_pip_metrics[trigger] = {}

    for timestamp in news_pip_data:
        # Retrieve deviation value and check if it is negative
        deviation = news_pip_data[timestamp]['deviation']
        negative_dev = False
        if deviation < 0:
            deviation = deviation * -1
            negative_dev = True

        for index, trigger in enumerate(list(triggers.items())):
            # Check if deviation falls within the range of the current trigger
            if index == len(triggers) - 1:
                if deviation >= triggers[trigger[0]]:
                    break  # Keeps trigger at current value before continuing
            else:
                if triggers[trigger[0]] <= deviation < list(triggers.items())[index + 1][1]:
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

            # Add pips to the corresponding trigger and time delta
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

            if underlying_currency_higher_dev == "positive":
                # Calculate the correlation 1 score for positive expected direction
                correlation_1_score = calc_correlation_1_score(values, expected_direction="positive")
                # Calculate the correlation 2 score for positive expected direction
                correlation_2_score = calc_correlation_2_score(values, expected_direction="positive")
            elif underlying_currency_higher_dev == "negative":
                # Calculate the correlation 1 score for negative expected direction
                correlation_1_score = calc_correlation_1_score(values, expected_direction="negative")
                # Calculate the correlation 2 score for negative expected direction
                correlation_2_score = calc_correlation_2_score(values, expected_direction="negative")
            else:
                # Raise an exception if higher_dev is not "bullish" or "bearish"
                raise ValueError("higher_dev must be 'positive' or 'negative'")

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

    # Return the dictionary of news_pip_metrics
    return news_pip_metrics


def calc_pip_averages_and_correlation(values: list):
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
    result = {}

    for haawks_id_str_and_symbol in haawks_id_strs_and_symbols:
        haawks_id_str = haawks_id_str_and_symbol[0]
        title = get_indicator_info(haawks_id_str)['inv_title']
        symbol = haawks_id_str_and_symbol[1]
        news_data = read_news_data(haawks_id_str)
        triggers = read_triggers(haawks_id_str)
        news_pip_data = load_news_pip_data(haawks_id_str, news_data, symbol)
        news_pip_metrics = calc_news_pip_metrics(haawks_id_str, symbol, news_pip_data, triggers)
        result.setdefault(f"{haawks_id_str}_{symbol} {title}", news_pip_metrics)

    return result

def calc_pip_metrics_df_total_averages(pip_metrics_df: pd.DataFrame):
    total_range = [0, 0]
    means = []
    medians = []
    c1_scores = []
    c2_scores = []
    c3_scores = []
    for index, row in pip_metrics_df.iterrows():
        if row['range'][0] < total_range[0]:
            total_range[0] = row['range'][0]
        if row['range'][1] > total_range[1]:
            total_range[1] = row['range'][1]

        means.append(row['mean'])
        medians.append(row['median'])
        c1_scores.append(row['c_1'])
        c2_scores.append(row['c_2'])
        c3_scores.append(row['c_3'])

    total_range = tuple(total_range)
    mean_mean = round(sum(means) / len(means), 1)
    mean_median = round(sum(medians) / len(medians), 1)
    mean_c1 = round(sum(c1_scores) / len(c1_scores), 1)
    mean_c2 = round(sum(c2_scores) / len(c2_scores), 1)
    mean_c3 = round(sum(c3_scores) / len(c3_scores), 1)

    return ['Total/Averages', total_range, mean_mean, mean_median, mean_c1, mean_c2, mean_c3]


def news_pip_trigger_data_to_df(trigger_data):
    df = pd.DataFrame(
        columns=['time_delta', 'range', 'mean', 'median', 'c_1', 'c_2', 'c_3'])
    for time_delta in trigger_data:
        range = trigger_data[time_delta]['range']
        mean = trigger_data[time_delta]['mean']
        median = trigger_data[time_delta]['median']
        correlation_1 = trigger_data[time_delta]['correlation_1']
        correlation_2 = trigger_data[time_delta]['correlation_2']
        correlation_3 = trigger_data[time_delta]['correlation_3']
        df.loc[len(df.index)] = [time_delta, range, mean, median, correlation_1, correlation_2, correlation_3]

    total_averages = calc_pip_metrics_df_total_averages(df)
    df.loc[len(df.index)] = total_averages
    return df


def news_pip_metrics_to_dfs(news_pip_metrics):
    dfs = {}
    for trigger in news_pip_metrics:
        dfs[trigger] = news_pip_trigger_data_to_df(news_pip_metrics[trigger])
        print(f"{trigger}\n{dfs[trigger]}")

    return dfs

"""
news_data = read_news_data("10290")
triggers = read_triggers("10290")
# mean_deviations = calc_median_deviations(news_data)
# calc_deviations_for_indicator("10000")
# calc_all_indicator_deviations()
# calc_and_save_all_trigger_levels()
# read_news_pip_data("10000", "EURUSD")
news_pip_data = load_news_pip_data("10290", news_data, "USDCAD")
news_pip_metrics = calc_news_pip_metrics(news_pip_data, triggers, higher_dev="bearish")
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