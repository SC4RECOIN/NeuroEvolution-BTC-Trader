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

    # sell if holding
    if holding:
        usd_wallet = btc_wallet * prices[-1] * (1 - fee)

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


def train_model(layers, 
                inputs, 
                prices,
                w_mutation_rate = 0.05,
                b_mutation_rate = 0.0,
                mutation_scale = 0.3,
                mutation_decay = 1.,
                reporter=None):
    # genetic parameters
    pop_size = 200
    w_mutation_rate = 0.05
    b_mutation_rate = 0.0
    mutation_scale = 0.3
    mutation_decay = 1.

    # rotate data to prevent overfitting
    data_rotation = 30
    rotate_data = False

    # network parameters
    network_params = {
        'network': 'feedforward',
        'input': inputs.shape[1],
        'hidden': layers,
        'output': 2
    }

    # build initial population
    pop = Population(network_params,
                     pop_size,
                     mutation_scale,
                     w_mutation_rate,
                     b_mutation_rate,
                     mutation_decay,
                     socket_reporter=reporter)
                     
    g = 0
    while True:
        pop.evolve()
        gen_best = pop.run((inputs, prices), fitness_callback=calculate_profit)
        g += 1
