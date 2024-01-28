from alpaca.data.historical import StockHistoricalDataClient
from secrets_helper import get_secret
from alpaca.trading.client import TradingClient
from trade_helper import (
    set_default_values,
    get_stock_data,
    get_open_positions,
    buying_condition,
    selling_condition,
    buy_stock,
    sell_stock
)


def start_trade_run(event, context):
    secret = get_secret()

    set_default_values(event)

    symbol = event["symbol"]
    offset = event["offset"]

    alpaca_api_key = secret['alpaca_api_key']
    alpaca_secret_key = secret['alpaca_secret_key']

    stock_client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret_key)
    trading_client = TradingClient(alpaca_api_key, alpaca_secret_key)

    mean_price, last_price = get_stock_data(stock_client, symbol, offset)
    position_held = get_open_positions(trading_client, symbol)

    if buying_condition(mean_price, last_price):
        print("Buying")
        buy_stock(trading_client, symbol)
    elif selling_condition(mean_price, last_price, position_held):
        print("Selling")
        sell_stock(trading_client, symbol)
    else:
        print("Not buying or selling...")
