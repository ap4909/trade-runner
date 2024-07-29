from alpaca.data.historical import StockHistoricalDataClient
from src.secrets_helper import get_secret
from alpaca.trading.client import TradingClient
from src.trade_helper import (
    get_stock_data,
    get_open_positions,
    calculate_realized_pnl,
    profit_loss_reached,
    get_orders,
    filter_for_closed_orders,
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

    job_status = event.get("jobStatus")
    run_count = get_current_run_count(job_status)

    # Setup Alpaca API clients
    alpaca_api_key = secret['alpaca_api_key']
    alpaca_secret_key = secret['alpaca_secret_key']

    stock_client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret_key)
    trading_client = TradingClient(alpaca_api_key, alpaca_secret_key)

    # check profit/loss limits
    all_orders = get_orders(trading_client, symbol, 'all', context['Execution']['StartTime'])
    closed_orders = filter_for_closed_orders(all_orders)
    if closed_orders:
        realized_pnl = calculate_realized_pnl(closed_orders)

    position = get_open_positions(trading_client, symbol)
    if position:
        unrealized_pnl = float(position.unrealized_pl)

    pnl = realized_pnl + unrealized_pnl

    if profit_loss_reached(take_profit, stop_loss, pnl):
        close_positions_by_percentage(trading_client, symbol, "100")
        return {"cancelTradeJob": 1}

    # Evaluate buying/selling conditions
    bars = get_stock_data(stock_client, symbol, window_length, offset)
    close_rolling_average = calculate_rolling_average(bars['close'], len(bars))

    last_average = close_rolling_average.iloc[-1]
    last_price = bars["close"].iloc[-1]

    if buying_condition(last_average, last_price):
        print("Buying")
        buy_stock(trading_client, symbol)
    elif selling_condition(last_average, last_price) and position:
        print("Selling")
        #cancel_orders(open_orders)
        close_positions_by_percentage(trading_client, symbol, "100")
    else:
        print("Not buying or selling...")

    # Check run count
    run_count = increment_run_count(run_count)
    if run_count >= max_runs:
        print("Run limit reached, job should now be cancelled; returning trade job cancellation indicator")
        return {"cancelTradeJob": 1,
                "runCount": run_count}

    return {"cancelTradeJob": 0,
            "runCount": run_count}
