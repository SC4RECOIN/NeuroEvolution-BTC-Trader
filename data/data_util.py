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

def load_indicators():
    # check if historical data is available
    if not os.path.exists('data/hist_data.npy'):
        fetch_data(15)

    hist = np.load('data/hist_data.npy')

    # split candles
    hist = {
        'open': hist[:, 1],
        'high': hist[:, 2],
        'low': hist[:, 3],
        'close': hist[:, 4],
        'volume': hist[:, 5],
    }

    # obtain features
    indicators = []
    indicators.append(PPO(hist['close'], 6, 12, 3).values)
    indicators.append(StochRsi(hist['close'], period=14).stoch_histo)
    indicators.append(Coppock(hist['close'], wma_pd=10, roc_long=6, roc_short=3).values)
    indicators.append(PolyInter(hist['close'], progress_bar=True).values)
    indicators.append(((hist['high'] - hist['close']) - (hist['close'] - hist['low'])) / hist['close'])

    # truncate bad values and transpose
    X = np.array(indicators)[:, 30:].transpose()
    hist  = hist['close'][30:]
    
    # test split index
    split_idx = int(0.8 * X.shape[0])

    # fit scaler to traing data only
    scaler = StandardScaler()
    scaler.fit(X[:split_idx])
    X = scaler.transform(X)

    # split training data
    X_train, X_test = X[:split_idx], X[split_idx:]
    prices_train, prices_test = hist[:split_idx], hist[split_idx:]

    return X_train, X_test, prices_train, prices_test

def plot(actions, prices, g):
    plt.clf()

    plt.figure(1)
    plt.suptitle("Trading Bot Generation {}".format(g))

    ax1 = plt.subplot(211)
    ax1.set_ylabel("Price Graph")
    ax1.plot(prices)

    btc_wallet = 0.
    starting_cash = 100.
    usd_wallet = starting_cash
    wallet_arr = []
    fee = 0.001

    # initially wait for buy signal
    holding = False

    for idx, trade in enumerate(actions):
        if holding:
            if not np.argmax(trade):
                holding = False
                usd_wallet = btc_wallet * prices[idx] * (1 - fee)
        else:
            if np.argmax(trade):
                holding = True
                btc_wallet = usd_wallet / prices[idx] * (1 - fee)

        wallet_arr.append(usd_wallet)

    ax2 = plt.subplot(212, sharex=ax1)
    ax2.set_ylabel("Wallet Value")
    ax2.plot(wallet_arr)

    plt.draw()
    plt.pause(0.001)
