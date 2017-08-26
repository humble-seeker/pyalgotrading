# -*- coding: utf-8 -*-
"""
@author: Pushpak Dagade
"""

import datetime as dt
import pandas

from backtesting import AlgoTradingBacktesting

PATH_DATA_POINTS = r'pycon-tatasteel-data.csv'


class Strategy2(AlgoTradingBacktesting):
    def __init__(self):
        AlgoTradingBacktesting.__init__(self)
        self.initialize_crossover()

    def read_data(self):
        self.csv = pandas.read_csv(PATH_DATA_POINTS)
        self.timeline= [dt.datetime.strptime(date,'%d/%m/%y %H:%M') for date in self.csv['Date']][::-1]
        self.candles_open = self.csv['TATASTEEL-EQ O'].tolist()[::-1]
        self.candles_close = self.csv['TATASTEEL-EQ C'].tolist()[::-1]
        self.candles_high = self.csv['TATASTEEL-EQ H'].tolist()[::-1]
        self.candles_low = self.csv['TATASTEEL-EQ L'].tolist()[::-1]

    def sma(self, data, window):
        """
        Calculates Simple Moving Average
        http://fxtrade.oanda.com/learn/forex-indicators/simple-moving-average
        """
        if len(data) < window:
            return None
        return sum(data[-window:]) / float(window)

    def ema(self, data, window):
        """
        Calculates Exponential Moving Average
        """
        if len(data) < 2 * window:
            raise ValueError("data is too short")
        c = 2.0 / (window + 1)
        current_ema = self.sma(data[-window*2:-window], window)
        for value in data[-window:]:
            current_ema = (c * value) + ((1 - c) * current_ema)
        return current_ema

    def initialize_crossover(self):
        self.prev_val1 = 0
        self.prev_val2 = 0

    def crossover(self, val1, val2):
        cmp1 = cmp(val1, val2)
        cmp2 = cmp(self.prev_val1, self.prev_val2)
        if (not (self.prev_val1 == 0 and self.prev_val2 == 0)):         # don't trigger crossover when called first time
            self.prev_val1, self.prev_val2 = val1, val2
            if cmp1 > cmp2:
                return 1
            elif cmp1 < cmp2:
                return -1
            else:
                return 0
        else:
            self.prev_val1, self.prev_val2 = val1, val2
            return 0

    def strategy(self, i, candle_open, candle_close, candle_low, candle_high):
        crossover = 0
        if i >= 29:      # ema(15) needs atleast 30 points
            crossover = self.crossover(self.ema(self.candles_close[:i+1], 3), self.ema(self.candles_close[:i+1], 15))
            if (crossover == 1):
                stop_loss = candle_close*(1 - 0.01)
                target = candle_close*(1 + 0.003)
                print 'Crossover, BUY: stock_price: %f, stop_loss: %f, target_price: %f' % (candle_close, stop_loss, target)
                self.buy_trade(entry_price=candle_close, quantity=1,
                               stop_loss_trigger=stop_loss, target_trigger=target)
            elif (crossover == -1):
                stop_loss = candle_close*(1 + 0.01)
                target = candle_close*(1 - 0.003)
                print 'Crossover, SELL: stock_price: %f, stop_loss: %f, target_price: %f' % (candle_close, stop_loss, target)
                self.sell_trade(entry_price=candle_close, quantity=1,
                                stop_loss_trigger=stop_loss, target_trigger=target)

if __name__ == "__main__":
    algotrading = Strategy2()
    algotrading.backtest()
    algotrading.plot()
#    algotrading.animate()
