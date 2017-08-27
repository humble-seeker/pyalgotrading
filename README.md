
# pyalgotrading

A python based framework for algorithmic trading. Framework supports backtesting, alongwith STOP LOSS and TARGET price features.

This GitHub repository is created for my proposal at PyCon India 2017 - ["Introduction to Algorithmic Trading at Indian Stock Markets using Python"](https://in.pycon.org/cfp/2017/proposals/introduction-to-algorithmic-trading-at-indian-stock-markets-using-python~bY0Wa)


### Example

#### Algorithm:
CROSSOVER(EMA(3), EMA(15)) : Buy Order
CROSSOVER(EMA(15), EMA(3)) : Sell Order

Every Buy and Sell order is placed with 0.3% Target Price and 1% Stop Loss.

#### Data:
* Quote: TATASTEEL (NSE),
* Duration of backtesting: 16th June to 14th August, 2017 (2 months)
* Datapoints: 15,180 (1 minute intra day data)

#### Statistics:
* Executed trades: 141
* Open trades: 1
* Profitable trades: 111
* Loss making trades: 30
* **Average profit: ~6%/month (~72% annually)**

Check out strategy2.log in the repository for complete list of transactions

#### Click the image below to watch video of backtesting strategy in action for TATSTEEL(NSE) datapoints.

[![Click the watch video of backtesting strategy2 in action on TATSTEEL(NSE) data](https://raw.githubusercontent.com/guanidene/pyalgotrading/master/strategy2-returns.png)](https://www.youtube.com/watch?v=NK1ZYsRfF44)


#### Instructions on how to install this repository would be added here soon.

