import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils import check_if_saturday
from bs4 import BeautifulSoup


from utils import haawks_id_to_str, str_to_datetime, get_indicator_info, save_news_data, read_news_data, convert_news_data_to_float, get_deviation
from selenium.webdriver.remote.webelement import WebElement
import time
import pandas as pd
import chromedriver_autoinstaller_fix
import os
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
chromedriver_autoinstaller_fix.install()
service = Service()
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
# options.add_argument("--headless")  # hide GUI
# options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
options.add_argument("start-maximized")  # ensure window is full-screen
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # Load without images
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=service, options=options)


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


def scrape_all_indicator_info():
    df = pd.read_excel("haawks-indicator-shortlist.xlsx")
    # print(df)

    for index, row in df.iterrows():
        if pd.isnull(row['inv_id']):
            df = df.drop(index=index)

    df = df.reset_index(drop=True)

    # df = df.iloc[0:1] # shortens the df for testing. remove this line when the script works
    df_row_count = df.shape[0]

    for index, row in df.iterrows():
        print(f"scraping indicator {index + 1}/{df_row_count}")
        event_id = str(row['inv_id'])
        info = scrape_indicator(event_id)
        df.at[index, 'inv_title'] = info['title']
        df.at[index, 'inv_importance'] = info['importance']
        df.at[index, 'inv_currency'] = info['currency']
        df.at[index, 'inv_source'] = info['source']
        df.at[index, 'inv_description'] = info['description']

    print("Finished scraping. Saving to excel file")
    df.to_excel("haawks-indicator-shortlist.xlsx")


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


def update_indicator_history(haawks_id_str):
    indicator_info = get_indicator_info(haawks_id_str)
    event_id = str(indicator_info['inv_id'])

    url = "https://www.investing.com/economic-calendar/" + event_id
    print("Scraping investing.com for any newer releases...")
    print("Loading webpage...")
    driver.get(url)

    for filename in os.listdir("./news_data"):
        if filename.startswith(haawks_id_str):
            print(f"Reading local news data: {filename}")
            local_news_data = pd.read_csv(f"./news_data/{filename}")
            newest_local_release = str_to_datetime(local_news_data.loc[0]['Timestamp'])
            oldest_local_release = str_to_datetime(local_news_data.loc[local_news_data.shape[0] - 1]['Timestamp'])
            print(f"Most recent local data: {newest_local_release}")

            table = driver.find_element(By.ID, f"eventHistoryTable{event_id}")
            expand_table(table, newest_local_release.date(), event_id)

            scraped_news_data = pd.DataFrame(columns=['Timestamp', 'Prelim', 'Actual', 'Forecast', 'Previous'])
            row_count = len(table.find_elements(By.XPATH, ".//tbody/tr"))
            # print(f"\r{scraped_news_data.shape[0]} new releases found. Updating local data", flush=True)
            current_row = 0
            for row in table.find_elements(By.XPATH, ".//tbody/tr"):

                current_row += 1
                release_date = row.find_element(By.XPATH, "./td[1]").text
                release_time = row.find_element(By.XPATH, "./td[2]").text
                timestamp_et = get_datetime(release_date, release_time)
                timestamp_gmt = timestamp_et + datetime.timedelta(hours=5)

                if row.find_elements(By.XPATH, "./td[2]/span[@class='smallGrayP']"):
                    prelim = True
                else:
                    prelim = False

                if newest_local_release < timestamp_gmt < datetime.datetime.now():
                    scraped_news_data = scraped_news_data.append({
                        'Timestamp': timestamp_gmt,
                        'Prelim': prelim,
                        'Actual': row.find_element(By.XPATH, "./td[3]/span").text,
                        'Forecast': row.find_element(By.XPATH, "./td[4]").text,
                        'Previous': row.find_element(By.XPATH, "./td[5]").text,

                    }, ignore_index=True)
            if scraped_news_data.shape[0] > 0:
                if scraped_news_data['Actual'].iloc[0].strip() == "":  # if actual is missing from first row then the event hasn't happened yet
                    scraped_news_data = scraped_news_data.drop(index=0).reset_index(drop=True)

                print(f"Found {scraped_news_data.shape[0]} more recent releases.")
                print(scraped_news_data)

                for index, row in scraped_news_data.iterrows():

                    print(f"\rCalculating deviation for: {row['Timestamp']} ({str(index + 1)}/{scraped_news_data.shape[0]})", end="",
                          flush=True)
                    try:
                        actual = convert_news_data_to_float(haawks_id_str, row['Actual'])
                        forecast = convert_news_data_to_float(haawks_id_str, row['Forecast'])
                        deviation = round(get_deviation(actual, forecast), 4)
                        scraped_news_data.loc[index, "Deviation"] = deviation
                    except ValueError:
                        print(f"\nForecast data missing from {row['Timestamp']}... Skipping")
                # print(f"{scraped_news_data.shape[0]} new releases found on investing.com. Updating local data...")

                updated_news_data = scraped_news_data.append(local_news_data)
                save_news_data(haawks_id_str, updated_news_data)

                return updated_news_data
            else:
                print("No new releases found. No need to update local data.")
                return local_news_data


