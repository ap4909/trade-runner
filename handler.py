from alpaca.data.historical import StockHistoricalDataClient
from secrets_helper import get_secret
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from trade_helper import (
    get_stock_data,
    get_open_positions,
    buying_condition)


def lambda_handler(event, context):
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
        market_order_data = MarketOrderRequest(
            symbol=symb,
            qty=1,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        # Market order
        market_order = trading_client.submit_order(
            order_data=market_order_data
        )
        pos_held = True
    elif mean_price > last_price and position_held:
        print("Selling")
        market_order_data = MarketOrderRequest(
            symbol=symb,
            qty=1,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        # Market order
        market_order = trading_client.submit_order(
            order_data=market_order_data
        )
    else:
        print("Not buying or selling...")
