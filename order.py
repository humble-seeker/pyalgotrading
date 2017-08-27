# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 21:31:37 2017

@author: pdagade
"""

import uuid


class Order:
    def __init__(self, type, entry_price, quantity, entry_time,
                 stop_loss_trigger=None, target_trigger=None):
        if type == 'buy' or type == 'sell':
            self.type = type
        else:
            raise Exception('Type has to be either buy or sell')
        self.entry_price = entry_price
        self.quantity = quantity
        self.entry_time = entry_time
        self.stop_loss_trigger = stop_loss_trigger
        self.target_trigger = target_trigger

        self.id = uuid.uuid4()      # unique random ids
        self.exit_time = None
        self.exit_price = None
        self.profit = None
        self.profit_percent = None
        self.position = 'open'

    def close(self, stock_price, time):
        """
        Call this methood to close this order.
        """
        self.exit_price = stock_price
        self.exit_time = time
        self.position = 'close'
        self.calculate_profit()
        print '[ID: %s] %sing %d@%f. Profit booked: %f %%' \
              % (self. id,self.type, self.quantity,
                 self.exit_price, self.profit_percent)


class BuyOrder(Order):
    def __init__(self, entry_price, quantity, entry_time,
                 stop_loss_trigger=None, target_trigger=None):
        if stop_loss_trigger and stop_loss_trigger >= entry_price:
            raise Exception('Stop loss trigger for buy order should be <= entry_price')
        if target_trigger and target_trigger <= entry_price:
            raise Exception('Stop loss trigger for buy order should be >= entry_price')

        Order.__init__(self, 'buy', entry_price, quantity, entry_time,
                       stop_loss_trigger, target_trigger)

    def calculate_profit(self):
        """
        Calculate profit after order is closed
        """
        if self.position == 'close':
            self.profit = (self.exit_price - self.entry_price)*self.quantity
            self.profit_percent = (100.0*self.profit/self.quantity)/self.entry_price
        else:
            print 'WARNING: Calling calculate_profit for open order!'

    def try_to_close(self, candle_high, candle_low, time):
        """
        Check if an open order can be closed for given stock_price depending on
        stop_loss_tigger or target_trigger
        """
        if self.position == 'open':
            if self.stop_loss_trigger >= candle_low:
                print '[ID: %s] Stop loss trigger executed at candle_low %f. Closing...' % (self.id, candle_low)
                self.close(candle_low, time)
                return True
            elif self.target_trigger <= candle_high:
                print '[ID: %s] Target price trigger executed at candle_high %f. Closing...' % (self.id, candle_high)
                self.close(candle_high, time)
                return True
            else:
                return False
        else:
            print 'Warning: Trying to close an Order which is already closed'
            return False


class SellOrder(Order):
    def __init__(self, entry_price, quantity, entry_time,
                 stop_loss_trigger=None, target_trigger=None):
        if stop_loss_trigger and stop_loss_trigger <= entry_price:
            raise Exception('Stop loss trigger for sell order should be >= entry_price')
        if target_trigger and target_trigger >= entry_price:
            raise Exception('target trigger for sell order should be <= entry_price')
        Order.__init__(self, 'sell', entry_price, quantity, entry_time,
                       stop_loss_trigger, target_trigger)

    def calculate_profit(self):
        """
        Calculate profit after order is closed
        """
        if self.position == 'close':
            self.profit = (self.entry_price - self.exit_price)*self.quantity
            self.profit_percent = (100.0*self.profit/self.quantity)/self.entry_price
        else:
            print 'WARNING: Calling calculate_profit for open order!'

    def try_to_close(self, candle_high, candle_low, time):
        """
        Check if an open order can be closed for given stock_price depending on
        stop_loss_tigger or target_trigger
        """
        if self.position == 'open':
            if self.stop_loss_trigger <= candle_high:
                print '[ID: %s] Stop loss trigger executed at candle_high %f. Closing...' % (self.id, candle_high)
                self.close(candle_high, time)
                return True
            elif self.target_trigger >= candle_low:
                print '[ID: %s] Target price trigger executed at candle_low %f. Closing...' % (self.id, candle_low)
                self.close(candle_low, time)
                return True
        else:
            print 'Warning: Trying to close an Order which is already closed'
            return False
