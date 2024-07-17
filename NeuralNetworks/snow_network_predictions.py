

# File to run tests on data.

# TODO: model from saved models
import file_mnist_loader
import network1
training_data, validation_data, test_data = file_mnist_loader.load_data_wrapper()
net = network1.Network([784, 30, 10])
net.show_data(test_data)