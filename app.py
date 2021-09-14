from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time


class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, req_id, error_code, error_string):
        print(f"Error {req_id} {error_code} {error_string}")

    def contractDetails(self, req_id, contract_details):
        print(f"redID: {req_id}, contract:{contract_details}")


def websocket_con():
    app.run()
    event.wait()
    if event.is_set():
        app.close()


event = threading.Event()
app = TradingApp()
app.connect("127.0.0.1", 7497, clientId=1)

# starting a separate daemon thread to execute the websocket connection
con_thread = threading.Thread(target=websocket_con)
con_thread.start()
# some latency added to ensure that the connection is established
time.sleep(1)

# creating object of the Contract class - will be used as a parameter for other function calls
contract = Contract()
contract.symbol = "AAPL"
contract.secType = "STK"
contract.currency = "USD"
contract.exchange = "SMART"


# EClient function to request contract details
app.reqContractDetails(100, contract)
# some latency added to ensure that the contract details request has been processed
time.sleep(5)
event.set()
