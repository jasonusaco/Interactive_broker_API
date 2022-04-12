from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.execution import *
import threading
import time
import pandas as pd


class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.execution_df = pd.DataFrame(columns=['ReqId', 'PermId', 'Symbol',
                                                  'SecType', 'Currency', 'ExecId',
                                                  'Time', 'Account', 'Exchange',
                                                  'Side', 'Shares', 'Price',
                                                  'AvPrice', 'cumQty', 'OrderRef'])

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)
        # print("ExecDetails. ReqId:", reqId, "Symbol:", contract.symbol, "SecType:", contract.secType, "Currency:", contract.currency, execution)
        dictionary = {"ReqId": reqId, "PermId": execution.permId, "Symbol": contract.symbol,
                      "SecType": contract.secType, "Currency": contract.currency,
                      "ExecId": execution.execId, "Time": execution.time, "Account": execution.acctNumber,
                      "Exchange": execution.exchange,
                      "Side": execution.side, "Shares": execution.shares, "Price": execution.price,
                      "AvPrice": execution.avgPrice, "cumQty": execution.cumQty, "OrderRef": execution.orderRef}
        self.execution_df = self.execution_df.append(dictionary, ignore_index=True)


def websocket_con():
    app.run()


app = TradingApp()
app.connect("127.0.0.1", 7497, clientId=1)

# starting a separate daemon thread to execute the websocket connection
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1)  # some latency added to ensure that the connection is established

app.reqExecutions(21, ExecutionFilter())
time.sleep(1)
execution_df = app.execution_df

# extrating execution details using Execution Filter
ef = ExecutionFilter()
ef.symbol = "INTC"  # filter by symbol

app.execution_df = pd.DataFrame(columns=['ReqId', 'PermId', 'Symbol',
                                         'SecType', 'Currency', 'ExecId',
                                         'Time', 'Account', 'Exchange',
                                         'Side', 'Shares', 'Price',
                                         'AvPrice', 'cumQty',
                                         'OrderRef'])  # refresh the dataframe else new information will be appended
app.reqExecutions(21, ef)
time.sleep(1)
execution_df = app.execution_df
