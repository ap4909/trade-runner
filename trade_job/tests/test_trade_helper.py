import unittest
from unittest.mock import create_autospec
from alpaca.data.historical import StockHistoricalDataClient
from trade_job.trade_helper import (
    get_stock_data
)


class TestTradeHelper(unittest.TestCase):
    def test_get_stock_data(self):
        mock_client = create_autospec(StockHistoricalDataClient)
        # Mocking the mean value
        mock_client.get_stock_bars.return_value.df.__getitem__.return_value.mean.return_value = 1
        # Mocking the last value
        mock_client.get_stock_bars.return_value.df.__getitem__.return_value.iloc.__getitem__.return_value = 2

        symbol = 'AAPL'
        offset = 30

        # Call the function
        mean_price, last_price = get_stock_data(mock_client, symbol, offset)

        self.assertEqual(mean_price, 1)
        self.assertEqual(last_price, 2)

