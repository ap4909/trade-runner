import unittest
from unittest.mock import MagicMock, patch
from trade_job.trade_run import start_trade_run


class TestTradeRun(unittest.TestCase):
    @patch()
    @patch('trade_job.trade_run.get_stock_data')
    @patch('trade_job.trade_run.TradingClient')
    @patch('trade_job.trade_run.StockHistoricalDataClient')
    @patch('trade_job.trade_run.get_secret')
    def test_start_trade_run_buying_condition(self,
                                              mock_get_secret,
                                              mock_stock_historical_client,
                                              mock_trading_client,
                                              mock_get_stock_data):
        mock_get_secret.return_value = {"alpaca_api_key": "test_api_key", "alpaca_secret_key": "test_secret_key"}
        mock_get_stock_data.return_value = [100, 200]

        # Mock event and context
        event = {"symbol": "AAPL", "offset": 10}
        context = MagicMock()

        # Mock open position
        position_held = False
        trading_client = MagicMock()
        trading_client.get_open_positions = MagicMock(return_value=position_held)

        # Test buying condition
        buying_condition = MagicMock(return_value=True)
        selling_condition = MagicMock(return_value=False)

        # Run the function
        start_trade_run(event, context)

        # Assertions
        buying_condition.assert_called_once_with(mean_price, last_price, position_held)
        buy_stock.assert_called_once_with(trading_client, "AAPL")
        selling_condition.assert_not_called()
        sell_stock.assert_not_called()

    # Add more tests for other scenarios...
