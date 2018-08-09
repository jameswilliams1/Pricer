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
                    return this_order[0]

        elif this_order[1] == 'A':  # Check for ADD orders
            book.append(this_order)
            return this_order[0]
    except OrderFormatError():
        'Order not formatted correctly'


def add_to_book_simple(log_file, order_book,counter_variable, output_log):
    i=0
    with open(log_file) as past_orders, open(output_log, 'w') as output:

        current_buy = 0.0
        current_sell = 0.0
        past_buy = 'NA'
        past_sell = 'NA'
        for j in past_orders:
            timestamp = process_order_simple(j, order_book, counter_variable)
            current_buy = total_buy_price(order_book, 200)
            current_sell = total_sell_price(order_book, 200)
            #print j
            if current_buy != past_buy:
                #print j
                #print timestamp, 'B ', current_buy
                past_buy = current_buy
                outputtext = str(timestamp) + ' B ' + str(current_buy) + '\n'
                output.write(outputtext)
            if current_sell != past_sell:
                #print j
                #print timestamp , 'S', current_sell
                past_sell = current_sell
                outputtext = str(timestamp) + ' S ' + str(current_sell) + '\n'
                output.write(outputtext)

            i += 1
            if i>999999999999:
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
            return "{:.2f}".format(total_cost)
        else:
            shares_needed -= available_shares
            total_cost += (available_shares * lowest_price)
            used_orders.append(current_id)

    return 'NA'


def total_sell_price(order_book, target_size):
    #  Cost to sell target_size shares
    total_sell = 0.0
    shares_needed = target_size
    available_shares = 0
    used_orders = []
    while len(order_book) > len(used_orders):
        current_id = ''
        highest_price = 0.0
        for order in order_book:
            current_id = order[2]
            current_price = float(order[4])
            order_type = order[3]
            if current_price > highest_price and current_id not in used_orders:
                if order_type == 'S':
                    used_orders.append(current_id)
                    continue
                highest_price = current_price
                available_shares = int(order[5])
        if available_shares >= shares_needed:
            total_sell += shares_needed * highest_price
            return "{:.2f}".format(total_sell)
        else:
            shares_needed -= available_shares
            total_sell += (available_shares * highest_price)
            used_orders.append(current_id)

    return 'NA'









order_book = []
counter = 0
add_to_book_simple('pricer.in', order_book, counter, "output200.txt")
