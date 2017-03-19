"""
@author: David Lei
@since: 19/03/2017
@modified: 

"""
import csv
import os


class DataFetcher:

    def __init__(self, lower_bound, upper_bound, output_path, ):
        self.lower = lower_bound
        self.upper = upper_bound


# ---
# Training data - We want Jan 2.
training_day_lower = datetime.datetime(2016, 1, 1, 23, 59, 59)  # Last second of Jan 1.
training_day_upper = datetime.datetime(2016, 1, 3, 0, 0, 0)  # First second of Jan 2.


def get_relevant_failures(lower_bound, upper_bound, failure_collection):
    """Returns array of relevant failures in the datetime bounds sorted by start time."""
    # Returns all relevant failures for a day.
    relevant = []
    for failure_id in failure_collection:
        failure = failure_collection[failure_id]
        if failure.start_time > lower_bound and failure.end_time < upper_bound:
            relevant.append(failure)
    relevant.sort(key=lambda f: f.start_time)  # sort failures by state time so can linear search through.
    return relevant


def is_time_failure(time_of_day, look_at_these_failures):
    """
    :param: time_of_day: datetime.datetime() withing bound range, check for all times of day increment by seconds.
    :param: look_at_these_failures: Failures sorted by failure.start_time
    """
    for failure in look_at_these_failures:
        f_start_time = failure.start_time
        if f_start_time > time_of_day:
            return 1  # Pass.
        else: # start_time <= time_of_day.
            f_end_time = failure.end_time
            if time_of_day <= f_end_time: # Failure occurs at this time.
                return 0  # Fail.
            # Continue
    return 1  # Pass

# Sorted failures.
look_at_these_failures = get_relevant_failures(training_day_lower, training_day_upper, failure_collection)

new_day = day.Day(training_day_lower, training_day_upper)
training_data_labels = [is_time_failure(time_of_day, look_at_these_failures) for time_of_day in new_day.datetime_instances]
print(training_data_labels)
print(len(training_data_labels))
print(len(new_day.datetime_instances))
print("Processed training labels")


def get_day_data(lower_bound, upper_bound, machines_to_look_at, writer, dt=False):
    """
    Writes all data for a machine to csv for neural network.

    :param: lower_buound, datetime.datetime().
    :param: upper_bound, datetime.datetime().
    :param: machines_to_look_at, dict of machine code: Machine mappings.
    """
    c = 0
    for machine_code in machines_to_look_at:
        machine = machines_to_look_at[machine_code]
        machine_daily_data = machine.get_daily_data(lower_bound, upper_bound)
        pi_values = [t[1] for t in machine_daily_data]
        if not pi_values.count(pi_values[0]) == 1440:  # Don't process lists with all values the same.
            if dt:
                row = [machine_code] + pi_values
                writer.writerow(row)
            else:
                writer.writerow(pi_values)
            print("processed %s %d machines" % (machine_code, c))
        else:
            print("skipped %s" % machine_code)
        c += 1

# Actual machines to look at.
relevant_machine_codes = SAG_MILL_MACHINE_CODES + HPGR
machines_to_look_at = {}
for m in relevant_machine_codes:
    machines_to_look_at[m] = relevant_machines[m]

# with open(os.path.join(NEURAL_NETWORK_DATA_PATH, "training_data.csv"), "w") as csv_fh:
with open(os.path.join(DECISION_TREE_DATA_PATH, "training_data.csv"), "w") as csv_fh:
    decision_tree = True # if dt.
    csv_writer = csv.writer(csv_fh)
    csv_writer.writerow(training_data_labels)
    # get_day_data(training_day_lower, training_day_upper, machines_to_look_at, csv_writer)
    get_day_data(training_day_lower, training_day_upper, machines_to_look_at, csv_writer, dt=decision_tree)


print("Finished processing training data")