import numpy as np
import pandas as pd
from timeit import Timer


class OrderFormatError(Exception):
    pass


def process_order(line, book):

    try:
        this_order = line.split()
        if this_order[1] == 'R': # Check for REDUCE orders
            for order in book: #Iterate existing order book
                if order[2] == this_order[2]: # Find ID match
                    previous_size = int(order[5])
                    reduction = int(this_order[3])
                    new_size = previous_size - reduction
                    if new_size <= 0:
                        book.remove(order)
                    order[5] = str(new_size)

        elif this_order[1] == 'A':# Check for ADD orders
            book.append(this_order)
    except OrderFormatError():
        'Order not formatted correctly'


# Existing log file
order_book = []
global i
i = 0
with open('pricer.in') as past_orders:
    for j in past_orders:
        #np.append(order_book, parse_order(line, order_book))
        process_order(j, order_book)
        i += 1
        if i > 10:
            break
for i in order_book:
    print i