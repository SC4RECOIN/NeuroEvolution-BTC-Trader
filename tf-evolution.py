import tensorflow as tf
import numpy as np
from time import time
import os

from utils.population import Population
from utils.network import Network
from data.load import load_data

# suppress tf GPU logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def calc_score(predictions, target):
    # find model accuracy
    correct = 0
    for prediction, label in zip(predictions, target):
        if np.argmax(prediction) == label:
            correct += 1

    genome_fitness = correct / len(target) * 100

    return genome_fitness


if __name__ == '__main__':
    # load iris data-set
    x_train, labels_train, x_test, labels_test = load_data()

    # genetic parameters
    pop_size = 250
    mutation_rate = 0.05
    mutation_scale = 0.3
    generations = 100

    # network parameters
    network_params = {
        'input' : x_train.shape[1],
        'hidden': [8],
        'output': len(set(labels_train))
    }

    # build initial population
    pop = Population(network_params, pop_size, mutation_rate, mutation_scale)
    best_genome = pop.genomes[0]

    # run for set number of generations
    for g in range(generations):
        start = time()
        print('creating next generation {}...'.format(g + 1))
        pop.evolve()

        # open session and evaluate population
        with tf.Session() as sess:
            for genome in pop.genomes:
                output = sess.run(genome.model.prediction, feed_dict={genome.model.X: x_train})
                genome.score = calc_score(output, labels_train)

                # save best genome
                if genome.score > best_genome.score:
                    best_genome = genome

        print('average score: {0:.2f}'.format(np.average(np.array([x.score for x in pop.genomes]))))
        print('best score: {0:.2f}'.format(max([x.score for x in pop.genomes])))
        print('record score: {0:.2f}'.format(best_genome.score))
        print('time: {0:.2f}\n'.format(time() - start))

        tf.reset_default_graph()

    # test accuracy of best model
    best_model = Network(best_genome)
    output = tf.Session().run(best_model.prediction, feed_dict={best_model.X: x_test})
    print("\n\nFinished.\nTest accuracy of best model: {0:.2f}".format(calc_score(output, labels_test)))
