import unittest
from unittest.mock import MagicMock, patch
from trade_job.src.trade_run import start_trade_run
from trade_job.test.data import payload
from trade_job.test.data.test_variables import (
    stock_data_df,
    rolling_average_values
)
import pandas.testing as pd_testing


@patch("trade_job.src.trade_run.get_secret")
@patch("trade_job.src.trade_run.StockHistoricalDataClient")
@patch("trade_job.src.trade_run.TradingClient")
@patch("trade_job.src.trade_run.get_stock_data")
@patch("trade_job.src.trade_run.calculate_rolling_average")
@patch("trade_job.src.trade_run.get_open_positions")
@patch("trade_job.src.trade_run.buying_condition")
@patch("trade_job.src.trade_run.selling_condition")
@patch("trade_job.src.trade_run.buy_stock")
@patch("trade_job.src.trade_run.sell_stock")
class TestTradeRun(unittest.TestCase):
    def test_start_trade_run_with_buying_condition(self,
                                                   mock_sell_stock,
                                                   mock_buy_stock,
                                                   mock_selling_condition,
                                                   mock_buying_condition,
                                                   mock_get_open_positions,
                                                   mock_calculate_rolling_average,
                                                   mock_get_stock_data,
                                                   mock_trading_client,
                                                   mock_stock_client,
                                                   mock_get_secret):
        # Mocking return values and behaviors
        context = MagicMock()

        secret = {"alpaca_api_key": "fake_api_key", "alpaca_secret_key": "fake_secret_key"}
        mock_get_secret.return_value = secret

        alpaca_api_key = secret['alpaca_api_key']
        alpaca_secret_key = secret['alpaca_secret_key']

        last_average = rolling_average_values.iloc[-1]
        last_price = stock_data_df['close'].iloc[-1]

        mock_get_stock_data.return_value = stock_data_df

        mock_calculate_rolling_average.return_value = rolling_average_values

        position_held = False
        mock_get_open_positions.return_value = position_held

        # Set up buying condition to be True
        mock_buying_condition.return_value = True
        mock_selling_condition.return_value = False

        # Run the function
        start_trade_run(payload.event, context)

        # Assertions
        mock_get_secret.assert_called_once()
        mock_stock_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_trading_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_get_stock_data.assert_called_once_with(mock_stock_client.return_value, 'AAPL', 5, 16)
        pd_testing.assert_series_equal(mock_calculate_rolling_average.call_args[0][0], stock_data_df['close'])
        self.assertEqual(mock_calculate_rolling_average.call_args[0][1], len(stock_data_df))
        mock_calculate_rolling_average.assert_called_once_with(stock_data_df['close'], len(stock_data_df))
        mock_get_open_positions.assert_called_once_with(mock_trading_client.return_value, 'AAPL')
        mock_buying_condition.assert_called_once_with(last_average, last_price)

        mock_buy_stock.assert_called_once_with(mock_trading_client.return_value, 'AAPL')
        mock_sell_stock.assert_not_called()
        mock_selling_condition.assert_not_called()

    def test_start_trade_run_with_selling_price_position_held(self,
                                                              mock_sell_stock,
                                                              mock_buy_stock,
                                                              mock_selling_condition,
                                                              mock_buying_condition,
                                                              mock_get_open_positions,
                                                              mock_calculate_rolling_average,
                                                              mock_get_stock_data,
                                                              mock_trading_client,
                                                              mock_stock_client,
                                                              mock_get_secret):
        # Mocking return values and behaviors
        context = MagicMock()

        secret = {"alpaca_api_key": "fake_api_key", "alpaca_secret_key": "fake_secret_key"}
        mock_get_secret.return_value = secret

        alpaca_api_key = secret['alpaca_api_key']
        alpaca_secret_key = secret['alpaca_secret_key']

        last_average = rolling_average_values.iloc[-1]
        last_price = stock_data_df['close'].iloc[-1]

        mock_get_stock_data.return_value = stock_data_df

        mock_calculate_rolling_average.return_value = rolling_average_values

        position_held = True
        mock_get_open_positions.return_value = position_held

        # Set up selling condition to be true
        mock_buying_condition.return_value = False
        mock_selling_condition.return_value = True

        # Run the function
        start_trade_run(payload.event, context)

        # Assertions
        mock_get_secret.assert_called_once()
        mock_stock_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_trading_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_get_stock_data.assert_called_once_with(mock_stock_client.return_value, 'AAPL', 5, 16)
        pd_testing.assert_series_equal(mock_calculate_rolling_average.call_args[0][0], stock_data_df['close'])
        self.assertEqual(mock_calculate_rolling_average.call_args[0][1], len(stock_data_df))
        mock_calculate_rolling_average.assert_called_once_with(stock_data_df['close'], len(stock_data_df))
        mock_get_open_positions.assert_called_once_with(mock_trading_client.return_value, 'AAPL')
        mock_buying_condition.assert_called_once_with(last_average, last_price)

        mock_sell_stock.assert_called_once_with(mock_trading_client.return_value, "AAPL")
        mock_buy_stock.assert_not_called()
        mock_buying_condition.assert_called_once_with(last_average, last_price)

    def test_start_trade_run_with_selling_price_no_position(self,
                                                            mock_sell_stock,
                                                            mock_buy_stock,
                                                            mock_selling_condition,
                                                            mock_buying_condition,
                                                            mock_get_open_positions,
                                                            mock_calculate_rolling_average,
                                                            mock_get_stock_data,
                                                            mock_trading_client,
                                                            mock_stock_client,
                                                            mock_get_secret):
        # Mocking return values and behaviors
        context = MagicMock()

        secret = {"alpaca_api_key": "fake_api_key", "alpaca_secret_key": "fake_secret_key"}
        mock_get_secret.return_value = secret

        alpaca_api_key = secret['alpaca_api_key']
        alpaca_secret_key = secret['alpaca_secret_key']

        last_average = rolling_average_values.iloc[-1]
        last_price = stock_data_df['close'].iloc[-1]

        mock_get_stock_data.return_value = stock_data_df

        mock_calculate_rolling_average.return_value = rolling_average_values

        position_held = False
        mock_get_open_positions.return_value = position_held

        # Set up buying condition to be True
        mock_buying_condition.return_value = False
        mock_selling_condition.return_value = False

        # Run the function
        start_trade_run(payload.event, context)

        # Assertions
        mock_get_secret.assert_called_once()
        mock_stock_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_trading_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_get_stock_data.assert_called_once_with(mock_stock_client.return_value, 'AAPL', 5, 16)
        pd_testing.assert_series_equal(mock_calculate_rolling_average.call_args[0][0], stock_data_df['close'])
        self.assertEqual(mock_calculate_rolling_average.call_args[0][1], len(stock_data_df))
        mock_calculate_rolling_average.assert_called_once_with(stock_data_df['close'], len(stock_data_df))
        mock_get_open_positions.assert_called_once_with(mock_trading_client.return_value, 'AAPL')
        mock_buying_condition.assert_called_once_with(last_average, last_price)

        mock_sell_stock.assert_not_called()
        mock_buy_stock.assert_not_called()
        mock_buying_condition.assert_called_once_with(last_average, last_price)


if __name__ == '__main__':
    unittest.main()
