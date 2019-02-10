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
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
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


fvList = {"BOND": [None,None], "VALE": [None,None], "VALBZ": [None,None], "GS": [None,None], "MS": [None,None], "WFC": [None,None], "XLF": [None,None]}

def trade(exchange, buysell, symbol, price, size):
        # order_id = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
        trade = {'type': 'add', 'order_id': random.randint(1,100), 'symbol': symbol,
                 'dir': buysell, 'price': price, 'size': size}
        print(trade)
        write_to_exchange(exchange, trade)
        # time.sleep(0.01)

def trade_batch(exchange, trades):
        # TODO check conflicts
        for buysell, symbol, price, size in trades:
            print(trades)
            print("***^***")
            if buysell and size != 0:
                trade(exchange, buysell, symbol, price, size)

def TradeBond(exchange):
    data = read_from_exchange(exchange)
    trades = []
    if data['type'] == 'book' and data['symbol'] == 'BOND':
        bids = data['buy']
        for price, size in bids:
            if price > 999:
                trades.append(('SELL', 'BOND', price, size))

        asks = data['sell']
        for price, size in asks:
            if price < 1001:
                trades.append(('BUY', 'BOND', price, size))
    return trades

def updateValues(data, symb):
    buys = data['buy']
    sells = data['sell']

    if(len(buys) > 0):
        mean_buy = sum([int(price) for price, size in buys]) / len(buys)
        if(fvList[symb][0] == None):
            fvList[symb][0] = mean_buy
        else:
            fvList[symb][0] = (fvList[symb][0] + mean_buy)/2
    if(len(sells) > 0):

        mean_sell = sum([int(price) for price, size in sells])/ len(sells)
        if(fvList[symb][1] == None):
            fvList[symb][1] = mean_sell
        else:
            fvList[symb][1] = (fvList[symb][1] + mean_sell)/2

def FairValuetrade(exchange):
    """Given the data in the book, decides whether we should make a trade.
    Returns a list of trades (buy/sell, symbol, price, size).
    """
    data = read_from_exchange(exchange)
    trades = []
    if(data['type'] != 'book'):
        return trades
    symb = data['symbol']
    fv = fvList[symb]

    updateValues(data, symb)
    if(fv[0] == None or fv[1] == None):
        return trades

    fv = fvList[symb]
    fv = sum(fv)/2
    diff = fv / 200

    print(symb)




    for entry in data['buy']:
        if(int(entry[0]) > fv + diff):
            trades.append(['SELL', symb, entry[0], entry[1]])
            print("wahoo")
    for entry in data['sell']:
        if(int(entry[0]) < fv - diff):
            trades.append(['BUY', symb, entry[0], entry[1]])
            print("yapoo")
    print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
    print(trades)
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    return trades

def buyNormalStocks(exchange):
    data = read_from_exchange(exchange)
    sym = data['symbol']
    trades = []
    if data['type'] == 'book' and data['symbol'] == 'GS' or data['symbol'] == 'MS':
        bids = data['buy']

        for price, size in bids:
            if price > fvList[sym][0]:
                trades.append(('SELL', sym, price, size))

        asks = data['sell']
        for price, size in asks:
            if price < fvList[sym][0]:
                trades.append(('BUY', sym, price, size))
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
        trades.extend(TradeBond(exchange))
        trades.extend(buyNormalStocks(exchange))
        trades.extend(FairValuetrade(exchange))
        trade_batch(exchange,trades)
        data = read_from_exchange(exchange)
        print(fvList)
        # trades = []
        print(data)


        # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)

if __name__ == "__main__":
    main()