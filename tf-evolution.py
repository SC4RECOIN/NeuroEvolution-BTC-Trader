import tensorflow as tf
import numpy as np
from time import time
import random
import os

from population.population import Population
from population.network import Network
import signal
import sys

# suppress tf GPU logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# catch interupt to kill program
def signal_handler(signal, frame):
    print('\nprogram exiting')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

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

def calculate_acc(predictions, targets):
    correct = 0
    for pred, targ in zip(predictions, targets):
        if np.argmax(pred) == np.argmax(targ): correct += 1

    return correct / len(targets)

if __name__ == '__main__':
    encoding = {'Iris-setosa' : 0, 'Iris-versicolor' : 1, 'Iris-virginica' : 2}

    X = []; Y = []
    for line in open('data/Iris.csv'):
        X.append(line.split(',')[:-1])
        Y.append(encoding[line.split(',')[-1][:-1]])

    Y = tf.keras.utils.to_categorical(Y)
    X = np.array(X)

    # genetic parameters
    pop_size = 1
    w_mutation_rate = 0.05
    b_mutation_rate = 0.0
    mutation_scale = 0.3
    generations = 1

    # network parameters
    timesteps = 5
    network_params = {
        'network': 'recurrent',
        'timesteps': timesteps,
        'input': 1,
        'hidden': [16],
        'output': 3
    }

    # build initial population
    pop = Population(network_params, pop_size, mutation_scale, w_mutation_rate, b_mutation_rate)
    tf.reset_default_graph()
    best_genome = pop.genomes[0]

    # run for set number of generations
    for g in range(generations):
        start = time()
        print('{}\ncreating generation {}...'.format('=' * 22, g + 1))

        # pop.evolve()

        # random subset of data, reshape
        shuffle_index = np.random.permutation(len(Y))
        X_subset, Y_subset = X[shuffle_index][:int(len(Y)/3)], Y[shuffle_index][:int(len(Y)/3)]
        X_subset = X_subset.reshape((len(X_subset), timesteps, 1))

        # open session and evaluate population
        with tf.Session() as sess:
            if network_params['network'] is 'recurrent':
                sess.run(tf.global_variables_initializer())

            print('evaluating population...')

            for genome in pop.genomes:
                print("running\n")
                actions = sess.run(genome.model.prediction, feed_dict={genome.model.X: X_subset})

                # profit score
                genome.score = calculate_acc(actions, Y_subset)

                # save best genome
                if genome.score > best_genome.score:
                    best_genome = genome
                    # genome.save()

        print('average score: {0:.2f}'.format(np.average(np.array([x.score for x in pop.genomes]))))
        print('best score: {0:.2f}'.format(max([x.score for x in pop.genomes])))
        print('record score: {0:.2f}'.format(best_genome.score))
        print('time: {0:.2f}s\n'.format(time() - start))

        tf.reset_default_graph()
