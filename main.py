from import_ticks import import_ticks_for_indicator
from analyze_data import read_triggers, load_news_tick_analysis_data, calc_news_pip_metrics, news_pip_metrics_to_dfs, read_news_data
from utils import get_indicator_info, get_higher_dev_expected_direction
from scrape import update_indicator_history
from generate_report import render_pdf_report, render_markdown
from scheduler import get_triggers_vars, get_day, render_event_html
import datetime

def analyze_indicator(trading_symbol, haawks_id_str):

    # Perform analysis on the selected indicator and trading symbol
    indicator_info = get_indicator_info(haawks_id_str) # Gets indicator info (dict) by reading from haawks shortlist
    underlying_currency = indicator_info['inv_currency']
    underlying_currency_higher_dev = indicator_info['higher_dev']
    symbol_higher_dev = get_higher_dev_expected_direction(trading_symbol, underlying_currency, underlying_currency_higher_dev)

    if input("Check investing.com for updated news data? (Y/n)").upper() in ['Y', ""]:
        news_data = update_indicator_history(haawks_id_str)
    else:
        news_data = read_news_data(haawks_id_str)
    import_ticks_for_indicator(haawks_id_str, trading_symbol)
    triggers = read_triggers(haawks_id_str)
    news_pip_data = load_news_tick_analysis_data(haawks_id_str, news_data, trading_symbol)
    news_pip_metrics = calc_news_pip_metrics(haawks_id_str, news_pip_data, triggers, symbol_higher_dev)
    news_pip_metrics_dfs = news_pip_metrics_to_dfs(news_pip_metrics)
    render_pdf_report(haawks_id_str, trading_symbol, news_data, news_pip_metrics_dfs, triggers, symbol_higher_dev, indicator_info)


def generate_report(trading_symbol, haawks_id_str):

    # Perform analysis on the selected indicator and trading symbol
    indicator_info = get_indicator_info(haawks_id_str) # Gets indicator info (dict) by reading from haawks shortlist
    underlying_currency = indicator_info['inv_currency']
    underlying_currency_higher_dev = indicator_info['higher_dev']
    symbol_higher_dev = get_higher_dev_expected_direction(trading_symbol, underlying_currency, underlying_currency_higher_dev)

    if input("Check investing.com for updated news data? (Y/n)").upper() in ['Y', ""]:
        news_data = update_indicator_history(haawks_id_str)
    else:
        news_data = read_news_data(haawks_id_str)
    import_ticks_for_indicator(haawks_id_str, trading_symbol)
    triggers = read_triggers(haawks_id_str)
    news_pip_data = load_news_tick_analysis_data(haawks_id_str, news_data, trading_symbol)
    news_pip_metrics = calc_news_pip_metrics(haawks_id_str, news_pip_data, triggers, symbol_higher_dev)
    news_pip_metrics_dfs = news_pip_metrics_to_dfs(news_pip_metrics)
    render_pdf_report(haawks_id_str, trading_symbol, news_data, news_pip_metrics_dfs, triggers, symbol_higher_dev, indicator_info)


if __name__ == "__main__":
   generate_report("USDJPY", "10000")

