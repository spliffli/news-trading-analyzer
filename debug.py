from import_ticks import import_ticks_for_indicator
from analyze_data import read_triggers, load_news_pip_data, calc_news_pip_metrics, news_pip_metrics_to_dfs, read_news_data
from utils import get_indicator_info, get_higher_dev_expected_direction
from scrape import update_indicator_history
from generate_report import generate_report, render_markdown

#import_ticks_for_indicator("10000", "EURUSD")

def debug_generate_report(trading_symbol, haawks_id_str):

    # Perform analysis on the selected indicator and trading symbol
    indicator_info = get_indicator_info(haawks_id_str)
    underlying_currency = indicator_info['inv_currency']
    underlying_currency_higher_dev = indicator_info['higher_dev']
    symbol_higher_dev = get_higher_dev_expected_direction(trading_symbol, underlying_currency, underlying_currency_higher_dev)

    if input("Check investing.com for updated news data? (Y/n)").upper() in ['Y', ""]:
        news_data = update_indicator_history(haawks_id_str)
    else:
        news_data = read_news_data(haawks_id_str)
    import_ticks_for_indicator(haawks_id_str, trading_symbol)
    triggers = read_triggers(haawks_id_str)
    news_pip_data = load_news_pip_data(haawks_id_str, news_data, trading_symbol)
    news_pip_metrics = calc_news_pip_metrics(haawks_id_str, news_pip_data, triggers, symbol_higher_dev)
    news_pip_metrics_dfs = news_pip_metrics_to_dfs(news_pip_metrics)
    generate_report(haawks_id_str, trading_symbol, news_data, news_pip_metrics_dfs, triggers, symbol_higher_dev, indicator_info)


