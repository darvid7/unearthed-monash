"""
@author: David Lei
@since: 18/03/2017
@modified: 

"""
import numpy as np
from sklearn import tree
import pydotplus
import os

DATAPATH = "/Users/David/Desktop/unearthed-2017/unearthed-monash/unearthed-monash/machine-timestamp-indicator/data/out/decision-tree"

class DecisionTreeCommonFeatures:
    def __init__(self):
        self.in_train = False
        self.in_test = False

    def in_both(self):
        return self.in_train and self.in_test

global decision_tree_common_features
decision_tree_common_features = {}

global can_use_machine_codes
can_use_machine_codes = []

def discretize_data(data_array):
    for i in range(len(data_array)):
        data = data_array[i]
        try:
            data = float(data)
        except ValueError:
            if i == 0:  # allow machine codes.
                data_array[i] = data
                continue
            else:
                return False
        # Either round of times buy biggest factor.
        data = data * 100000  # increase granularity.
        data = int(round(data, 0))
        data_array[i] = data
    return data_array

def parse_labels(labels):
    labels = labels.split(",")
    res = []
    for v in labels:
        v = v.strip("\n")
        if v == '0':
            res.append("No")
        elif v == '1':
            res.append("Yes")
        else:
            # raise ValueError
            pass # \n
    # print(str(len(res)) + " labels")
    return res

def parse_csv(data_path, filename):
    with open(os.path.join(data_path, filename), 'r') as csv_file:
        data = csv_file.readlines()
        labels = parse_labels(data[0])
        machine_pi = data[1:]
        processed_machine_pi_data = []
        for csv_string in machine_pi:
            machine_data = csv_string.split(",")
            fixed_data = discretize_data(machine_data)
            if not fixed_data:  # Remove array.
                pass
            else:
                processed_machine_pi_data.append(fixed_data)
    return processed_machine_pi_data, labels

def commonize_features_pre_processing(matrix, data_is_training):
    global decision_tree_common_features
    for machine_pi_row in matrix:
        machine_component = machine_pi_row[0].strip("\n,\r")

        if machine_component in decision_tree_common_features:
            if data_is_training:
                decision_tree_common_features[machine_component].in_train = True
            else:
                decision_tree_common_features[machine_component].in_test = True
        else:
            dtcf = DecisionTreeCommonFeatures()
            if data_is_training:
                dtcf.in_train = True
            else:
                dtcf.in_test = True
            decision_tree_common_features[machine_component] = dtcf


def only_use_features_in_both(test_features, training_features):
    for machine_code, decision_tree_common_features_object in decision_tree_common_features.items():
        if decision_tree_common_features_object.in_both():
            can_use_machine_codes.append(machine_code)  # Keep feature ordering consistent.

    test_features = samples_as_time_slots(test_features, can_use_machine_codes)

    training_features = samples_as_time_slots(training_features, can_use_machine_codes)

    return test_features, training_features


def samples_as_time_slots(samples_matrix, can_use_machine_codes):
    """Around 36 entries for 36 machines, 1440 data points for throughout the day.
    -> At data point 1, this is the state for all the machines.
    -> 1440 data points.
    """
    as_time_points = [[] for _ in range(1440)]  # 1 list per time point (column).
    for machine_pi_row in samples_matrix:
        # if index = 0 is machine name.
        machine_code = machine_pi_row[0]
        if machine_code not in can_use_machine_codes:
            continue # Skip over machines not in testing and training.
        for i in range(1, len(machine_pi_row)):
            pi_value = machine_pi_row[i]
            as_time_points[i-1].append(pi_value)

    return as_time_points


def cal_you_god(groot, filename):
    dot_data = tree.export_graphviz(groot, feature_names=can_use_machine_codes, out_file=None, filled=True, proportion=True)
    graph = pydotplus.graph_from_dot_data(dot_data)
    graph.write_pdf(filename)

def calc_accuracy(prediction, actual_labels):
    if not len(prediction) == len(actual_labels):
        raise IndexError("Prediction results not same len as actual")
    correct = 0

    for i in range(len(prediction)):
        if prediction[i] == actual_labels[i]:
            correct += 1
    # print(correct)
    return correct, len(actual_labels)

def make_my_decisions():
    training_features, labels = parse_csv(DATAPATH, "training_data.csv")
    commonize_features_pre_processing(training_features, data_is_training=True)


    # training_features = samples_as_time_slots(training_features, data_is_training=True)

    test_features, test_labels = parse_csv(DATAPATH, "test_data.csv")
    commonize_features_pre_processing(test_features, data_is_training=False)

    # test_features = samples_as_time_slots(test_features, data_is_training=False)

    test_features, training_features = only_use_features_in_both(test_features, training_features)
    print("Number of training data points %d" % (len(test_features) * len(test_features[0])))
    print("Training Groot")
    # print(len(training_features))
    print("Training features: " + str(training_features))
    print("Processing test data on Groot")
    # print(len(test_features))
    print("Test features: " + str(test_features))

    groot = tree.DecisionTreeClassifier()
    groot = groot.fit(training_features, labels)

    cal_you_god(groot, "decision_tree.pdf")


    prediction = groot.predict(test_features)
    print("Predictions: " + str(prediction))
    print("Actual: " + str(test_labels))
    prediction = list(prediction)
    # print(prediction)
    correct, total = calc_accuracy(prediction, test_labels)
    # print("Accuracy: %f" % (correct/total))
    calculate_correct_predictions(prediction, test_labels)


def calculate_correct_predictions(prediction, actual):
    nf = actual.count("No")
    # print("NF: %s" % nf)
    n_failures = 0
    n_correct_predicted_failures = 0
    failed_but_predicted_pass = 0
    correct_pass = 0
    passed_but_predicted_failed = 0

    for i in range(len(prediction)):
        res = prediction[i]
        res_actual = actual[i]

        if res_actual == "No":
            n_failures += 1

            if res == "No":
                n_correct_predicted_failures += 1
            else:
                failed_but_predicted_pass += 1

        if res_actual == "Yes":
            if res == "Yes":
                correct_pass  += 1
            elif res == "No":
                passed_but_predicted_failed += 1

    # print("<<Stats>>")
    # print("Failed but predicted pass: %d" % failed_but_predicted_pass)
    # print("Passed but predicted failed: %d" % passed_but_predicted_failed)
    # print("Passed and predicted passed: %d" % correct_pass)
    print("Number of failures: %d" % n_failures)
    print("Number of correctly predicted failures: %d" % n_correct_predicted_failures)
    print("Accuracy of correct predicted failures %s" % (float(n_correct_predicted_failures)/float(n_failures)))



make_my_decisions()