from alpaca.data.historical import StockHistoricalDataClient
from src.secrets_helper import get_secret
from alpaca.trading.client import TradingClient
from src.trade_helper import (
    get_stock_data,
    get_open_positions,
    buying_condition,
    selling_condition,
    buy_stock,
    sell_stock,
    calculate_rolling_average
)


def start_trade_run(event, context):
    secret = get_secret()

    symbol = event["symbol"]
    offset = event["offsetTime"]
    window_size = event["windowLength"]

    alpaca_api_key = secret['alpaca_api_key']
    alpaca_secret_key = secret['alpaca_secret_key']

    stock_client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret_key)
    trading_client = TradingClient(alpaca_api_key, alpaca_secret_key)

    bars = get_stock_data(stock_client, symbol, window_size, offset)
    close_rolling_average = calculate_rolling_average(bars['close'], len(bars))

    last_average = close_rolling_average.iloc[-1]
    last_price = bars["close"].iloc[-1]

    position_held = get_open_positions(trading_client, symbol)

    if buying_condition(last_average, last_price):
        print("Buying")
        buy_stock(trading_client, symbol)
    elif selling_condition(last_average, last_price) and position_held:
        print("Selling")
        sell_stock(trading_client, symbol)
    else:
        print("Not buying or selling...")
