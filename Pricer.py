import numpy as np
import pandas as pd
import timeit


class OrderFormatError(Exception):
    pass


def process_order_simple(line, book, counter_variable):

    try:
        this_order = line.split()
        if this_order[1] == 'R':  # Check for REDUCE orders
            for order in book:  # Iterate existing order book
                if order[2] == this_order[2]: # Find ID match
                    previous_size = int(order[5])
                    reduction = int(this_order[3])
                    new_size = previous_size - reduction
                    if new_size == 0:
                        book.remove(order)
                    order[5] = str(new_size)

        elif this_order[1] == 'A':  # Check for ADD orders
            book.append(this_order)
    except OrderFormatError():
        'Order not formatted correctly'


def add_to_book_simple(log_file, order_book,counter_variable):
    i=0
    with open(log_file) as past_orders:
        current = 0.0
        past = 'NA'
        for j in past_orders:
            process_order_simple(j, order_book, counter_variable)
            current = total_buy_price(order_book, 200)
            if current != past:
                print j
                print current
                past = current

            i += 1
            if i>50:
                break


def total_buy_price(order_book, target_size):
    #  Cost to buy target_size shares
    total_cost = 0.0
    shares_needed = target_size
    available_shares = 0
    used_orders = []
    while len(order_book) > len(used_orders):
        current_id = ''
        lowest_price = float('inf')
        for order in order_book:
            current_id = order[2]
            current_price = float(order[4])
            order_type = order[3]
            if current_price < lowest_price and current_id not in used_orders:
                if order_type == 'B':
                    used_orders.append(current_id)
                    continue
                lowest_price = current_price
                available_shares = int(order[5])
        if available_shares >= shares_needed:
            total_cost += shares_needed * lowest_price
            return total_cost
        else:
            shares_needed -= available_shares
            total_cost += (available_shares * lowest_price)
            used_orders.append(current_id)

    return 'NA'









order_book = []
counter = 0
add_to_book_simple('pricer.in', order_book, counter)
for i in order_book:
    print i