import tensorflow as tf
import numpy as np


class Network(object):
    def __init__(self, params):
        self.id = params.id

        self.X = None
        self.Y = None
        self.timesteps = None

        # apply weights and biases
        self.weights, self.biases = [], []
        for w, b in zip(params.weights, params.biases):
            self.weights.append(tf.constant(w))
            self.biases.append(tf.constant(b))

        if params.network == 'feedforward':
            self.X = tf.placeholder("float", [None, params.inputs])
            self.Y = tf.placeholder("float", [None, params.outputs])
            self.prediction = self.feedforward()

        elif params.network == 'recurrent':
            self.timesteps = params.timesteps
            self.X = tf.placeholder("float", [None, params.timesteps])
            self.Y = tf.placeholder("float", [None, params.timesteps])
            self.prediction = self.recurrent(params.inputs)

        else:
            raise AttributeError(params.network, ' is not a valid network type')

    def feedforward(self):
        layer = self.X
        for w, b in zip(self.weights[:-1], self.biases[:-1]):
            layer = tf.add(tf.matmul(layer, w), b)
            layer = tf.nn.sigmoid(layer)

        layer = tf.add(tf.matmul(layer, self.weights[-1]), self.biases[-1])

        return tf.nn.softmax(layer)

    def recurrent(self, inputs):
        with tf.variable_scope('rnn_{}'.format(self.id)):
            pass
