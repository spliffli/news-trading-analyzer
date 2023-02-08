import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from import_ticks import import_ticks
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
        timestamp = get_datetime(release_date, release_time)

        if row.find_elements(By.XPATH, "./td[2]/span[@class='smallGrayP']"):
            prelim = True
        else:
            prelim = False

        if start_datetime < timestamp:
            df = df.append({
                'Timestamp': timestamp,
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
    df = df.iloc[11:]  # shortens the df for testing. remove this line when the script works
    df = df.reset_index()
    df_row_count = df.shape[0]

    for index, row in df.iterrows():
        event_id = str(row['inv_id'])
        name_formatted = row['inv_title'].replace(" ", "_").replace(".", "")
        haawks_id = row['Id']
        print(f"Scraping {index + 1}/{df_row_count}: {row['inv_title']}")
        news_data = scrape(event_id, start_date)

        news_data.to_csv(f"news_data/{haawks_id}_{event_id}_{name_formatted}.csv", index=False)
        print(f"Saving to news_data/{haawks_id}_{event_id}_{name_formatted}.csv")


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
    for filename in os.listdir("./news_data"):
        if filename.startswith(haawks_id):
            print(f"Reading news data: {filename}")
            news_data = pd.read_csv(f"./news_data/{filename}")
            row_count = news_data.shape[0]
            for index, row in news_data.iterrows():
                print(f"Downloading {symbol} tick data for: {datetime.datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S').date()} ({int(index)+1}/{row_count})")
                release_datetime = datetime.datetime.strptime((row['Timestamp']), "%Y-%m-%d %H:%M:%S")
                release_date = release_datetime.date()
                release_date_hyphenated = release_datetime.strftime("%Y-%m-%d")
                release_date_underscored = release_datetime.strftime("%Y_%m_%d")
                import_ticks(symbol, release_date)
                downloaded_tick_data_filename = f"{symbol}-{release_date_underscored}-{release_date_underscored}.csv"

                tick_df = pd.read_csv(f"./tick_data/{downloaded_tick_data_filename}")
                tick_start_dt = release_datetime - datetime.timedelta(minutes=5)
                tick_end_dt = release_datetime + datetime.timedelta(minutes=15)

                print("Truncating tick data")
                tick_df = truncate_tick_data(tick_df, tick_start_dt, tick_end_dt)
                os.remove(f"./tick_data/{downloaded_tick_data_filename}")
                new_filename = f"{symbol}__{release_date_hyphenated}__{tick_start_dt.strftime('%H-%M-%S')}_{tick_end_dt.strftime('%H-%M-%S')}.csv"
                tick_df.to_csv(f"./tick_data/{new_filename}", index=False)
                # print(tick_df)


import_ticks_for_indicator("10000", 'EURUSD')
