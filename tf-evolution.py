import tensorflow as tf
import numpy as np
from time import time
import os

from population.population import Population
from population.network import Network
from data.data_util import load_indicators
import matplotlib.pyplot as plt
from data.data_util import plot

# suppress tf GPU logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# interactive plots
plt.ion()


def calculate_profit(trades, trade_prices):
    btc_wallet = 0.
    starting_cash = 100.
    usd_wallet = starting_cash
    fee = 0.001

    # initially wait for buy signal
    holding = False

    for idx, trade in enumerate(trades):
        if holding:
            if not np.argmax(trade):
                holding = False
                usd_wallet = btc_wallet * trade_prices[idx] * (1 - fee)
        else:
            if np.argmax(trade):
                holding = True
                btc_wallet = usd_wallet / trade_prices[idx] * (1 - fee)

    return (usd_wallet / starting_cash - 1) * 100


if __name__ == '__main__':
    # genetic parameters
    pop_size = 150
    w_mutation_rate = 0.05
    b_mutation_rate = 0.
    mutation_scale = 0.3
    generations = 1000

    # network parameters
    network_params = {
        'input': 4,
        'hidden': [16, 32],
        'output': 2
    }

    # build initial population
    pop = Population(network_params, pop_size, mutation_scale, w_mutation_rate, b_mutation_rate)
    best_genome = pop.genomes[0]

    # load indicators
    indicators_train, indicators_test, prices_train, prices_test = load_indicators()

    print('Buy and hold profit: {0:.2f}%'.format((prices_train[-1] / prices_train[0] - 1) * 100))
    print('Train set size: ', indicators_train.shape[0], ' candles\n')

    # run for set number of generations
    for g in range(generations):
        start = time()
        print('{}\ncreating generation {}...'.format('=' * 22, g + 1))

        pop.evolve()

        # open session and evaluate population
        with tf.Session() as sess:
            print('evaluating population...')

            for genome in pop.genomes:
                actions = sess.run(genome.model.prediction, feed_dict={genome.model.X: indicators_train})

                # profit score
                genome.score = calculate_profit(actions, prices_train)

                # save best genome
                if genome.score > best_genome.score:
                    best_genome = genome
                    genome.save()

            # plot best genome of generation
            gen_best = pop.genomes[np.argmax(np.array([x.score for x in pop.genomes]))]
            actions = sess.run(gen_best.model.prediction, feed_dict={gen_best.model.X: indicators_train})
            actions_test = sess.run(gen_best.model.prediction, feed_dict={gen_best.model.X: indicators_test})
            # plot(actions, prices_train, g)

            print('average score: {0:.2f}'.format(np.average(np.array([x.score for x in pop.genomes]))))
            print('best score: {0:.2f}'.format(max([x.score for x in pop.genomes])))
            print('test score of best network: {0:.2f}%'.format(calculate_profit(actions_test, prices_test)))
            print('record score: {0:.2f}'.format(best_genome.score))
            print('time: {0:.2f}s\n'.format(time() - start))

        tf.reset_default_graph()
