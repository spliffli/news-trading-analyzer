# News Trading System Explained

## Intro

In this document I will outline the system I'm developing for trading economic news indicators on the forex market. The main principle is that there are various scheduled economic statistics which are released on a regular basis that impact the market's prices. If you know what the release figures are, then you can make informed predictions on which way the price will move. Since the price reacts very quickly, it's important to enter the trade as quickly as possible to capture the movement.

## What this system is not

It's worth noting that the vast majority of trading strategies involve technical analysis (TA). That essentially means looking at the price charts and adding indicators such as RSI, MACD and others to predict which way the price will move. This is based entirely on the historic price and nothing more, and most traders who use only technical analysis lose in the long term. Probably about 95% of traders are using technical analysis and about 95% of traders lose. The only way to consistently win in the market is to have an edge, and this is impossible with only TA.

## How I found out about this strategy

If you go on youtube or google and search for videos about algorithmic trading advice, practically all of them will be about technical analysis. Not only that, but the general advice given is to turn off your trading algorithm during news events because it causes 'unpredictable' price movements. However, it's only unpredictable through the paradigm of technical analysis. After seeing this many times it got me thinking:

### Why does the price still move if everybody is saying to turn off their trading during these news events?

It's only possible for the price to move when people trade, so clearly there are some people trading the news. But who? If you try to find out, you won't find much information anywhere on the internet, and so it can be inferred that most likely the people who are causing these prices to move during news events are institutional traders, not retail traders.

## What kind of news moves the market?

If you go to `investing.com/economic-calendar/` you will find a big list of news events which have an impact on the market:

![](images/economic-calendar.png)
For each event, there are three figures: Actual, Forecast & Previous

- **Actual**
  This is the figure that is released at the sceduled release time
- **Forecast**
  This number represents the average/consensus of predictions that economists around the world have made
- **Previous**
  This is the number from the previous release

The most important ones are the Forecast and Actual numbers. What actually causes the market to move is when the Actual number deviates from the forecast. If we look at Canada's monthly GDP as an example:
![](images/canada-gdp-mom.png)
Each time the actual number was higher than the forecast, the number is shown in green. Each time it was lower than the forecast, it is shown in red.

For GDP, a higher than expected number is positive or 'bullish' for the underlying currency which in this case is the Canadian dollar (CAD). Therefore, a higher deviation should make the price of CAD go up, and a lower deviation should make the price go down. If there is no deviation i.e. the actual number is the same as the forecast, then there's no trade setup.

If you were actually going to trade this event, then the currency pair/symbol to use would be USDCAD. In any currency pair there are two currencies: the base currency and the quote currency.

The base currency is the first one, which is USD, and the quote currency is the second one, which is CAD. The price of USDCAD is the amount of CAD you need to buy 1 USD.

* The exchange rate can be affected by various factors, such as changes in interest rates, economic indicators, geopolitical events, and market sentiment. These factors can influence the demand and supply of the currencies in the pair, and therefore affect their relative value and the exchange rate.
* In the USDJPY pair, USD is the base currency so the exchange rate tells you how many JPY you need to buy 1 USD. If the exchange rate is 110.00, you need to spend 110 JPY to buy 1 USD. Positive news for USD can make the exchange rate go up, while negative news can make it go down. As with USDCAD, you can trade USDJPY by going long or short, depending on your view of the market
* In the USDCAD pair, CAD is the quote currency, so the exchange rate tells you how much CAD you need to buy 1 USD. For example, if the exchange rate is 1.25, you need to spend 1.25 CAD to buy 1 USD. This means that if you have 100 CAD, you can only buy 80 USD if the exchange rate is 0.80. Positive news for CAD can make the exchange rate go down, while negative news can make it go up. As with USDJPY, you can trade USDCAD by going long or short, depending on your view of the market
* When the underlying currency is the **base currency** in the pair (e.g. **USD** in **USD**JPY) and there is:

  * **positive news:** the price goes up
  * **negative news:** the price goes down
* When the underlying currency is the **quote currency** in the pair (e.g. **CAD** in USD**CAD**) and there is:

  * **positive news:** the price goes down
  * **negative news:** the price goes up
* When you trade a currency pair, you are speculating on the direction of the exchange rate. If you think that the base currency will appreciate against the quote currency, you can buy the pair (go long). If you think that the base currency will depreciate against the quote currency, you can sell the pair (go short). The profit or loss you make depends on the difference between the entry and exit price of the trade, and the size of your position.

## Latency/Speed

- Because the price usually moves in under a second after these events are released, it's necessary to be as fast as possible to enter the trade before the price moves. That can only be achieved by running a computer program on a server that's co-located with the broker you are trading with.
- Co-location means when you have a server that's physically in the same building as the broker's server. This means the latency i.e. the time it takes for data to travel from one point to another on the internet will be lower

  - Think of it like sending a letter in the mail. If you live far away from the person you're sending the letter to, it will take longer for the letter to arrive compared to if they live just down the street. Similarly, if you're sending data over the internet and the server you're sending it to is located far away, it will take longer for the data to get there compared to if the server is located nearby.
  - This delay in data transfer is what we call ping/latency. It's measured in milliseconds (ms) and can be influenced by a variety of factors, such as distance, network congestion, and the quality of the internet connection.
  - In the context of trading, low latency is important because it allows traders to execute trades faster and take advantage of market opportunities before others can.
  - Most forex brokers have their servers located in one of the Equinix datacenters around the world. The main two are in London (Equinix LD4) and New York (Equinix NY4)
- A fast, low-latency news feed is also required to get the news faster than the price moves. One service provider for this is Haawks, who have low-latency subscriptions with many of the institutions who release the news in the USA, Canada and a few other countries, such as the US Bureau of Labor Statistics (BLS), Bureau of Economic Analysis (BEA), US Department of Commerce, US Census Bureau, Statistics Canada, Bank of Canada, Statistics Norway, Norges Bank, SCB - Statistics Sweden, and more

  - Haawks news-feed is available on both Equinix LD4 & NY4 datacenters

## Forex Brokers

## Trading Software

### MetaTrader 4

![](images/MT4.png)
MetaTrader 4 (MT4) is a popular trading platform used by traders to access and trade financial markets. It was developed by MetaQuotes Software and released in 2005.

MT4 provides traders with a range of tools and features to help them analyze the markets, develop and execute trading strategies, and manage their trades. Some of the key features of MT4 include:

**Charting and technical analysis tools:** MT4 provides traders with a range of charting tools and indicators to help them analyze market trends.

**Automated trading:** MT4 allows traders to develop and automate their trading strategies using Expert Advisors (EAs), which are computer programs that can execute trades based on pre-defined rules and conditions.

**Backtesting:** Traders can use MT4's built-in strategy tester to backtest their trading strategies and see how they would have performed in the past.

**Mobile trading**: MT4 is available as a mobile app, allowing traders to access their accounts and trade on the go.

### Haawks News Trader

## Historic Data Analysis

In order to have the most solid trading plan as possible, I created a data analysis program which gets the historic news figures from investing.com, then gets the historic price (tick) data for the relevent trading pair at the exact time of each news release, then generates metrics/statistics such as:

- the mean average pip movements
- the median pip movements
- the range of pip movements
- Three correlation scores (c_1, c_2 & c_3)
