import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from population.population import Population
from population.network import Network
from finta import TA

# suppress tf GPU logging
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


# for evaluating model fitness
def calculate_profit(trades, prices):
    btc_wallet, starting_cash = 0., 100.
    usd_wallet = starting_cash
    fee = 0.001

    holding = False
    for idx, trade in enumerate(trades):
        if holding and not np.argmax(trade):
            holding = False
            usd_wallet = btc_wallet * prices[idx] * (1 - fee)
        if not holding and np.argmax(trade):
            holding = True
            btc_wallet = usd_wallet / prices[idx] * (1 - fee)

    return (usd_wallet / starting_cash - 1) * 100


def get_data(filepath, min_inv: int = 5):
    ohlc = pd.read_csv(filepath, index_col=[0])
    ohlc = ohlc.iloc[::min_inv, :]
    print('Calculating TA...')

    ta = [
        TA.ER(ohlc),
        TA.ROC(ohlc),
        TA.PPO(ohlc)["HISTO"],
        TA.STOCHRSI(ohlc),
        TA.IFT_RSI(ohlc),
        TA.BBWIDTH(ohlc),
        TA.PERCENT_B(ohlc),
        TA.ADX(ohlc),
        TA.UO(ohlc),
        TA.AO(ohlc),
        TA.WILLIAMS(ohlc),
        TA.RSI(ohlc),
        TA.COPP(ohlc),
        TA.CCI(ohlc),
        TA.CHAIKIN(ohlc),
        TA.FISH(ohlc),
        TA.SQZMI(ohlc) * 1
    ]
    
    # transpose and remove NaN 
    ta = np.array(ta).transpose()
    ta[np.isnan(ta)] = 0
    ta[np.isinf(ta)] = 0
    closing_prices = ohlc.values[:, ohlc.columns.get_loc('close')]

    print('Scaling...')
    scaler = StandardScaler()
    scaler.fit(ta)
    inputs = scaler.transform(ta)

    return inputs, closing_prices


def get_rand_segment(inputs, prices, size):
    max_idx = len(prices) - size
    rand_idx = np.random.randint(0, max_idx)
    x = inputs[rand_idx:rand_idx + size]
    price = prices[rand_idx:rand_idx + size]

    return x, price


def get_rand_col(inputs, col):
    max_idx = inputs.shape[1]
    cols = [inputs[:, np.random.randint(0, max_idx)] for i in range(col)]
    return np.stack(cols, axis=1)


if __name__ == '__main__':
    inputs, prices = get_data('data/coinbase-1min.csv')
    
    # genetic parameters
    pop_size = 200
    w_mutation_rate = 0.05
    b_mutation_rate = 0.0
    mutation_scale = 0.3
    mutation_decay = 1.
    generations = 10000

    # rotate data to prevent overfitting
    data_rotation = 15
    train_size, test_size = 15000, 5000
    stagnation_limit = 100

    # network parameters
    num_inputs = 4
    network_params = {
        'network': 'feedforward',
        'input': num_inputs,
        'hidden': [32, 16],
        'output': 2
    }

    # build initial population
    pop = Population(network_params,
                     pop_size,
                     mutation_scale,
                     w_mutation_rate,
                     b_mutation_rate,
                     mutation_decay)
                     
    inputs = get_rand_col(inputs, num_inputs)

    # run for set number of generations
    for g in range(generations):
        if g % data_rotation == 0:
            # grab three sets of data segments
            train_data = [get_rand_segment(inputs, prices, train_size) for i in range(3)]
            x_test, price_test = get_rand_segment(inputs, prices, test_size)

        if pop.gen_stagnation > stagnation_limit:
            pop.gen_stagnation = 0

        pop.evolve()
        gen_best = pop.run(train_data, fitness_callback=calculate_profit)
        pop.test(x_test, price_test, fitness_callback=calculate_profit)
