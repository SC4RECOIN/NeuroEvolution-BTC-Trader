import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class TA(object):
    def __init__(self, ohlcv):
        self.ohlcv = pd.DataFrame(data=ohlcv)

        # deconstuct ohlcv
        self.open = ohlcv['open']
        self.high = ohlcv['high']
        self.low = ohlcv['low']
        self.close = ohlcv['close']
        self.volume = ohlcv['volume']

    def EMA(self, period, column='close'):
        return self.ohlcv[column].ewm(ignore_na=False,
                                      min_periods=period - 1,
                                      span=period).mean()

    def DEMA(self, period, column='close'):
        return 2 * self.EMA(period, column) - self.EMA(period, column).ewm(ignore_na=False,
                                                                           min_periods=period - 1,
                                                                           span=period).mean()

    def graph(self,
              include_open=False,
              include_high=False,
              include_low=False,
              include_close=False,
              **kwargs):

        if include_open: plt.plot(self.open, label='open')
        if include_high: plt.plot(self.high, label='high')
        if include_low: plt.plot(self.low, label='low')
        if include_close: plt.plot(self.close, label='close')

        for key, value in kwargs.items():
            plt.plot(value, label=key)

        leg = plt.legend(loc='best', shadow=True)
        leg.get_frame().set_alpha(0.5)

        plt.show()

    def remove_NaN(self, inputs, outputs):
        valid_idx = 0
        for check in np.isnan(inputs):
            if True in check: valid_idx += 1
            else: break

        return valid_idx


if __name__ == '__main__':
    data = {'open': [32, 33, 19, 25, 29, 37, 38, 35, 32, 38, 42, 49],
            'high': [36, 35, 25, 29, 31, 40, 41, 39, 33, 45, 50, 51],
            'low':  [32, 33, 19, 25, 29, 37, 38, 35, 32, 38, 42, 49],
            'close':[31, 31, 14, 24, 25, 32, 37, 32, 29, 31, 40, 45],
            'volume': [150, 200, 172, 177, 163, 189, 111, 98, 211, 215, 70, 98]}

    ta = TA(data)
    ema_3 = ta.EMA(3).values
    ema_5 = ta.EMA(5).values
    dema_3 = ta.DEMA(3).values

    ta.graph(include_close=True,
             EMA_3=ema_3,
             EMA_5=ema_5,
             DEMA_3=dema_3)
