from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest
from alpaca.common.exceptions import APIError
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import datetime


def get_stock_data(client, symbol, window_length_mins, offset):
    window_end = datetime.datetime.now() - datetime.timedelta(minutes=offset)
    window_length = datetime.timedelta(minutes=window_length_mins)
    window_start = window_end - window_length

    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Minute,
        start=window_start
    )
    try:
        bars = client.get_stock_bars(request_params)
    except AttributeError:
        print("Error getting stock bars, data may not be available")
        raise
    return bars.df


def calculate_rolling_average(bars_data, n):
    return bars_data.rolling(n).mean()


def get_open_positions(trading_client, symb):
    try:
        trading_client.get_open_position(symb)
        return True
    except APIError as e:
        print(f"Error during open position retrieval, potentially no open positions, message: {e}")
        return False
    except Exception as e:
        print(f"Error during open position retrieval, message: {e}")
        raise


def buying_condition(mean_price, last_price):
    if mean_price < last_price:
        return True
    else:
        return False


def selling_condition(mean_price, last_price):
    if mean_price > last_price:
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
