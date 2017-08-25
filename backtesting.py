# -*- coding: utf-8 -*-
"""
@author: Pushpak Dagade
"""

from abc import ABCMeta, abstractmethod
import time

import matplotlib.pyplot as plt
import pandas


class AlgoTradingBacktesting:
    __metaclass__ = ABCMeta

    def __init__(self):
        # Store timeline for backtesting.
        # Timeframe can be anything - days, minutes, etc.
        self.timeline = []

        # Store stock price corresponding to each entry in self.timeline
        # Can be open, high, low, close, etc. depending on your strategy
        self.datapoints = []

        # Keep track of prices at which stocks were brought and sold
        self.buy_trades = []
        self.sell_trades = []

        # Keep track of stoploss orders
        self.buy_stoploss_orders = []
        self.sell_stoploss_orders = []

        # For storing trade history.
        self.trade_history = []

        # Used during backtesting
        self.current_time = None
        self.current_stock_price = None
        self.current_quantity = 0

        # Read data into self.timeline and self.datapoints
        self.read_data()

    @abstractmethod
    def read_data(self):
        """
        Implement this method to read input data into 2 variables -
        1. timeline
        2. datapoints
        """

    def update_trade_history(func):
        def wrapper(self, quantity=1, stop_loss_trigger=None):
            func(self, quantity, stop_loss_trigger)
            buy_qty = len(self.buy_trades)
            sell_qty = len(self.sell_trades)
            qty = min(buy_qty, sell_qty)
            print buy_qty, sell_qty, qty, 'debug'
            if qty:
                sell_value = sum(self.sell_trades[:qty])
                buy_value = sum(self.buy_trades[:qty])
                profit = sell_value - buy_value
                print sell_value, buy_value, profit
                profit_percent = 100.0*profit/buy_value
            else:
                profit_percent = 0
            print 'Profit: %f percent' % profit_percent

            self.trade_history.append({'time': self.current_time,
                                       'stock_price': self.current_stock_price,
                                       'quantity': self.current_quantity,
                                       'profit_percent': profit_percent})

        return wrapper

    @update_trade_history
    def buy_trade(self, quantity=1, stop_loss_trigger=None):
        self.current_quantity += quantity
        self.buy_trades += [self.current_stock_price]*quantity

        if stop_loss_trigger:
            if stop_loss_trigger >= self.current_stock_price:
                raise Exception('buy_trade: Stop loss trigger should be less than current stock price')
            else:
                self.buy_stoploss_orders.append({'trigger': stop_loss_trigger, 'quantity': quantity})

        print 'Brought %d@%f' % (quantity, self.current_stock_price),

    @update_trade_history
    def sell_trade(self, quantity=1, stop_loss_trigger=None):
        self.current_quantity -= quantity
        self.sell_trades += [self.current_stock_price]*quantity

        if stop_loss_trigger:
            if stop_loss_trigger <= self.current_stock_price:
                raise Exception('sell_trade: Stop loss trigger should be greater than current stock price')
            else:
                self.sell_stoploss_orders.append({'trigger': stop_loss_trigger, 'quantity': quantity})

        print 'Sold %d@%f' % (quantity, self.current_stock_price),

    @abstractmethod
    def strategy(self):
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
        for i, datapoint in enumerate(self.datapoints):
            self.current_time = self.timeline[i]
            self.current_stock_price = datapoint

            # Exectue stoploss orders, if any
            stoploss_qty = 0
            for j, stoploss_order in reversed(list(enumerate(self.buy_stoploss_orders))):
                if self.current_stock_price <= stoploss_order['trigger']:
                    stoploss_qty += stoploss_order['quantity']
                    self.buy_stoploss_orders.pop(j)
            if stoploss_qty:
                print 'BUY Stoploss triggered. Selling %d stock(s)...' % stoploss_qty
                self.sell_trade(stoploss_qty)

            stoploss_qty = 0
            for j, stoploss_order in reversed(list(enumerate(self.sell_stoploss_orders))):
                if self.current_stock_price >= stoploss_order['trigger']:
                    stoploss_qty += stoploss_order['quantity']
                    self.sell_stoploss_orders.pop(j)
            if stoploss_qty:
                print 'SELL Stoploss triggered. Buying %d stock(s)...' % stoploss_qty
                self.buy_trade(stoploss_qty)

            # Execute strategy
            self.strategy(i, datapoint)

    def __preplot_process(self):
        # Generate full trade history i.e. also for those times when there
        # no buy or sell
        trade_history_times = [th['time'] for th in self.trade_history]
        for i, _time in enumerate(self.timeline):
            if _time not in trade_history_times:
                if i != 0:
                    self.trade_history.insert(i, self.trade_history[i-1])
                else:
                    self.trade_history.insert(0, {'time': _time,
                                       'stock_price': self.datapoints[0],
                                       'quantity': 0,
                                       'profit_percent': 0})

        # Create pandas dataframe from data
        self.df = pandas.DataFrame(self.trade_history)

        # Plotting
        f, (self.ax1, self.ax2) = plt.subplots(2, 1)

        ylim1_min = min(self.df['stock_price'])
        ylim1_max = max(self.df['stock_price'])
        ylim2_min = min(self.df['profit_percent'])
        ylim2_max = max(self.df['profit_percent'])

        # Subplots
        self.ax1.set_xlabel('Date')
        self.ax1.set_ylabel('Stock price')
        self.ax1.set_xlim([self.timeline[0], self.timeline[-1]])
        self.ax1.set_ylim([ylim1_min, ylim1_max])
#        self.ax1.grid(b=True, which='both', axis='both')

        self.ax2.set_xlabel('Date')
        self.ax2.set_ylabel('Percentage profit')
        self.ax2.set_xlim([self.timeline[0], self.timeline[-1]])
        self.ax2.set_ylim([ylim2_min, ylim2_max])
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
        self.ax1.plot(self.timeline, self.df['stock_price'], color='b')

        # Percentage profit
        self.ax2.plot(self.timeline, self.df['profit_percent'], color='b')

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
            ax1_plot, = self.ax1.plot(self.timeline[:i], self.df['stock_price'][:i], color='b')

            # Percentage profit
            if ax2_plot:
                ax2_plot.remove()
            ax2_plot, = self.ax2.plot(self.timeline[:i], self.df['profit_percent'][:i], color='b')

            plt.pause(0.01)

            if i == 0:
                time.sleep(1)

        for i in xrange(10):
            # Wait for 10 sec and then exit
            time.sleep(1)
