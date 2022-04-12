from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time

tickers = ["AMZN", "FB", "INTC"]


class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.lastPrice = {}
        
    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        #print("TickPrice. TickerId:", reqId, "tickType:", tickType, "Price:", price)
        self.lastPrice[reqId] = price

def usTechStk(symbol,sec_type="STK",currency="USD",exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract 

def streamSnapshotData(tickers):
    """stream tick leve data"""
    for ticker in tickers:
        app.reqMktData(reqId=tickers.index(ticker), 
                       contract=usTechStk(ticker),
                       genericTickList="",
                       snapshot=False,
                       regulatorySnapshot=False,
                       mktDataOptions=[])
        time.sleep(1)
    
def last_price(ticker):
    return app.lastPrice[tickers.index(ticker)]
    
def connection():
    app.run()

app = TradeApp()
app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading

ConThread = threading.Thread(target=connection)
ConThread.start()

streamThread = threading.Thread(target=streamSnapshotData, args=(tickers,))
streamThread.start()
time.sleep(3) #some lag added to ensure that streaming has started
