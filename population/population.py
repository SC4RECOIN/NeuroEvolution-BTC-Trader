from population.genome import Genome
from population.network import Network
from time import time
import numpy as np
import tensorflow as tf
import shutil, os
import json


class Population(object):
    def __init__(self,
                 network_params,
                 pop_size,
                 mutation_scale,
                 w_mutation_rate,
                 b_mutation_rate=0,
                 mutation_decay=1.0,
                 breeding_ratio=0,
                 verbose=True,
                 clear_old_saves=True,
                 socket_updater=None):

        self.network_params = network_params
        self.population_size = pop_size
        self.w_mutation_rate = w_mutation_rate
        self.b_mutation_rate = b_mutation_rate
        self.mutation_scale = mutation_scale
        self.mutation_decay = mutation_decay
        self.breeding_ratio = breeding_ratio

        self.verbose_load_bar = 25
        self.socket_updater = socket_updater
        self.verbose = verbose

        self.genomes = self.initial_pop()
        self.overall_best = self.genomes[0]
        self.gen_stagnation = 0
        self.gen_best = self.genomes[0]
        self.gen = 0

        self.model_json = {
            "network_params": self.network_params,
            "population_size": self.population_size,
            "w_mutation_rate": self.w_mutation_rate,
            "b_mutation_rate": self.b_mutation_rate,
            "mutation_scale": self.mutation_scale,
            "mutation_decay": self.mutation_decay,
            "breeding_ratio": self.breeding_ratio,
        }

        if clear_old_saves:
            shutil.rmtree('model') 
            os.mkdir('model')

    def initial_pop(self):
        if self.verbose:
            print(f"{'=' * self.verbose_load_bar}\ncreating genesis population")

        return [
            Genome(i, self.network_params,
                   self.mutation_scale,
                   self.w_mutation_rate,
                   self.b_mutation_rate) 
            for i in range(self.population_size)
        ]

    def evolve(self):
        # genesis population
        self.gen += 1
        if self.gen == 1:
            return

        if self.verbose:
            print(f"{'=' * self.verbose_load_bar}\ncreating population {self.gen}")

        # find fitness by normalizing score
        self.normalize_score()

        # find pool of genomes to breed and mutate
        parents_1 = self.pool_selection()
        parents_2 = self.pool_selection()
        children = []

        # create next generation
        for idx, (p1, p2) in enumerate(zip(parents_1, parents_2)):
            children.append(Genome(idx,
                                   self.network_params,
                                   self.mutation_scale,
                                   self.w_mutation_rate,
                                   self.b_mutation_rate,
                                   parent_1=self.genomes[p1],
                                   parent_2=self.genomes[p2] if np.random.random() < self.breeding_ratio else None))

            if self.verbose:
                progress = int((idx + 1)/len(parents_1) * self.verbose_load_bar)
                progress_left = self.verbose_load_bar - progress
                print('[{0}>{1}]'.format('=' * progress, ' ' * progress_left), end='\r')

        if self.verbose: print(' ' * (self.verbose_load_bar + 3), end='\r')
        self.genomes = children

        # mutation scale will decay over time
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

    def run(self, data, fitness_callback):
        start = time()

        # open session and evaluate population
        with tf.Session() as sess:
            if self.verbose: print('evaluating population....')
            for idx, genome in enumerate(self.genomes):
                # list of tuples 
                if type(data) is list:
                    actions = [sess.run(genome.model.prediction, feed_dict={genome.model.X: seg[0]}) for seg in data]
                    
                    # return minimum score to discount random high scores
                    scores = [fitness_callback(actions[idx], seg[1]) for idx, seg in enumerate(data)]
                    genome.score = min(scores)
                    genome.actions = actions[np.argmin(scores)]
                    genome.prices = data[np.argmin(scores)][1]
                else:
                    genome.actions = sess.run(genome.model.prediction, feed_dict={genome.model.X: data[0]})
                    genome.score = fitness_callback(genome.actions, data[1])
                
                if self.verbose: self.print_progress(idx)

        tf.reset_default_graph()
        self.gen_stagnation += 1

        # evaluate best model in generation and overall
        self.gen_best = self.genomes[np.argmax([x.score for x in self.genomes])]
        if self.gen_best.score > self.overall_best.score: 
            self.overall_best = self.gen_best
            self.send_best_trading_data()
            self.gen_best.save(f"gen_{self.gen}")
            self.model_json["fitness"] = self.gen_best.score
            self.gen_stagnation = 0
            
            with open(f'model/gen_{self.gen}/params.json', 'w') as f:
                json.dump(self.model_json, f, indent=4)

        if self.verbose:
            results = {
                'average_score': f"{np.average(np.array([x.score for x in self.genomes])):.2f}",
                'best_score': f"{max([x.score for x in self.genomes]):.2f}",
                'record_score': f"{self.overall_best.score:.2f}",
            }
            self.socket_updater('genResults', {'results': results, 'generation': self.gen})
            print(' ' * (self.verbose_load_bar + 3), end='\r')
            print(f"average score: {results['average_score']}%")
            print(f"best score: {results['best_score']}%")
            print(f"record score: {results['record_score']}%")
            print(f"stagnation: {self.gen_stagnation}")
            print('time: {0:.2f}s'.format(time() - start))

        return self.gen_best

    def test(self, inputs, outputs, fitness_callback, to_test='gen_best'):
        model = Network(0, self.gen_best)
        with tf.Session() as sess:
            actions = sess.run(model.prediction, feed_dict={model.X: inputs})
            print('test score: {0:.2f}%\t(hold: {1:.2f}%)'.format(fitness_callback(actions, outputs), (outputs[-1]/outputs[0]-1)*100))

        tf.reset_default_graph()

    def send_best_trading_data(self):
        # send to interface
        graph_data = [{'price': f'{price:.3f}'} for price in self.overall_best.prices]
        holding = False
        for idx, trade in enumerate(self.overall_best.actions):
            price = self.overall_best.prices[idx]
            if holding and not np.argmax(trade):
                holding = False
                graph_data[idx]['sell'] = f"{price:.3f}"
            if not holding and np.argmax(trade):
                holding = True
                graph_data[idx]['buy'] = f"{price:.3f}"
        
        self.socket_updater('genUpdate', {'generation_trades': graph_data, 'generation': self.gen})

    def print_progress(self, progress):
        progress = int((progress + 1)/len(self.genomes) * self.verbose_load_bar)
        progress_left = self.verbose_load_bar - progress
        print('[{0}>{1}]'.format('=' * progress, ' ' * progress_left), end='\r')
