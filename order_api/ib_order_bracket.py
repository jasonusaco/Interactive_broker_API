# -*- coding: utf-8 -*-
"""
IBAPI - Bracket Orders

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

#creating object of the bracket order class - will be used as a parameter for other function calls
def bktOrder(order_id,direction,quantity,lmt_price, sl_price, tp_price):
    parent = Order()
    parent.orderId = order_id
    parent.action = direction
    parent.orderType = "LMT"
    parent.totalQuantity = quantity
    parent.lmtPrice = lmt_price
    parent.transmit = False
    
    slOrder = Order()
    slOrder.orderId = parent.orderId + 1
    slOrder.action =  "SELL" if direction == "BUY" else "BUY"
    slOrder.orderType = "STP" 
    slOrder.totalQuantity = quantity
    slOrder.auxPrice = sl_price
    slOrder.parentId = order_id
    slOrder.transmit = False
    
    tpOrder = Order()
    tpOrder.orderId = parent.orderId + 2
    tpOrder.action = "SELL" if direction == "BUY" else "BUY"
    tpOrder.orderType = "LMT"
    tpOrder.totalQuantity = quantity
    tpOrder.lmtPrice = tp_price
    tpOrder.parentId = order_id
    tpOrder.transmit = True
    
    bracket_order = [parent, slOrder, tpOrder]
    return bracket_order


bracket = bktOrder(app.nextValidOrderId,"BUY",10,85,75,95)

for ordr in bracket:
    app.placeOrder(ordr.orderId, usStk("INTC"), ordr)
 
app.reqIds(3) #reqId api updated the nextValidOrderId class variable with the available order id
time.sleep(2) #some lag needs to be introduced

