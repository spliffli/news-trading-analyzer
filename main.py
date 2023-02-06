import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import time
import pandas as pd

options = Options()
options.headless = True  # hide GUI
options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
options.add_argument("start-maximized")  # ensure window is full-screen
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # Load without images

driver = webdriver.Chrome(options=options)


def get_datetime(release_date: str, release_time: str):
    if ' (' in release_date:
        release_date = release_date.split(" (")[0]

    timestamp = datetime.datetime.strptime(f"{release_date} {release_time}".strip(), "%b %d, %Y %H:%M")
    return timestamp


def expand_table(table: WebElement, start_date: datetime.date, event_id):
    start_datetime = datetime.datetime.combine(start_date, datetime.time(0,0))
    while True:
        rows_count = len(table.find_elements(By.XPATH, ".//tbody/tr"))
        last_row = table.find_element(By.XPATH, f"//tbody/tr[{rows_count}]")
        last_row_date = last_row.find_element(By.XPATH, "./td[1]").text
        last_row_time = last_row.find_element(By.XPATH, "./td[2]").text
        last_row_datetime = get_datetime(last_row_date, last_row_time)

        if last_row_datetime > start_datetime: # if last row is still newer than given start date
            driver.execute_script(f"ecEvent.moreHistory({event_id}, this, 0)") # JavaScript to expand the table
            time.sleep(1)
            if rows_count == len(table.find_elements(By.XPATH, ".//tbody/tr")): # if the table doesn't expand after the script, it's the end of the data
                print("The data on investing.com doesn't go as far back as your start date."
                      f"\nThe data is only available as far back as: {last_row_datetime}")
                return 1
        else:
            return 0


def scrape(event_id: str, start_date: datetime.date):
    url = "https://www.investing.com/economic-calendar/" + event_id
    driver.get(url)

    # while(True):
    #   driver.execute_script(f"ecEvent.moreHistory({event_id}, this, 0)")
    #   time.sleep(1)
    table = driver.find_element(By.ID, f"eventHistoryTable{event_id}")
    expand_table(table, start_date, event_id)

    df = pd.DataFrame(columns=['Timestamp', 'Prelim', 'Actual', 'Forecast', 'Previous'])
    for row in table.find_elements(By.XPATH, ".//tbody/tr"):
        # print(row.find_element(By.XPATH, "./td[1]").text)
        release_date = row.find_element(By.XPATH, "./td[1]").text
        release_time = row.find_element(By.XPATH, "./td[2]").text
        timestamp = get_datetime(release_date, release_time)

        if row.find_elements(By.XPATH, "./td[2]/span[@class='smallGrayP']"):
            prelim = True
        else:
            prelim = False

        df = df.append({
            'Timestamp': timestamp,
            'Prelim': prelim,
            'Actual': row.find_element(By.XPATH, "./td[3]/span").text,
            'Forecast': row.find_element(By.XPATH, "./td[4]").text,
            'Previous': row.find_element(By.XPATH, "./td[5]").text,

        }, ignore_index=True)

    print(df)


scrape("130", datetime.date(2020, 7, 4))
