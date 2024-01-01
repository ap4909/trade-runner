from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest
from alpaca.common.exceptions import APIError
import datetime


def get_stock_data(client, symb):
    today = datetime.datetime.now() - datetime.timedelta(days=3.1)

    request_params = StockBarsRequest(
        symbol_or_symbols=symb,
        timeframe=TimeFrame.Minute,
        start=today
    )

    bars = client.get_stock_bars(request_params)

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
