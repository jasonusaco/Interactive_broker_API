# -*- coding: utf-8 -*-
"""
IBAPI - Fetching and refreshing positions - updated code

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time
import pandas as pd


class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self,self)
        self.pos_df = pd.DataFrame(columns=['Account', 'Symbol', 'SecType',
                                            'Currency', 'Position', 'Avg cost'])
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId) 
        
    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)
        dictionary = {"Account":account, "Symbol": contract.symbol, "SecType": contract.secType,
                      "Currency": contract.currency, "Position": position, "Avg cost": avgCost}
        if self.pos_df["Symbol"].str.contains(contract.symbol).any():
            self.pos_df.loc[self.pos_df["Symbol"]==contract.symbol,"Position"] = position
            self.pos_df.loc[self.pos_df["Symbol"]==contract.symbol,"Avg cost"] = avgCost
        else:
            self.pos_df = self.pos_df.append(dictionary, ignore_index=True)
        

def websocket_con():
    app.run()
    
app = TradingApp()      
app.connect("127.0.0.1", 7497, clientId=1)

# starting a separate daemon thread to execute the websocket connection
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1) # some latency added to ensure that the connection is established

def usStk(symbol, sectype ="STK", currency = "USD", exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sectype
    contract.currency = currency
    contract.exchange = exchange
    return contract

#creating object of the Contract class - will be used as a parameter for other function calls
def mktOrder(direction,quantity):
    order = Order()
    order.action = direction
    order.orderType = "MKT"
    order.totalQuantity = quantity
    return order

app.reqPositions()
time.sleep(1)
pos_df = app.pos_df

app.placeOrder(app.nextValidOrderId,usStk("CSCO"),mktOrder("SELL",5))

app.reqPositions()
time.sleep(1)
pos_df = app.pos_df
