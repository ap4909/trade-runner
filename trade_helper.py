from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest
from alpaca.common.exceptions import APIError
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import datetime


def get_stock_data(client, symb):
    today = datetime.datetime.now() - datetime.timedelta(minutes=20)

    request_params = StockBarsRequest(
        symbol_or_symbols=symb,
        timeframe=TimeFrame.Minute,
        start=today
    )
    try:
        bars = client.get_stock_bars(request_params)
    except AttributeError:
        print("Error getting stock bars, data may not be available")
        raise

    close_data = bars.df["close"]
    mean_price = close_data.mean()
    last_price = close_data.iloc[-1]
    return mean_price, last_price


def get_open_positions(trading_client, symb):
    try:
        trading_client.get_open_position(symb)
        return True
    except APIError as e:
        print(f"Error during open position retrieval, message: {e}")
        return False


def buying_condition(mean_price, last_price, pos_held):
    if mean_price < last_price and not pos_held:
        return True
    else:
        return False


def selling_condition(mean_price, last_price, pos_held):
    if mean_price > last_price and pos_held:
        return True
    else:
        return False


def buy_stock(trading_client, symb):
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


def sell_stock(trading_client, symb):
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
