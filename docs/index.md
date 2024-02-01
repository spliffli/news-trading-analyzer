# **Intro**

## **01.02.2024**

It's been a while since I looked at this project because of personal circumstances but I want to give a more concise outline of my system that's quicker to read than the [in-depth explanation](system-explained-en.md) that I wrote last year ([Deutsche Version](system-explained-de.md)).

The system I've developed is quite unique among trading strategies. Very few people in the world are doing this type of trading, and nobody else has publicly released an analysis tool like mine ([Available on Github](https://github.com/spliffli/news-trading-analyzer)).

99.99% of trading advice online is about technical analysis or TA, which pretty much always involves something working in the short term but not in the long term because market behaviours change over time and the strategy breaks. The current price is always an after-effect, not a cause. The same is true for technical indicators like RSI, MACD, moving averages, etc. TA is a fallacy and that's why most people lose, since most people use only TA. Smart money always has an edge and they live basic TA to the masses to provide their liquidity in the market.


With macroeconomic news indicators like [GDP](https://www.investing.com/economic-calendar/gdp-375), [CPI](https://www.investing.com/economic-calendar/cpi-69), [NFP](https://www.investing.com/economic-calendar/nonfarm-payrolls-227), [Unemployment Change](https://www.investing.com/economic-calendar/unemployment-rate-300) & others, they cause the price to move in a predictable way which I measured & analyzed to create a tool which generats trading plans for these events with different triggers based on news deviations, with each trigger having different lot sizes calculated by the probabilites of the event to move the market in an expected direction i.e. the correlation percentage scores which are calculated by looking at historic news figures and cross referencing it with the raw tick data (price data) to see how often the price moves in the expected direction.

I only trade events which have triggers with 75% probability/correlation or more, with 75% being the smallest trade size and 95% being the biggest trades. This means there is a mathematical edge and the main challenge isn't predicting the correct direction since that is easy. The main challenge is instead being fast to enter the trade which requires a low latency news feed such as the one provided by [haawks](https://haawks.com).

The only other succesful low-latency strategy with a mathematical edge that I know of is latency arbitrage i.e. taking advantage of a slow price feed from a broker and being able to glimpse into the future slightly by connecting to a faster price feed like from [Rithmic](https://yyy3.rithmic.com/?page_id=9). 

However, latency arbitrage is against basically every broker's rules since it happens so fast that they often can't send an order to their liquidity providers/ECNs and get filled at the same price which they fill you at. It basically causes slippage on their end and that makes them lose money so they don't like it and it's banned, even if the broker is on a commission model and would otherwise profit no matter if you win or lose like most brokers.

This is a similar situation to how counting cards is against a casino's rules despite being legal, although arbitrage & news trading have much higher odds than counting cards. News trading isn't banned by brokers and is another way of having a quasi-glimpse into the future by knowing the cause before the effect i.e. the reactions of the price to news events depending on how bullish or bearish the news is compared to its forecast number.

Higher deviations/triggers generally mean higher correlation scores like would be common sense but that is not always true from what I measured. 