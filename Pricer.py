"""This module uses a live market orders feed and/or stored log file for a particular stock to output changes in the
best buy and sell price for a user defined amount of shares.
"""
import numpy as np
import pandas as pd
import timeit


class Error(Exception):
    """Base class for exceptions in this module."""
    def __call__(self, *args):
        return self.__class__(*(self.args + args))
    """Return arguments in a readable format"""
    def __str__(self):
        return ': '.join(self.args)


class OrderNotFoundError(Error):
    """Exception raised for errors in reduce orders."""


class OrderBook:
    def __init__(self):
        """Create a blank dictionary for each side (bid/ask), format: price:total and one for order ids,
        format: id:(price, side)."""
        self.bids = {}
        self.asks = {}
        self.ids = {}

    def update_total(self, side, price, size):
        """Add (/subtract if negative) size to total if price already exists, else create new price total."""
        if side == 'B':
            if price in self.bids:
                self.bids[price] += size
            else:
                self.bids[price] = size
        if side == 'S':
            if price in self.asks:
                self.asks[price] += size
            else:
                self.asks[price] = size

    def add_order(self, timestamp, order_id, side, price, size):
        """Add a new order to the ids dictionary so it can later be removed and update total, id must be unique."""
        self.ids[order_id] = (timestamp, side, price)
        self.update_total(side, price, size)

    def reduce_order(self, order_id, size):
        """Find order_id and side in ids then remove size shares from total in bids/asks."""
        if order_id in self.ids:
            price, side = self.ids.get(order_id)
            self.update_total(side, price, size)
        else:
            raise OrderNotFoundError('Order does not exist', order_id)

    def new_order(self, *args):
        """Determine an order type and call the correct method"""
        timestamp = args[0]
        order_id = args[1]
        if len(args) == 5:  # Add order
            side = args[2]
            price = args[3]
            size = args[4]
            self.add_order(timestamp, order_id, side, price, size)
        elif len(args) == 3:  # Reduce order
            size = args[2]
            self.reduce_order(order_id, size)


def parse_order(order):
    """Parse order message into input for OrderBook methods"""
    parsed_order = order.split()
    timestamp = parsed_order[0]
    order_id = parsed_order[2]
    if parsed_order[1] == 'A':
        side = parsed_order[3]
        price = parsed_order[4]
        size = parsed_order[5]
        return timestamp, order_id, side, price, size
    elif parsed_order[1] == 'R':
        size = parsed_order[3]
        return timestamp, order_id, size

