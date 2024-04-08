from src.trade_run import start_trade_run

if __name__ == "__main__":
    event = {
        "minimumPoints": 3,
        "symbol": "BGC",
        "offsetTime": 3000,
        "windowLength": 5,
        "takeProfit": 10,
        "stopLoss": -10}
    start_trade_run(event, None)
