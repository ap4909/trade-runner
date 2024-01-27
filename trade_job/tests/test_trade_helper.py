import unittest
from unittest.mock import create_autospec, patch, MagicMock
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.client import TradingClient
from alpaca.common.exceptions import APIError
from trade_job.trade_helper import (
    get_stock_data,
    get_open_positions,
    buying_condition,
    selling_condition,
    buy_stock,
    sell_stock
)


class TestTradeHelper(unittest.TestCase):
    @patch("trade_job.trade_helper.TimeFrame.Minute")
    @patch("trade_job.trade_helper.StockBarsRequest")
    @patch("trade_job.trade_helper.datetime")
    def test_get_stock_data(self,
                            mock_datetime,
                            mock_stock_bars_request,
                            mock_timeframe):
        symbol = 'AAPL'
        offset = 30

        mock_datetime.datetime.now.return_value = 2
        mock_datetime.timedelta.return_value = 1
        mock_client = create_autospec(StockHistoricalDataClient)
        mock_stock_bars_request.return_value = 1

        # Mocking the mean value
        mock_client.get_stock_bars.return_value.df.__getitem__.return_value.mean.return_value = 1
        # Mocking the last DF value, as returned by iloc
        mock_client.get_stock_bars.return_value.df.__getitem__.return_value.iloc.__getitem__.return_value = 2

        mean_price, last_price = get_stock_data(mock_client, symbol, offset)

        self.assertEqual(mean_price, 1)
        self.assertEqual(last_price, 2)
        mock_stock_bars_request.assert_called_once_with(symbol_or_symbols=symbol,
                                                        timeframe=mock_timeframe,
                                                        start=1)
        mock_client.get_stock_bars.assert_called_once_with(1)

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

    def test_buying_condition_mean_price_less_last_price(self):
        assert buying_condition(50, 60, False) == True, "Test case failed"

    def test_buying_condition_mean_price_greater_last_price(self):
        assert buying_condition(70, 60, False) == False, "Test case failed"

    def test_buying_condition_mean_price_less_last_price_position_held(self):
        assert buying_condition(50, 40, True) == False, "Test case failed"

    def test_buying_condition_mean_price_equal_last_price(self):
        assert buying_condition(50, 50, False) == False, "Test case failed"

    def test_buying_condition_mean_price_less_last_price_position_held(self):
        assert buying_condition(40, 50, True) == False, "Test case failed"

    def test_mean_price_greater_last_price_position_held(self):
        assert selling_condition(70, 60, True) == True, "Test case failed"

    def test_mean_price_less_last_price(self):
        assert selling_condition(50, 60, False) == False, "Test case failed"

    def test_mean_price_greater_last_price_position_not_held(self):
        assert selling_condition(70, 60, False) == False, "Test case failed"

    def test_mean_price_equal_last_price_position_held(self):
        assert selling_condition(60, 60, True) == False, "Test case failed"

    def test_mean_price_greater_last_price_position_held(self):
        assert selling_condition(80, 60, True) == True, "Test case failed"

    @patch("trade_job.trade_helper.TimeInForce")
    @patch("trade_job.trade_helper.OrderSide")
    @patch("trade_job.trade_helper.MarketOrderRequest", autospec=True)
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

    @patch("trade_job.trade_helper.TimeInForce")
    @patch("trade_job.trade_helper.OrderSide")
    @patch("trade_job.trade_helper.MarketOrderRequest", autospec=True)
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
