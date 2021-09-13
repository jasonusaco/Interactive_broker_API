from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract


class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, req_id, error_code, error_string):
        print(f"Error {req_id} {error_code} {error_string}")

    def contractDetails(self, req_id, contract_details):
        print(f"redID: {req_id}, contract:{contract_details}")


app = TradingApp()
app.connect("127.0.0.1", 7497, clientId=1)

contract = Contract()
contract.symbol = "AAPL"
contract.secType = "STK"
contract.currency = "USD"
contract.exchange = "SMART"

app.reqContractDetails(100, contract)
app.run()
