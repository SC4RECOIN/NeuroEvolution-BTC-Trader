import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class TA(object):
    def __init__(self, ohlcv):
        self.ohlcv = pd.DataFrame(data=ohlcv)

        # deconstuct ohlcv
        self.open = np.array(ohlcv['open'])
        self.high = np.array(ohlcv['high'])
        self.low = np.array(ohlcv['low'])
        self.close = np.array(ohlcv['close'])
        self.volume = np.array(ohlcv['volume'])

    def EMA(self, period, column='close'):
        """
        Exponential Moving Average
        """
        return self.ohlcv[column].ewm(ignore_na=False,
                                      min_periods=period - 1,
                                      span=period).mean()

    def DEMA(self, period, column='close'):
        """
        Double Exponential Moving Average
        """
        return 2 * self.EMA(period, column) - self.EMA(period, column).ewm(ignore_na=False,
                                                                           min_periods=period - 1,
                                                                           span=period).mean()

    def MACD(self, period_fast=12, period_slow=26, signal=9, column='close'):
        """
        MACD Signal and MACD difference
        """
        EMA_fast = self.ohlcv[column].ewm(ignore_na=False, min_periods=period_slow - 1, span=period_fast).mean()
        EMA_slow = self.ohlcv[column].ewm(ignore_na=False, min_periods=period_slow - 1, span=period_slow).mean()
        MACD = pd.Series(EMA_fast - EMA_slow, name='macd')
        MACD_signal = pd.Series(MACD.ewm(ignore_na=False, span=signal).mean(), name='signal')

        return pd.concat([MACD, MACD_signal], axis=1)

    def RSI(self, period=14, column='close'):
        """
        Relative Strength Index
        """
        delta = self.ohlcv[column].diff()[1:]
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        gain = up.ewm(span=period, min_periods=period - 1).mean()
        loss = down.abs().ewm(span=period, min_periods=period - 1).mean()

        return 100 - (100 / (1 + (gain / loss)))

    def STOCHRSI(self, rsi_period=14, stoch_period=14, column='close'):
        """
        Stochatic RSI
        """
        rsi = self.RSI(rsi_period, column)

        return ((rsi - rsi.min()) / (rsi.max() - rsi.min())).rolling(window=stoch_period).mean()

    def FISH(self, period=10):
        """
        Fisher Transform
        """
        med = (self.ohlcv['high'] + self.ohlcv['low']) / 2
        ndaylow = med.rolling(window=period).min()
        ndayhigh = med.rolling(window=period).max()
        raw = (2 * ((med - ndaylow) / (ndayhigh - ndaylow))) - 1
        smooth = raw.ewm(span=5).mean()

        return pd.Series((np.log((1 + smooth) / (1 - smooth))).ewm(span=3).mean(),
                          name='{0} period FISH.'.format(period))

    def SAR(self, acceleration_factor=0.02, acc_max=0.2):
        """
        Stop and Reverse
        """
        # signal, extreme-point, acceleration factor
        sig0, xpt0, af0 = True, self.high[0], acceleration_factor
        sar = [self.low[0] - (self.high - self.low).std()]

        for i in range(1, len(self.high)):
            sig1, xpt1, af1 = sig0, xpt0, af0

            lmin = min(self.low[i - 1], self.low[i])
            lmax = max(self.high[i - 1], self.high[i])

            if sig1:
                sig0 = self.low[i] > sar[-1]
                xpt0 = max(lmax, xpt1)
            else:
                sig0 = self.high[i] >= sar[-1]
                xpt0 = min(lmin, xpt1)

            if sig0 == sig1:
                sari = sar[-1] + (xpt1 - sar[-1])*af1
                af0 = min(acc_max, af1 + acceleration_factor)

                if sig0:
                    af0 = af0 if xpt0 > xpt1 else af1
                    sari = min(sari, lmin)
                else:
                    af0 = af0 if xpt0 < xpt1 else af1
                    sari = max(sari, lmax)
            else:
                af0 = acceleration_factor
                sari = xpt0

            sar.append(sari)

        return sar

    def TR(self):
        """
        True Range
        """
        tr1 = pd.Series(self.ohlcv['high'] - self.ohlcv['low']).abs()
        tr2 = pd.Series(self.ohlcv['high'] - self.ohlcv['close'].shift()).abs()
        tr3 = pd.Series(self.ohlcv['close'].shift() - self.ohlcv['low']).abs()

        tr = pd.concat([tr1, tr2, tr3], axis=1)

        return tr.max(axis=1)

    def VORTEX(self, period=14):
        """
        Vortex
        """
        VMP = pd.Series(self.ohlcv['high'] - self.ohlcv['low'].shift(-1).abs())
        VMM = pd.Series(self.ohlcv['low'] - self.ohlcv['high'].shift(-1).abs())

        VMPx = VMP.rolling(window=period).sum().tail(period)
        VMMx = VMM.rolling(window=period).sum().tail(period)

        VIp = pd.Series(VMPx / self.TR(), name='VI+').interpolate(method='index')
        VIm = pd.Series(VMMx / self.TR(), name='VI-').interpolate(method='index')

        return pd.concat([VIm, VIp], axis=1)

    def BASP(self, period=40):
        """
        Buy and Sell Pressure
        """
        sp = self.ohlcv['high'] - self.ohlcv['close']
        bp = self.ohlcv['close'] - self.ohlcv['low']
        sp_avg = sp.ewm(span=period, min_periods=period - 1).mean()
        bp_avg = bp.ewm(span=period, min_periods=period - 1).mean()

        v_avg = self.ohlcv['volume'].ewm(span=period, min_periods=period - 1).mean()
        nv = self.ohlcv['volume'] / v_avg

        buy_press = pd.Series(bp / bp_avg * nv, name='Buy')
        sell_press = pd.Series(sp / sp_avg * nv, name='Sell')

        return pd.concat([buy_press, sell_press], axis=1)

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
