from collections import deque

import numpy as np
import tensorflow as tf
import numpy
import os


def to_number(value):
    try:
        return float(value)
    except:
        return -100


def read_data(directory, file_name):
    with open(os.path.join(directory, file_name), 'r') as file_handler:
        return file_handler.readlines()


def to_rows(file_lines):
    rows = [[to_number(x.strip()) for x in row.split(',')] for row in file_lines]
    for row in rows:
        max_value = max(row)
        if max_value == 0:
            continue
        for column_index in range(len(row)):
            row[column_index] /= max_value
    return rows


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
    # [[1],[0],[-1]]
    # [[0,1],[0,1,2,3],[2,3,4,5]] becomes [window - 1:]
    # [[1], [0]] # becomes [:1+len() - window] 1+ 3 - 2 = 1
    for data_index in range(len(array) + 1 - window):
        for offset in range(1, window):
            array[data_index].extend(array[data_index + offset])
    print("Extended: %s" % array)
    return array[:get_start_split_index(array, window)]


def get_start_split_index(array, window_size):
    return 1 + len(array) - window_size


def get_test_data(directory, file_name, minute_window, prediction_time):
    data = read_data(directory, file_name)
    print(data)
    data_per_machine = to_rows(data)
    print(data_per_machine)
    data_per_minute = transpose_columns(data_per_machine)
    # print("Transposed: " + str(data_per_minute))
    training_inputs = split_to_windows(data_per_minute, minute_window)
    training_outputs = [[int(success)] for success in data_per_machine[0]]
    training_outputs_to_predicted(training_outputs, prediction_time)
    return training_inputs, training_outputs[:get_start_split_index(training_outputs, minute_window)]


def to_rounded_value(value):
    return 0 if value < 0.5 else 1


def training_outputs_to_predicted(outputs, prediction_time):
    prediction_minutes_left = 0
    i = 0
    predictions_added = 0
    while i < len(outputs):
        if outputs[i][0] == 0:
            prediction_minutes_left = prediction_time
        elif prediction_minutes_left > 0:
            predictions_added += 1
            outputs[i][0] = 0
            prediction_minutes_left -= 1
        i += 1
    print("Added %s 0s" % predictions_added)


def test_ai(session, logits, inputs, testing_inputs_data, correct_outputs_data):
    correct_prediction_count = 0
    prediction_count = 0
    correct_zero_count = 0
    zero_count = 0
    correct_count = 0
    ai_outputs_data = (x for x in session.run(logits, feed_dict={inputs: np.array(testing_inputs_data)}))
    previous_ai_value = None
    previous_correct_value = None
    for test_case_index in range(len(correct_outputs_data)):
        correct_outputs = correct_outputs_data[test_case_index]
        ai_outputs = next(ai_outputs_data)
        ai_output = (1 if 0.5 < ai_outputs[0] else 0)
        is_correct = correct_outputs[0] == ai_output
        if is_correct:
            # Correct!
            correct_count += 1
        if ai_output == 0:
            if previous_ai_value != ai_output:
                # False prediction!
                prediction_count += 1
                if is_correct:
                    correct_prediction_count += 1
        elif correct_outputs[0] == 0:
            if previous_correct_value != correct_outputs_data[0]:
                # False everything-is-okay!
                prediction_count += 1
        if correct_outputs[0] == 0:
            # Falsely outputting that downtime is going to happen
            zero_count += 1
            if is_correct:
                correct_zero_count += 1
        # Set the previous values so we can check if the neural network has made another prediction
        # or if it SHOULD make another prediction
        previous_ai_value = ai_output
        previous_correct_value = correct_outputs[0]
    results = len(correct_outputs_data), correct_count, zero_count, correct_zero_count, prediction_count, correct_prediction_count
    return results


def get_correction_rate(count, correct_count):
    return correct_count / count if count > 0 else 1


tf.set_random_seed(0)
PREDICTION_TIME = 20
MINUTE_WINDOW = 5  # 0
directory = '../machine-timestamp-indicator/data/out/neural-network/'
training_inputs, training_outputs = get_test_data(directory, 'training_data.csv', MINUTE_WINDOW, PREDICTION_TIME)
testing_inputs, testing_outputs = get_test_data(directory, 'test_data.csv', MINUTE_WINDOW, PREDICTION_TIME)
print("Training inputs")
# print(training_inputs)
print("Training outputs")
print(training_outputs)
print("Training size: %s" % len(training_inputs))
input()
INPUT_SIZE = len(training_inputs[0])
HIDDEN_UNITS = INPUT_SIZE

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
error_function = 0.5 * tf.reduce_sum(tf.square(tf.subtract(logits, desired_outputs)))

