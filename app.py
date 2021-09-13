from ibapi.client import EClient
from ibapi.wrapper import EWrapper


class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, req_id, error_code, error_string):
        print(f"Error {req_id} {error_code} {error_string}")


app = TradingApp()
app.connect("127.0.0.1", 7497, clientId=1)
app.run()
