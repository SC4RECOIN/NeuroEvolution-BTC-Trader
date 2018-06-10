from utils.network import Network
import numpy as np
import copy


class Genome(object):
    def __init__(self, network_params, mutation_rate, mutation_scale, inherit=None):
        self.fitness = 0
        self.score = 0

        self.inputs = network_params['input']
        self.hidden = network_params['hidden']
        self.outputs = network_params['output']

        self.mutation_rate = mutation_rate
        self.mutation_scale = mutation_scale

        self.weights = None
        self.biases = None

        if inherit is None:
            self.init_w_b()
        else:
            # perform deep copy so weights are not by reference
            self.weights = copy.deepcopy(inherit.weights)
            self.biases = copy.deepcopy(inherit.biases)
            self.mutate()

        # pass genome to network object
        self.model = Network(self)

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

    def mutate(self):
        # iterate through layers
        for i, layers in enumerate(self.weights):
            for (j, k), x in np.ndenumerate(layers):

                # randomly mutate based on mutation rate
                if np.random.random() < self.mutation_rate:
                    self.weights[i][j][k] += np.random.normal(scale=self.mutation_scale) * 0.5
