import unittest
from unittest.mock import MagicMock, patch
from trade_job.trade_run import start_trade_run


class TestTradeRun(unittest.TestCase):
    @patch("trade_job.trade_run.get_secret")
    @patch("trade_job.trade_run.StockHistoricalDataClient")
    @patch("trade_job.trade_run.TradingClient")
    @patch("trade_job.trade_run.get_stock_data")
    @patch("trade_job.trade_run.get_open_positions")
    @patch("trade_job.trade_run.buying_condition")
    @patch("trade_job.trade_run.selling_condition")
    @patch("trade_job.trade_run.buy_stock")
    @patch("trade_job.trade_run.sell_stock")
    def test_start_trade_run_with_buying_position(self,
                             mock_sell_stock,
                             mock_buy_stock,
                             mock_selling_condition,
                             mock_buying_condition,
                             mock_get_open_positions,
                             mock_get_stock_data,
                             mock_trading_client,
                             mock_stock_client,
                             mock_get_secret):
        # Mocking return values and behaviors
        event = {"symbol": "AAPL", "offset": 10}
        context = MagicMock()

        secret = {"alpaca_api_key": "fake_api_key", "alpaca_secret_key": "fake_secret_key"}
        mock_get_secret.return_value = secret

        alpaca_api_key = secret['alpaca_api_key']
        alpaca_secret_key = secret['alpaca_secret_key']

        mean_price = 100
        last_price = 110
        mock_get_stock_data.return_value = (mean_price, last_price)

        position_held = False
        mock_get_open_positions.return_value = position_held

        # Set up buying condition to be True
        mock_buying_condition.return_value = True
        mock_selling_condition.return_value = False

        # Run the function
        start_trade_run(event, context)

        # Assertions
        mock_get_secret.assert_called_once()
        mock_stock_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_trading_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_get_stock_data.assert_called_once_with(mock_stock_client.return_value, "AAPL", 10)
        mock_get_open_positions.assert_called_once_with(mock_trading_client.return_value, "AAPL")
        mock_buying_condition.assert_called_once_with(mean_price, last_price, position_held)
        mock_buy_stock.assert_called_once_with(mock_trading_client.return_value, "AAPL")
        mock_sell_stock.assert_not_called()
        mock_selling_condition.assert_not_called()


