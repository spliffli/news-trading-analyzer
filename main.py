from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.headless = False  # hide GUI
options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
options.add_argument("start-maximized")  # ensure window is full-screen

driver = webdriver.Firefox(options=options)


def scrape(event_id: str):
    url = "https://www.investing.com/economic-calendar/" + event_id
    driver.get(url)

    show_more_history_id = "showMoreHistory" + event_id
    element = driver.find_element(By.ID, show_more_history_id)

    while(element.get_attribute("display") != "none"):
        # element.click()
        driver.execute_script(f"ecEvent.moreHistory({event_id}, this, 0)")
        time.sleep(1)

scrape("345")
