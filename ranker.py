# Import necessary libraries and modules
from import_ticks import import_ticks_for_indicator
from analyze_data import read_triggers, load_news_pip_data, calc_news_pip_metrics, \
    news_pip_metrics_to_dfs, read_news_data
from utils import get_indicator_info, get_higher_dev_expected_direction, haawks_id_to_str
# from scrape import update_indicator_history
from generate_report import render_pdf_report
import pandas as pd
from collections import Counter
import os

# Read the existing results file containing previous analysis
results_file = pd.read_excel('./reports/ranker_results.xls')
results_length = results_file.shape[0]

def read_indicators():
    # Read the list of indicators to be analyzed
    indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")
    indicators = indicators.loc[results_length:].reset_index()
    
    return indicators


# Function to get the best trigger based on specific criteria
def get_best_trigger_c3(news_pip_metrics_dfs):
    triggers = []
    total_c3_scores = []
    for trigger in news_pip_metrics_dfs:
        triggers.append(trigger)
        total_c3_scores.append(news_pip_metrics_dfs[trigger].iloc[-1]['lowest_c3_val'])

    try:
        best_trigger = triggers[total_c3_scores.index(max(total_c3_scores))]
        return best_trigger
    except:
        return None


# Main function to run the analysis for each indicator
def run():
    indicators = read_indicators()

    for index, row in indicators.iterrows():
        # Extract information about the indicator
        haawks_id_str = haawks_id_to_str(row['Id'])
        indicator_info = get_indicator_info(haawks_id_str)
        underlying_currency = indicator_info['inv_currency']
        underlying_currency_higher_dev = indicator_info['higher_dev']
        trading_symbol = indicator_info['default_symbol']

        # Print information about the current indicator being analyzed
        print("\n----------------------------------------\n"
              f"Indicator {int(index) + 1}/{indicators.shape[0]}: {indicator_info['inv_title']} ({trading_symbol})")

        # Get the expected direction of the trading symbol
        symbol_higher_dev = get_higher_dev_expected_direction(trading_symbol, underlying_currency,
                                                              underlying_currency_higher_dev)

        # Read news data, import ticks, and read triggers for the indicator
        news_data = read_news_data(haawks_id_str)

        expected_directions = []

        for value in news_data['Deviation']:
            if value >= 0:
                expected_directions.append("up")
            else:
                expected_directions.append("down")

        news_data['expected_direction'] = expected_directions

        import_ticks_for_indicator(haawks_id_str, trading_symbol)
        triggers = read_triggers(haawks_id_str)

        # Load news pip data at timedeltas and calculate news pip metrics
        news_pip_data = load_news_pip_data(haawks_id_str, news_data,
                                           trading_symbol)
mm        news_pip_metrics = calc_news_pip_metrics(haawks_id_str, news_pip_data, triggers,
                                                 symbol_higher_dev)

        # [!!!*SANITY CHECK*!!!] does news_pip_metrics include lowest_c3_val?
        news_pip_trigger_metrics_dfs = news_pip_metrics_to_dfs(news_pip_metrics)



        # Generate a PDF report for the current indicator
        render_pdf_report(haawks_id_str, trading_symbol, news_data, news_pip_trigger_metrics_dfs, triggers, symbol_higher_dev,
                          indicator_info)

        # Get the best trigger based on the calculated metrics
        best_trigger_c3 = get_best_trigger_c3(news_pip_trigger_metrics_dfs)

        # Check if the results file already exists
        results_file_exists = False
        for filename in os.listdir('./reports'):
            if filename == 'ranker_results.xls':
                results = pd.read_excel('reports/ranker_results.xls')
                results_file_exists = True
                break

        # If the results file does not exist, create an empty DataFrame
        if not results_file_exists:
            results = pd.DataFrame(columns=['haawks_id_str', 'haawks_title', 'inv_title', 'symbol', 'higher_dev',
                                            'best_trigger_c3', 'range (pips)', 'mean (pips)', 'median (pips)', 'c1', 'c2',
                                            'lowest_ema_val', 'mean_cont_score', 'median_cont_score', 'lowest_avg_cont_pips',
                                            'cont_score', 'probability'])

        try:
            # Append the results for the current indicator to the DataFrame
            results = results.append({
                'haawks_id': haawks_id_str,
                'haawks_title': indicator_info['Indicator'],
                'inv_title': indicator_info['inv_title'],
                'symbol': trading_symbol,
                'higher_dev': symbol_higher_dev,
                'best_trigger_c3': f"{best_trigger_c3}: +-{triggers[best_trigger_c3]}{indicator_info['suffix']}",
                'range (pips)': news_pip_trigger_metrics_dfs[best_trigger_c3].iloc[-1]['range'],
                'mean (pips)': news_pip_trigger_metrics_dfs[best_trigger_c3].iloc[-1]['mean'],
                'median (pips)': news_pip_trigger_metrics_dfs[best_trigger_c3].iloc[-1]['median'],
                'c1': news_pip_trigger_metrics_dfs[best_trigger_c3].iloc[-1]['c1'],
                'c2': news_pip_trigger_metrics_dfs[best_trigger_c3].iloc[-1]['c2'],
                'lowest_c3_val': news_pip_trigger_metrics_dfs[best_trigger_c3].iloc[-1]['lowest_c3_val'],
                'mean_cont_pips': news_pip_metrics['avg_cont_pips']['mean'],
                'median_cont_pips': news_pip_metrics['avg_cont_pips']['median'],
                'lowest_avg_cont_pips': news_pip_metrics['lowest_avg_cont_pips'],
                'cont_pips': news_pip_metrics['cont_pips'],
                'cont_score': news_pip_metrics['cont_score'],
                'win_rate': news_pip_metrics['win_rate'],
                'win_rate_1_pip': news_pip_metrics['win_rate_1_pip'],
                'win_rate_5_pips': news_pip_metrics['win_rate_5_pips'],
                'probability': news_pip_metrics['probability']

            }, ignore_index=True)

            # Write the updated results DataFrame to the results file
            results.to_excel('reports/ranker_results.xls', index=False)
        except:
            continue


# Run the analysis for all indicators
run()
