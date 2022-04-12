# -*- coding: utf-8 -*-
"""
IB API - Opening Range Breakout strategy implementation

@author: Mayank Rasu (http://rasuquant.com/)
"""


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.execution import *
import pandas as pd
import time
import threading

ib_acct = "DU2296545" #update the ib account (different from real account and paper account)
tickers = ["CALT","CNTY","CYBE","RAIN"] #pick tickers with highest gap up or gap down
pos_size = 3000
profit_limit = 1000
loss_limit = -500

class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.pos_df = pd.DataFrame(columns=['Account', 'Symbol', 'SecType', 'Currency', 'Position', 'Avg cost'])
        self.order_df = pd.DataFrame(columns=['PermId', 'ClientId', 'OrderId',
                                  'Account', 'Symbol', 'SecType',
                                  'Exchange', 'Action', 'OrderType',
                                  'TotalQty', 'CashQty', 'LmtPrice',
                                  'AuxPrice', 'Status'])
        self.execution_df = pd.DataFrame(columns=['ReqId', 'PermId', 'Symbol',
                                          'SecType', 'Currency', 'ExecId',
                                          'Time', 'Account', 'Exchange',
                                          'Side', 'Shares', 'Price',
                                          'AvPrice', 'cumQty', 'OrderRef'])    
        self.hist_data = {}    
        self.last_price = {}
        self.hi_price = {}
        self.lo_price = {}
        self.pos_pnl = {}
        self.contract_id = {}
        self.av_volume = {}

##### wrapper function for reqMktData. this function handles streaming market data  (last current price)
    def tickPrice(self, reqId, tickType, price, attrib):    
        super().tickPrice(reqId, tickType, price, attrib)
        #print("TickPrice. TickerId:", reqId, "tickType:", tickType, "Price:", price)
        if tickType == 4:
            self.last_price[reqId] = price
                     
 ####  wrapper function for reqIds. this function manages the Order ID.
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)

#####   wrapper function for reqContractDetails. this function gives the contract ID for a given contract to be used in requesting PnL.
    def contractDetails(self, reqId, contractDetails):
        string = str(contractDetails.contract).split(",")
        if string[1] not in self.contract_id:
            self.contract_id[string[1]] = string[0]