def debug_render_markdown(template_vars=None):

    if template_vars is None:
        template_vars = {'year': '2023', 'week_no': '',
                         'start_date': '2023/04/06', 'end_date': '2023/04/06',
                         'sunday_events': '',
                         'monday_events': '',
                         'tuesday_events': '',
                         'wednesday_events': '',
                         'thursday_events': '  <div class="card-wrapper">\n    <div class="card">\n      <h3>U.S. Initial Jobless Claims</h3>\n      <h3>Thursday 6/4 @12:30 (GMT)</h3>\n      <h3>Thursday 6/4 @08:30 (ET)</h3>\n      <h3>USDJPY</h3>\n      <hr>\n      <div class="triggers">\n        <h4>LTA: <span>Buy</span></h4>\n        <h4>UTA: <span>Sell</span></h4>\n        <br>\n          <div class="lower-triggers">\n          <div class="trigger">\n            <h4>-LT1:</h4>\n            <h5>c_3: <span>78.6</span></h5>\n            <h5>data pts: <span>72</span></h5>\n            <h5>dev: <span>-12.0</span></h5>\n            <h5>lots/$1k: <span>0.5</span></h5>\n            <h5>lots: <span>0.5</span></h5>\n          </div>\n        </div>\n        <br>\n        <div class="upper-triggers">\n          <div class="trigger">\n          <h4>+UT1:</h4>\n            <h5>c_3: <span>78.6</span></h5>\n            <h5>data pts: <span>72</span></h5>\n            <h5>dev: <span>12.0</span></h5>\n            <h5>lots/$1k: <span>0.5</span></h5>\n            <h5>lots: <span>0.5</span></h5>\n          </div>\n        </div>\n\n      </div>\n    </div>\n  </div>  <div class="card-wrapper">\n    <div class="card">\n      <h3>Canada Employment Change</h3>\n      <h3>Thursday 6/4 @12:30 (GMT)</h3>\n      <h3>Thursday 6/4 @08:30 (ET)</h3>\n      <h3>USDCAD</h3>\n      <hr>\n      <div class="triggers">\n        <h4>LTA: <span>Buy</span></h4>\n        <h4>UTA: <span>Sell</span></h4>\n        <br>\n          <div class="lower-triggers">\n          <div class="trigger">\n            <h4>-LT1:</h4>\n            <h5>c_3: <span>87.6</span></h5>\n            <h5>data pts: <span>15</span></h5>\n            <h5>dev: <span>-10.0</span></h5>\n            <h5>lots/$1k: <span>1</span></h5>\n            <h5>lots: <span>1.0</span></h5>\n          </div>\n          <div class="trigger">\n            <h4>-LT2:</h4>\n            <h5>c_3: <span>78.8</span></h5>\n            <h5>data pts: <span>15</span></h5>\n            <h5>dev: <span>-25.0</span></h5>\n            <h5>lots/$1k: <span>0.5</span></h5>\n            <h5>lots: <span>0.5</span></h5>\n          </div>\n          <div class="trigger">\n            <h4>-LT3:</h4>\n            <h5>c_3: <span>99.0</span></h5>\n            <h5>data pts: <span>16</span></h5>\n            <h5>dev: <span>-50.0</span></h5>\n            <h5>lots/$1k: <span>2</span></h5>\n            <h5>lots: <span>2.0</span></h5>\n          </div>\n        </div>\n        <br>\n        <div class="upper-triggers">\n          <div class="trigger">\n          <h4>+UT1:</h4>\n            <h5>c_3: <span>87.6</span></h5>\n            <h5>data pts: <span>15</span></h5>\n            <h5>dev: <span>10.0</span></h5>\n            <h5>lots/$1k: <span>1</span></h5>\n            <h5>lots: <span>1.0</span></h5>\n          </div>\n          <div class="trigger">\n          <h4>+UT2:</h4>\n            <h5>c_3: <span>78.8</span></h5>\n            <h5>data pts: <span>15</span></h5>\n            <h5>dev: <span>25.0</span></h5>\n            <h5>lots/$1k: <span>0.5</span></h5>\n            <h5>lots: <span>0.5</span></h5>\n          </div>\n          <div class="trigger">\n          <h4>+UT3:</h4>\n            <h5>c_3: <span>99.0</span></h5>\n            <h5>data pts: <span>16</span></h5>\n            <h5>dev: <span>50.0</span></h5>\n            <h5>lots/$1k: <span>2</span></h5>\n            <h5>lots: <span>2.0</span></h5>\n          </div>\n        </div>\n\n      </div>\n    </div>\n  </div>  <div class="card-wrapper">\n    <div class="card">\n      <h3>Canada Unemployment Rate</h3>\n      <h3>Thursday 6/4 @12:30 (GMT)</h3>\n      <h3>Thursday 6/4 @08:30 (ET)</h3>\n      <h3>USDCAD</h3>\n      <hr>\n      <div class="triggers">\n        <h4>LTA: <span>Sell</span></h4>\n        <h4>UTA: <span>Buy</span></h4>\n        <br>\n          <div class="lower-triggers">\n          <div class="trigger">\n            <h4>-LT1:</h4>\n            <h5>c_3: <span>86.5</span></h5>\n            <h5>data pts: <span>18</span></h5>\n            <h5>dev: <span>-0.3</span></h5>\n            <h5>lots/$1k: <span>1</span></h5>\n            <h5>lots: <span>1.0</span></h5>\n          </div>\n        </div>\n        <br>\n        <div class="upper-triggers">\n          <div class="trigger">\n          <h4>+UT1:</h4>\n            <h5>c_3: <span>86.5</span></h5>\n            <h5>data pts: <span>18</span></h5>\n            <h5>dev: <span>0.3</span></h5>\n            <h5>lots/$1k: <span>1</span></h5>\n            <h5>lots: <span>1.0</span></h5>\n          </div>\n        </div>\n\n      </div>\n    </div>\n  </div>',
                         'friday_events': ''}

    output_markdown = render_markdown(template_vars)
    return output_markdown


def debug_save_markdown(markdown_str):

    week_no = "14"

    with open(f'docs/weekly-schedules/week-{week_no}-schedule.md', 'w') as file:
        file.write(markdown_str)


# debug_generate_report("USDJPY", "10000")
md = debug_render_markdown()
debug_save_markdown(md)
