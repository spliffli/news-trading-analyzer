# News Trading Analyzer

A tool which scrapes economic news data from investing.com and cross-references it with historical tick data to generate news trading trigger recommendations.
This is meant for use with [haawks.com](https://haawks.com) G4A API or news trader tool it comes with.

## Part 1: Scraping & populating database

- [X] Navigate to `investing.com/economic-calendar/{event_id}` with selenium webdriver
- [X] Make sure entire historic data table is loaded into the DOM. JS or clicking 'show more' required due to the design of the webpage, hence using selenium.

  - [ ] Better than this would be to take a specified date and only load as far back as needed
- [X] Scrape the table values & add into a pandas DataFrame
- [X] Parse given dates & times into datetime object & append to an extra column for each row
- [ ] For each row in the DF, create a database entry using SQLite in the table 'news_data', making sure to include the following columns:

  - investing.com event id
  - haawks indicator id
  - datetime/timestamp
  - prelim boolean flag
  - forecast
  - actual
  - previous
  - deviation
- [ ] Make a second database table called 'indicators' with the following columns:

  - investing.com event id (if available, otherwise null)
  - haawks indicator id
  - higher_dev (ie. whether a higher deviation from the forecast is bullish or bearish. This info is usually available on investing.com Lower deviation can be inferred as the opposite)
  - impact_level (according to investing.com)
  - tradable symbols
- [ ] For each haawks indicator which has available data on investing.com, scrape data & add to the database
- [ ] Later, modify the script to update the database as new data comes into investing.com without repopulating the db from scratch

## Part 2: Analyzing tick data

- [ ] Using the duka python package, get historical tick data ~~going back eg. 5 years.~~ Actually, because tick data uses up so much storage (~10Gb per symbol per year), it will be more efficient to only download the relevent days as needed instead of the entire history. Then it would be even more efficient to truncate the daily file to just 5 mins before and 15 mins after the news event, or simply delete the tick data after usage.
  - [ ] This can be a basic script at first but ideally it should be a CLI wizard
- [ ] for a given indicator and symbol:
  - [ ] for each timestamp entry in database:
    - [ ] navigate to 5 mins before the release time in the tick data
    - [ ] capture all ticks up until 15 mins after release time
    - [ ] get the price at the exact time of release
    - [ ] calculate the price movement in pips for the following times after release saved into a DataFrame:

      - 5 seconds
      - 10 seconds
      - 20 seconds
      - 30 seconds
      - 1 minute
      - 2 minutes
      - 3 minutes
      - 4 minutes
      - 5 minutes
      - 10 minutes
      - 15 minutes
    - [ ] From the DataFrame, append each column to the respective row in the news_data table in the database. Make sure the column is prefixed with the symbol and has the time as well, to differentiate it from any other symbols that might be analyzed for the same indicator. Eg. 'EURUSD_5s', 'EURUSD_10s'... 'XAUUSD_5s'... etc

## Part 3: Generating a report with data insights & trigger recommendations

- [ ] After the news and tick data has been added to the database, new data insights can be inferred/calculated from that such as:
  - [ ] Average deviation
  - [ ] Pip movement per level of deviation. This will vary depending on the units but eg. interest rates might include 0.1% | then the average pip movements of each time there was 0.1% deviation. Then 0.2% | then the average pip movements of each time there was 0.2% deviation, etc etc)
  - [ ] recommended news triggers derived from the above data. Not exactly sure what formula this will use, and maybe it will offer several different recommendations depending on how long you intend to keep the trade open, and/or how many pips you want to capture.
  - [ ] recommended stoploss & takeprofit, estimated slippage can be an input
- [ ] Once all that data is mined, it would be nice to display it in graphs with matplotlib, then maybe generate a pdf report
