"""
This is a single-use script to patch the timezones on the data I already downloaded because
I didn't realize all the tick data is in GMT+0 and the default time on investing.com is GMT-5,
so they don't match up. After patching the local data I'll modify the scraper to convert to GMT+0
"""

import pandas as pd
import datetime
import os

for filename in os.listdir("./news_data"):

    df = pd.read_csv(f"./news_data/{filename}")
    print(df)
    for index, row in df.iterrows():
        et_timestamp = datetime.datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S')
        gmt_timestamp = et_timestamp + datetime.timedelta(hours=5)

        # row['Timestamp'] = gmt_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        df.loc[index, 'Timestamp'] = gmt_timestamp.strftime('%Y-%m-%d %H:%M:%S')

    print(df)
    df.to_csv(f"./news_data/{filename}")
    blah = 1