from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time


class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, req_id, error_code, error_string):
        print(f"Error {req_id} {error_code} {error_string}")

    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)


def websocket_con():
    app.run()


app = TradingApp()
app.connect("127.0.0.1", 7497, clientId=1)

# starting a separate daemon thread to execute the websocket connection
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
# some latency added to ensure that the connection is established
time.sleep(1)


# creating object of the Contract class
# will be used as a parameter for other function calls
def us_tech_stock(symbol, sec_type="STK", currency="USD", exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract


# creating object of the limit order class
# will be used as a parameter for other function calls
def limit_order(direction, quantity, lmt_price):
    order = Order()
    order.action = direction
    order.orderType = "LMT"
    order.totalQuantity = quantity
    order.lmtPrice = lmt_price
    return order


def market_order(direction, quantity):
    order = Order()
    order.action = direction
    order.orderType = "MKT"
    order.totalQuantity = quantity
    return order


def stop_order(direction, quantity, st_price):
    order = Order()
    order.action = direction
    order.orderType = "STP"
    order.totalQuantity = quantity
    order.auxPrice = st_price
    return order


def trail_stop_order(direction, quantity, st_price, tr_step=1):
    order = Order()
    order.action = direction
    order.orderType = "TRAIL"
    order.totalQuantity = quantity
    order.auxPrice = tr_step
    order.trailStopPrice = st_price
    return order


order_id = app.nextValidOrderId
app.placeOrder(order_id, us_tech_stock("FB"), market_order("BUY", 1))
time.sleep(5)

app.reqIds(-1)
time.sleep(2)
order_id = app.nextValidOrderId
app.placeOrder(order_id, us_tech_stock("FB"), stop_order("SELL", 1, 200))
time.sleep(5)

app.reqIds(-1)
time.sleep(2)
order_id = app.nextValidOrderId
# EClient function to request contract details
app.placeOrder(order_id,
               us_tech_stock("TSLA"),
               trail_stop_order("BUY", 1, 1400, 2))
# some latency added to ensure
# that the contract details request has been processed
time.sleep(5)
