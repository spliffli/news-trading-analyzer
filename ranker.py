from import_ticks import import_ticks_for_indicator
from analyze_data import read_triggers, load_news_pip_data, calc_news_pip_metrics, news_pip_metrics_to_dfs, read_news_data
from utils import get_indicator_info, get_higher_dev_expected_direction, haawks_id_to_str
# from scrape import update_indicator_history
from generate_report import generate_report
import pandas as pd
from collections import Counter
import os

indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")
indicators = indicators.loc[3:].reset_index()


def get_best_trigger(news_pip_metrics_dfs):
    triggers = []
    total_c_3_scores = []
    for trigger in news_pip_metrics_dfs:
        triggers.append(trigger)
        total_c_3_scores.append(news_pip_metrics_dfs[trigger].iloc[-1]['c_3'])

    best_trigger = triggers[total_c_3_scores.index(max(total_c_3_scores))]

    return best_trigger


for index, row in indicators.iterrows():

    haawks_id_str = haawks_id_to_str(row['Id'])
    indicator_info = get_indicator_info(haawks_id_str)
    underlying_currency = indicator_info['inv_currency']
    underlying_currency_higher_dev = indicator_info['higher_dev']
    trading_symbol = indicator_info['default_symbol']

    print("\n----------------------------------------\n"
          f"Indicator {int(index) + 1}/{indicators.shape[0]}: {indicator_info['inv_title']} ({trading_symbol})")

    symbol_higher_dev = get_higher_dev_expected_direction(trading_symbol, underlying_currency,
                                                          underlying_currency_higher_dev)

    # news_data = update_indicator_history(haawks_id_str)

    news_data = read_news_data(haawks_id_str)
    import_ticks_for_indicator(haawks_id_str, trading_symbol)
    triggers = read_triggers(haawks_id_str)
    news_pip_data = load_news_pip_data(haawks_id_str, news_data, trading_symbol)
    news_pip_metrics = calc_news_pip_metrics(haawks_id_str, news_pip_data, triggers, symbol_higher_dev)
    news_pip_metrics_dfs = news_pip_metrics_to_dfs(news_pip_metrics)
    generate_report(haawks_id_str, trading_symbol, news_data, news_pip_metrics_dfs, triggers, symbol_higher_dev, indicator_info)

    best_trigger = get_best_trigger(news_pip_metrics_dfs)

    results_file_exists = False

    for filename in os.listdir('./reports'):
        if filename == 'ranker_results.xls':
            results = pd.read_excel('reports/ranker_results.xls')
            results_file_exists = True
            break

    if not results_file_exists:
        results = pd.DataFrame(columns=['haawks_id', 'haawks_title', 'inv_title', 'symbol', 'higher_dev', 'best_trigger', 'range (pips)', 'mean (pips)', 'median (pips)', 'c_1', 'c_2', 'c_3'])

    results = results.append({
        'haawks_id': haawks_id_str,
        'haawks_title': indicator_info['Indicator'],
        'inv_title': indicator_info['inv_title'],
        'symbol': trading_symbol,
        'higher_dev': symbol_higher_dev,
        'best_trigger': f"{best_trigger}: +-{triggers[best_trigger]}{indicator_info['suffix']}",
        'range (pips)': news_pip_metrics_dfs[best_trigger].iloc[-1]['range'],
        'mean (pips)': news_pip_metrics_dfs[best_trigger].iloc[-1]['mean'],
        'median (pips)': news_pip_metrics_dfs[best_trigger].iloc[-1]['median'],
        'c_1': news_pip_metrics_dfs[best_trigger].iloc[-1]['c_1'],
        'c_2': news_pip_metrics_dfs[best_trigger].iloc[-1]['c_2'],
        'c_3': news_pip_metrics_dfs[best_trigger].iloc[-1]['c_3']
    }, ignore_index=True)


    results.to_excel('reports/ranker_results.xls', index=False)



