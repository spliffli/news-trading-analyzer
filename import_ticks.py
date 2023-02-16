import duka.app.app as duka_import
from duka.core.utils import TimeFrame
import datetime
import os
import pandas as pd
import warnings
from utils import haawks_id_to_str, str_to_datetime

warnings.simplefilter(action='ignore', category=FutureWarning)


start_date = datetime.date(2023, 2, 3)
end_date = datetime.date(2023, 2, 3)
assets = ["EURUSD"]

# duka_import(assets, start_date, end_date, 4, TimeFrame.TICK, ".", True)


def import_ticks(asset: str, date: datetime.date): # Wrapper function with fewer params. It imports ticks for one day
    duka_import([asset], date, date, 1, TimeFrame.TICK, "tick_data/", True)


def truncate_tick_data(tick_df, start_datetime, end_datetime):
    tick_start_index = 0
    tick_end_index = 0
    tick_start_index_found = False
    for index, value in tick_df['time'].items():
        try:
            timestamp = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
        except:
            timestamp = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        if timestamp > start_datetime:
            if not tick_start_index_found:
                tick_start_index = index
                tick_start_index_found = True
        if timestamp > end_datetime:
            tick_end_index = index
            break

    tick_df = tick_df.loc[tick_start_index:tick_end_index]
    return tick_df

def import_ticks_for_indicator(haawks_id, symbol):
    haawks_id_str = haawks_id_to_str(haawks_id)
    for filename in os.listdir("./news_data"):
        if filename.startswith(haawks_id_str):
            print(f"Reading news data: {filename}")
            news_data = pd.read_csv(f"./news_data/{filename}")
            # news_data = news_data.iloc[296:]
            # news_data = news_data.reset_index()

            row_count = news_data.shape[0]
            release_timestamps = []

            for index, timestamp in news_data['Timestamp'].items():
                release_timestamps.append(str_to_datetime(timestamp))

            timestamps_to_download = list(release_timestamps)

            for timestamp in release_timestamps:
                for tick_data_filename in os.listdir(f"./tick_data"):
                    date_hyphenated = timestamp.strftime('%Y-%m-%d')
                    start_time_hyphenated = (timestamp - datetime.timedelta(minutes=5)).strftime('%H-%M-%S')
                    end_time_hyphenated = (timestamp + datetime.timedelta(minutes=15)).strftime('%H-%M-%S')
                    if tick_data_filename == f"{symbol}__{date_hyphenated}__{start_time_hyphenated}_{end_time_hyphenated}.csv":
                        timestamps_to_download.remove(timestamp)
                        break
            if len(timestamps_to_download) == 0:
                print(f"Local {symbol} tick data exists for {row_count}/{row_count} releases. No need to download.")
            else:
                print(f"Local {symbol} tick data exists for {row_count - len(timestamps_to_download)}/{row_count} releases. The remaining {len(timestamps_to_download)} will be downloaded.")


            for index, timestamp in enumerate(timestamps_to_download):
                print(
                    f"Downloading {symbol} tick data for: {timestamp} ({int(index) + 1}/{len(timestamps_to_download)})")
                release_date = timestamp.date()
                release_date_hyphenated = timestamp.strftime("%Y-%m-%d")
                release_date_underscored = timestamp.strftime("%Y_%m_%d")
                import_ticks(symbol, release_date)
                downloaded_tick_data_filename = f"{symbol}-{release_date_underscored}-{release_date_underscored}.csv"

                tick_df = pd.read_csv(f"./tick_data/{downloaded_tick_data_filename}")
                tick_start_dt = timestamp - datetime.timedelta(minutes=5)
                tick_end_dt = timestamp + datetime.timedelta(minutes=15)

                print("Truncating tick data")
                try:
                    tick_df = truncate_tick_data(tick_df, tick_start_dt, tick_end_dt)
                except TypeError:
                    print(f"tick data for {timestamp} invalid")
                os.remove(f"./tick_data/{downloaded_tick_data_filename}")
                new_filename = f"{symbol}__{release_date_hyphenated}__{tick_start_dt.strftime('%H-%M-%S')}_{tick_end_dt.strftime('%H-%M-%S')}.csv"
                tick_df.to_csv(f"./tick_data/{new_filename}", index=False)
                # print(tick_df)
