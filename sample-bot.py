#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
import datetime
import time
import random

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="gettingthingsdone"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = False

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=2500 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

order_id = 1
position = {"alex" : 1}
last_data = None

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

# def read_from_exchange(exchange):
#     data = json.loads(exchange.readline())
#     last_data = data
#     return data

def read_from_exchange(e):
    data = e.readline()
    if (data == None):
        return None
    else:
        data = json.loads(data)
        last_data = data
        return data
#
def getData(exchange):
    return last_data


# ~~~~~============== MAIN LOOP ==============~~~~~




def trade(exchange, buysell, symbol, price, size):
        # order_id = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
        trade = {'type': 'add', 'order_id': random.randint(1,100), 'symbol': symbol,
                 'dir': buysell, 'price': price, 'size': size}
        print(trade)
        write_to_exchange(exchange, trade)

def trade_batch(exchange, trades):
        # TODO check conflicts
        for buysell, symbol, price, size in trades:
            if buysell and size != 0:
                trade(exchange, buysell, symbol, price, size)

def Bondtrade(exchange):
    data = read_from_exchange(exchange)
    trades = []
    if data['type'] == 'book' and data['symbol'] == 'BOND':
        bids = data['buy']
        for price, size in bids:
            if price > 1000:
                trades.append(('SELL', 'BOND', price, size))

        asks = data['sell']
        for price, size in asks:
            if price < 1000:
                trades.append(('BUY', 'BOND', price, size))
    return trades

# def createPosition(output):
#     for symbol in output['symbols']:
#         currentPosition[symbol['symbol']]= symbol['position']
#         currentSellOrders[symbol['symbol']] = symbol['position']
#         currentBuyOrders[symbol['symbol']] = symbol['position']


def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    data = read_from_exchange(exchange)

    trades = []

    while data:
        trades.extend(Bondtrade(exchange))
        trade_batch(exchange,trades)
        data = read_from_exchange(exchange)
        # print(data)
        print(trades)

        # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)

if __name__ == "__main__":
    main()
