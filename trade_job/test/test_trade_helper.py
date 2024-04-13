import unittest
from unittest.mock import create_autospec, patch, MagicMock
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.client import TradingClient
from alpaca.common.exceptions import APIError
import pandas as pd
import numpy as np
from trade_job.src.trade_helper import (
    get_stock_data,
    calculate_rolling_average,
    get_open_positions,
    take_profit_reached,
    stop_loss_reached,
    buying_condition,
    selling_condition,
    buy_stock,
    sell_stock,
    close_positions_by_percentage
)


class TestTradeHelper(unittest.TestCase):
    @patch("trade_job.src.trade_helper.TimeFrame.Minute")
    @patch("trade_job.src.trade_helper.StockBarsRequest")
    @patch("trade_job.src.trade_helper.datetime")
    def test_get_stock_data(self,
                            mock_datetime,
                            mock_stock_bars_request,
                            mock_timeframe):
        symbol = 'AAPL'
        offset = 30
        window_size = 5

        mock_datetime.datetime.now.return_value = 2
        mock_datetime.timedelta.return_value = 1
        mock_client = create_autospec(StockHistoricalDataClient)
        mock_stock_bars_request.return_value = 1

        mock_client.get_stock_bars.return_value.df = 2

        result = get_stock_data(mock_client, symbol, window_size, offset)

        self.assertEqual(result, 2)

        mock_stock_bars_request.assert_called_once_with(symbol_or_symbols=symbol,
                                                        timeframe=mock_timeframe,
                                                        start=0,
                                                        end=1)
        mock_client.get_stock_bars.assert_called_once_with(1)

    def test_calculate_rolling_average(self):
        bars = pd.Series({
                             "2024-02-09 23:58:00+00:00": "100",
                             "2024-02-09 23:59:00+00:00": "200",
                             "2024-02-10 00:03:00+00:00": "100",
                             "2024-02-10 00:08:00+00:00": "200"
                             })
        n = len(bars)

        expected = pd.Series({
                                 "2024-02-09 23:58:00+00:00": np.nan,
                                 "2024-02-09 23:59:00+00:00": np.nan,
                                 "2024-02-10 00:03:00+00:00": np.nan,
                                 "2024-02-10 00:08:00+00:00": 150
                                 })
        result = calculate_rolling_average(bars, n)
        pd.testing.assert_series_equal(result, expected)

    def test_get_open_positions_returns_true(self):
        mock_client = create_autospec(TradingClient)
        symbol = 'AAPL'

        position_held = get_open_positions(mock_client, symbol)
        self.assertTrue(position_held)
        mock_client.get_open_position.assert_called_once()

    def test_get_open_positions_returns_false(self):
        mock_client = create_autospec(TradingClient)
        mock_client.get_open_position.side_effect = APIError("error")
        symbol = 'AAPL'

        position_held = get_open_positions(mock_client, symbol)
        self.assertFalse(position_held)

    def test_take_profit_reached_true(self):
        # Test when take_profit is reached
        take_profit = 100
        unrealized_pl = 120
        self.assertTrue(take_profit_reached(take_profit, unrealized_pl))

    def test_take_profit_reached_false(self):
        # Test when take_profit is not reached
        take_profit = 100
        unrealized_pl = 80
        self.assertFalse(take_profit_reached(take_profit, unrealized_pl))

    def test_take_profit_reached_equal(self):
        # Test when unrealized_pl is equal to take_profit
        take_profit = 100
        unrealized_pl = 100
        self.assertTrue(take_profit_reached(take_profit, unrealized_pl))

    def test_take_profit_reached_negative(self):
        # Test when unrealized_pl is negative
        take_profit = 100
        unrealized_pl = -50
        self.assertFalse(take_profit_reached(take_profit, unrealized_pl))

    def test_take_profit_reached_zero(self):
        # Test when unrealized_pl is zero
        take_profit = 100
        unrealized_pl = 0
        self.assertFalse(take_profit_reached(take_profit, unrealized_pl))

    def test_stop_loss_reached_true(self):
        # Test when stop_loss is reached
        stop_loss = -100
        unrealized_pl = -120
        self.assertTrue(stop_loss_reached(stop_loss, unrealized_pl))

    def test_stop_loss_reached_false(self):
        # Test when stop_loss is not reached
        stop_loss = -100
        unrealized_pl = -80
        self.assertFalse(stop_loss_reached(stop_loss, unrealized_pl))

    def test_stop_loss_reached_equal(self):
        # Test when unrealized_pl is equal to stop_loss
        stop_loss = -100
        unrealized_pl = -100
        self.assertTrue(stop_loss_reached(stop_loss, unrealized_pl))

    def test_stop_loss_reached_positive(self):
        # Test when unrealized_pl is positive
        stop_loss = -100
        unrealized_pl = 50
        self.assertFalse(stop_loss_reached(stop_loss, unrealized_pl))

    def test_stop_loss_reached_zero(self):
        # Test when unrealized_pl is zero
        stop_loss = -100
        unrealized_pl = 0
        self.assertFalse(stop_loss_reached(stop_loss, unrealized_pl))

    def test_buying_condition_mean_price_less_last_price(self):
        assert buying_condition(50, 60) == True, "Test case failed"

    def test_buying_condition_mean_price_greater_last_price(self):
        assert buying_condition(70, 60) == False, "Test case failed"

    def test_buying_condition_mean_price_equal_last_price(self):
        assert buying_condition(50, 50) == False, "Test case failed"

    def test_selling_condition_mean_price_greater(self):
        # Test when mean price is greater than last price
        result = selling_condition(20, 10)
        self.assertTrue(result)

    def test_selling_condition_mean_price_less(self):
        # Test when mean price is less than last price
        result = selling_condition(10, 20)
        self.assertFalse(result)

    def test_selling_condition_mean_price_equal_last_price(self):
        # Test when mean price is equal to last price
        result = selling_condition(15, 15)
        self.assertFalse(result)

    def test_selling_condition_negative_prices(self):
        # Test when prices are negative
        result = selling_condition(-10, -20)
        self.assertTrue(result)

    def test_selling_condition_zero_prices(self):
        # Test when prices are zero
        result = selling_condition(0, 0)
        self.assertFalse(result)

    @patch("trade_job.src.trade_helper.TimeInForce")
    @patch("trade_job.src.trade_helper.OrderSide")
    @patch("trade_job.src.trade_helper.MarketOrderRequest", autospec=True)
    def test_buy_stock(self,
                       mock_market_order_request,
                       mock_buy,
                       mock_day):
        mock_client = create_autospec(TradingClient)
        symb = "AAPL"
        mock_market_order_request.return_value = 1

        buy_stock(mock_client, symb)

        mock_market_order_request.assert_called_once_with(
            symbol=symb,
            qty=1,
            side=mock_buy.BUY,
            time_in_force=mock_day.DAY)

        mock_client.submit_order.assert_called_once_with(order_data=1)

    @patch("trade_job.src.trade_helper.TimeInForce")
    @patch("trade_job.src.trade_helper.OrderSide")
    @patch("trade_job.src.trade_helper.MarketOrderRequest", autospec=True)
    def test_sell_stock(self,
                        mock_market_order_request,
                        mock_buy,
                        mock_day):
        mock_client = create_autospec(TradingClient)
        symb = "AAPL"
        mock_market_order_request.return_value = 1

        sell_stock(mock_client, symb)

        mock_market_order_request.assert_called_once_with(
            symbol=symb,
            qty=1,
            side=mock_buy.SELL,
            time_in_force=mock_day.DAY)

        mock_client.submit_order.assert_called_once_with(order_data=1)

    @patch("trade_job.src.trade_helper.ClosePositionRequest", autospec=True)
    def test_close_positions_by_percentage(self,
                                           mock_close_position_request):
        # Mocking trading client
        trading_client = create_autospec(TradingClient)

        # Test data
        symbol = "AAPL"
        percentage = 50

        # Calling the function
        close_positions_by_percentage(trading_client, symbol, percentage)

        # Asserting if close_position method was called with correct arguments
        trading_client.close_position.assert_called_once_with(symbol_or_asset_id=symbol, close_options=mock_close_position_request(percentage=percentage))


if __name__ == '__main__':
    unittest.main()
