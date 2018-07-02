from binance.client import Client
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np
import os

from ta.macd import PPO
from ta.rsi import StochRsi
from ta.coppock import Coppock
from ta.poly_interpolation import PolyInter


def fetch_data(interval):
    intervals = {240: '4h', 60: '1h', 15: '15m', 5: '5m'}
    start = '17 Aug, 2017'
    end = '17 Feb, 2018'
    trading_pair = 'BTCUSDT'

    # load key and secret and connect to API
    keys = open('keys.txt').readline()
    print('Connecting to Client...')
    api = Client(keys[0], keys[1])

    # fetch desired candles of all data
    print('Fetching data (may take multiple API requests)')
    hist = api.get_historical_klines(trading_pair, intervals[interval], start, end)
    print('Finished.\n')

    # cast as float16 numpy array
    hist = np.array(hist, dtype=np.float16)

    # data information
    print("Datapoints:  {0}".format(hist.shape[0]))
    print("Memory:      {0:.2f} Mb\n".format((hist.nbytes) / 1000000))

    # save to file as numpy object
    np.save("data/hist_data", hist)
