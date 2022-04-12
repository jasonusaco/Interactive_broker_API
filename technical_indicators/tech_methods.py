"""
Implement MACD, ATR, BB, ADX, Stoch, RSI
"""

# Import libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import threading
import time
import numpy as np


class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = {}

    def historicalData(self, req_id, bar):
        if req_id not in self.data:
            self.data[req_id] = [
                {"Date": bar.date, "Open": bar.open, "High": bar.high,
                 "Low": bar.low, "Close": bar.close, "Volume": bar.volume}]
        else:
            self.data[req_id].append(
                {"Date": bar.date, "Open": bar.open, "High": bar.high,
                 "Low": bar.low, "Close": bar.close, "Volume": bar.volume})
        print(f"req_id:{req_id}, date:{bar.date}, open:{bar.open}, "
              f"high:{bar.high}, low:{bar.low}, close:{bar.close}, "
              f"volume:{bar.volume}")


def us_tech_stock(symbol, sec_type="STK", currency="USD", exchange="ISLAND"):
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


def websocket_con():
    app.run()


app = TradeApp()
# port 4002 for ib gateway paper trading/7497 for TWS paper trading
app.connect(host='127.0.0.1', port=7497, clientId=23)
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
# some latency added to ensure that the connection is established
time.sleep(1)

tickers = ["FB", "AMZN", "INTC"]
for ticker in tickers:
    hist_data(tickers.index(ticker), us_tech_stock(ticker), '2 D', '5 mins')
    time.sleep(5)


# storing trade app object in dataframe
def data_dataframe(symbols, TradeApp_obj):
    # returns extracted historical data in dataframe format
    df_data = {}
    for symbol in symbols:
        df_data[symbol] = pd.DataFrame(
            TradeApp_obj.data[symbols.index(symbol)])
        df_data[symbol].set_index("Date", inplace=True)
    return df_data


