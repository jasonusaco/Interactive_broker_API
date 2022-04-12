from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import threading
import time


class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = {}

    def historicalData(self, req_id, bar):
        if req_id not in self.data:
            self.data[req_id] = [
                {"Date": bar.date, "Open": bar.open, "High": bar.high, "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume}]
        else:
            self.data[req_id].append(
                {"Date": bar.date, "Open": bar.open, "High": bar.high, "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume})
        print("req_id:{}, date:{}, open:{}, high:{}, low:{}, close:{}, volume:{}".format(req_id, bar.date, bar.open,
                                                                                        bar.high, bar.low, bar.close,
                                                                                        bar.volume))

    def historicalDataEnd(self, req_id, start, end):
        super().historicalDataEnd(req_id, start, end)
        print("HistoricalDataEnd. req_id:", req_id, "from", start, "to", end)
        event.set()


def us_tech_stock(symbol, sec_type="STK", currency="USD", exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract


def hist_data(req_num, contract, duration, candle_size):
    """extracts historical data"""
    app.reqHistoricalData(reqId=req_num,
                          contract=contract,
                          endDateTime='',
                          durationStr=duration,
                          barSizeSetting=candle_size,
                          whatToShow='ADJUSTED_LAST',
                          useRTH=1,
                          formatDate=1,
                          keepUpToDate=True,
                          chartOptions=[])  # EClient function to request contract details


def websocket_con():
    app.run()


app = TradeApp()
app.connect(host='127.0.0.1', port=7497,
            clientId=23)  # port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1)  # some latency added to ensure that the connection is established

event = threading.Event()

tickers = ["FB", "AMZN", "INTC"]
for ticker in tickers:
    event.clear()
    hist_data(tickers.index(ticker), us_tech_stock(ticker), '200 D', '15 mins')
    event.wait()


def dataDataframe(symbols, TradeApp_obj):
    # returns extracted historical data in dataframe format
    df_data = {}
    for symbol in symbols:
        df_data[symbol] = pd.DataFrame(TradeApp_obj.data[symbols.index(symbol)])
        df_data[symbol].set_index("Date", inplace=True)
    return df_data


# extract and store historical data in dataframe
historicalData = dataDataframe(tickers, app)