def prepare_calendar(next_week=False, custom_date=False):
    driver.get("https://www.investing.com/economic-calendar/")
    time.sleep(1)

    print("Setting filters:\nClearing all countries")
    driver.execute_script("clearAll('country[]');")

    # Click country checkboxes for USD, CAD, NOK, SEK, PLN, TRY & EUR
    print("Clicking checkboxes for USD, CAD, NOK, SEK, PLN, TRY & EUR")
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "country5"))  # USA (USD)
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "country6"))  # Canada (CAD)
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "country60"))  # Norway (NOK)
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "country9"))  # Sweden (SEK)
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "country53"))  # Poland (PLN)
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "country63"))  # Turkey (TRY)
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "country72"))  # Europe (EUR)

    # Display time only instead of remaining time until announcement
    print("Showing time only instead of remaining time until announcements")
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "timetimeOnly"))

    # Select all categories
    print("Selecting all categories")
    driver.execute_script("selectAll('category[]');")

    # Select all importance levels
    print("Selecting all importance levels")
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "importance1"))
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "importance2"))
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "importance3"))

    # Apply filters
    print("Applying filters")
    driver.execute_script("calendarFilters.innerFiltersSubmit();")

    # Close popup
    popup = None
    while popup is None:
        try:
            print("Waiting for popup...")
            popup = WebDriverWait(driver, 1,).until(EC.presence_of_element_located((By.CLASS_NAME, "signupWrap")))
        except TimeoutException:
            continue
    print("Closing popup")
    driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, "popupCloseIcon"))
    # driver.execute_script("return window.stop")

    if not next_week and not custom_date:
        print("Checking if Saturday")
        if next_week:
            print("Showing next week's events")
            driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "timeFrame_nextWeek"))
        elif check_if_saturday():
            print("Today is Saturday. Showing next week's events")
            driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "timeFrame_nextWeek"))
        else:
            print("Today is not Saturday. Showing this week's events")
            driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "timeFrame_thisWeek"))
    elif next_week and not custom_date:
        driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "timeFrame_nextWeek"))
    elif custom_date and not next_week:
        input_str = "."

        while input_str != "":
            input_str = input("Press enter after manually selecting dates on investing.com...")
    elif next_week and custom_date:
        raise ValueError("Either `next_week` or `custom_date` can be true but not both of them at the same time.")


def scrape_economic_calendar(indicators: list, next_week=False, custom_date=False):
    relevent_events = []

    while len(relevent_events) == 0:
        print("Loading economic calendar")
        prepare_calendar(next_week=next_week, custom_date=custom_date)
        print("Getting table's HTML")
        table = driver.find_element(By.ID, "economicCalendarData").get_attribute("outerHTML")
        print("Parsing HTML")
        soup = BeautifulSoup(table, 'html.parser')
        rows = soup.find_all("tr")

        print("Scraping table rows:")
        for index, row in enumerate(rows):
            print(f"\rrow {int(index) + 1}/{len(rows)}", end="", flush=True)
            try:
                class_name = row['class']
            except KeyError:
                class_name = ""

            if type(class_name) == list:
                class_name = class_name[0]

            if class_name.startswith("js-event-item"):
                inv_id = row['event_attr_id']

                for indicator in indicators:
                    if indicator[0] == inv_id:
                        dt = datetime.datetime.strptime(row['data-event-datetime'], "%Y/%m/%d %H:%M:%S")
                        relevent_events.append((inv_id, indicator[1], indicator[2], indicator[3], indicator[4], dt))
        print("\n")
        if len(relevent_events) == 0:   # or 'Friday' not in soup or table
            print("Scraping failed. Trying Again...")
        # else:
        #     for index, event in enumerate(relevent_events):
        #         if event[1] == "10150":
        #             relevent_events.insert(0, relevent_events.pop(index))

    return relevent_events
