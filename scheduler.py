from scrape import scrape_economic_calendar
import pandas as pd
from utils import get_indicator_info, haawks_id_to_str
from datetime import date


def create_schedule():
    indicators = pd.read_excel("reports/top_indicators.xlsx")
    inv_ids = []

    for index, value in indicators['inv_id'].items():
        inv_ids.append(str(value))



    scrape_economic_calendar(inv_ids)

create_schedule()