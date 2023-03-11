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
    - [X] Calculate a predictability score based on how often the market moves in the expected direction

## Part 3: Generating a report with data insights & trigger recommendations

- [X] After the news and tick data has been added to the database, new data insights can be inferred/calculated from that such as:

  - [X] Pip movement per trigger. The triggers vary depending on the units but eg. interest rates might include 0.1% | then the average pip movements of each time there was 0.1% deviation. Then 0.2% | then the average pip movements of each time there was 0.2% deviation, etc etc)

    - [X] I ended up generating trigger levels based on 5 quantiles of the news deviations, then manually edit them to more round numbers
  - [X] recommended news triggers derived from the above data. Not exactly sure what formula this will use, and maybe it will offer several different recommendations depending on how long you intend to keep the trade open, and/or how many pips you want to capture.
  - [X] Once all that data is mined, it would be nice to generate a pdf report

## Part 4: Generating a schedule pdf

### Outline:

- [X] For indicators with a c_3 score of 80+, scrape the investing.com economic calendar for the next week to see if any of those indicators are scheduled to be released
- [ ] If an indicator is scheduled to be released, make an entry in the local schedule and include as much useful information as possible such as:
  - [ ] Recommended triggers:
    - The trigger with the highest c_3 score
    - Any triggers below the best trigger to set with a lower amount of money

### Steps:

1. - [X] Scrape economic calendar from investing.com

- Open `https://www.investing.com/economic-calendar/` in selenium
- Find filters section on the dom
- clear all countries
- select countries:
  - USA (USD)
  - Canada (CAD)
  - Norway (NOK)
  - Sweden (SEK)
  - Poland (PLN)
  - Turkey (TRY)
  - European Union (EUR)
- Select all categories
- Select all importance levels
- Apply filter
- if weekday:
  - Show results for current week
- if weekend:
  - show results for the upcoming monday-friday

1. - [X] Open ranker results file as df
2. - [X] Loop through each row of ranker results:

- Get the indicator's investing.com id
- if there are any events which match the investing.com id:
  - get event datetime
  - add indicator to upcoming indicators df

3. - [X] For each upcoming indicator:

- fill in vars to html template div- Date:
  - Event title
  - Event time
- if c_3 > 80:
  - get news_pips_metrics_dfs for current indicator
  - get best trigger and any triggers below it which have c_3 above 80 (up to 3 triggers)
  - for each valid trigger:
    - if c_3 < 85:
      - lot size = 0.5/$1000
    - if 85 < c_3 < 90:
      - lot size = 0.75/$1000
    - if 95 >  c_3 > 90:
      - lot size = 1/$1000
    - if c3 > 95:
      - lot size = 1.5/$1000
    - for each trigger append variables to html template div
      - Trigger name ie.
        - -LT3
        - -LT2
        - -LT1
        - +UT1
        - +UT2
        - +UT3
      - Trigger deviation
      - c_1
      - c_2
      - c_3
      - lot size
    - append html to trigger recommendations html

5. - [X] render trigger recommendations as a variable in an html template
6. - [X] Convert output html into a pdf file
