# -*- coding: utf-8 -*-
"""
IB API - Backtesting Open Range Breakout Strategy

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

# Import libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import threading
import time
from copy import deepcopy

tickers = ["VUZI","EXPI","ZION","MVIS","TIGR","TWST","NNOX","PACB","GNOG","FLGT","CLSK","APPS","BLSA"]


class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 
        self.data = {}
        self.skip = False
        
    def error(self, reqId, errorCode, errorString):
        print("Error {} {} {}".format(reqId,errorCode,errorString))
        self.skip = True
        print("skipping calculations")
        ticker_event.set()
        
    def historicalData(self, reqId, bar):
        if reqId not in self.data:
            self.data[reqId] = [{"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume}]
        else:
            self.data[reqId].append({"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume})
        #print("reqID:{}, date:{}, open:{}, high:{}, low:{}, close:{}, volume:{}".format(reqId,bar.date,bar.open,bar.high,bar.low,bar.close,bar.volume))
          
    def historicalDataEnd(self, reqId, start, end):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        self.skip = False
        ticker_event.set()

def usTechStk(symbol,sec_type="STK",currency="USD",exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract 

def histData(req_num,contract,endDate,duration,candle_size):
    """extracts historical data"""
    app.reqHistoricalData(reqId=req_num, 
                          contract=contract,
                          endDateTime=endDate,
                          durationStr=duration,
                          barSizeSetting=candle_size,
                          whatToShow='TRADES',
                          useRTH=1,
                          formatDate=1,
                          keepUpToDate=0,
                          chartOptions=[])	 # EClient function to request contract details

####storing trade app object in dataframe
def dataDataframe(symbols,TradeApp_obj):
    "returns extracted historical data in dataframe format"
    df_data = {}
    for symbol in symbols:
        df_data[symbol] = pd.DataFrame(TradeApp_obj.data[symbols.index(symbol)])
        df_data[symbol].set_index("Date",inplace=True)
    return df_data


def connection():
    app.run()

ticker_event = threading.Event()    
app = TradeApp()
app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=connection, daemon=True)
con_thread.start()
time.sleep(1) # some latency added to ensure that the connection is established


for ticker in tickers:
    try:
        ticker_event.clear()
        histData(tickers.index(ticker),usTechStk(ticker),'','1 M', '1 day',)
        ticker_event.wait()
    except Exception as e:
        print(e)
        print("unable to extract data for {}".format(ticker))
    
#extract and store historical data in dataframe
historicalData = dataDataframe(tickers,app)
data = deepcopy(historicalData)
for hd in data:
    data[hd]["Gap"] = ((data[hd]["Open"]/data[hd]["Close"].shift(1))-1)*100
    data[hd]["AvVol"] = data[hd]["Volume"].rolling(5).mean().shift(1)
    data[hd].dropna(inplace=True)


def topGap(data):
    top_gap_by_date = {}
    dates = data[tickers[0]].index.to_list()    
    for date in dates:
        temp = pd.Series()
        for hd in data:
            temp.loc[hd] = data[hd].loc[date,"Gap"]
        top_gap_by_date[date] = temp.sort_values(ascending=False)[:5].index.to_list()
        print("top 5 gap stocks on {}".format(date))
        print(temp.sort_values(ascending=False)[:5])
    
    return top_gap_by_date
        
    
        
top_gap_by_date = topGap(data)


def backtest(top_gap_by_date, data, app):
    date_stats = {}
    reqID = 1000
    for date in top_gap_by_date:
        date_stats[date] = {}
        for ticker in top_gap_by_date[date]:
            ticker_event.clear()
            histData(reqID,usTechStk(ticker),date+" 22:05:00",'1 D', '5 mins')
            ticker_event.wait()
            
            if app.skip == False:                
                hi_price = app.data[reqID][0]['High']
                lo_price = app.data[reqID][0]['Low']
                open_price = ''
                direction = ''
                date_stats[date][ticker] = 0
                for i in range(1,len(app.data[reqID][1:])):
                    if app.data[reqID][i-1]["Volume"] > 2*(data[ticker].loc[date,"AvVol"])/78 \
                       and app.data[reqID][i]["High"] > hi_price \
                       and open_price == '':
                        open_price = 0.8*app.data[reqID][i+1]["Open"] + 0.2*app.data[reqID][i+1]["High"] #factoring in slippage
                        direction = 'long'
                    elif app.data[reqID][i-1]["Volume"] > 2*(data[ticker].loc[date,"AvVol"])/78 \
                       and app.data[reqID][i]["Low"] < lo_price \
                       and open_price == '':
                        open_price = 0.8*app.data[reqID][i+1]["Open"] + 0.2*app.data[reqID][i+1]["Low"] #factoring in slippage
                        direction = 'short'
                        
                    if open_price != '' and direction == 'long':
                        if app.data[reqID][i]["High"] > hi_price*1.05:
                            ticker_return = ((hi_price*1.05)/open_price)-1
                            date_stats[date][ticker] = ticker_return
                            break
                        elif app.data[reqID][i]["Low"] < lo_price:
                            ticker_return = (lo_price/open_price) - 1
                            date_stats[date][ticker] = ticker_return
                            break
                        else:
                            ticker_return = (app.data[reqID][i]["Close"]/open_price) - 1
                            date_stats[date][ticker] = ticker_return
                            
                    if open_price != '' and direction == 'short':
                        if app.data[reqID][i]["Low"] < lo_price*0.95:
                            ticker_return = 1 - ((lo_price*0.95)/open_price)
                            date_stats[date][ticker] = ticker_return
                            break
                        elif app.data[reqID][i]["High"] > hi_price:
                            ticker_return = 1 - (hi_price/open_price)
                            date_stats[date][ticker] = ticker_return
                            break
                        else:
                            ticker_return = 1 - (app.data[reqID][i]["Close"]/open_price)
                            date_stats[date][ticker] = ticker_return
                            
            reqID+=1            
    return date_stats
                    
date_stats = backtest(top_gap_by_date, data, app)


###########################KPIs#####################################
def abs_return(date_stats):
    df = pd.DataFrame(date_stats).T
    df["ret"] = 1+df.mean(axis=1)
    cum_ret = (df["ret"].cumprod() - 1)[-1]
    return  cum_ret

def win_rate(date_stats):
    win_count = 0
    lose_count = 0
    for i in date_stats:
        for ret in date_stats[i]:
            if date_stats[i][ret] > 0:
                win_count+=1
            elif date_stats[i][ret] < 0:
                lose_count+=1
    return (win_count/(win_count+lose_count))*100

def mean_ret_winner(date_stats):
    win_ret = []
    for i in date_stats:
        for ret in date_stats[i]:
            if date_stats[i][ret] > 0:
                win_ret.append(date_stats[i][ret])                
    return sum(win_ret)/len(win_ret)

def mean_ret_loser(date_stats):
    los_ret = []
    for i in date_stats:
        for ret in date_stats[i]:
            if date_stats[i][ret] < 0:
                los_ret.append(date_stats[i][ret])                
    return sum(los_ret)/len(los_ret)


print("**********Strategy Performance Statistics**********")
print("total cumulative return = {}".format(round(abs_return(date_stats),4)))
print("total win rate = {}".format(round(win_rate(date_stats),2)))
print("mean return per win trade = {}".format(round(mean_ret_winner(date_stats),4)))
print("mean return per loss trade = {}".format(round(mean_ret_loser(date_stats),4)))