train_step = tf.train.MomentumOptimizer(0.0001012342128, 0.2012653236565).minimize(error_function)

sess.run(tf.global_variables_initializer())
previous_success_rate = -1
CONSECTUIVE_DOWNGRADE_THRESHOLD = 40
CONSECUTIVE_STAGNATION_THRESHOLD = 60
consectutive_downgrades = 0
consectutive_stagnations = 0
for i in range(2000):
    _, train_error = sess.run([train_step, error_function],
                              feed_dict={inputs: np.array(training_inputs),
                                         desired_outputs: np.array(training_outputs)})
    test_count, test_correct, downtime_count, downtime_correct_count, prediction_count, prediction_correct_count = test_ai(
        sess, logits, inputs, testing_inputs, testing_outputs)
    train_count, train_correct, train_downtime_count, train_downtime_correct_count, train_prediction_count, train_prediction_correct_count = test_ai(
        sess, logits, inputs, testing_inputs, testing_outputs)
    test_count += train_count
    test_correct += train_correct
    downtime_count += train_downtime_count
    downtime_correct_count += train_downtime_correct_count
    prediction_count += train_prediction_count
    prediction_correct_count += train_prediction_correct_count
    downtime_weighting = 1
    prediction_weighting = 2
    downtime_success_rate = downtime_correct_count / downtime_count
    test_success_rate = test_correct / test_count
    prediction_success_rate = prediction_correct_count / prediction_count
    success_rate = (
                   downtime_success_rate * downtime_weighting + test_success_rate + prediction_success_rate * prediction_weighting) / (
                   downtime_weighting + prediction_weighting + 1)
    if i % 20 == 0:
        print("Downgrades %s, stagnation %s" % (consectutive_downgrades, consectutive_stagnations))
        print("%s, %s, %s" % (test_success_rate, downtime_success_rate, prediction_success_rate))
        print("Test success rate %s: %s" % (i, success_rate))
    if i % 100 == 0:
        print("Iteration %s: %s" % (i, train_error))

    if success_rate < previous_success_rate:
        consectutive_downgrades += 1
        if consectutive_downgrades >= CONSECTUIVE_DOWNGRADE_THRESHOLD:
            print("%s consecutive downgrades, breaking at %s" % (consectutive_downgrades, i))
            break
    elif success_rate == previous_success_rate:
        consectutive_stagnations += 1
        if consectutive_stagnations >= CONSECUTIVE_STAGNATION_THRESHOLD:
            print("%s consecutive stagnation, breaking at %s" % (consectutive_stagnations, i))
            break
    else:
        consectutive_downgrades = 0
        consectutive_stagnations = 0

    previous_success_rate = success_rate
print()
training_test_count, training_correct_count, training_prediction_count, training_correct_prediction_count, tr_pr_c, tr_pr_c_c = test_ai(
    sess, logits, inputs, training_inputs, training_outputs)
testing_test_count, testing_correct_count, testing_prediction_count, testing_correct_prediction_count, t_pr_c, t_pr_c_c = test_ai(
    sess,
    logits,
    inputs,
    testing_inputs,
    testing_outputs)
print("Training data accuracy: %s percent" % (get_correction_rate(training_test_count, training_correct_count) * 100))
print("Training data prediction rate: %s percent" % (
    get_correction_rate(training_prediction_count, training_correct_prediction_count) * 100))
print("Testing data downtime warning accuracy: %s percent" % (get_correction_rate(tr_pr_c, tr_pr_c_c) * 100))
print()
print("Testing data accuracy: %s percent" % (get_correction_rate(testing_test_count, testing_correct_count) * 100))
print("Testing data prediction accuracy: %s percent" % (
    get_correction_rate(testing_prediction_count, testing_correct_prediction_count) * 100))
print("Testing data downtime warning accuracy: %s percent" % (get_correction_rate(t_pr_c, t_pr_c_c) * 100))
