import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import time
import pandas as pd

options = Options()
options.headless = False  # hide GUI
options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
options.add_argument("start-maximized")  # ensure window is full-screen
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # Load without images

driver = webdriver.Chrome(options=options)


def scrape_indicator(event_id):
    url = "https://www.investing.com/economic-calendar/" + event_id
    driver.get(url)

    title = driver.find_element(By.CLASS_NAME, "ecTitle").text
    overview_box = driver.find_element(By.ID, "overViewBox")
    importance = 0
    overview_right = overview_box.find_element(By.CLASS_NAME, "right")
    for icon in overview_right.find_elements(By.XPATH, "//div[1]/span[2]/i"):
        if icon.get_attribute('class') == 'grayFullBullishIcon':
            importance += 1

    currency = overview_right.find_element(By.XPATH, "//div[3]/span[2]").text
    source = overview_right.find_element(By.XPATH, "//div[4]/span[2]/a").get_attribute('title')

    if 'noDesc' in overview_right.get_attribute('class'):
        description = "No description available"
    else:
        description = overview_box.find_element(By.XPATH, "//div[@class='left']").text

    return {
        "title": title,
        "importance": importance,
        "currency": currency,
        "source": source,
        "description": description
    }

# scrape_indicator("375")


df = pd.read_excel("haawks-g4a-indicator-list-20190806.xls")
# print(df)

for index, row in df.iterrows():
    if pd.isnull(row['inv_id']):
        df = df.drop(index=index)

df = df.reset_index(drop=True)

# df = df.iloc[0:1] # shortens the df for testing. remove this line when the script works
df_row_count = df.shape[0]

for index, row in df.iterrows():
    print(f"scraping indicator {index+1}/{df_row_count}")
    event_id = str(row['inv_id'])
    info = scrape_indicator(event_id)
    df.at[index, 'inv_title'] = info['title']
    df.at[index, 'inv_importance'] = info['importance']
    df.at[index, 'inv_currency'] = info['currency']
    df.at[index, 'inv_source'] = info['source']
    df.at[index, 'inv_description'] = info['description']


print("Finished scraping. Saving to excel file")
df.to_excel("haawks-indicator-shortlist.xlsx")
