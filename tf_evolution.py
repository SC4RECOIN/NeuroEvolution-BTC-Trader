import tensorflow as tf
import numpy as np
import pandas as pd
import random

from population.population import Population
from population.network import Network

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

    # discourage models that dont trade
    if usd_wallet == starting_cash:
        return -100.

    return (usd_wallet / starting_cash - 1) * 100


def get_rand_segment(inputs, prices, size):
    max_idx = len(prices) - size
    rand_idx = np.random.randint(0, max_idx)
    x = inputs[rand_idx:rand_idx + size]
    price = prices[rand_idx:rand_idx + size]

    return x, price


def get_rand_col(inputs, col):
    idxs = random.sample(range(inputs.shape[1]), col)
    cols = [inputs[:, idx] for idx in idxs]
    return np.stack(cols, axis=1), idxs


def train_model(inputs, prices, send_data):
    # genetic parameters
    pop_size = 200
    w_mutation_rate = 0.05
    b_mutation_rate = 0.0
    mutation_scale = 0.3
    mutation_decay = 1.

    # rotate data to prevent overfitting
    data_rotation = 30
    train_size, test_size = 5000, 2000
    stagnation_limit = 125

    # network parameters
    num_inputs = 4
    network_params = {
        'network': 'feedforward',
        'input': num_inputs,
        'hidden': [16, 32],
        'output': 2
    }

    # build initial population
    pop = Population(network_params,
                     pop_size,
                     mutation_scale,
                     w_mutation_rate,
                     b_mutation_rate,
                     mutation_decay,
                     socket_updater=send_data)
                     
    partial_inputs, idxs = get_rand_col(inputs, num_inputs)
    pop.model_json["ta_indexes"] = idxs

    g = 0
    while True:
        if g % data_rotation == 0:
            # grab three sets of data segments
            train_data = [get_rand_segment(partial_inputs, prices, train_size) for i in range(3)]
            x_test, price_test = get_rand_segment(partial_inputs, prices, test_size)

        if pop.gen_stagnation > stagnation_limit:
            partial_inputs, idxs = get_rand_col(inputs, num_inputs)
            pop.model_json["ta_indexes"] = idxs
            pop.initial_pop()
            pop.gen_stagnation = 0

        pop.evolve()
        gen_best = pop.run(train_data, fitness_callback=calculate_profit)
        pop.test(x_test, price_test, fitness_callback=calculate_profit)
        print(f'TA idx: {idxs}')
        g += 1
