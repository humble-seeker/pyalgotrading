# -*- coding: utf-8 -*-
"""
@author: Pushpak Dagade
"""

from abc import ABCMeta, abstractmethod
import time
import matplotlib.pyplot as plt
from order import BuyOrder, SellOrder


class AlgoTradingBacktesting:
    __metaclass__ = ABCMeta

    def __init__(self):
        # Store timeline for backtesting.
        # Timeframe can be anything - days, minutes, etc.
        self.timeline = []

        # Candles corresponding to each entry in self.timeline
        self.candles_open = []
        self.candles_close = []
        self.candles_high = []
        self.candles_low = []

        # For keeping track of orders
        self.open_orders = []
        self.closed_orders = []

        # Used during backtesting
        self.current_time = None
        self.current_candle_open = None
        self.current_candle_close = None
        self.current_candle_high = None
        self.current_candle_low = None

        # Read data into self.timeline and self.datapoints
        self.read_data()

    @abstractmethod
    def read_data(self):
        """
        Implement this method to read input data into 2 variables -
        1. timeline
        2. datapoints
        """

    def buy_trade(self, entry_price, quantity=1,
                  stop_loss_trigger=None, target_trigger=None):
        buyorder = BuyOrder(entry_price, quantity, self.current_time,
                            stop_loss_trigger, target_trigger)
        self.open_orders.append(buyorder)

    def sell_trade(self, entry_price, quantity=1,
                   stop_loss_trigger=None, target_trigger=None):
        sellorder = SellOrder(entry_price, quantity, self.current_time,
                              stop_loss_trigger, target_trigger)
        self.open_orders.append(sellorder)

    @abstractmethod
    def strategy(self, i, candle_open, candle_close, candle_low, candle_high):
        """
        Implement your algo trading strategy in this method.
        Follow the following guidelines -
        1. iterate over self.datapoints
        2. for each such iteration, "yield" the profit percent
           i.e. this method should be a generator
        3. When buy condition is met, call self.buy_trade
        4. When sell condition is met, call self.sell_trade
        """

    def backtest(self):
        """
        Call this method to start backtesting
        """
        for i in xrange(len(self.candles_open)):
            self.current_time = self.timeline[i]
            self.current_candle_open = self.candles_open[i]
            self.current_candle_close = self.candles_close[i]
            self.current_candle_high = self.candles_high[i]
            self.current_candle_low = self.candles_low[i]

            # Try to close, open orders
            for i, order in reversed(list(enumerate(self.open_orders))):
                if order.try_to_close(self.current_candle_high,
                                      self.current_candle_low,
                                      self.current_time):
                    self.closed_orders.append(self.open_orders.pop(i))

            # Execute strategy (which will generate create open orders)
            self.strategy(i, self.current_candle_open,
                             self.current_candle_close,
                             self.current_candle_high,
                             self.current_candle_low)

    def __preplot_process(self):
        self.profit_percents = []

        # This confusing piece of code below generates the list
        # self.profit_percents, holding proft_percents corresponding to
        # every entry in timeline.
        j = 0
        total_profit = 0
        total_orders = len(self.closed_orders)
        max_j = total_orders - 1
        max_entry_price = 1e-10     # a very small value; not using 0 to avoid divide by zero error
        for i, _time in enumerate(self.timeline):
            if j <= max_j and _time == self.closed_orders[j].exit_time:
                total_profit += self.closed_orders[j].profit
                j += 1
                if j <= max_j:
                    while True:
                        if self.closed_orders[j].exit_time == _time:
                            total_profit += (self.close_orders[j].profit)
                            max_entry_price = self.closed_orders[j].entry_price if self.closed_orders[j].entry_price > max_entry_price else max_entry_price
                            j += 1
                        else:
                            break

            if j <= max_j:
                max_entry_price = self.closed_orders[j].entry_price if self.closed_orders[j].entry_price > max_entry_price else max_entry_price
            profit_percent = 100.0*total_profit/(max_entry_price)
            self.profit_percents.append(profit_percent)


        # Plotting
        f, (self.ax1, self.ax2) = plt.subplots(2, 1)

        ylim1_min = min(self.candles_close)
        ylim1_max = max(self.candles_close)
        ylim2_min = min(self.profit_percents)
        ylim2_max = max(self.profit_percents)

        # Subplots
        self.ax1.set_xlabel('Date')
        self.ax1.set_ylabel('Stock price')
        self.ax1.set_xlim([self.timeline[0], self.timeline[-1]])
        self.ax1.set_ylim([ylim1_min, ylim1_max])
        self.ax1.set_title('Close candle price vs Timeline')
#        self.ax1.grid(b=True, which='both', axis='both')

        self.ax2.set_xlabel('Date')
        self.ax2.set_ylabel('Percentage profit')
        self.ax2.set_xlim([self.timeline[0], self.timeline[-1]])
        self.ax2.set_ylim([ylim2_min, ylim2_max])
        self.ax1.set_title('Profit percent vs Timeline')
#        self.ax2s.grid(b=True, which='both', axis='both')

    def plot(self):
        """
        Creates 2 plots -
        1. Stock Price vs Date
        2. Profit percentage vs Date

        Generates the plot which will be generated at the end of
        self.animation method
        """

        self.__preplot_process()

        # Stock price
        self.ax1.plot(self.timeline, self.candles_close, color='b')

        # Percentage profit
        self.ax2.plot(self.timeline, self.profit_percents, color='b')

        # Annotate ax1 with buy and sell information
#        previous_quantity = 0
#        for i, th in enumerate(self.trade_history):
#            if previous_quantity < th['quantity']:
#                self.ax1.annotate('',
#                            xy=(self.timeline[i], th['stock_price']), xycoords='data',
#                            xytext=(self.timeline[i], th['stock_price'] + 3), textcoords='data',
#                            size=20, va="center", ha="center",
#                            arrowprops=dict(arrowstyle="-", color="green"),
#                            )
#            if previous_quantity > th['quantity']:
#                self.ax1.annotate('',
#                            xy=(self.timeline[i], th['stock_price']), xycoords='data',
#                            xytext=(self.timeline[i], th['stock_price'] - 3), textcoords='data',
#                            size=20, va="center", ha="center",
#                            arrowprops=dict(arrowstyle="-", color="red"),
#                            )
#
##            previous_quantity = th['quantity']

        plt.show()

    def animate(self):
        """
        Animates 2 plots -
        1. Stock Price vs Date
        2. Profit percentage vs Date

        Speed of animation can be controlled by playing with 3rd argument of xrange
        """
        self.__preplot_process()

        plt.ion()
        plt.figure(1)
        plt.hold(True)

        ax1_plot = None
        ax2_plot = None

        step = self.df.shape[0]/100 if self.df.shape[0]/100 >= 1 else 1
        for i in xrange(0, self.df.shape[0], step):
            # Stock price
            if ax1_plot:
                ax1_plot.remove()
            ax1_plot, = self.ax1.plot(self.timeline[:i], self.candles_close[:i], color='b')

            # Percentage profit
            if ax2_plot:
                ax2_plot.remove()
            ax2_plot, = self.ax2.plot(self.timeline[:i], self.profit_percents[:i], color='b')

            plt.pause(0.01)

            if i == 0:
                time.sleep(1)

        for i in xrange(10):
            # Wait for 10 sec and then exit
            time.sleep(1)
