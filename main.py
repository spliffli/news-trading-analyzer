import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from import_ticks import import_ticks
from utils import str_to_datetime, datetime_to_str, haawks_id_to_str

import chromedriver_autoinstaller
import os
import time
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

chromedriver_autoinstaller.install()
options = Options()
options.headless = True  # hide GUI
options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
options.add_argument("start-maximized")  # ensure window is full-screen
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # Load without images

driver = webdriver.Chrome(options=options)


def get_datetime(release_date: str, release_time: str):
    if ' (' in release_date:
        release_date = release_date.split(" (")[0]

    timestamp = datetime.datetime.strptime(f"{release_date} {release_time}".strip(), "%b %d, %Y %H:%M")
    return timestamp


def expand_table(table: WebElement, start_date: datetime.date, event_id):
    start_datetime = datetime.datetime.combine(start_date, datetime.time(0, 0))
    while True:
        rows_count = len(table.find_elements(By.XPATH, ".//tbody/tr"))
        last_row = table.find_element(By.XPATH, f"//tbody/tr[{rows_count}]")
        last_row_date = last_row.find_element(By.XPATH, "./td[1]").text
        last_row_time = last_row.find_element(By.XPATH, "./td[2]").text
        last_row_datetime = get_datetime(last_row_date, last_row_time)

        if last_row_datetime > start_datetime:  # if last row is still newer than given start date
            driver.execute_script(f"ecEvent.moreHistory({event_id}, this, 0)")  # JavaScript to expand the table
            time.sleep(2)
            if rows_count == len(table.find_elements(By.XPATH,
                                                     ".//tbody/tr")):  # if the table doesn't expand after the script, it's the end of the data
                print("The data on investing.com doesn't go as far back as your start date."
                      f"\nThe data is only available as far back as: {last_row_datetime}")
                return 1
        else:
            return 0


def scrape(event_id: str, start_date: datetime.date):
    url = "https://www.investing.com/economic-calendar/" + event_id
    print("Loading webpage...")
    driver.get(url)
    start_datetime = datetime.datetime.combine(start_date, datetime.time(0, 0))

    # while(True):
    #   driver.execute_script(f"ecEvent.moreHistory({event_id}, this, 0)")
    #   time.sleep(1)
    table = driver.find_element(By.ID, f"eventHistoryTable{event_id}")
    print("Expanding table...")
    expand_table(table, start_date, event_id)

    df = pd.DataFrame(columns=['Timestamp', 'Prelim', 'Actual', 'Forecast', 'Previous'])
    row_count = len(table.find_elements(By.XPATH, ".//tbody/tr"))
    current_row = 0
    for row in table.find_elements(By.XPATH, ".//tbody/tr"):
        # print(row.find_element(By.XPATH, "./td[1]").text)
        current_row += 1
        print(f"scraping row {current_row}/{row_count}")
        release_date = row.find_element(By.XPATH, "./td[1]").text
        release_time = row.find_element(By.XPATH, "./td[2]").text
        timestamp_et = get_datetime(release_date, release_time)
        timestamp_gmt = timestamp_et + datetime.timedelta(hours=5)

        if row.find_elements(By.XPATH, "./td[2]/span[@class='smallGrayP']"):
            prelim = True
        else:
            prelim = False

        if start_datetime < timestamp_et:
            df = df.append({
                'Timestamp': timestamp_gmt,
                'Prelim': prelim,
                'Actual': row.find_element(By.XPATH, "./td[3]/span").text,
                'Forecast': row.find_element(By.XPATH, "./td[4]").text,
                'Previous': row.find_element(By.XPATH, "./td[5]").text,

            }, ignore_index=True)

    if df['Actual'].iloc[0].strip() == "":  # if actual is missing from first row then the event hasn't happened yet
        df = df.drop(index=0).reset_index(drop=True)
    return df


def scrape_all_indicator_history(start_date: datetime.date):
    df = pd.read_excel("haawks-indicator-shortlist.xlsx")
    # df = df.iloc[11:]  # shortens the df for testing. remove this line when the script works
    df = df.reset_index()
    df_row_count = df.shape[0]

    for index, row in df.iterrows():
        event_id = str(row['inv_id'])
        name_formatted = row['inv_title'].replace(" ", "_").replace(".", "")
        haawks_id_str = haawks_id_to_str(row['Id'])
        print(f"Scraping {index + 1}/{df_row_count}: {row['inv_title']}")
        news_data = scrape(event_id, start_date)

        news_data.to_csv(f"news_data/{haawks_id_str}_{event_id}_{name_formatted}.csv", index=False)
        print(f"Saving to news_data/{haawks_id_str}_{event_id}_{name_formatted}.csv")


# scrape_all_indicator_history(datetime.date(2017, 1, 1))
# df = scrape("130", datetime.date(2020, 7, 4))

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


def scrape_bullish_or_bearish():
    indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")

    for index, row in indicators.iterrows():
        description = row['inv_description']
        if "higher than expected reading should be taken as positive" in description:
            indicators.loc[index, "higher_dev"] = "bullish"
        elif "higher than expected reading should be taken as negative" in description:
            indicators.loc[index, "higher_dev"] = "bearish"
        else:
            indicators.loc[index, "higher_dev"] = "unknown"

    print(indicators)
    indicators.to_excel("haawks-indicator-shortlist.xlsx", index=False)


def scrape_suffixes():
    indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")

    for index, row in indicators.iterrows():
        haawks_id_str = haawks_id_to_str(row['Id'])

        for filename in os.listdir('./news_data'):
            if filename.startswith(haawks_id_str):
                news_data = pd.read_csv(f"./news_data/{filename}")

                sample_figure = str(news_data.loc[1]['Actual'])
                str_length = len(sample_figure)

                for i in range(str_length):
                    try:
                        float(sample_figure[0:str_length-i])
                        suffix = sample_figure[str_length-i:]
                        break
                    except ValueError:
                        pass
                indicators.loc[index, "suffix"] = suffix
                break

    print(indicators)
    indicators.to_excel("haawks-indicator-shortlist.xlsx", index=False)


# scrape_bullish_or_bearish()
# scrape_bullish_or_bearish()
# scrape_all_indicator_history(datetime.date(2017, 1, 1))
import_ticks_for_indicator("00051", "USDSEK")
