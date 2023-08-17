import datetime

from scrape import scrape_economic_calendar
import pandas as pd
from utils import get_indicator_info, haawks_id_to_str
from datetime import date
from scrape import update_indicator_history
from import_ticks import import_ticks_for_indicator
from analyze_data import read_triggers, load_news_pip_data, calc_news_pip_metrics, news_pip_metrics_to_dfs
from utils import read_news_data, get_day
from generate_report import render_event_html, generate_weekly_schedule
import numpy


def get_trigger_vars(data_points, lowest_c_3_type, lowest_c_3_val, dev, account_balance, dev_direction, symbol):

    if 75 <= lowest_c_3_val < 80:
        match symbol:
            case 'USDJPY':
                lots_per_1000 = 1.5
            case 'USDCAD':
                lots_per_1000 = 1.53
            case 'USDSEK':
                lots_per_1000 = 0.77
            case 'USDNOK':
                lots_per_1000 = 0.79
    elif 80 <= lowest_c_3_val < 85:
        match symbol:
            case 'USDJPY':
                lots_per_1000 = 2.5
            case 'USDCAD':
                lots_per_1000 = 2.55
            case 'USDSEK':
                lots_per_1000 = 1.28
            case 'USDNOK':
                lots_per_1000 = 1.31
    elif 85 <= lowest_c_3_val < 90:
        match symbol:
            case 'USDJPY':
                lots_per_1000 = 3.5
            case 'USDCAD':
                lots_per_1000 = 3.57
            case 'USDSEK':
                lots_per_1000 = 1.79
            case 'USDNOK':
                lots_per_1000 = 1.83
    elif 90 <= lowest_c_3_val < 95:
        match symbol:
            case 'USDJPY':
                lots_per_1000 = 4
            case 'USDCAD':
                lots_per_1000 = 4.08
            case 'USDSEK':
                lots_per_1000 = 2.04
            case 'USDNOK':
                lots_per_1000 = 2.08
    elif lowest_c_3_val >= 95:
        match symbol:
            case 'USDJPY':
                lots_per_1000 = 4.5
            case 'USDCAD':
                lots_per_1000 = 4.59
            case 'USDSEK':
                lots_per_1000 = 2.3
            case 'USDNOK':
                lots_per_1000 = 2.35

    lots = (account_balance / 1000) * lots_per_1000

    trigger_vars = {}
    trigger_vars["data_points"] = str(data_points)
    trigger_vars["lowest_c_3_type"] = str(lowest_c_3_type)
    trigger_vars["lowest_c_3_val"] = str(lowest_c_3_val)
    if dev_direction == "positive":
        trigger_vars["dev"] = str(dev)
    elif dev_direction == 'negative':
        trigger_vars["dev"] = str(dev * -1)
    trigger_vars["lots_per_1000"] = str(lots_per_1000)
    trigger_vars["lots"] = str(lots)

    return trigger_vars


