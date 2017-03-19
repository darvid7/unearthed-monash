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
    training_outputs = [[int(success)] for success in data_per_machine[0]]
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
tf.set_random_seed(0)
PREDICTION_TIME = 20
MINUTE_WINDOW = 10
directory = '../machine-timestamp-indicator/data/out/neural-network/'
training_inputs, training_outputs = get_test_data(directory, 'training_data.csv', MINUTE_WINDOW, PREDICTION_TIME)
testing_inputs, testing_outputs = get_test_data(directory, 'training_data.csv', MINUTE_WINDOW, PREDICTION_TIME)
print("Training inputs")
print(training_inputs)
print("Training outputs")
print(training_outputs)
print("Training size: %s" % len(training_inputs))
input()
HIDDEN_UNITS = 50
INPUT_SIZE = len(training_inputs[0])

tf.contrib.layers.real_valued_column("r")
