# -*- coding: utf-8 -*-
"""
IBAPI - Order API recap

@author: Mayank Rasu (http://rasuquant.com)
"""


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time


class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId) 
        

def websocket_con():
    app.run()
    
app = TradeApp()
app.connect("127.0.0.1", 7497, clientId=20)

con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1)

#creating object of the Contract class - will be used as a parameter for other function calls
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

#creating object of the Contract class - will be used as a parameter for other function calls
def lmtOrder(direction,quantity,lmt_price):
    order = Order()
    order.action = direction
    order.orderType = "LMT"
    order.totalQuantity = quantity
    order.lmtPrice = lmt_price
    return order

app.placeOrder(app.nextValidOrderId,usStk("FB"),lmtOrder("BUY",5,311)) # EClient function to request contract details

app.reqIds(3) #reqId api updated the nextValidOrderId class variable with the available order id
time.sleep(2) #some lag needs to be introduced
app.placeOrder(app.nextValidOrderId,usStk("RIOT"),lmtOrder("BUY",10,49))
app.placeOrder(app.nextValidOrderId,usStk("INTC"),mktOrder("BUY",10))
