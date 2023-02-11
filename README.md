# News Trading Analyzer

A tool which scrapes economic news data from investing.com and cross-references it with historical tick data to generate news trading trigger recommendations.
This is meant for use with [haawks.com](https://haawks.com) G4A API or news trader tool it comes with.

## Part 1: Scraping & populating database

- [X] Navigate to `investing.com/economic-calendar/{event_id}` with selenium webdriver
- [X] Make sure entire historic data table is loaded into the DOM. JS or clicking 'show more' required due to the design of the webpage, hence using selenium.

  - [X] Better than this would be to take a specified date and only load as far back as needed
- [X] Scrape the table values & add into a pandas DataFrame
- [X] Parse given dates & times into datetime object & append to an extra column for each row
- [X] For each row in the DF, create a save into a .csv file `/news_data/{haawks_id}_{investing.com id}_{investing.com title}.csv` eg. `/news_data/10000_227_US_Nonfarm_Payrolls.csv`, making sure to include the following columns:

  - datetime/timestamp
  - prelim boolean flag
  - forecast
  - actual
  - previous
  - deviation
- [X] Make an excel file called `indicators-list` with the following columns:

  - investing.com event id (if available, otherwise null)
  - haawks indicator id
  - higher_dev (ie. whether a higher deviation from the forecast is bullish or bearish. This info is usually available on investing.com Lower deviation can be inferred as the opposite)
  - impact_level (according to investing.com)
  - tradable symbols
- [X] For each haawks indicator which has available data on investing.com, scrape news data & add to the database
- [ ] Later, modify the script to update the database as new data comes into investing.com without repopulating the db from scratch

## Part 2: Importing & Analyzing tick data

- [X] Using the duka python package, get historical tick data ~~going back eg. 5 years.~~ Actually, because tick data uses up so much storage (~10Gb per symbol per year), it will be more efficient to only download the relevent days as needed instead of the entire history. Then it would be even more efficient to truncate the daily file to just 5 mins before and 15 mins after the news event, or simply delete the tick data after usage.
  - [ ] This can be a basic script at first but ideally it should be a CLI wizard
- [X] for a given indicator and symbol:
  - [X] for each release:

    - [X] download tick data for that day using duka (Can't download only a portion of a day so it has to be the whole day)
    - [X] truncate the tick data to start 5 mins before the release and end 15 mins after the release
    - [X] get the price at the exact time of release
    - [X] calculate the price movement in pips for the following times after release saved into a DataFrame:

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
    - [X] From the pip data, calculate the mean, median and range of the pip movements
    - [ ] Calculate a predictability score based on how often the market moves in the expected direction

## Part 3: Generating a report with data insights & trigger recommendations

- [ ] After the news and tick data has been added to the database, new data insights can be inferred/calculated from that such as:
  - [X] Pip movement per trigger. The triggers vary depending on the units but eg. interest rates might include 0.1% | then the average pip movements of each time there was 0.1% deviation. Then 0.2% | then the average pip movements of each time there was 0.2% deviation, etc etc)
    - [X] I ended up generating trigger levels based on 5 quantiles of the news deviations, then manually edit them to more round numbers
  - [ ] recommended news triggers derived from the above data. Not exactly sure what formula this will use, and maybe it will offer several different recommendations depending on how long you intend to keep the trade open, and/or how many pips you want to capture.
  - [ ] recommended stoploss & takeprofit, estimated slippage can be an input
- [ ] Once all that data is mined, it would be nice to generate a pdf report