#####   wrapper function for reqHistoricalData. this function gives the candle historical data
    def historicalData(self, reqId, bar):
        if reqId not in self.hist_data:
            self.hist_data[reqId] = [{"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume}]
        else:
            self.hist_data[reqId].append({"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume})
        print("reqID:{}, date:{}, open:{}, high:{}, low:{}, close:{}, volume:{}".format(reqId,bar.date,bar.open,bar.high,bar.low,bar.close,bar.volume))

#####   wrapper function for reqHistoricalData. this function triggers when historical data extraction is completed      
    def historicalDataEnd(self, reqId, start, end):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        ticker_event.set()
        if reqId == len(tickers) - 1:
            hist_event.clear()

#####   wrapper function for reqPositions.   this function gives the current positions
    def position(self, account, contract, position, avgCost):
            super().position(account, contract, position, avgCost)
            dictionary = {"Account":account, "Symbol": contract.symbol, "SecType": contract.secType,
                          "Currency": contract.currency, "Position": position, "Avg cost": avgCost}
            if self.pos_df["Symbol"].str.contains(contract.symbol).any():
                self.pos_df.loc[self.pos_df["Symbol"]==contract.symbol,"Position"]= dictionary["Position"]
                self.pos_df.loc[self.pos_df["Symbol"]==contract.symbol,"Avg cost"]= dictionary["Avg cost"]
            else:
                self.pos_df = self.pos_df.append(dictionary, ignore_index=True)

#####   wrapper function for reqExecutions.   this function gives the executed orders                
    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)
        #print("ExecDetails. ReqId:", reqId, "Symbol:", contract.symbol, "SecType:", contract.secType, "Currency:", contract.currency, execution)
        dictionary = {"ReqId":reqId, "PermId":execution.permId, "Symbol":contract.symbol, "SecType":contract.secType, "Currency":contract.currency, 
                      "ExecId":execution.execId, "Time":execution.time, "Account":execution.acctNumber, "Exchange":execution.exchange,
                      "Side":execution.side, "Shares":execution.shares, "Price":execution.price,
                      "AvPrice":execution.avgPrice, "cumQty":execution.cumQty, "OrderRef":execution.orderRef}
        self.execution_df = self.execution_df.append(dictionary, ignore_index=True)
                
#####   this function is operated when the function reqPnLSingle is called. this function gives the p&L of each Ticker
    def pnlSingle(self, reqId, pos, dailyPnL, unrealizedPnL, realizedPnL, value):
        super().pnlSingle(reqId, pos, dailyPnL, unrealizedPnL, realizedPnL, value)
        self.pos_pnl[reqId] = dailyPnL           

#### wrapper function for reqOpenOrders. this function gives the open orders
    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        dictionary = {"PermId":order.permId, "ClientId": order.clientId, "OrderId": orderId, 
                      "Account": order.account, "Symbol": contract.symbol, "SecType": contract.secType,
                      "Exchange": contract.exchange, "Action": order.action, "OrderType": order.orderType,
                      "TotalQty": order.totalQuantity, "CashQty": order.cashQty, 
                      "LmtPrice": order.lmtPrice, "AuxPrice": order.auxPrice, "Status": orderState.status}
        self.order_df = self.order_df.append(dictionary, ignore_index=True)
        
    def inExec(self,ticker):
        if len(self.execution_df[self.execution_df["Symbol"]==ticker]) == 0:
            return 0
        else:
            return -1 
        
    def tickerAllOpenOrders(self,ticker):
        return len(self.order_df[self.order_df["Symbol"]==ticker])
        
        
####  this function declares the properties of the instrument. 
def usStk(symbol,sec_type="STK",currency="USD",exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract

####  this function declare market orders type. 
def marketOrder(direction,quantity):
    order = Order()
    order.action = direction
    order.orderType = "MKT"
    order.totalQuantity = quantity
    return order

####  this function declare BracketOrder orders type. 
def BracketOrder(parentOrderId, action, quantity, takeProfitLimitPrice, stopLossPrice):
    parent = Order()
    parent.orderId = parentOrderId
    parent.action = action
    parent.orderType = "MKT"
    parent.totalQuantity = quantity
    parent.transmit = False

    takeProfit = Order()
    takeProfit.orderId = parent.orderId + 1
    takeProfit.action = "SELL" if action == "BUY" else "BUY"
    takeProfit.orderType = "LMT"
    takeProfit.totalQuantity = quantity
    takeProfit.lmtPrice = takeProfitLimitPrice
    takeProfit.parentId = parentOrderId
    takeProfit.transmit = False

    stopLoss = Order()
    stopLoss.orderId = parent.orderId + 2
    stopLoss.action = "SELL" if action == "BUY" else "BUY"
    stopLoss.orderType = "STP"
    stopLoss.auxPrice = stopLossPrice
    stopLoss.totalQuantity = quantity
    stopLoss.parentId = parentOrderId
    stopLoss.transmit = True

    bracketOrder = [parent, takeProfit, stopLoss]
    return bracketOrder 

####  this function starts the streaming data of current ticker.
def streamSnapshotData(req_num,contract):
    """stream tick leve data"""
    app.reqMktData(reqId=req_num, 
                   contract=contract,
                   genericTickList="",
                   snapshot=False,
                   regulatorySnapshot=False,
                   mktDataOptions=[])

####  this function refreshes the order dataframe				   
def OrderRefresh(app):
    app.order_df = pd.DataFrame(columns=['PermId', 'ClientId', 'OrderId',
                                      'Account', 'Symbol', 'SecType',
                                      'Exchange', 'Action', 'OrderType',
                                      'TotalQty', 'CashQty', 'LmtPrice',
                                      'AuxPrice', 'Status'])
    app.reqOpenOrders()
    time.sleep(2)


def execRefresh(app):
    app.execution_df = pd.DataFrame(columns=['ReqId', 'PermId', 'Symbol',
                                      'SecType', 'Currency', 'ExecId',
                                      'Time', 'Account', 'Exchange',
                                      'Side', 'Shares', 'Price',
                                      'AvPrice', 'cumQty', 'OrderRef'])  
    app.reqExecutions(21, ExecutionFilter())
    time.sleep(2)
    
def kill_switch(app):
        print("Kill Switch Activated!! Total day Pnl = {}".format(sum(app.pos_pnl.values())))
        app.reqGlobalCancel()
        app.reqIds(-1)
        time.sleep(2)
        order_id = app.nextValidOrderId
        pos_df = app.pos_df
        for ticker in pos_df["Symbol"]:
            quantity = pos_df[pos_df["Symbol"]==ticker]["Position"].values[0]
            if quantity > 0:
                app.placeOrder(order_id,usStk(ticker),marketOrder("SELL",quantity)) # EClient function to request contract details
            if quantity < 0:
                app.placeOrder(order_id,usStk(ticker),marketOrder("BUY",abs(quantity))) 
            order_id+=1
        print("Program Shutting Down!!")
        #exit()

def fetchHistorical(app):
    starttime = time.time()
    first_pass = True
    while not kill_event.is_set():
        hist_event.set()
        app.hist_data = {}
        for ticker in tickers:
            ticker_event.clear()
            app.reqHistoricalData(reqId=tickers.index(ticker), 
                                  contract=usStk(ticker),
                                  endDateTime='',
                                  durationStr="5 D" if first_pass else "1 D",
                                  barSizeSetting="15 mins" if first_pass else "5 mins",
                                  whatToShow='ADJUSTED_LAST',
                                  useRTH=1,
                                  formatDate=1,
                                  keepUpToDate=0,
                                  chartOptions=[])
            ticker_event.wait()
            if first_pass:
                tot_vol = sum([candle["Volume"] for candle in app.hist_data[tickers.index(ticker)]])
                num = len([candle["Volume"] for candle in app.hist_data[tickers.index(ticker)]])
                app.av_volume[ticker] = int(tot_vol/(num*3))
                app.hi_price[ticker] = app.hist_data[tickers.index(ticker)][-1]["High"]
                app.lo_price[ticker] = app.hist_data[tickers.index(ticker)][-1]["Low"]
        first_pass = False
        time.sleep(300 - ((time.time() - starttime) % 300.0))    

        
def openRangeBrkout(app):
    while not kill_event.is_set():
        for ticker in tickers:
            OrderRefresh(app)
            execRefresh(app)
            current_tot_pnl = sum(app.pos_pnl.values())
            [hour , minute] = time.strftime("%H %M").split() #getting local system time
            print ("local time - hour {} minute {} ".format(hour,minute))
            
            if current_tot_pnl > profit_limit or current_tot_pnl < loss_limit or ((int(hour) >= 22 and int(minute) > 30)):
                kill_event.set()
                kill_switch(app)
                continue
         
            if app.inExec(ticker) == 0 and app.tickerAllOpenOrders(ticker) == 0 and not hist_event.is_set():
                last_volume = app.hist_data[tickers.index(ticker)][-1]["Volume"]
                if 2*app.av_volume[ticker] < last_volume:
                    if app.last_price[tickers.index(ticker)] > app.hi_price[ticker]:
                        quantity = int(pos_size/app.last_price[tickers.index(ticker)])
                        tp_price = round(app.last_price[tickers.index(ticker)]*1.05,2)
                        sl_price = app.lo_price[ticker]
                        
                        app.reqIds(-1)
                        time.sleep(2)
                        order_id = app.nextValidOrderId
                        bracket = BracketOrder(order_id,"BUY",quantity,tp_price,sl_price)
                        for o in bracket:
                            app.placeOrder(o.orderId, usStk(ticker), o)
                            
                            
                    if app.last_price[tickers.index(ticker)] < app.lo_price[ticker]:
                        quantity = int(pos_size/app.last_price[tickers.index(ticker)])
                        tp_price = round(app.last_price[tickers.index(ticker)]*0.95,2)
                        sl_price = app.hi_price[ticker]
                        
                        app.reqIds(-1)
                        time.sleep(2)
                        order_id = app.nextValidOrderId
                        bracket = BracketOrder(order_id,"SELL",quantity,tp_price,sl_price)
                        for o in bracket:
                            app.placeOrder(o.orderId, usStk(ticker), o)
                            
        time.sleep(15)
    
##### function to establish the websocket connection to TWS
def connection():
    app.run()

app = TradeApp()
app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading

ConThread = threading.Thread(target=connection)
ConThread.start()

kill_event = threading.Event()
ticker_event = threading.Event()
hist_event = threading.Event()

for ticker in tickers:
    app.reqContractDetails(tickers.index(ticker),usStk(ticker))
    time.sleep(2)
    streamSnapshotData(tickers.index(ticker),usStk(ticker))
    time.sleep(2)
    app.reqPnLSingle(tickers.index(ticker), ib_acct, "", app.contract_id[ticker])
    time.sleep(2)

app.reqPositions()
time.sleep(1)
    
histdataTread = threading.Thread(target = fetchHistorical, args=(app,))
histdataTread.start()
    
startegyThread = threading.Thread(target = openRangeBrkout, args =(app,))
startegyThread.start()


