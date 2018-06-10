from utils.genome import Genome
import numpy as np


class Population(object):
    def __init__(self, network_params, pop_size, mutation_rate, mutation_scale, interval_selection=False):
        self.network_params = network_params
        self.population_size = pop_size
        self.mutation_rate = mutation_rate
        self.mutation_scale = mutation_scale

        self.interval_sel = interval_selection

        self.genomes = self.initial_pop()

    def initial_pop(self):
        genomes = []
        for i in range(self.population_size):
            genomes.append(Genome(self.network_params, self.mutation_rate, self.mutation_scale))

        return genomes

    def evolve(self):
        # find fitness by normalizing score
        self.normalize_score()

        # find indexes of genomes for next generation
        indexes = self.pool_selection()

        # create next generation
        new_genomes = []
        for idx in indexes:
            new_genomes.append(Genome(self.network_params, self.mutation_rate, self.mutation_scale, inherit=self.genomes[idx]))

        self.genomes = new_genomes

    def normalize_score(self):
        # create np array of genome scores
        score_arr = np.array([x.score for x in self.genomes])

        # if there is more than one unique element
        if len(set(score_arr)) != 1:
            # normalize scores
            score_arr = (score_arr - score_arr.min()) / (score_arr - score_arr.min()).sum()
        else:
            # if all the scores were the same
            score_arr = [1/self.population_size] * self.population_size

        # assign fitness
        for fitness, genome in zip(score_arr, self.genomes):
            genome.fitness = fitness

    def pool_selection(self):
        # sort genomes by fitness
        self.genomes.sort(key=lambda x: x.fitness, reverse=True)

        # intervals for stochastic universal sampling
        intervals = np.linspace(0, 1, self.population_size + 1)

        idx_arr = []
        for i in range(self.population_size):
            idx, cnt = 0, 0

            # fitness proportionate selection or stochastic universal sampling
            r = np.random.uniform(intervals[i], intervals[i + 1]) if self.interval_sel else np.random.random()

            while cnt < r and idx < self.population_size:
                cnt += self.genomes[idx].fitness
                idx += 1

            idx_arr.append(idx - 1)

        return idx_arr
