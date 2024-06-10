from src.trade_run import start_trade_run

if __name__ == "__main__":
    event = {"symbol": "AAPL",
             "offsetTime": 2800,
             "windowLength": 5,
             "minimumPoints": 3,
             "takeProfit": 1000,
             "stopLoss": -2000,
             "maxRuns": 1}
    start_trade_run(event, None)
