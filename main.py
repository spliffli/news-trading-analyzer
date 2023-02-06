import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd

options = Options()
options.headless = False  # hide GUI
options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
options.add_argument("start-maximized")  # ensure window is full-screen
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # Load without images

driver = webdriver.Chrome(options=options)


def scrape(event_id: str):
    url = "https://www.investing.com/economic-calendar/" + event_id
    driver.get(url)

    # while(True):
    #   driver.execute_script(f"ecEvent.moreHistory({event_id}, this, 0)")
    #   time.sleep(1)
    table = driver.find_element(By.ID, f"eventHistoryTable{event_id}")

    df = pd.DataFrame(columns=['Timestamp', 'Prelim', 'Actual', 'Forecast', 'Previous'])
    for row in table.find_elements(By.XPATH, ".//tbody/tr"):
        # print(row.find_element(By.XPATH, "./td[1]").text)
        release_date = row.find_element(By.XPATH, "./td[1]").text
        if ' (' in release_date:
            release_date = release_date.split(" (")[0]

        release_time = row.find_element(By.XPATH, "./td[2]").text
        timestamp = datetime.datetime.strptime(f"{release_date} {release_time}".strip(), "%b %d, %Y %H:%M")

        df = df.append({
            'Timestamp': timestamp,
            'Prelim': "Unknown",  # Add a check for this
            'Actual': row.find_element(By.XPATH, "./td[3]/span").text,
            'Forecast': row.find_element(By.XPATH, "./td[4]").text,
            'Previous': row.find_element(By.XPATH, "./td[5]").text,

        }, ignore_index=True)

    print(df)



scrape("262")
