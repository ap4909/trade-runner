from alpaca.data.historical import StockHistoricalDataClient
from secrets_helper import get_secret
from alpaca.trading.client import TradingClient
from trade_helper import (
    get_stock_data,
    get_open_positions,
    buying_condition,
    selling_condition,
    buy_stock,
    sell_stock
)


def start_trade_run(event, context):
    secret = get_secret()
    symb = event["symb"]

    alpaca_api_key = secret['alpaca_api_key']
    alpaca_secret_key = secret['alpaca_secret_key']

    stock_client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret_key)
    trading_client = TradingClient(alpaca_api_key, alpaca_secret_key)

    mean_price, last_price = get_stock_data(stock_client, symb)
    position_held = get_open_positions(trading_client, symb)

    if buying_condition(mean_price, last_price, position_held):
        print("Buying")
        buy_stock(trading_client, symb)
    elif selling_condition(mean_price, last_price, position_held):
        print("Selling")
        sell_stock(trading_client, symb)
    else:
        print("Not buying or selling...")
