from alpaca.data.historical import StockHistoricalDataClient
from src.secrets_helper import get_secret
from alpaca.trading.client import TradingClient
from src.trade_helper import (
    get_stock_data,
    get_open_positions,
    calculate_realized_pl,
    profit_loss_reached,
    get_orders,
    filter_for_order_status,
    filter_for_order_side,
    buying_condition,
    selling_condition,
    cancel_orders,
    buy_stock,
    calculate_rolling_average,
    close_positions_by_percentage,
    increment_run_count,
    get_current_run_count
)


def start_trade_run(event, context):
    secret = get_secret()

    job_parameters = event["jobParameters"]
    symbol = job_parameters["symbol"]
    offset = job_parameters["offsetTime"]
    window_length = job_parameters["windowLength"]
    take_profit = job_parameters["takeProfit"]
    stop_loss = job_parameters["stopLoss"]
    max_runs = job_parameters["maxRuns"]

    job_start_time = event["jobInfo"]

    job_status = event.get("jobStatus")
    run_count = get_current_run_count(job_status)

    # Setup Alpaca API clients
    alpaca_api_key = secret['alpaca_api_key']
    alpaca_secret_key = secret['alpaca_secret_key']

    stock_client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret_key)
    trading_client = TradingClient(alpaca_api_key, alpaca_secret_key)

    # check profit/loss limits
    all_orders = get_orders(trading_client, symbol, 'all', job_start_time)
    closed_orders = filter_for_order_status(all_orders, "closed")

    if closed_orders:
        realized_pl = calculate_realized_pl(closed_orders)
    else:
        realized_pl = 0

    position = get_open_positions(trading_client, symbol)
    if position:
        print(f"Position exists, unrealized pl {position.unrealized_pl}")
        unrealized_pl = float(position.unrealized_pl)
    else:
        print("No positions exist")
        unrealized_pl = 0

    theoretical_pl = realized_pl + unrealized_pl
    print(f"Realized profit/loss is ${realized_pl}, unrealized profit/loss is ${unrealized_pl}. Theoretical "
          f"profit/loss is ${theoretical_pl}")
    if profit_loss_reached(take_profit, stop_loss, theoretical_pl):
        close_positions_by_percentage(trading_client, symbol, "100")
        print("Profit/Loss limit reached, cancelling trade job")
        return {"cancelTradeJob": 1}

    # Evaluate buying/selling conditions
    bars = get_stock_data(stock_client, symbol, window_length, offset)
    close_rolling_average = calculate_rolling_average(bars['close'], len(bars))

    last_average = close_rolling_average.iloc[-1]
    last_price = bars["close"].iloc[-1]

    if buying_condition(last_average, last_price):
        print("Buying condition met")
        buy_stock(trading_client, symbol)
    elif selling_condition(last_average, last_price) and position:
        print("Selling conditions met")
        open_orders = filter_for_order_status(all_orders, "open")

        open_sell_orders = filter_for_order_side(open_orders, "sell")
        open_buy_orders = filter_for_order_side(open_orders, "buy")
        if not open_sell_orders:
            print("No currently existing sell orders, proceeding to make sell orders")
            cancel_orders(open_buy_orders, trading_client)
            close_positions_by_percentage(trading_client, symbol, "100")
    else:
        print("Not buying or selling...")

    # Check run count
    run_count = increment_run_count(run_count)
    if run_count >= max_runs:
        cancel_orders(open_buy_orders, trading_client)
        close_positions_by_percentage(trading_client, symbol, "100")
        print("Run limit reached, job should now be cancelled; returning trade job cancellation indicator")
        return {"cancelTradeJob": 1,
                "runCount": run_count}
    print("Run finished, returning to step function")
    return {"cancelTradeJob": 0,
            "runCount": run_count}
