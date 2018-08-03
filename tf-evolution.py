import tensorflow as tf
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib

from population.population import Population
from population.network import Network
from data.data_util import BinanceAPI
from ta.ta import TA

# suppress tf GPU logging
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# for evaluating model fitness
def calculate_profit(trades, trade_prices):
    btc_wallet = 0.
    starting_cash = 100.
    usd_wallet = starting_cash
    fee = 0.001

    holding = False
    for idx, trade in enumerate(trades):
        if holding and not np.argmax(trade):
            holding = False
            usd_wallet = btc_wallet * trade_prices[idx] * (1 - fee)
        if not holding and np.argmax(trade):
            holding = True
            btc_wallet = usd_wallet / trade_prices[idx] * (1 - fee)

    return (usd_wallet / starting_cash - 1) * 100

def get_data(test_size):
    client = BinanceAPI(trading_pair='BTCUSDT')
    price_data = client.fetch_data(5, save='data/historical_data.npy')
    ta = TA(price_data)
    inputs = np.transpose(np.array([ta.PPO(period_fast=7, period_slow=15, signal=6)['histo'].values,
                                    ta.STOCH()['ratio'].values,
                                    ta.FISH()['histo'].values,
                                    ta.BASP(period=10)['ratio'].values,
                                    ta.VORTEX()['ratio'].values]))
    valid_idx = ta.remove_NaN(inputs)
    inputs, price_data = inputs[valid_idx:], price_data['close'][valid_idx:]

    # test set
    test_idx = int(len(price_data) *  (1 - test_size))

    scaler = StandardScaler()
    scaler.fit(inputs[:test_idx])
    inputs = scaler.transform(inputs)
    joblib.dump(scaler, 'model/scaler.pkl')

    return inputs[:test_idx], inputs[test_idx:], price_data[:test_idx], price_data[test_idx:]


if __name__ == '__main__':
    # inputs
    inputs_train, inputs_test, price_train, price_test = get_data(test_size=0.2)
    print('Buy and hold profit: {0:.2f}%'.format((price_train[-1] / price_train[0] - 1) * 100))
    print('Buy and hold profit (test): {0:.2f}%'.format((price_test[-1] / price_test[0] - 1) * 100))

    # genetic parameters
    pop_size = 4
    w_mutation_rate = 0.05
    b_mutation_rate = 0.0
    mutation_scale = 0.3
    mutation_decay = 0.995
    generations = 500

    # network parameters
    network_params = {
        'network': 'recurrent',
        'timesteps': 4,
        'input': inputs_train.shape[1],
        'hidden': [16, 16, 16],
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
        pop.evolve(g)
        gen_best = pop.run(inputs_train, price_train, fitness_callback=calculate_profit)
        gen_best.save()
        pop.test(inputs_test, price_test, fitness_callback=calculate_profit)
