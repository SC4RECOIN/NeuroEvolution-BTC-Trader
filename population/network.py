import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv1D, MaxPooling1D, Flatten, InputLayer, LSTM
import numpy as np
import math
import os


class Network(object):
    def __init__(self, id, params=None, load_path=None, load_keras=None):
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
            # network type
            if params.network == 'feedforward':
                self.X = tf.placeholder("float", [None, params.inputs])
                self.Y = tf.placeholder("float", [None, params.outputs])

                # apply weights and biases
                for w, b in zip(params.weights, params.biases):
                    self.weights.append(tf.constant(w))
                    self.biases.append(tf.constant(b))

                self.prediction = self.feedforward()

            elif load_keras is not None: self.prediction = load_keras

            elif params.network == 'recurrent':
                self.timesteps = params.timesteps
                self.prediction = self.recurrent(params.inputs, params.hidden, params.outputs)

            elif params.network == 'convolutional':
                self.prediction = self.convolutional(params.inputs, params.hidden, params.outputs)

            else: raise AttributeError(params.network, ' is not a valid network type')

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

    def recurrent(self, num_inputs, hidden, num_outputs):
        model = Sequential()
        model.add(InputLayer(input_shape=(self.timesteps, num_inputs)))

        for idx, hidden_size in enumerate(hidden[:-1]):
            model.add(LSTM(hidden_size, return_sequences=True))

        model.add(LSTM(hidden[-1], return_sequences=False))
        model.add(Dense(num_outputs, activation='softmax'))
        model.compile(loss='mse', optimizer='adam')

        return model

    def convolutional(self, num_inputs, hidden, num_outputs):
        # downsampling by a factor of 2
        pooling_layers = math.floor(math.log(num_inputs, 2))
        kernel_size = 3

        model = Sequential()
        model.add(InputLayer(input_shape=(num_inputs, 1)))

        for idx, hidden_size in enumerate(hidden):
            if idx < pooling_layers - 1:
                model.add(Conv1D(hidden_size,
                                 kernel_size,
                                 padding='same',
                                 activation='relu'))

                model.add(MaxPooling1D(pool_size=2))

            elif idx == pooling_layers:
                model.add(Flatten())
                model.add(Dense(hidden_size, activation='relu'))

            else:
                model.add(Dense(hidden_size, activation='relu'))

        model.add(Dense(num_outputs, activation='softmax'))
        model.compile(loss='mse', optimizer='adam')

        return model

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
