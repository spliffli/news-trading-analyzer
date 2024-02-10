import pandas as pd
from utils import haawks_id_to_str, get_indicator_info
from scrape import update_indicator_history
"""
indicators = pd.read_excel("haawks-indicator-shortlist-1.xlsx")
indicators = indicators.iloc[16:].reset_index()
row_count = indicators.shape[0]

for index, row in indicators.iterrows():
    print(f"Indicator {int(index) + 1}/{row_count}: {row['inv_title']}")
    update_indicator_history(haawks_id_to_str(row['Id']))
"""
ranker_results = pd.read_excel("reports/ranker_results (copy).xls")
row_count = ranker_results.shape[0]
df = ranker_results.copy()

for index, row in ranker_results.iterrows():
    print(f"{int(index) + 1}/{row_count}")
    df.loc[index]['interval'] = get_indicator_info(haawks_id_to_str(row['haawks_id']))['Interval']

print(df)
