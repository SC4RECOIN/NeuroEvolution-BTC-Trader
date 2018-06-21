from population.genome import Genome
import numpy as np


class Population(object):
    def __init__(self, network_params, pop_size, mutation_scale, w_mutation_rate, b_mutation_rate=0, breeding_ratio=0):
        self.network_params = network_params
        self.population_size = pop_size
        self.w_mutation_rate = w_mutation_rate
        self.b_mutation_rate = b_mutation_rate
        self.mutation_scale = mutation_scale
        self.breeding_ratio = breeding_ratio

        self.genomes = self.initial_pop()

    def initial_pop(self):
        genomes = []
        for i in range(self.population_size):
            genomes.append(Genome(self.network_params, self.mutation_scale, self.w_mutation_rate, self.b_mutation_rate))

        return genomes

    def evolve(self):
        # find fitness by normalizing score
        self.normalize_score()

        # find pool of genomes to breed and mutate
        parents_1 = self.pool_selection()
        parents_2 = self.pool_selection()
        children = []

        # create next generation
        for p1, p2 in zip(parents_1, parents_2):
            if np.random.random() < self.breeding_ratio:
                # breeding
                children.append(Genome(self.network_params,
                                       self.mutation_scale,
                                       self.w_mutation_rate,
                                       self.b_mutation_rate,
                                       parent_1=self.genomes[p1],
                                       parent_2=self.genomes[p2]))
            else:
                # mutating
                children.append(Genome(self.network_params,
                                       self.mutation_scale,
                                       self.w_mutation_rate,
                                       self.b_mutation_rate,
                                       parent_1=self.genomes[p1]))

        self.genomes = children

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
