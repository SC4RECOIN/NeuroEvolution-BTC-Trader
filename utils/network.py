import tensorflow as tf


class Network(object):
    def __init__(self, params):

        self.X = tf.placeholder("float", [None, params.inputs])
        self.Y = tf.placeholder("float", [None, params.outputs])

        # apply weights and biases
        self.weights, self.biases = [], []
        for w, b in zip(params.weights, params.biases):
            self.weights.append(tf.constant(w))
            self.biases.append(tf.constant(b))

        # construct model
        self.prediction = self.feedforward()

    def feedforward(self):
        layer = self.X
        for w, b in zip(self.weights[:-1], self.biases[:-1]):
            layer = tf.add(tf.matmul(layer, w), b)
            layer = tf.nn.relu(layer)

        layer = tf.add(tf.matmul(layer, self.weights[-1]), self.biases[-1])
        layer = tf.nn.softmax(layer)

        return layer
