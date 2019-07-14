import numpy as np
import pandas as pd


class Data(object):
    def __init__(self, filepath, interval=5):
        self._interval = interval
        self.ohlc_data = pd.read_csv(filepath, index_col=[0])
        self.ohlc = self.ohlc_data.iloc[::self.interval, :]

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        # update ohlc data when interval changes
        self._interval = value
        self.ohlc = self.ohlc_data.iloc[::value, :]

    def get_rand_segment(self, size):
        max_idx = len(self.ohlc) - size
        rand_idx = np.random.randint(0, max_idx)
        
        return self.ohlc[rand_idx:rand_idx + size]
 