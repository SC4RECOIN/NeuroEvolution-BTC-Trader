from binance.client import Client
import numpy as np
from keys import key, secret

class BinanceAPI(object):
    def __init__(self, trading_pair='BTCUSDT'):
        self.intervals = {240: '4h', 60: '1h', 15: '15m', 5: '5m'}
        self.trading_pair = trading_pair

        # any valid dateparser format
        self.start = '08/17/2017'
        self.end = 'today'

        # connect to API
        self.api = Client(key, secret)

    def fetch_data(self, interval=15, start=None, end=None):
        # start and end times in dateparser format
        start_date = self.start if start is None else start
        end_date = self.end if end is None else end

        # fetch desired candles of all data
        print('Fetching data (may take multiple API requests)\n')
        hist = self.api.get_historical_klines(self.trading_pair,
                                              self.intervals[interval],
                                              start_date,
                                              end_date)

        # data information
        hist = np.array(hist, dtype=np.float32)
        print('Datapoints:  {0}'.format(hist.shape[0]))
        print('Memory:      {0:.2f} kB\n'.format((hist.nbytes) / 1000))

        # save to file as numpy object
        np.save("historical_data", hist)

        # ignore epoch
        return {'open': hist[:, 1],
                'high': hist[:, 2],
                'low': hist[:, 3],
                'close': hist[:, 4],
                'volume': hist[:, 5]}


if __name__ == '__main__':
        client = BinanceAPI(trading_pair='BTCUSDT')
        data = client.fetch_data(15, start='yesterday', end='today')

        import matplotlib.pyplot as plt
        plt.plot(data['low'])
        plt.plot(data['high'])
        plt.show()
