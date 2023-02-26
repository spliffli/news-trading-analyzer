import pandas as pd
from utils import haawks_id_to_str
from scrape import update_indicator_history

indicators = pd.read_excel("haawks-indicator-shortlist.xlsx")
indicators = indicators.iloc[16:].reset_index()
row_count = indicators.shape[0]

for index, row in indicators.iterrows():
    print(f"Indicator {int(index) + 1}/{row_count}: {row['inv_title']}")
    update_indicator_history(haawks_id_to_str(row['Id']))