class TechMethod:
    @staticmethod
    def macd(DF, a=12, b=26, c=9):
        """function to calculate MACD
           typical values a(fast moving average) = 12;
                          b(slow moving average) =26;
                          c(signal line ma window) =9"""
        df = DF.copy()
        df["MA_Fast"] = df["Close"].ewm(span=a, min_periods=a).mean()
        df["MA_Slow"] = df["Close"].ewm(span=b, min_periods=b).mean()
        df["MACD"] = df["MA_Fast"] - df["MA_Slow"]
        df["Signal"] = df["MACD"].ewm(span=c, min_periods=c).mean()
        df.dropna(inplace=True)
        return df

    @staticmethod
    def boll_bnd(DF, n=20):
        # function to calculate Bollinger Band
        # ddof=0 is required since we want to take
        # the standard deviation of the population and not sample
        df = DF.copy()
        df["MA"] = df['Close'].ewm(span=n, min_periods=n).mean()
        df["BB_up"] = df["MA"] + 2 * df['Close'].rolling(n).std(
            ddof=0)
        df["BB_dn"] = df["MA"] - 2 * df['Close'].rolling(n).std(
            ddof=0)
        df["BB_width"] = df["BB_up"] - df["BB_dn"]
        df.dropna(inplace=True)
        return df

    @staticmethod
    def atr(DF, n):
        # function to calculate True Range and Average True Range
        df = DF.copy()
        df['H-L'] = abs(df['High'] - df['Low'])
        df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
        df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
        df['ATR'] = df['TR'].ewm(com=n, min_periods=n).mean()
        return df['ATR']

    @staticmethod
    def rsi(DF, n=20):
        # function to calculate RSI
        df = DF.copy()
        df['delta'] = df['Close'] - df['Close'].shift(1)
        df['gain'] = np.where(df['delta'] >= 0, df['delta'], 0)
        df['loss'] = np.where(df['delta'] < 0, abs(df['delta']), 0)
        avg_gain = []
        avg_loss = []
        gain = df['gain'].tolist()
        loss = df['loss'].tolist()
        for i in range(len(df)):
            if i < n:
                avg_gain.append(np.NaN)
                avg_loss.append(np.NaN)
            elif i == n:
                avg_gain.append(df['gain'].rolling(n).mean()[n])
                avg_loss.append(df['loss'].rolling(n).mean()[n])
            elif i > n:
                avg_gain.append(((n - 1) * avg_gain[i - 1] + gain[i]) / n)
                avg_loss.append(((n - 1) * avg_loss[i - 1] + loss[i]) / n)
        df['avg_gain'] = np.array(avg_gain)
        df['avg_loss'] = np.array(avg_loss)
        df['RS'] = df['avg_gain'] / df['avg_loss']
        df['RSI'] = 100 - (100 / (1 + df['RS']))
        return df['RSI']

    @staticmethod
    def adx(DF, n=20):
        # function to calculate ADX
        df2 = DF.copy()
        df2['H-L'] = abs(df2['High'] - df2['Low'])
        df2['H-PC'] = abs(df2['High'] - df2['Close'].shift(1))
        df2['L-PC'] = abs(df2['Low'] - df2['Close'].shift(1))
        df2['TR'] = df2[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
        df2['+DM'] = np.where((df2['High'] - df2['High'].shift(1)) > (
                df2['Low'].shift(1) - df2['Low']),
                              df2['High'] - df2['High'].shift(1), 0)
        df2['+DM'] = np.where(df2['+DM'] < 0, 0, df2['+DM'])
        df2['-DM'] = np.where((df2['Low'].shift(1) - df2['Low']) > (
                df2['High'] - df2['High'].shift(1)),
                              df2['Low'].shift(1) - df2['Low'], 0)
        df2['-DM'] = np.where(df2['-DM'] < 0, 0, df2['-DM'])

        df2["+DMMA"] = df2['+DM'].ewm(span=n, min_periods=n).mean()
        df2["-DMMA"] = df2['-DM'].ewm(span=n, min_periods=n).mean()
        df2["TRMA"] = df2['TR'].ewm(span=n, min_periods=n).mean()

        df2["+DI"] = 100 * (df2["+DMMA"] / df2["TRMA"])
        df2["-DI"] = 100 * (df2["-DMMA"] / df2["TRMA"])
        df2["DX"] = 100 * (abs(df2["+DI"] - df2["-DI"]) /
                           (df2["+DI"] + df2["-DI"]))

        df2["ADX"] = df2["DX"].ewm(span=n, min_periods=n).mean()

        return df2['ADX']

    @staticmethod
    def stoch_oscltr(DF, a=20, b=3):
        """function to calculate Stochastics
           a = lookback period
           b = moving average window for %D"""
        df = DF.copy()
        df['C-L'] = df['Close'] - df['Low'].rolling(a).min()
        df['H-L'] = df['High'].rolling(a).max() - df['Low'].rolling(a).min()
        df['%K'] = df['C-L'] / df['H-L'] * 100
        df['%D'] = df['%K'].ewm(span=b, min_periods=b).mean()
        return df[['%K', '%D']]


# extract and store historical data in dataframe
historicalData = data_dataframe(tickers, app)

tech = TechMethod()
# calculate and store bollBnd values
TI_dict = {}
for ticker in tickers:
    TI_dict[ticker] = tech.boll_bnd(historicalData[ticker], 20)

# calculate and store MACD values
macdDF = {}
for ticker in tickers:
    macdDF[ticker] = tech.macd(historicalData[ticker], 12, 26, 9)

# calculate and store ATR values
TI_dict = {}
for ticker in tickers:
    TI_dict[ticker] = tech.atr(historicalData[ticker], 20)

# calculate and store RSI values
TI_dict = {}
for ticker in tickers:
    TI_dict[ticker] = tech.rsi(historicalData[ticker], 20)

# calculate and store ADX values
TI_dict = {}
for ticker in tickers:
    TI_dict[ticker] = tech.adx(historicalData[ticker], 20)

# calculate and store Stochastic Oscillator values
TI_dict = {}
for ticker in tickers:
    TI_dict[ticker] = tech.stoch_oscltr(historicalData[ticker], 20, 3)
