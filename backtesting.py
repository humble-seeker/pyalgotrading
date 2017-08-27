# -*- coding: utf-8 -*-
"""
@author: Pushpak Dagade
"""

from abc import ABCMeta, abstractmethod
from itertools import chain
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
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

    def get_statistics(self, i=None):
        """
        Get various statistics.
        If i is None, provide end of simulation statistics
        If i in not None, provide statistics generated upto self.timeline[i]
        """
        executed_trades = 0
        open_trades = 0
        profitable_trades = 0
        loss_making_trades = 0

        if i is None:
            i = -1          # till last element of self.timeline

        # Code for recreating scenario of executed and open trades for
        # given time 'i' (ie self.timeline[i])
        for j, order in enumerate(chain(self.closed_orders, self.open_orders)):
            if (order.exit_time is not None and order.exit_time <= self.timeline[i]):
                executed_trades += 1
                if order.profit >= 0:
                    profitable_trades += 1
                else:
                    loss_making_trades += 1
            elif (order.entry_time < self.timeline[i] and (order.exit_time is None or order.exit_time > self.timeline[i])):
                open_trades += 1
            else:
                break

        return """
Statistics:
---------------------------
Executed trades: %d
Open trades: %d
Profitable trades: %d
Loss making trades: %d
             """ % (executed_trades, open_trades, profitable_trades, loss_making_trades)

    def print_statistics(self):
        print self.get_statistics()

    def __preplot_process(self):
        self.profit_percents = []
#        self.buy_quantities = []
#        self.sell_quantities = []

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
#                if self.closed_orders[j].type == 'buy':
#                    self.buy_quantities.append(self.closed_orders[j].quantity)
#                    self.sell_quantities.append(0)
#                else:
#                    self.sell_quantities.append(-self.closed_orders[j].quantity)
#                    self.buy_quantities.append(0)
                j += 1
                if j <= max_j:
                    while True:
                        if self.closed_orders[j].exit_time == _time:
                            total_profit += (self.close_orders[j].profit)
                            max_entry_price = self.closed_orders[j].entry_price if self.closed_orders[j].entry_price > max_entry_price else max_entry_price
#                            if self.closed_orders[j].type == 'buy':
#                                self.buy_quantities[i] = self.buy_quantities[i] + self.closed_orders[j].quantity
#                            else:
#                                self.sell_quantities[i] = self.sell_quantities[i] - self.closed_orders[j].quantity
                            j += 1
                        else:
                            break
#            else:
#                self.buy_quantities.append(0)
#                self.sell_quantities.append(0)

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
        tick_label_frequency = 10
        self.ax1.set_xlabel('Date')
        self.ax1.set_ylabel('Stock price')
        self.ax1.set_xlim([self.timeline[0], self.timeline[-1]])
        self.ax1.set_ylim([ylim1_min, ylim1_max])
        if hasattr(self, 'timeline_labels'):
            self.ax1.set_xticks(self.timeline[::len(self.timeline)/tick_label_frequency])
            self.ax1.set_xticklabels(self.timeline_labels[::len(self.timeline)/tick_label_frequency])
#        self.ax1.set_title('Close candle price vs Timeline')
#        self.ax1.grid(b=True, which='both', axis='both')

        self.ax2.set_xlabel('Date')
        self.ax2.set_ylabel('Percentage profit')
        self.ax2.set_xlim([self.timeline[0], self.timeline[-1]])
        self.ax2.set_ylim([ylim2_min, ylim2_max])
        if hasattr(self, 'timeline_labels'):
            self.ax2.set_xticks(self.timeline[::len(self.timeline)/tick_label_frequency])
            self.ax2.set_xticklabels(self.timeline_labels[::len(self.timeline)/tick_label_frequency])
#        self.ax2.set_title('Profit percent vs Timeline')
#        self.ax2.grid(b=True, which='both', axis='both')

        # For showing statistics on plot
        self.plot_text = Rectangle((0, 0), 1.5, 1, fc="w", fill=False, edgecolor='none', linewidth=0)

        # open plot as maximized
        mng = plt.get_current_fig_manager()
        mng.window.showMaximized()
        plt.tight_layout()

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

        # Percentage profit with statistics
        self.ax2.plot(self.timeline, self.profit_percents, color='b')
        self.ax2.legend([self.plot_text], [self.get_statistics()], loc='upper left')

        # Buy/sell bar charts
#        self.ax3.plot(self.timeline, self.buy_quantities, color='g')
#        self.ax3.plot(self.timeline, self.sell_quantities, color='r')


        plt.show()

    def animate(self):
        """
        Animates 2 plots -
        1. Stock Price vs Date
        2. Profit percentage vs Date

        Speed of animation can be controlled by playing with 3rd argument of xrange
        """
        self.__preplot_process()

        # interactive plot mode 'on'
        plt.ion()

        ax1_plot = None
        ax2_plot = None
        animation_frames = 100
        step = len(self.timeline)/animation_frames  if len(self.timeline)/animation_frames >= 1 else 1

        for i in chain(xrange(0, len(self.timeline), step), [len(self.timeline)-1]):
            # Stock price
            if ax1_plot:
                ax1_plot.remove()
            ax1_plot, = self.ax1.plot(self.timeline[:i], self.candles_close[:i], color='b')

            # Percentage profit with statistics
            if ax2_plot:
                ax2_plot.remove()
            ax2_plot, = self.ax2.plot(self.timeline[:i], self.profit_percents[:i], color='b')
            self.ax2.legend([self.plot_text], [self.get_statistics(i)], loc='upper left')

            plt.pause(0.01)

        for i in xrange(20):
            # Wait for 10 sec and then exit
            time.sleep(1)
