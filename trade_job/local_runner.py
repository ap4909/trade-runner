from trade_run import start_trade_run

if __name__ == "__main__":
    event = {
        "minimumPoints": 3,
        "symbol": "AAPL",
        "offsetTime": 2160,
        "windowLength": 5}
    start_trade_run(event, None)
