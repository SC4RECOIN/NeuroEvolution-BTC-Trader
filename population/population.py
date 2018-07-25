from population.genome import Genome
from population.network import Network
from time import time
import numpy as np
import tensorflow as tf


class Population(object):
    def __init__(self,
                 network_params,
                 pop_size,
                 mutation_scale,
                 w_mutation_rate,
                 b_mutation_rate=0,
                 mutation_decay=None,
                 breeding_ratio=0):

        self.network_params = network_params
        self.population_size = pop_size
        self.w_mutation_rate = w_mutation_rate
        self.b_mutation_rate = b_mutation_rate
        self.mutation_scale = mutation_scale
        self.mutation_decay = mutation_decay
        self.breeding_ratio = breeding_ratio

        self.genomes = self.initial_pop()
        self.overall_best = self.genomes[0]
        self.gen_best = self.genomes[0]

        self.verbose_load_bar = 25

    def initial_pop(self):
        genomes = []
        for i in range(self.population_size):
            genomes.append(Genome(i,
                                  self.network_params,
                                  self.mutation_scale,
                                  self.w_mutation_rate,
                                  self.b_mutation_rate))

        return genomes

    def evolve(self, g, verbose=True):
        # genisis population
        if g == 0:
            return

        if verbose:
            print('{0}\ncreating population {1}'.format('='*self.verbose_load_bar, g+1))

        # find fitness by normalizing score
        self.normalize_score()

        # find pool of genomes to breed and mutate
        parents_1 = self.pool_selection()
        parents_2 = self.pool_selection()
        children = []

        # create next generation
        for idx, (p1, p2) in enumerate(zip(parents_1, parents_2)):
            if np.random.random() < self.breeding_ratio:
                # breeding
                children.append(Genome(idx,
                                       self.network_params,
                                       self.mutation_scale,
                                       self.w_mutation_rate,
                                       self.b_mutation_rate,
                                       parent_1=self.genomes[p1],
                                       parent_2=self.genomes[p2]))
            else:
                # mutating
                children.append(Genome(idx,
                                       self.network_params,
                                       self.mutation_scale,
                                       self.w_mutation_rate,
                                       self.b_mutation_rate,
                                       parent_1=self.genomes[p1]))

            if verbose:
                progress = int((idx + 1)/len(parents_1) * self.verbose_load_bar)
                progress_left = self.verbose_load_bar - progress
                print('[{0}>{1}]'.format('=' * progress, ' ' * progress_left), end='\r')

        if verbose: print(' ' * (self.verbose_load_bar + 3), end='\r')
        self.genomes = children

        # mutation scale will decay over time
        if self.mutation_decay is not None:
            self.mutation_scale *= self.mutation_decay

    def normalize_score(self):
        # create np array of genome scores
        score_arr = np.array([x.score for x in self.genomes])

        # normalize scores
        if len(set(score_arr)) != 1:
            score_arr = (score_arr - score_arr.min()) / (score_arr - score_arr.min()).sum()

        # if all the scores were the same
        else: score_arr = [1/self.population_size] * self.population_size

        # assign fitness
        for fitness, genome in zip(score_arr, self.genomes):
            genome.fitness = fitness

    def pool_selection(self, interval_sel=False):
        # sort genomes by fitness
        self.genomes.sort(key=lambda x: x.fitness, reverse=True)

        # intervals for stochastic universal sampling
        intervals = np.linspace(0, 1, self.population_size + 1)

        idx_arr = []
        for i in range(self.population_size):
            idx, cnt = 0, 0

            # fitness proportionate selection or stochastic universal sampling
            r = np.random.uniform(intervals[i], intervals[i + 1]) if interval_sel else np.random.random()

            while cnt < r and idx < self.population_size:
                cnt += self.genomes[idx].fitness
                idx += 1

            idx_arr.append(idx - 1)

        return idx_arr

    def run(self, inputs, outputs, fitness_callback, verbose=True):
        start = time()

        # built using tf.keras
        if self.network_params['network'] == 'convolutional':
            if verbose: print('evaluating population....')

            # add extra dimension for conv1D channel
            inputs = inputs[:,:, np.newaxis]

            for idx, genome in enumerate(self.genomes):
                actions = genome.model.prediction.predict(inputs)
                genome.score = fitness_callback(actions, outputs)
                if verbose: self.print_progress(idx)

        else:
            # open session and evaluate population
            with tf.Session() as sess:
                if verbose: print('evaluating population....')
                for idx, genome in enumerate(self.genomes):
                    actions = sess.run(genome.model.prediction, feed_dict={genome.model.X: inputs})
                    genome.score = fitness_callback(actions, outputs)
                    if verbose: self.print_progress(idx)

            tf.reset_default_graph()

        # evaluate best model in generation and overall
        self.gen_best = self.genomes[np.argmax([x.score for x in self.genomes])]
        if self.gen_best.score > self.overall_best.score: self.overall_best = self.gen_best

        if verbose:
            if verbose: print(' ' * (self.verbose_load_bar + 3), end='\r')
            print('average score: {0:.2f}%'.format(np.average(np.array([x.score for x in self.genomes]))))
            print('best score: {0:.2f}%'.format(max([x.score for x in self.genomes])))
            print('record score: {0:.2f}%'.format(self.overall_best.score))
            print('time: {0:.2f}s'.format(time() - start))

        return self.gen_best

    def test(self, inputs, outputs, fitness_callback, to_test='gen_best'):
        model = Network(self.gen_best)
        with tf.Session() as sess:
            actions = sess.run(model.prediction, feed_dict={model.X: inputs})
            print('test score: {0:.2f}%'.format(fitness_callback(actions, outputs)))

        tf.reset_default_graph()

    def print_progress(self, progress):
        progress = int((progress + 1)/len(self.genomes) * self.verbose_load_bar)
        progress_left = self.verbose_load_bar - progress
        print('[{0}>{1}]'.format('=' * progress, ' ' * progress_left), end='\r')
