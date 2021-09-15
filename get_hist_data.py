# Import libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import threading
import time
import logging


class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = {}

    def historica_data(self, req_id, bar):
        if req_id not in self.data:
            self.data[req_id] = [
                {"Date": bar.date, "Open": bar.open, "High": bar.high,
                 "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume}]
        else:
            self.data[req_id].append(
                {"Date": bar.date, "Open": bar.open, "High": bar.high,
                 "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume})
        print(f"reqID:{req_id}, "
              f"date:{bar.date}, "
              f"open:{bar.open}, "
              f"high:{bar.high}, "
              f"low:{bar.low}, "
              f"close:{bar.close}, "
              f"volume:{bar.volume}")


def websocket_con():
    app.run()


app = TradeApp()
app.connect("127.0.0.1", 7497, clientId=1)

# starting a separate daemon thread to execute the websocket connection
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
# some latency added to ensure that the connection is established
time.sleep(1)


# creating object of the Contract class -
# will be used as a parameter for other function calls
def general_stk(symbol, currency, exchange, sec_type="STK"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract


def hist_data(req_num, contract, duration, candle_size):
    # EClient function to request contract details
    app.reqHistoricalData(reqId=req_num,
                          contract=contract,
                          endDateTime='',
                          durationStr=duration,
                          barSizeSetting=candle_size,
                          whatToShow='ADJUSTED_LAST',
                          useRTH=1,
                          formatDate=1,
                          keepUpToDate=False,
                          chartOptions=[])


tickers_data = {"INTC": {"index": 0, "currency": "USD", "exchange": "ISLAND"},
                "BARC": {"index": 1, "currency": "GBP", "exchange": "LSE"},
                "INFY": {"index": 2, "currency": "INR", "exchange": "NSE"}}

for ticker in tickers_data:
    hist_data(tickers_data[ticker]["index"],
              general_stk(ticker, tickers_data[ticker]["currency"],
              tickers_data[ticker]["exchange"]), '1 M', '5 mins')

    # some latency added to ensure that
    # the contract details request has been processed
    time.sleep(5)


# storing trade app object in dataframe
def data_frame(ticker_data, trade_app_obj):
    "returns extracted historical data in dataframe format"
    df_data = {}
    for symbol in ticker_data:
        try:
            df_data[symbol] = pd.DataFrame(
                trade_app_obj.data[ticker_data[symbol]["index"]])
            df_data[symbol].set_index("Date", inplace=True)
        except Exception as e:
            logging.exception(e)
            print(f"error encountered for {symbol} data....skipping")
    return df_data


# extract and store historical data in dataframe
historical_data = data_frame(tickers_data, app)
