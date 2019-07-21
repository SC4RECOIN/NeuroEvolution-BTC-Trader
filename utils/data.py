import numpy as np
import pandas as pd
from finta import TA
from sklearn.preprocessing import StandardScaler


class Data(object):
    def __init__(self, filepath, interval=5):
        self._interval = interval
        self.ohlc_data = pd.read_csv(filepath, index_col=[0])
        self.ohlc = self.ohlc_data.iloc[::self.interval, :]
        self.last_index = None
        
        # calculate TA
        self.scaler = None
        self.ta = None
        self.calc_ta()

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        # update ohlc data when interval changes
        self._interval = value
        self.ohlc = self.ohlc_data.iloc[::value, :]
        self.calc_ta()

    def get_rand_segment(self, size):
        max_idx = len(self.ohlc) - size
        rand_idx = np.random.randint(0, max_idx)
        self.last_index = (rand_idx, rand_idx + size)
        
        return self.ohlc[rand_idx:rand_idx + size], self.ta[rand_idx:rand_idx + size]

    def get_closing(self):
        close_col = self.ohlc.columns.get_loc('close')
        return self.ohlc.values[:, close_col]

    def get_training_segment(self):
        inputs = self.ta[self.last_index[0]:self.last_index[1]]
        closing = self.get_closing()[self.last_index[0]:self.last_index[1]]
        return inputs, closing
    
    def calc_ta(self):
        ta = [
            TA.ER(self.ohlc),
            TA.PPO(self.ohlc)["HISTO"],
            TA.STOCHRSI(self.ohlc),
            TA.ADX(self.ohlc),
            TA.RSI(self.ohlc),
            TA.COPP(self.ohlc),
            TA.CCI(self.ohlc),
            TA.CHAIKIN(self.ohlc),
            TA.FISH(self.ohlc)
        ]

        ta = np.array(ta).transpose()
        ta[np.isnan(ta)] = 0
        ta[np.isinf(ta)] = 0

        # scale them to the same range
        self.scaler = StandardScaler()
        self.scaler.fit(ta)
        self.ta = self.scaler.transform(ta)

    @staticmethod
    def to_dict(ta_arr):
        return [{
            "ER": row[0],
            "PPO": row[1],
            "STOCHRSI": row[2],
            "ADX": row[3],
            "RSI": row[4],
            "COPP": row[5],
            "CCI": row[6],
            "CHAIKIN": row[7],
            "FISH": row[8],
        } for row in ta_arr]
