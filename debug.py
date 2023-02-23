from import_ticks import import_ticks_for_indicator
from analyze_data import read_triggers, load_news_pip_data, calc_news_pip_metrics, news_pip_metrics_to_dfs
from utils import get_indicator_info, get_higher_dev_expected_direction
from scrape import update_indicator_history
from generate_report import generate_report

#import_ticks_for_indicator("10000", "EURUSD")
# Get the user's input as a string (up to 20 characters long)
trading_symbol = "USDCAD"

# Perform analysis on the selected indicator and trading symbol
haawks_id_str = "10290"
indicator_info = get_indicator_info(haawks_id_str)
underlying_currency = indicator_info['inv_currency']
underlying_currency_higher_dev = indicator_info['higher_dev']
symbol_higher_dev = get_higher_dev_expected_direction(trading_symbol, underlying_currency, underlying_currency_higher_dev)

news_data = update_indicator_history(haawks_id_str)
import_ticks_for_indicator(haawks_id_str, trading_symbol)
triggers = read_triggers(haawks_id_str)
news_pip_data = load_news_pip_data(haawks_id_str, news_data, trading_symbol)
news_pip_metrics = calc_news_pip_metrics(haawks_id_str, news_pip_data, triggers, symbol_higher_dev)
news_pip_metrics_dfs = news_pip_metrics_to_dfs(news_pip_metrics)
generate_report(haawks_id_str, trading_symbol, news_data, news_pip_metrics_dfs, triggers, symbol_higher_dev, indicator_info)
