import pandas as pd
from datetime import datetime, timedelta

DEFAULT_TIME_DELTAS = {
    "1s": timedelta(seconds=1),
    "2s": timedelta(seconds=2),
    "3s": timedelta(seconds=3),
    "4s": timedelta(seconds=4),
    "5s": timedelta(seconds=5),
    "6s": timedelta(seconds=6),
    "7s": timedelta(seconds=7),
    "8s": timedelta(seconds=8),
    "9s": timedelta(seconds=9),
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
    decimal_places = len(str(num).split(".")[1])
    return decimal_places


def get_decimal_places_from_tick_data(tick_data):
    """ Necessary to loop through a few items and find the largest since sometimes rows in the tick data are rounded to lower decimal places"""
    df = tick_data.loc[1:20]
    decimal_places_list = []

    for index, value in df['ask'].items():
        decimal_places = get_decimal_places(value)
        decimal_places_list.append(decimal_places)

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
    prices = {}

    for td in time_deltas:
        for index, row in tick_df.iterrows():
            try:
                timestamp = datetime.strptime(row['time'], "%Y-%m-%d %H:%M:%S.%f")
            except:
                timestamp = datetime.strptime(row['time'], "%Y-%m-%d %H:%M:%S")

            if timestamp > (release_datetime + time_deltas[td]):
                prices[td] = (row['ask'], row['bid'])
                break

    return prices


def get_relative_price_movements(prices_per_time_delta, release_time_price, decimal_places):
    release_ask = float(release_time_price[0])
    release_bid = float(release_time_price[1])

    price_movements = {}

    for price in prices_per_time_delta:
        ask = float(prices_per_time_delta[price][0])
        bid = float(prices_per_time_delta[price][1])

        if ask > release_ask:
            difference = round(ask - release_ask, decimal_places)
            price_movements[price] = difference
        elif bid < release_bid:
            difference = round(bid - release_bid, decimal_places)
            price_movements[price] = difference
        else:
            raise ValueError("Something went wrong")

    for time in price_movements:
        print(f"{time}: {price_movements[time]:.5f}")

    return price_movements

def get_pip_movements(price_movements, decimal_places):

    pip_movements = {}

    for price_movement in price_movements:
        pip_movements[price_movement] = price_movement_to_pips(price_movements[price_movement], decimal_places)

    return pip_movements


tick_data = pd.read_csv("tick_data/EURUSD__2017-01-06__08-25-00_08-45-00.csv")
release_datetime = datetime(2017, 1, 6, 8, 30, 0)
prices = get_prices_at_time_deltas(release_datetime, tick_data)
release_price = get_release_time_price(release_datetime, tick_data)
decimal_places = get_decimal_places_from_tick_data(tick_data)

relative_price_movements = get_relative_price_movements(prices, release_price, decimal_places)

pip_movements = get_pip_movements(relative_price_movements, decimal_places)

breakpoint()