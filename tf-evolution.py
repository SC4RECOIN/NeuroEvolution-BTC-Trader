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

    ta = [
        TA.PPO(ohlc)["HISTO"],
        TA.STOCHRSI(ohlc),
        TA.RSI(ohlc),
        TA.COPP(ohlc),
        TA.CCI(ohlc)
    ]
    
    # transpose and remove NaN 
    ta = np.array(ta).transpose()
    ta[np.isnan(ta)] = 0
    closing_prices = ohlc.values[:, ohlc.columns.get_loc('close')]

    scaler = StandardScaler()
    scaler.fit(ta)
    inputs = scaler.transform(ta)

    return inputs, closing_prices


if __name__ == '__main__':
    inputs, prices = get_data('data/coinbase-1min.csv')
    
    # genetic parameters
    pop_size = 200
    w_mutation_rate = 0.05
    b_mutation_rate = 0.0
    mutation_scale = 0.3
    mutation_decay = 0.998
    generations = 100

    # rotate data to prevent overfitting
    data_rotation = 15
    train_size, test_size = 15000, 5000
    max_idx = len(prices) - max(train_size, test_size)
    x_train, x_test = None, None
    price_train, price_test = None, None

    # network parameters
    network_params = {
        'network': 'feedforward',
        'input': inputs.shape[1],
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

    # run for set number of generations
    for g in range(generations):
        if g % data_rotation == 0:
            rand_idx = np.random.randint(0, max_idx)
            rand_idx_test = np.random.randint(0, max_idx)
            x_train = inputs[rand_idx:rand_idx + train_size]
            x_test = inputs[rand_idx_test:rand_idx_test + test_size]
            price_train = prices[rand_idx:rand_idx + train_size]
            price_test = prices[rand_idx_test:rand_idx_test + test_size]

        pop.evolve(g)
        gen_best = pop.run(x_train, price_train, fitness_callback=calculate_profit)
        gen_best.save()
        pop.test(x_test, price_test, fitness_callback=calculate_profit)
