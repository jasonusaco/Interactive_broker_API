# -*- coding: utf-8 -*-
"""
IBAPI - Streaming position level P&L

@author: Mayank Rasu (http://rasuquant.com)
"""


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time


class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self,self)
        self.contract_id = 0
   
    def pnlSingle(self, reqId, pos, dailyPnL, unrealizedPnL, realizedPnL, value):
        super().pnlSingle(reqId, pos, dailyPnL, unrealizedPnL, realizedPnL, value)
        print("PnL for contract ID {} = {}".format(app.contract_id,dailyPnL))
        
    def contractDetails(self, reqId, contractDetails):
        self.contract_id = int(str(contractDetails.contract).split(",")[0])


contract = Contract()
contract.symbol = "INTC"
contract.secType = "STK"
contract.currency = "USD"
contract.exchange = "ISLAND"

    
def websocket_con():
    app.run()
    
app = TradingApp()      
app.connect("127.0.0.1", 7497, clientId=1)

# starting a separate daemon thread to execute the websocket connection
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1) # some latency added to ensure that the connection is established


app.reqContractDetails(100, contract)
time.sleep(2)

app.reqPnLSingle(2, "DU123456", "", app.contract_id) #update the account ID
time.sleep(2)



