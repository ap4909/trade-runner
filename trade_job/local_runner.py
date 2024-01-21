from trade_run import start_trade_run

if __name__ == "__main__":
    event = {"symb": "AAPL",
             "offset": "2586"}
    start_trade_run(event, None)
