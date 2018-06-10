import tensorflow as tf
import numpy as np
from time import time
import os

from utils.population import Population
from utils.network import Network

# suppress tf GPU logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def calc_score(predictions, target):
    # find model accuracy
    correct = 0
    for prediction, label in zip(predictions, target):
        if np.argmax(prediction) == label: correct += 1

    return correct / len(target) * 100


if __name__ == '__main__':
    # load mnist data and one-hot encode labels
    mnist = {'test_images': np.load('data/test_images.npy'),
             'test_labels': np.load('data/test_labels.npy'),
             'train_images': np.load('data/train_images.npy'),
             'train_labels': np.load('data/train_labels.npy')}

    # genetic parameters
    pop_size = 50
    mutation_rate = 0.05
    mutation_scale = 0.3
    breeding_ratio = 0.0
    generations = 50

    # network parameters
    network_params = {
        'input' : 784,
        'hidden': [256, 256],
        'output': 10
    }

    # build initial population
    pop = Population(network_params, pop_size, mutation_rate, mutation_scale, breeding_ratio)
    best_genome = pop.genomes[0]

    # run for set number of generations
    for g in range(generations):
        start = time()
        print('{}\ncreating generation {}...'.format('='*22, g + 1))
        pop.evolve()

        # open session and evaluate population
        with tf.Session() as sess:
            print('evaluating population...')
            for genome in pop.genomes:
                output = sess.run(genome.model.prediction, feed_dict={genome.model.X: mnist['train_images']})
                genome.score = calc_score(output, mnist['train_labels'])

                # save best genome
                if genome.score > best_genome.score:
                    best_genome = genome

        print('average score: {0:.2f}'.format(np.average(np.array([x.score for x in pop.genomes]))))
        print('best score: {0:.2f}'.format(max([x.score for x in pop.genomes])))
        print('record score: {0:.2f}'.format(best_genome.score))
        print('time: {0:.2f}s\n'.format(time() - start))

        tf.reset_default_graph()

    # test accuracy of best model
    best_model = Network(best_genome)
    output = tf.Session().run(best_model.prediction, feed_dict={best_model.X: mnist['test_images']})
    print("\n\nFinished.\nTest accuracy of best model: {0:.2f}".format(calc_score(output, mnist['test_labels'])))
