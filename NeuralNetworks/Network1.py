
# Erik Kaufman
# 
# based on: http://neuralnetworksanddeeplearning.com/
#
# Goal: Create and train a neural network that processes 28x28 black and white 
# pixel images to detect whitch number (0-9) they are.
#
# I also want to be able to write the weights into a seperate file so I don't 
# have to retrain the model each time I want to test it out

# copy this into a terminal window opened in the neural networks folder to load up and run this. 
# you can change neural network size and training paramaters for different results
"""
import mnist_loader
training_data, validation_data, test_data = mnist_loader.load_data_wrapper()
import network1
net = network1.Network([784, 40, 10])
net.SGD(training_data, 5, 20, 3.0, test_data=test_data)
"""

import numpy as np
import random
import time
from matplotlib import pyplot as plt
import keyboard as kb

class Network(object):

    # Constructor
    def __init__(self, sizes): # sizes is number of nodes in each layer (i think)
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x) for x, y in zip(sizes[:-1], sizes[1:])]

    def feedforward(self, a):
        # input the activation of a layer
        # Cycles through
        for b, w in zip(self.biases, self.weights):
            a = sigmoid(np.dot(w, a) + b)
        return a
    
    def SGD(self, training_data, epochs, mini_batch_size, eta,
            test_data=None):
        """Train the neural network using mini-batch stochastic
        gradient descent.  The ``training_data`` is a list of tuples
        ``(x, y)`` representing the training inputs and the desired
        outputs.  The other non-optional parameters are
        self-explanatory.  If ``test_data`` is provided then the
        network will be evaluated against the test data after each
        epoch, and partial progress printed out.  This is useful for
        tracking progress, but slows things down substantially."""
        if test_data: n_test = len(test_data)
        n = len(training_data)

        # Train through each epoch
        for j in range(epochs):
            time1 = time.time()
            # Randomly Shuffle the data
            random.shuffle(training_data)

            # Create array of minibatches
            mini_batches = [
                training_data[k:k+mini_batch_size] 
                for k in range(0, n, mini_batch_size)]
            # start at 0, to to n, the total amount of training data, in steps of the minibatch size
            # this will use all the data as good as it can
            
            # for each mini batch
            for mini_batch in mini_batches:
                # call update minibatch (not created yet) eta is learning rate
                self.learn_on_minibatch(mini_batch, eta)

            # print out test data for updates
            time2 = time.time()
            if test_data:
                print("Epoch {0}: {1} / {2}, took {3:.2f} seconds".format(
                    j, self.evaluate(test_data), n_test, time2-time1))
            else:
                print("Epoch {0} complete".format(j))

    def learn_on_minibatch(self, mini_batch, eta):
        """Update the network's weights and biases by applying
        gradient descent using backpropagation to a single mini batch.
        The ``mini_batch`` is a list of tuples ``(x, y)``, and ``eta``
        is the learning rate."""

        # create gradiant vectors for the biases and weights
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.biases]

        # add the change in each bias and weight for eacch example in the minibatch (Takes the most time)
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w = self.backpropagation(x, y)
            nabla_b = [nb+dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]     

        # Nudge the biases and weights based on the averege gradiant vector of the mini batch
        self.weights = [w-(eta/len(mini_batch))*nw for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b-(eta/len(mini_batch))*nb for b, nb in zip(self.biases, nabla_b)]

    def backpropagation(self, x, y):
        """Return a tuple ``(nabla_b, nabla_w)`` representing the
        gradient for the cost function C_x.  ``nabla_b`` and
        ``nabla_w`` are layer-by-layer lists of numpy arrays, similar
        to ``self.biases`` and ``self.weights``."""
        # feedforward
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.biases]
        activation = x
        activations = [x] # list to store all the activations, layer by layer
        zs = [] # list to store all the z vectors, layer by layer
        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, activation) + b 
            zs.append(z)
            activation = sigmoid(z) # calcualates the next activation
            activations.append(activation) # just adds on activations as you get deeper in layers

            
        # backward pass
        # Note that the variable l in the loop below is used a little
        # differently to the notation in Chapter 2 of the book.  Here,
        # l = 1 means the last layer of neurons, l = 2 is the
        # second-last layer, and so on.  It's a renumbering of the
        # scheme in the book, used here to take advantage of the fact
        # that Python can use negative indices in lists.


        # start the chain rule in calc to begin back propogation (See ChainRuleReference photo)
        # this accounts for (parcial C / parcial a) and (parcial a / parcial z)
        delta = self.cost_derivative(activations[-1], y) * sigmoid_prime(zs[-1])
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())

        # Loop throught the same parocess for the remaining layers
        for l in range(2, self.num_layers):
            z = zs[-l]
            sp = sigmoid_prime(z)
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())

        # return the gradients for the biases and weights
        return (nabla_b, nabla_w)


    def evaluate(self, test_data):
        # feed forward and take the highest activation index
        test_results = [(np.argmax(self.feedforward(x)), y) for (x, y) in test_data]
        return sum(int(x == y) for (x, y) in test_results)    
    
    
    def cost_derivative(self, output_activations, y):
        """Return the vector of partial derivatives (partial C_x /
        partial a) for the output activations."""
        return 2*(output_activations-y) # I added this two here becaseu thats what my calc says but I might be wrong
    
    def show_data(self, test_data):
        print("Close the window to advance to the next one")
        print("Press Q to quit")
        np.random.shuffle(test_data)
        for (x, y) in test_data:
            predicted_result = np.argmax(self.feedforward(x))
            plt.imshow((np.reshape(x, (28, 28)) * 255), cmap='gray', vmin=0, vmax=255)
            plt.title(f"{y} -> {predicted_result}", fontsize=35)
            plt.show()
            if (kb.is_pressed('q')):
                break

# other functions
def sigmoid(z):
    return (1/(1+np.exp(-z)))

def sigmoid_prime(z):
    return sigmoid(z)*(1-sigmoid(z))
    
