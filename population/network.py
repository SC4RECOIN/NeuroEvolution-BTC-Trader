import tensorflow as tf
import numpy as np


class Network(object):
    def __init__(self, params):

        self.X = None
        self.Y = tf.placeholder("float", [None, params.outputs])
        self.timesteps = None
        self.outputs = params.outputs

        # apply weights and biases
        self.weights, self.biases = [], []
        for w, b in zip(params.weights, params.biases):
            self.weights.append(tf.constant(w))
            self.biases.append(tf.constant(b))

        if params.network == 'feedforward':
            self.X = tf.placeholder("float", [None, params.inputs])
            self.prediction = self.feedforward()

        elif params.network == 'recurrent':
            self.timesteps = params.timesteps
            self.X = tf.placeholder("float", [None, params.timesteps, params.inputs])
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
        batch_size_holder = tf.placeholder(tf.int32, [], name='batch_size_holder')

        num_units = [16, 16]
        cells = [tf.nn.rnn_cell.BasicLSTMCell(num_units=n) for n in num_units]
        lstm_stacked = tf.nn.rnn_cell.MultiRNNCell(cells)

        init_state = lstm_stacked.zero_state(batch_size_holder, dtype=tf.float32)
        outputs, final_state = tf.nn.dynamic_rnn(lstm_stacked, self.X, dtype=tf.float32)

        output = tf.layers.dense(outputs[:, -1, :], self.outputs)

        return tf.nn.softmax(output)
