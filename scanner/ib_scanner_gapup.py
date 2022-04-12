# -*- coding: utf-8 -*-
"""
IBAPI - Implementing scanner to find top gap up stocks

@author: Mayank Rasu (http://rasuquant.com)
"""


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.scanner import ScannerSubscription, ScanData
import time
import threading
import os

class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self) 
    
    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
        super().scannerData(reqId, rank, contractDetails, distance, benchmark, projection, legsStr)
        print("ScannerData. ReqId:", reqId, ScanData(contractDetails.contract, rank, distance, benchmark, projection, legsStr))

def usStkScan(asset_type="STK",asset_loc="STK.NASDAQ",scan_code="HIGH_OPEN_GAP"):
    scan_obj = ScannerSubscription()
    scan_obj.numberOfRows = 10
    scan_obj.instrument = asset_type
    scan_obj.locationCode = asset_loc
    scan_obj.scanCode = scan_code
    return scan_obj

def websocket_con():
    app.run()
    
app = TradeApp()
app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading

con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1) # some latency added to ensure that the connection is established

app.reqScannerSubscription(20,usStkScan(),[],[])
time.sleep(30)

app.cancelScannerSubscription(20)