def get_triggers_vars(haawks_id_str, symbol, higher_dev, account_balance=3000):
    news_data = read_news_data(haawks_id_str)  # read_news_data(haawks_id_str)
    # import_ticks_for_indicator(haawks_id_str, symbol)
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

    if higher_dev == 'bullish':
        trigger_vars['lta'] = 'Sell'
        trigger_vars['uta'] = 'Buy'
    elif higher_dev == 'bearish':
        trigger_vars['lta'] = 'Buy'
        trigger_vars['uta'] = 'Sell'

    all_c_3_scores = {}

    for trigger in news_pip_metrics_dfs:
        last_row = news_pip_metrics_dfs[trigger].iloc[-1]
        data_points = news_pip_metrics_dfs[trigger].iloc[0]['data_points']
        if data_points < 15:
            continue

        c_3_scores = {
            'data_points': data_points,
            'lowest_c_3_type': last_row['lowest_c_3_type'],
            'lowest_c_3_val': last_row['lowest_c_3_val'],
            'c_3': last_row['c_3'],
            'c_3_ema5': last_row['c_3_ema5'],
            'c_3_ema10': last_row['c_3_ema10'],
            'c_3_ema15': last_row['c_3_ema15'],
        }

        all_c_3_scores[f"{trigger}"] = c_3_scores

        print(f"c_3_scores ({trigger}):\n  ", c_3_scores)

    if len(all_c_3_scores) == 0:
        return "Not enough data"

    # Create a list of the keys in the c_3_scores dictionary (trigger names)
    triggers_c_3_keys = list(all_c_3_scores.keys())

    # Create a list of the values in the c_3_scores dictionary (trigger scores)
    triggers_c_3_values = list(all_c_3_scores.values())

    # Find the index of the key (trigger name) with the highest 'lowest_c_3_val' in the
    # triggers_c_3_keys list by first finding the trigger/key with the highest 'lowest_c_3_val' using
    # the max() function with a custom key function that looks up the 'lowest_c_3_val' for each key.
    # Then, find the index of that key in the triggers_c_3_keys list and assign it to
    # the best_trigger_index variable.
    best_trigger_index = triggers_c_3_keys.index(
        max(triggers_c_3_keys, key=lambda x: all_c_3_scores[x]['lowest_c_3_val'])
    )

    if len(triggers_c_3_values) == 4 and best_trigger_index == 3:
        triggers_c_3_keys = triggers_c_3_keys.pop(0)
        triggers_c_3_values = triggers_c_3_values.pop(0)

    over_75_count = 0

    if type(triggers_c_3_values) == numpy.float64 or type(triggers_c_3_values) == float:
        if len(c_3_scores) == 0:  # Check if there are no valid triggers
            triggers_vars = "Not enough data"
        else:
            if triggers_c_3_values[0]['lowest_c_3_val'] >= 75:
                trigger_vars["upper_triggers"].setdefault(f"ut1", "")
                trigger_vars["lower_triggers"].setdefault(f"lt1", "")
                trigger_vars["upper_triggers"][f"ut1"] = get_trigger_vars(data_points=triggers_c_3_values[0]['data_points'],
                                                                      lowest_c_3_type=triggers_c_3_values[0]['lowest_c_3_type'],
                                                                       lowest_c_3_val=triggers_c_3_values[0]['lowest_c_3_val'],
                                                                                  dev=triggers[triggers_c_3_keys[0]],
                                                                      account_balance=account_balance,
                                                                        dev_direction="positive",
                                                                               symbol=symbol)
                trigger_vars["lower_triggers"][f"lt1"] = get_trigger_vars(data_points=triggers_c_3_values[0]['data_points'],
                                                                      lowest_c_3_type=triggers_c_3_values[0]['lowest_c_3_type'],
                                                                       lowest_c_3_val=triggers_c_3_values[0]['lowest_c_3_val'],
                                                                                  dev=triggers[triggers_c_3_keys[0]],
                                                                      account_balance=account_balance,
                                                                        dev_direction="negative",
                                                                               symbol=symbol)
            else:
                trigger_vars = "lowest_c_3_val too low"

        return trigger_vars
    else:
        for index, trigger in enumerate(triggers_c_3_values):
            if trigger['lowest_c_3_val'] >= 75:
                over_75_count += 1
                trigger_vars["upper_triggers"].setdefault(f"ut{over_75_count}", "")
                trigger_vars["lower_triggers"].setdefault(f"lt{over_75_count}", "")

                trigger_vars["upper_triggers"][f"ut{over_75_count}"] = get_trigger_vars(data_points=trigger['data_points'],
                                                                                    lowest_c_3_type=trigger['lowest_c_3_type'],
                                                                                     lowest_c_3_val=trigger['lowest_c_3_val'],
                                                                                                dev=triggers[triggers_c_3_keys[index]],
                                                                                    account_balance=account_balance,
                                                                                      dev_direction="positive",
                                                                                             symbol=symbol)
                trigger_vars["lower_triggers"][f"lt{over_75_count}"] = get_trigger_vars(data_points=trigger['data_points'],
                                                                                    lowest_c_3_type=trigger['lowest_c_3_type'],
                                                                                     lowest_c_3_val=trigger['lowest_c_3_val'],
                                                                                                dev=triggers[triggers_c_3_keys[index]],
                                                                                    account_balance=account_balance,
                                                                                      dev_direction="negative",
                                                                                             symbol=symbol)

                # Add the c_3_ema and c_3_ema_val to the trigger_vars dictionary for rendering
                trigger_vars["upper_triggers"][f"ut{over_75_count}"]["c_3_ema"] = trigger['lowest_c_3_type']
                trigger_vars["upper_triggers"][f"ut{over_75_count}"]["c_3_ema_val"] = trigger['lowest_c_3_val']
                trigger_vars["lower_triggers"][f"lt{over_75_count}"]["c_3_ema"] = trigger['lowest_c_3_type']
                trigger_vars["lower_triggers"][f"lt{over_75_count}"]["c_3_ema_val"] = trigger['lowest_c_3_val']

        if len(trigger_vars['lower_triggers']) == 0 or len(trigger_vars['upper_triggers']) == 0:
            return "lowest_c_3_val too low"
        else:
            return trigger_vars



