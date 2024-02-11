from pandas import Timestamp
import pandas as pd
import numpy as np

stock_data_df = pd.DataFrame({
            'open': {
                ('AAPL', Timestamp('2024-02-09 18:29:00+0000', tz='UTC')): 189.46,
                ('AAPL', Timestamp('2024-02-09 18:30:00+0000', tz='UTC')): 189.48,
                ('AAPL', Timestamp('2024-02-09 18:31:00+0000', tz='UTC')): 189.47
                },
            'close': {
                ('AAPL', Timestamp('2024-02-09 18:29:00+0000', tz='UTC')): 189.4701,
                ('AAPL', Timestamp('2024-02-09 18:30:00+0000', tz='UTC')): 189.48,
                ('AAPL', Timestamp('2024-02-09 18:31:00+0000', tz='UTC')): 189.4589
                }
            })

rolling_average_values = pd.Series({
                                       "2024-02-09 23:58:00+00:00": np.nan,
                                       "2024-02-09 23:59:00+00:00": np.nan,
                                       "2024-02-10 00:03:00+00:00": np.nan,
                                       "2024-02-10 00:08:00+00:00": 150
                                       })
