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
@patch("trade_job.src.trade_run.profit_loss_reached")
@patch("trade_job.src.trade_run.buying_condition")
@patch("trade_job.src.trade_run.selling_condition")
@patch("trade_job.src.trade_run.buy_stock")
@patch("trade_job.src.trade_run.sell_stock")
@patch("trade_job.src.trade_run.increment_run_count")
class TestTradeRun(unittest.TestCase):
    def test_start_trade_run_with_buying_condition(self,
                                                   mock_increment_run_count,
                                                   mock_sell_stock,
                                                   mock_buy_stock,
                                                   mock_selling_condition,
                                                   mock_buying_condition,
                                                   mock_profit_loss_reached,
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

        position = MagicMock()
        position.unrealized_pl = 1
        mock_get_open_positions.return_value = position

        mock_profit_loss_reached.return_value = False

        # Set up buying condition to be True
        mock_buying_condition.return_value = True
        mock_selling_condition.return_value = False

        mock_increment_run_count.return_value = 1

        # Run the function
        trade_run_result = start_trade_run(payload.event, context)

        # Test get secret
        mock_get_secret.assert_called_once()

        # Test setup stock clients
        mock_stock_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_trading_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)

        # Test check open positions for PnL
        mock_get_open_positions.assert_called_once_with(mock_trading_client.return_value, 'AAPL')
        mock_profit_loss_reached.assert_called_once_with(10, -10, 1)

        # Test evaluate buy/sell conditions
        mock_get_stock_data.assert_called_once_with(mock_stock_client.return_value, 'AAPL', 5, 16)
        pd_testing.assert_series_equal(mock_calculate_rolling_average.call_args[0][0], stock_data_df['close']) # checking calculate_rolling_average called with close prices in stock data df
        self.assertEqual(mock_calculate_rolling_average.call_args[0][1], len(stock_data_df))
        mock_calculate_rolling_average.assert_called_once_with(stock_data_df['close'], len(stock_data_df))

        mock_buying_condition.assert_called_once_with(last_average, last_price)
        mock_buy_stock.assert_called_once_with(mock_trading_client.return_value, 'AAPL')
        mock_sell_stock.assert_not_called()
        mock_selling_condition.assert_not_called()

        # Test check/update run count
        mock_increment_run_count.assert_called_once_with(1)
        mock_increment_run_count.return_value = 3

        # Test trade run result correct
        self.assertEqual(trade_run_result, {
            "cancelTradeJob": 0,
            "runCount": 1
            })


    def test_start_trade_run_with_selling_price_position_held(self,
                                                              mock_increment_run_count,
                                                              mock_sell_stock,
                                                              mock_buy_stock,
                                                              mock_selling_condition,
                                                              mock_buying_condition,
                                                              mock_profit_loss_reached,
                                                              mock_get_open_positions,
                                                              mock_calculate_rolling_average,
                                                              mock_get_stock_data,
                                                              mock_trading_client,
                                                              mock_stock_client,
                                                              mock_get_secret):
        # Mocking return values and behaviors
        context = MagicMock()

        secret = {
            "alpaca_api_key": "fake_api_key",
            "alpaca_secret_key": "fake_secret_key"
            }
        mock_get_secret.return_value = secret

        alpaca_api_key = secret['alpaca_api_key']
        alpaca_secret_key = secret['alpaca_secret_key']

        last_average = rolling_average_values.iloc[-1]
        last_price = stock_data_df['close'].iloc[-1]

        mock_get_stock_data.return_value = stock_data_df

        mock_calculate_rolling_average.return_value = rolling_average_values

        position = MagicMock()
        position.unrealized_pl = 1
        mock_get_open_positions.return_value = position

        mock_profit_loss_reached.return_value = False

        # Set up buying condition to be True
        mock_buying_condition.return_value = False
        mock_selling_condition.return_value = True

        mock_increment_run_count.return_value = 1

        # Run the function
        trade_run_result = start_trade_run(payload.event, context)

        # Test get secret
        mock_get_secret.assert_called_once()

        # Test setup stock clients
        mock_stock_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_trading_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)

        # Test check open positions for PnL
        mock_get_open_positions.assert_called_once_with(mock_trading_client.return_value, 'AAPL')
        mock_profit_loss_reached.assert_called_once_with(10, -10, 1)

        # Test evaluate buy/sell conditions
        mock_get_stock_data.assert_called_once_with(mock_stock_client.return_value, 'AAPL', 5, 16)
        pd_testing.assert_series_equal(mock_calculate_rolling_average.call_args[0][0], stock_data_df[
            'close'])  # checking calculate_rolling_average called with close prices in stock data df
        self.assertEqual(mock_calculate_rolling_average.call_args[0][1], len(stock_data_df))
        mock_calculate_rolling_average.assert_called_once_with(stock_data_df['close'], len(stock_data_df))

        mock_buying_condition.assert_called_once_with(last_average, last_price)
        mock_buy_stock.assert_not_called()
        mock_sell_stock.assert_called_once_with(mock_trading_client.return_value, 'AAPL')
        mock_selling_condition.assert_called_once_with(last_average, last_price)

        # Test check/update run count
        mock_increment_run_count.assert_called_once_with(1)
        mock_increment_run_count.return_value = 3

        # Test trade run result correct
        self.assertEqual(trade_run_result, {
            "cancelTradeJob": 0,
            "runCount": 1
        })

    def test_start_trade_run_with_selling_price_no_position(self,
                                                            mock_increment_run_count,
                                                            mock_sell_stock,
                                                            mock_buy_stock,
                                                            mock_selling_condition,
                                                            mock_buying_condition,
                                                            mock_profit_loss_reached,
                                                            mock_get_open_positions,
                                                            mock_calculate_rolling_average,
                                                            mock_get_stock_data,
                                                            mock_trading_client,
                                                            mock_stock_client,
                                                            mock_get_secret):

        # Mocking return values and behaviors
        context = MagicMock()

        secret = {
            "alpaca_api_key": "fake_api_key",
            "alpaca_secret_key": "fake_secret_key"
        }
        mock_get_secret.return_value = secret

        alpaca_api_key = secret['alpaca_api_key']
        alpaca_secret_key = secret['alpaca_secret_key']

        last_average = rolling_average_values.iloc[-1]
        last_price = stock_data_df['close'].iloc[-1]

        mock_get_stock_data.return_value = stock_data_df

        mock_calculate_rolling_average.return_value = rolling_average_values

        position = MagicMock()
        position.unrealized_pl = 1
        mock_get_open_positions.return_value = False

        mock_profit_loss_reached.return_value = False

        # Set up buying condition to be True
        mock_buying_condition.return_value = False
        mock_selling_condition.return_value = False

        mock_increment_run_count.return_value = 1

        # Run the function
        trade_run_result = start_trade_run(payload.event, context)

        # Test get secret
        mock_get_secret.assert_called_once()

        # Test setup stock clients
        mock_stock_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_trading_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)

        # Test check open positions for PnL
        mock_get_open_positions.assert_called_once_with(mock_trading_client.return_value, 'AAPL')
        mock_profit_loss_reached.assert_not_called()

        # Test evaluate buy/sell conditions
        mock_get_stock_data.assert_called_once_with(mock_stock_client.return_value, 'AAPL', 5, 16)
        pd_testing.assert_series_equal(mock_calculate_rolling_average.call_args[0][0], stock_data_df[
            'close'])  # checking calculate_rolling_average called with close prices in stock data df
        self.assertEqual(mock_calculate_rolling_average.call_args[0][1], len(stock_data_df))
        mock_calculate_rolling_average.assert_called_once_with(stock_data_df['close'], len(stock_data_df))

        mock_buying_condition.assert_called_once_with(last_average, last_price)
        mock_buy_stock.assert_not_called()
        mock_sell_stock.assert_not_called()
        mock_selling_condition.assert_called_once_with(last_average, last_price)

        # Test check/update run count
        mock_increment_run_count.assert_called_once_with(1)

        # Test trade run result correct
        self.assertEqual(trade_run_result, {
            "cancelTradeJob": 0,
            "runCount": 1
        })

    def test_start_trade_run_with_selling_price_no_position(self,
                                                            mock_increment_run_count,
                                                            mock_sell_stock,
                                                            mock_buy_stock,
                                                            mock_selling_condition,
                                                            mock_buying_condition,
                                                            mock_profit_loss_reached,
                                                            mock_get_open_positions,
                                                            mock_calculate_rolling_average,
                                                            mock_get_stock_data,
                                                            mock_trading_client,
                                                            mock_stock_client,
                                                            mock_get_secret):

        # Mocking return values and behaviors
        context = MagicMock()

        secret = {
            "alpaca_api_key": "fake_api_key",
            "alpaca_secret_key": "fake_secret_key"
        }
        mock_get_secret.return_value = secret

        alpaca_api_key = secret['alpaca_api_key']
        alpaca_secret_key = secret['alpaca_secret_key']

        last_average = rolling_average_values.iloc[-1]
        last_price = stock_data_df['close'].iloc[-1]

        mock_get_stock_data.return_value = stock_data_df

        mock_calculate_rolling_average.return_value = rolling_average_values

        position = MagicMock()
        position.unrealized_pl = 1
        mock_get_open_positions.return_value = False

        mock_profit_loss_reached.return_value = False

        # Set up buying condition to be True
        mock_buying_condition.return_value = False
        mock_selling_condition.return_value = False

        mock_increment_run_count.return_value = 1

        # Run the function
        trade_run_result = start_trade_run(payload.event, context)

        # Test get secret
        mock_get_secret.assert_called_once()

        # Test setup stock clients
        mock_stock_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_trading_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)

        # Test check open positions for PnL
        mock_get_open_positions.assert_called_once_with(mock_trading_client.return_value, 'AAPL')
        mock_profit_loss_reached.assert_not_called()

        # Test evaluate buy/sell conditions
        mock_get_stock_data.assert_called_once_with(mock_stock_client.return_value, 'AAPL', 5, 16)
        pd_testing.assert_series_equal(mock_calculate_rolling_average.call_args[0][0], stock_data_df[
            'close'])  # checking calculate_rolling_average called with close prices in stock data df
        self.assertEqual(mock_calculate_rolling_average.call_args[0][1], len(stock_data_df))
        mock_calculate_rolling_average.assert_called_once_with(stock_data_df['close'], len(stock_data_df))

        mock_buying_condition.assert_called_once_with(last_average, last_price)
        mock_buy_stock.assert_not_called()
        mock_sell_stock.assert_not_called()
        mock_selling_condition.assert_called_once_with(last_average, last_price)

        # Test check/update run count
        mock_increment_run_count.assert_called_once_with(1)

        # Test trade run result correct
        self.assertEqual(trade_run_result, {
            "cancelTradeJob": 0,
            "runCount": 1
        })

    def test_start_trade_run_max_run_count_reached(self,
                                                   mock_increment_run_count,
                                                   mock_sell_stock,
                                                   mock_buy_stock,
                                                   mock_selling_condition,
                                                   mock_buying_condition,
                                                   mock_profit_loss_reached,
                                                   mock_get_open_positions,
                                                   mock_calculate_rolling_average,
                                                   mock_get_stock_data,
                                                   mock_trading_client,
                                                   mock_stock_client,
                                                   mock_get_secret):

        # Mocking return values and behaviors
        context = MagicMock()

        secret = {
            "alpaca_api_key": "fake_api_key",
            "alpaca_secret_key": "fake_secret_key"
        }
        mock_get_secret.return_value = secret

        alpaca_api_key = secret['alpaca_api_key']
        alpaca_secret_key = secret['alpaca_secret_key']

        last_average = rolling_average_values.iloc[-1]
        last_price = stock_data_df['close'].iloc[-1]

        mock_get_stock_data.return_value = stock_data_df

        mock_calculate_rolling_average.return_value = rolling_average_values

        position = MagicMock()
        position.unrealized_pl = 1
        mock_get_open_positions.return_value = False

        mock_profit_loss_reached.return_value = False

        # Set up buying condition to be True
        mock_buying_condition.return_value = False
        mock_selling_condition.return_value = False

        mock_increment_run_count.return_value = 3

        # Run the function
        trade_run_result = start_trade_run(payload.event, context)

        # Test get secret
        mock_get_secret.assert_called_once()

        # Test setup stock clients
        mock_stock_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)
        mock_trading_client.assert_called_once_with(alpaca_api_key, alpaca_secret_key)

        # Test check open positions for PnL
        mock_get_open_positions.assert_called_once_with(mock_trading_client.return_value, 'AAPL')
        mock_profit_loss_reached.assert_not_called()

        # Test evaluate buy/sell conditions
        mock_get_stock_data.assert_called_once_with(mock_stock_client.return_value, 'AAPL', 5, 16)
        pd_testing.assert_series_equal(mock_calculate_rolling_average.call_args[0][0], stock_data_df[
            'close'])  # checking calculate_rolling_average called with close prices in stock data df
        self.assertEqual(mock_calculate_rolling_average.call_args[0][1], len(stock_data_df))
        mock_calculate_rolling_average.assert_called_once_with(stock_data_df['close'], len(stock_data_df))

        mock_buying_condition.assert_called_once_with(last_average, last_price)
        mock_buy_stock.assert_not_called()
        mock_sell_stock.assert_not_called()
        mock_selling_condition.assert_called_once_with(last_average, last_price)

        # Test check/update run count
        mock_increment_run_count.assert_called_once_with(1)

        # Test trade run result correct
        self.assertEqual(trade_run_result, {
            "cancelTradeJob": 1,
            "runCount": 3
        })


if __name__ == '__main__':
    unittest.main()
