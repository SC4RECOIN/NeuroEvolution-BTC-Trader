from population.network import Network
import numpy as np
import copy


class Genome(object):
    def __init__(self,
                 id,
                 network_params,
                 mutation_scale,
                 w_mutation_rate,
                 b_mutation_rate,
                 parent_1=None,
                 parent_2=None):

        # fitness is score normalized
        self.fitness = 0
        self.score = 0
        self.id = id

        # keep track of how genome came to be
        self.mutated = False
        self.bred = False

        self.inputs = network_params['input']
        self.hidden = network_params['hidden']
        self.outputs = network_params['output']
        self.network = network_params['network']
        self.model = None

        self.w_mutation_rate = w_mutation_rate
        self.b_mutation_rate = b_mutation_rate
        self.mutation_scale = mutation_scale

        self.weights = None
        self.biases = None

        # two parents available for breeding
        if parent_2 is not None:
            self.weights = copy.deepcopy(parent_1.weights)
            self.biases = copy.deepcopy(parent_1.biases)
            self.breed(parent_2)
            self.bred = True

        # mutate if only one parent available
        elif parent_1 is not None:
            self.weights = copy.deepcopy(parent_1.weights)
            self.biases = copy.deepcopy(parent_1.biases)
            self.mutate_w_feedforward()
            self.mutate_b_feedforward()
            self.mutated = True

        # initial values when population is first created
        else: self.init_w_b()

    def init_w_b(self):
        # create weights and bias for first hidden layer
        self.weights = [np.random.randn(self.inputs, self.hidden[0]).astype(np.float32)]
        self.biases = [np.random.rand(self.hidden[0]).astype(np.float32)]

        # if there are additional hidden layers
        for i in range(len(self.hidden) - 1):
            self.weights.append(np.random.randn(self.hidden[i], self.hidden[i+1]).astype(np.float32))
            self.biases.append(np.random.randn(self.hidden[i+1]).astype(np.float32))

        # weights for last layer
        self.weights.append(np.random.randn(self.hidden[-1], self.outputs).astype(np.float32))
        self.biases.append(np.random.randn(self.outputs).astype(np.float32))

    def mutate_w_feedforward(self):
        # iterate through layers
        for i, layers in enumerate(self.weights):
            for (j, k), x in np.ndenumerate(layers):

                # randomly mutate weight
                if np.random.random() < self.w_mutation_rate:
                    self.weights[i][j][k] += np.random.normal(scale=self.mutation_scale) * 0.5

    def mutate_b_feedforward(self):
        # iterate through layers
        for i, layers in enumerate(self.biases):
            for j, bias in enumerate(layers):

                # randomly mutate bias
                if np.random.random() < self.b_mutation_rate:
                    self.biases[i][j] += np.random.normal(scale=self.mutation_scale) * 0.5

    def breed(self, parent):
        # iterate through layers
        for i, layers in enumerate(self.weights):
            for (j, k), x in np.ndenumerate(layers):

                # equal chance of weight being from each parent
                if np.random.random() > 0.5:
                    self.weights[i][j][k] = parent.weights[i][j][k]

        # should assign designated biases as well

    def save(self, save_folder='model/'):
        for i, layers in enumerate(self.weights):
            np.save(save_folder + 'weights{}'.format(i), layers)

        for i, layers in enumerate(self.biases):
            np.save(save_folder + 'biases{}'.format(i), layers)
