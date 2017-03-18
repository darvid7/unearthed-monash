from collections import deque

import numpy as np
import tensorflow as tf
import numpy
import os


def to_number(value):
    try:
        return float(value)
    except:
        return 0


def read_data(directory, file_name):
    with open(os.path.join(directory, file_name), 'r') as file_handler:
        return file_handler.readlines()


def to_rows(file_lines, minute_window):
    return [[to_number(x) for x in row.strip().split(',')] for row in file_lines]


def transpose_columns(data_per_machine):
    print("STUFF %s" % data_per_machine)
    minutes_len = len(data_per_machine[0])
    data_per_minute = [None] * minutes_len
    for minute in range(minutes_len):
        # add the minute
        data_for_minute = [None] * len(data_per_machine)
        for machine_index in range(len(data_per_machine)):
            data_for_minute[machine_index] = data_per_machine[machine_index][minute]
        data_per_minute[minute] = data_for_minute
    return data_per_minute


def split_to_windows(array, window):
    # [[0,1],[2,3],[4,5]] 1 + 3 - 2 = 1
    # [[0,1],[0,1,2,3],[2,3,4,5]] becomes [window - 1:]
    for data_index in range(len(array) - 1, window - 1, -1):
        for offset in range(1, window):
            array[data_index].extend(array[data_index - offset])
    print("Extended: %s" % array)
    return array[get_start_split_index(window):]


def get_start_split_index(window_size):
    return window_size


def get_test_data(directory, file_name, minute_window, prediction_time):
    data = read_data(directory, file_name)
    print(data)
    data_per_machine = to_rows(data, minute_window)
    print(data_per_machine)
    data_per_minute = transpose_columns(data_per_machine)
    print("Transposed: " + str(data_per_minute))
    training_inputs = split_to_windows(data_per_minute, minute_window)
    training_outputs = [[0 if -1 == success else 1] for success in data_per_machine[0]]
    training_outputs_to_predicted(training_outputs, prediction_time)
    return training_inputs, training_outputs[get_start_split_index(minute_window):]

def training_outputs_to_predicted(outputs, predicition_time):
    prediction_minutes_left = 0
    i = len(outputs) - 1
    predictions_added = 0
    while i >= 0:
        if outputs[i][0] == 0:
            prediction_minutes_left = predicition_time
        elif prediction_minutes_left > 0:
            predictions_added += 1
            outputs[i][0] = 0
            prediction_minutes_left -= 1
        i -= 1
    print("Added %s 0s" % predictions_added)

PREDICTION_TIME = 20
MINUTE_WINDOW = 10
training_inputs, training_outputs = get_test_data('./', 'training-real.csv', MINUTE_WINDOW, PREDICTION_TIME)
testing_inputs, testing_outputs = get_test_data('./', 'training-real.csv', MINUTE_WINDOW, PREDICTION_TIME)
print("Training inputs")
#print(training_inputs)
print("Training outputs")
print(training_outputs)
print("Training size: %s" % len(training_inputs))
input()
HIDDEN_UNITS = 2
INPUT_SIZE = len(training_inputs[0])

sess = tf.InteractiveSession()

# a batch of inputs of 2 value each
inputs = tf.placeholder(tf.float32, shape=[None, INPUT_SIZE])

# a batch of output of 1 value each
desired_outputs = tf.placeholder(tf.float32, shape=[None, 1])

# [!] define the number of hidden units in the first layer

# connect 2 inputs to 3 hidden units
# [!] Initialize weights with random numbers, to make the network learn
weights_1 = tf.Variable(tf.truncated_normal([INPUT_SIZE, HIDDEN_UNITS]))

# [!] The biases are single values per hidden unit
biases_1 = tf.Variable(tf.zeros([HIDDEN_UNITS]))

# connect 2 inputs to every hidden unit. Add bias
layer_1_outputs = tf.nn.sigmoid(tf.matmul(inputs, weights_1) + biases_1)

# [!] The XOR problem is that the function is not linearly separable
# [!] A MLP (Multi layer perceptron) can learn to separe non linearly separable points ( you can
# think that it will learn hypercurves, not only hyperplanes)
# [!] Lets' add a new layer and change the layer 2 to output more than 1 value

# connect first hidden units to 2 hidden units in the second hidden layer
weights_2 = tf.Variable(tf.truncated_normal([HIDDEN_UNITS, 2]))
# [!] The same of above
biases_2 = tf.Variable(tf.zeros([2]))

# connect the hidden units to the second hidden layer
layer_2_outputs = tf.nn.sigmoid(
    tf.matmul(layer_1_outputs, weights_2) + biases_2)

# [!] create the new layer
weights_3 = tf.Variable(tf.truncated_normal([2, 1]))
biases_3 = tf.Variable(tf.zeros([1]))

logits = tf.nn.sigmoid(tf.matmul(layer_2_outputs, weights_3) + biases_3)

# [!] The error function chosen is good for a multiclass classification taks, not for a XOR.
# TODO: replaced sub with subtract
error_function = 0.5 * tf.reduce_sum(tf.subtract(logits, desired_outputs) * tf.subtract(logits, desired_outputs))

train_step = tf.train.MomentumOptimizer(0.05, 0.1).minimize(error_function)

sess.run(tf.initialize_all_variables())

for i in range(1000):
    _, loss = sess.run([train_step, error_function],
                       feed_dict={inputs: np.array(training_inputs),
                                  desired_outputs: np.array(training_outputs)})
    if i % 100 == 0:
        print(loss)
actual_outputs = [0 if x < 0.5 else 1 for x in sess.run(logits, feed_dict={inputs: np.array(testing_inputs)})]
print(actual_outputs)
print(testing_outputs)
correct_answers = 0
for actual_output_index in range(len(actual_outputs)):
    actual_output = actual_outputs[actual_output_index]
    correct_output = testing_outputs[actual_output_index][0]
    print("Comparing %s with %s" % (actual_output, correct_output))
    if actual_output == correct_output:
        correct_answers += 1
print("Success rate = %s percent" % ((correct_answers / len(actual_outputs)) * 100))
