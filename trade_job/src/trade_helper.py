from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest
from alpaca.common.exceptions import APIError
from alpaca.trading.requests import MarketOrderRequest, ClosePositionRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import datetime
from constants import MAX_RETRIES


def get_current_run_count(job_status):
    if job_status:
        run_count = job_status.get("runCount")
    else:
        run_count = 0
    return run_count


def get_stock_data(client, symbol, window_length_mins, offset):
    window_end = datetime.datetime.now() - datetime.timedelta(minutes=offset)
    window_length = datetime.timedelta(minutes=window_length_mins)
    window_start = window_end - window_length

    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Minute,
        start=window_start,
        end=window_end
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
        position = trading_client.get_open_position(symb)
        return position
    except APIError as e:
        print(f"Error during open position retrieval, potentially no open positions, message: {e}")
        return False
    except Exception as e:
        print(f"Error during open position retrieval, message: {e}")
        raise


def get_open_orders(trading_client, symbol):
    print("Getting open orders")
    attempts = 0
    request_params = GetOrdersRequest(
        status="Open",
        symbol=symbol
    )
    while attempts < MAX_RETRIES:
        try:
            orders = trading_client.get_orders(request_params)
            return orders
        except Exception as e:
            print(f"Error during open order retrieval, message: {e}. Retrying...")
            attempts += 1
            if attempts == MAX_RETRIES:
                raise Exception(f"Error during open order retrieval: all {MAX_RETRIES} attempts failed") from e


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


def profit_loss_reached(take_profit, stop_loss, unrealized_pl):
    if unrealized_pl >= take_profit:
        print("Profit has reached take-profit limit")
        return True
    elif unrealized_pl <= stop_loss:
        print("Loss has reached stop-loss limit")
        return True
    else:
        return False


def close_positions_by_percentage(trading_client, symbol, percentage):
    close_position_request = ClosePositionRequest(
        percentage=percentage
    )
    try:
        close_response = trading_client.close_position(
            symbol_or_asset_id=symbol,
            close_options=close_position_request
        )
    except Exception as e:
        print(f"Error when closing position, message: {e}")
        raise


def increment_run_count(count):
    count += 1
    return count
