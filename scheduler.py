import datetime

from scrape import scrape_economic_calendar
import pandas as pd
from utils import get_indicator_info, haawks_id_to_str
from datetime import date
from analyze_data import read_triggers, load_news_pip_data, calc_news_pip_metrics, news_pip_metrics_to_dfs
from utils import read_news_data, get_day
from generate_report import render_event_html, generate_weekly_schedule


def get_trigger_vars(c_3, dev, account_balance, dev_direction):

    if c_3 < 85:
        lots_per_1000 = 0.5
    elif 85 <= c_3 < 90:
        lots_per_1000 = 0.75
    elif 90 <= c_3 < 95:
        lots_per_1000 = 1
    elif c_3 >= 95:
        lots_per_1000 = 1.5

    lots = (account_balance / 1000) * lots_per_1000

    trigger_vars = {}
    if dev_direction == "positive":
        trigger_vars["dev"] = str(dev)
    elif dev_direction == 'negative':
        trigger_vars["dev"] = str(dev * -1)
    trigger_vars["lots_per_1000"] = str(lots_per_1000)
    trigger_vars["lots"] = str(lots)

    return trigger_vars


def get_triggers_vars(haawks_id_str, symbol, higher_dev, account_balance=1000):
    news_data = read_news_data(haawks_id_str)
    triggers = read_triggers(haawks_id_str)
    news_pip_data = load_news_pip_data(haawks_id_str, news_data, symbol)
    news_pip_metrics = calc_news_pip_metrics(haawks_id_str, news_pip_data, triggers, higher_dev)
    news_pip_metrics_dfs = news_pip_metrics_to_dfs(news_pip_metrics)

    trigger_vars = {
        "lta": "",
        "uta": "",
        "lower_triggers": {},
        "upper_triggers": {}
    }
    c_3_scores = {}

    if higher_dev == 'bullish':
        trigger_vars['lta'] = 'Sell'
        trigger_vars['uta'] = 'Buy'
    elif higher_dev == 'bearish':
        trigger_vars['lta'] = 'Buy'
        trigger_vars['uta'] = 'Sell'

    for trigger in news_pip_metrics_dfs:
        c_3_scores[trigger] = news_pip_metrics_dfs[trigger].iloc[-1]['c_3']

    trigger_c_3_keys = list(c_3_scores.keys())
    trigger_c_3_values = list(c_3_scores.values())
    best_trigger_index = trigger_c_3_values.index(max(trigger_c_3_values))

    if len(trigger_c_3_values) == 4 and best_trigger_index == 3:
        trigger_c_3_keys = trigger_c_3_keys.pop(0)
        trigger_c_3_values = trigger_c_3_values.pop(0)

    over_80_count = 0
    for index, value in enumerate(trigger_c_3_values):
        if value >= 80:
            over_80_count += 1
            # trigger_vars.setdefault("upper_triggers", {}).setdefault("ut1", {})
            trigger_vars["upper_triggers"].setdefault(f"ut{over_80_count}", "")
            trigger_vars["lower_triggers"].setdefault(f"lt{over_80_count}", "")


            trigger_vars["upper_triggers"][f"ut{over_80_count}"] = get_trigger_vars(value, triggers[trigger_c_3_keys[index]], account_balance, "positive")
            trigger_vars["lower_triggers"][f"lt{over_80_count}"] = get_trigger_vars(value, triggers[trigger_c_3_keys[index]], account_balance, "negative")




            # breakpoint()
    return trigger_vars



def create_schedule():
    top_indicators = pd.read_excel("reports/top_indicators.xlsx")
    indicators = []

    for index, row in top_indicators.iterrows():
        indicators.append((str(row['inv_id']), haawks_id_to_str(row['haawks_id']), row['symbol'], row['higher_dev'], row['inv_title']))

    upcoming_events = scrape_economic_calendar(indicators)

    weekdays_html = {
        "Sunday": "",
        "Monday": "",
        "Tuesday": "",
        "Wednesday": "",
        "Thursday": "",
        "Friday": "",
    }
    for event in upcoming_events:
        haawks_id_str = event[1]
        symbol = event[2]
        higher_dev = event[3]
        title = event[4]
        dt_gmt = event[5] + datetime.timedelta(hours=5)
        time = dt_gmt.strftime("%H:%M")
        triggers_vars = get_triggers_vars(haawks_id_str, symbol, higher_dev)
        day = get_day(dt=dt_gmt)

        event_html = render_event_html(title, time, symbol, triggers_vars)
        if weekdays_html[day] == "":
            weekdays_html[day] += f"<h3>{dt_gmt.strftime('%A, %B %-d, %Y')}</h3>\n"
        weekdays_html[day] += event_html

    template_vars = {
        "year": datetime.datetime.now().strftime("%Y"),
        "week_no": (upcoming_events[0][5] + datetime.timedelta(hours=5)).strftime("%Y"),
        "start_date": (upcoming_events[0][5] + datetime.timedelta(hours=5)).strftime("%Y/%m/%d"),
        "end_date": (upcoming_events[0][-1] + datetime.timedelta(hours=5)).strftime("%Y/%m/%d"),
        "sunday_events": weekdays_html['Sunday'],
        "monday_events": weekdays_html['Monday'],
        "tuesday_events": weekdays_html['Tuesday'],
        "wednesday_events": weekdays_html['Wednesday'],
        "thursday_events": weekdays_html['Thursday'],
        "friday_events": weekdays_html['Friday']
    }

    generate_weekly_schedule(template_vars)



create_schedule()