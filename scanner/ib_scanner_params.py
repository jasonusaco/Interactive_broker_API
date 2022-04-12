# -*- coding: utf-8 -*-
"""
IBAPI - Scanner Parameters XML

@author: Mayank Rasu (http://rasuquant.com)
"""


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import time
import threading
import os

os.chdir("D:\\Udemy\\Interactive Brokers Python API\\12_scanner")

class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self) 
    
    def scannerParameters(self, xml):
        super().scannerParameters(xml)
        open('scanner_params.xml', 'w').write(xml)
        print("ScannerParameters received.")

def websocket_con():
    app.run()
    
app = TradeApp()
app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading

con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1) # some latency added to ensure that the connection is established

app.reqScannerParameters()