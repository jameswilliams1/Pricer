"""This module uses a live market orders feed and/or stored log file for a particular stock to output changes in the
best buy and sell price for a user defined amount of shares.
"""


class Error(Exception):
    """Base class for exceptions in this module."""
    def __call__(self, *args):
        return self.__class__(*(self.args + args))
    """Return arguments in a readable format"""
    def __str__(self):
        return ': '.join(self.args)


class OrderNotFoundError(Error):
    """Exception raised for reduce orders containing a new order_id."""


class OrderFormatError(Error):
    """Exception raised for input orders with an incorrect format."""


class OrderBook:
    def __init__(self):
        """Create a blank dictionary for each side (bid/ask), format: price:total and one for order ids,
        format: id:(timestamp, side, price)."""
        self.bids = {}
        self.asks = {}
        self.ids = {}

    def __str__(self):
        """Display stored order as timestamp, order_id, side, price."""
        return_list = []
        for order_id in self.ids.keys():
            order = self.ids[order_id]
            if order[1] == 'B':
                return_list.append(str(order[0] + ' ' + order_id + ' B ' + order[2]))
            elif order[1] == 'S':
                return_list.append(str(order[0] + ' ' + order_id + ' S ' + order[2]))
        return '\n'.join(return_list)


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
            timestamp, side, price = self.ids.get(order_id)
            self.update_total(side, price, size)
        else:
            raise OrderNotFoundError('Order does not exist', order_id)

    def new_order(self, details):
        """Determine an order type from tuple details and call the correct method."""
        timestamp = details[0]
        order_id = details[1]
        if len(details) == 5:  # Add order
            side = details[2]
            price = details[3]
            size = details[4]
            self.add_order(timestamp, order_id, side, price, size)
        elif len(details) == 3:  # Reduce order
            size = details[2]
            self.reduce_order(order_id, size)

    def lowest_buy(self, target_size):
        """Find lowest cost of buying target_size shares."""
        shares_needed = target_size
        total_cost = 0.0
        prices = sorted(self.asks.keys())
        for price in prices:
            available_shares = self.asks[price]
            if available_shares >= shares_needed:
                total_cost += shares_needed * price
                return "{:.2f}".format(total_cost)
            else:
                total_cost += available_shares * price
                shares_needed -= available_shares
        if shares_needed > 0:
            return 'NA'

    def highest_sell(self, target_size):
        """Find highest price for selling target_size shares."""
        shares_needed = target_size
        total_income = 0.0
        prices = sorted(self.bids.keys(), reverse=True)
        for price in prices:
            available_shares = self.bids[price]
            if available_shares >= shares_needed:
                total_income += shares_needed * price
                return "{:.2f}".format(total_income)
            else:
                total_income += available_shares * price
                shares_needed -= available_shares
        if shares_needed > 0:
            return 'NA'


def parse_order(order):
    """Parse order message into input for OrderBook methods."""
    parsed_order = order.split()
    timestamp = parsed_order[0]
    order_id = parsed_order[2]
    if parsed_order[1] == 'A':  # Add order
        side = parsed_order[3]
        price = float(parsed_order[4])
        size = int(parsed_order[5])
        return timestamp, order_id, side, price, size
    elif parsed_order[1] == 'R':  # Reduce order
        size = -int(parsed_order[3])
        return timestamp, order_id, size


def find_prices(order_book, input_data, target_size):
    """Print the best buy and sell prices for target_size shares with each order if prices change."""
    last_buy = 'NA'
    last_sell = 'NA'
    for line in input_data:
        order_details = parse_order(line)
        order_book.new_order(order_details)
        timestamp = order_details[0]
        if order_details[2] == 'S':  # Ask order
            this_buy = order_book.lowest_buy(target_size)
            if this_buy == last_buy:
                pass
            else:
                print timestamp, 'B', this_buy
                last_buy = this_buy
        elif order_details[2] == 'B':  # Bid order
            this_sell = order_book.highest_sell(target_size)
            if this_sell == last_sell:
                pass
            else:
                print timestamp, 'S', this_sell
                last_sell = this_sell
        elif len(order_details) == 3:  # Reduce order (cannot determine B/S without checking order_book)
            this_buy = order_book.lowest_buy(target_size)
            if this_buy == last_buy:
                pass
            else:
                print timestamp, 'B', this_buy
                last_buy = this_buy
            this_sell = order_book.highest_sell(target_size)
            if this_sell == last_sell:
                pass
            else:
                print timestamp, 'S', this_sell
                last_sell = this_sell


order_book = OrderBook()
with open('pricer.in') as f:
    find_prices(order_book, f, 1)