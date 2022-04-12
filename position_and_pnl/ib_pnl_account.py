# -*- coding: utf-8 -*-
"""
IBAPI - Streaming account level P&L

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import time


class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self,self)
  
    def pnl(self, reqId, dailyPnL, unrealizedPnL, realizedPnL):
        super().pnl(reqId, dailyPnL, unrealizedPnL, realizedPnL)
        dictionary = {"ReqId":reqId, "DailyPnL": dailyPnL, "UnrealizedPnL": unrealizedPnL, "RealizedPnL": realizedPnL}
        print(dictionary)

    
def websocket_con():
    app.run()
    
app = TradingApp()      
app.connect("127.0.0.1", 7497, clientId=1)

# starting a separate daemon thread to execute the websocket connection
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1) # some latency added to ensure that the connection is established


app.reqPnL(5, "DU2296545", "")