def create_schedule(next_week=False, custom_date=False, update_news_and_tick_data=True):
    top_indicators = pd.read_excel("reports/top_indicators.xlsx")
    indicators = []

    for index, row in top_indicators.iterrows():
        indicators.append((str(row['inv_id']), haawks_id_to_str(row['haawks_id']), row['symbol'], row['higher_dev'], row['inv_title']))

    upcoming_events = scrape_economic_calendar(indicators, next_week=next_week, custom_date=custom_date)
    no_of_events = len(upcoming_events)

    weekdays_html = {
        "Sunday": "",
        "Monday": "",
        "Tuesday": "",
        "Wednesday": "",
        "Thursday": "",
        "Friday": "",
    }

    if update_news_and_tick_data:
        print(f"Updating news & tick data for {len(upcoming_events)} upcoming events")
        for index, event in enumerate(upcoming_events):
            haawks_id_str = event[1]
            symbol = event[2]
            title = event[4]
            print(f"[{int(index) + 1}/{len(upcoming_events)}] {haawks_id_str}  {title} ({symbol})")
            print("  Updating indicator history...")
            update_indicator_history(haawks_id_str)
            print("  Importing ticks...")
            import_ticks_for_indicator(haawks_id_str, symbol)

    print(f"Analyzing & generating recommended triggers for {len(upcoming_events)} events...")
    for index, event in enumerate(upcoming_events):
        haawks_id_str = event[1]
        symbol = event[2]
        higher_dev = event[3]
        title = event[4]
        print(f"[{int(index) + 1}/{no_of_events}] {haawks_id_str}  {title} ({symbol})")
        # timedelta_hrs = 5

        dt_gmt = event[5] + datetime.timedelta(hours=4)
        datetime_et_str = event[5].strftime("%A %-d/%-m @%H:%M") + " (ET)"
        datetime_str = dt_gmt.strftime("%A %-d/%-m @%H:%M") + " (GMT)"

        triggers_vars = get_triggers_vars(haawks_id_str, symbol, higher_dev)
        day = get_day(dt=dt_gmt)

        # Check if triggers_vars has "Not enough data" of "lowest_c_3_val too low"
        if triggers_vars in ["Not enough data", "lowest_c_3_val too low"]:
            event_html = ""
        else:
            event_html = render_event_html(title, datetime_str, datetime_et_str, symbol, triggers_vars)

        weekdays_html[day] += "\n" + event_html

    template_vars = {
        "year": datetime.datetime.now().strftime("%Y"),
        "week_no": "",  # (upcoming_events[0][5] + datetime.timedelta(hours=5)).strftime("%Y"),
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


# create_schedule(custom_date=True, update_news_and_tick_data=True)
