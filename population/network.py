import tensorflow as tf
import numpy as np
import os


class Network(object):
    def __init__(self, id, params=None, load_path=None):
        self.id = id
        self.X = None
        self.Y = None
        self.weights, self.biases = [], []
        self.prediction = None

        # only relevant for rnn
        self.timesteps = None

        if params is None and load_path is None:
            raise AttributeError('You must specify network parameters')

        # creating network from config params
        if params is not None:
            self.X = tf.placeholder("float", [None, params.inputs])
            self.Y = tf.placeholder("float", [None, params.outputs])

            # apply weights and biases
            for w, b in zip(params.weights, params.biases):
                self.weights.append(tf.constant(w))
                self.biases.append(tf.constant(b))

            self.prediction = self.feedforward()

        # loading network from saved weights
        if load_path is not None:
            self.infer_network(load_path)
            self.prediction = self.feedforward()

    def feedforward(self):
        layer = self.X
        for w, b in zip(self.weights[:-1], self.biases[:-1]):
            layer = tf.add(tf.matmul(layer, w), b)
            layer = tf.nn.sigmoid(layer)

        layer = tf.add(tf.matmul(layer, self.weights[-1]), self.biases[-1])

        return tf.nn.softmax(layer)

    def infer_network(self, load_dir):
        layers = []
        for file in os.listdir(load_dir):
            path = load_dir + '/' + file
            if 'weights{}'.format(len(self.weights)) in file:
                weights = np.load(path)
                layers.append(weights.shape[0])
                if self.X is None:
                    self.X = tf.placeholder("float", [None, weights.shape[0]])
                    layers.pop(0)
                self.weights.append(tf.constant(weights))
                self.Y = tf.placeholder("float", [None, weights.shape[-1]])
            elif 'biases{}'.format(len(self.biases)) in file:
                self.biases.append(tf.constant(np.load(path)))
            elif 'weights' in file or 'biases' in file:
                raise Exception('files came in wrong order')

        print('successfully loaded', layers, 'network')
