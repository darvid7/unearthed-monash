"""
@author: David Lei
@since: 18/03/2017
@modified:

"""
import os
import shelve
import time
import datetime
import csv
from model import csv_pi_parser
from model import csv_failure_parser
from model import day

# Want to stablalize:  3311hs181A.PV	 SAG Dry (Fd  or Fd - Pbl)

# Constants
PERFORMANCE_INDICATOR_DATA = "/Users/David/Desktop/unearthed-2017/unearthed-monash/unearthed-monash/" \
                             "machine-timestamp-indicator/data/in/perf-indicator"
FAILURE_DATA = "/Users/David/Desktop/unearthed-2017/unearthed-monash/unearthed-monash/machine-timestamp-indicator/" \
               "data/in/failures/"

DATAOUT_PATH = "/Users/David/Desktop/unearthed-2017/unearthed-monash/unearthed-monash/machine-timestamp-indicator/" \
               "data/out/leading-up-to-failures/"

SHELVE_PERSISTANCE_PATH = "/Users/David/Desktop/unearthed-2017/unearthed-monash/unearthed-monash/" \
                          "machine-timestamp-indicator/data/out/persistence/"

NEURAL_NETWORK_DATA_PATH = "/Users/David/Desktop/unearthed-2017/unearthed-monash/unearthed-monash/" \
                          "machine-timestamp-indicator/data/out/neural-network/"

use_persisting = True

SAG_MILL_MACHINE_CODES = [
    "1101047CL1.P01",
    "1101047CL1.P02",
    "3311hs181A.PV",
    "3311WI127.PV",
    "3311WI671.PV",
    "3311WIC151.PV",
    "CV2012.PV",
    "CV2015.PV",
    "CV2019.PV",
    "FD2005.PV",
    "FIC22302.PV",
    "FY22302CL2.CPV1",
    "JIC22366.PV",
    "SIC22371.MV",
    "SIC22371.SV",
    "WI151-127.CPV",
    "WIC22026A.PV",
    "YIC22001.PV"
]

HPGR = [
    "3311HS450.MV",
    "3311JI612A.PV",
    "3311JI612B.PV",
    "3311JY612.CPV",
    "3311LI081.PV",
    "3311LI540.PV",
    "3311PI543.PV",
    "3311PI591.PV",
    "3311PI591SP.SV",
    "3311SI361.PV",
    "3311SI364.PV",
    "3311SI614A.PV",
    "3311SI614B.PV",
    "3311WI140.PV",
    "3311WI323.PV",
    "3311WI331.PV",
    "3311WIC540.PV",
    "3311ZI535.PV",
    "3311ZI536.PV",
    "3311ZI561.PV",
    "3311ZI564.PV",
    "3311ZI615.PV",
    "3311ZI616.PV",
    "CV2010.PV",
    "CV2010II.PV",
    "CV2011.PV",
    "CV2011II.PV",
    "CV2018.PV",
    "CV2018II.PV",
    "FD2007.PV",
    "FD2007II.PV",
    "FD2007VSD.SV",
    "FD2013VSD.MV"
]
# 51 Machines for NN.

start = time.time()

if use_persisting:
    machine_shelve = shelve.open(os.path.join(SHELVE_PERSISTANCE_PATH, "machine.shelve"))
    relevant_machines = machine_shelve["Parsed_Machines"]
    machine_shelve.close()
    print("Read from machine.shelve")
else:
    machines = {}  # Collection of machine code: Machine object mappings.

    # Parse all unearthed-hackathon/Cadia plant downtime/PI/*.csv files.
    for perf_indicator_file in os.listdir(PERFORMANCE_INDICATOR_DATA):
        if not perf_indicator_file.endswith(".csv"):
            continue
        with open(os.path.join(PERFORMANCE_INDICATOR_DATA, perf_indicator_file), 'rb') as csv_file:
            contents = csv_file.readlines()
            contents = [str(l)[2:] for l in contents]  # Change bytes to strings, without leading 'b\'
            pi_parser = csv_pi_parser.CsvPISheetParser(contents, machines)
            machines = pi_parser.parse()
        print("Processed %s" % perf_indicator_file)

    relevant_machines = machines
    # [machines[code] for code in SAG_MILL_MACHINE_CODES]
    print("Parse PI time %s" % (time.time() - start))

    # All Machines Parsed, save in shelve
    machine_shelve = shelve.open(os.path.join(SHELVE_PERSISTANCE_PATH, "machine.shelve"))
    machine_shelve["Parsed_Machines"] = relevant_machines  # Save as array.
    machine_shelve.close()
    print("Wrote machines to shelve.")

if use_persisting:
    failure_shelve = shelve.open(os.path.join(SHELVE_PERSISTANCE_PATH, "failure.shelve"))
    failure_collection = failure_shelve["Parsed_Failures"]
    failure_shelve.close()
    print("Read from failure.shelve")
else:
    # Parse unearthed-hackathon/Cadia plant downtime/PPMS/Cadia Sag Mill 2 Years.csv
    with open(os.path.join(FAILURE_DATA, "Cadia Sag Mill 2 Years.csv"), "rb") as csv_file:  # Due to encoding need to read as bytes.

        contents = csv_file.readlines()
        # Convert to strings so can process.
        contents = [str(l) for l in contents]

        failure_parser = csv_failure_parser.CsvFailureSheetParser(contents)
        failure_collection = failure_parser.parse()

    print("Processed Cadia Sag Mill 2 Years.csv")

    print("Parse failures time %s" % (time.time() - start))
    # ALL FAILURES PARSED, save in shelve
    failure_shelve = shelve.open(os.path.join(SHELVE_PERSISTANCE_PATH, "failure.shelve"))
    failure_shelve["Parsed_Failures"] = failure_collection  # Saved as dict.
    failure_shelve.close()
    print("Wrote failures to shelve")

print("~~ Outputting stuff...")

"""
# Results for first quater 2016.
thresh_lower = datetime.datetime(2016, 1, 1)  # First month first day 2016.
thresh_upper = datetime.datetime(2016, 4, 1)  # 4th month 1nd day 2016

look_at_failures = [failure_collection[f_id] for f_id in failure_collection
                    if (
                        (failure_collection[f_id].end_time > thresh_lower) and (failure_collection[f_id].end_time < thresh_upper)
                    )]
"""

"""
important dates:
- 1/1/2016 (train): ~ 150 shutdowns
- 3/1/2016 (test): ~ 90 shut downs
data points per day= 1 * 60 * 60 * 24 = 864000
"""
# We want Jan 2.
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
                return -1  # Fail.
            # Continue
    return 1  # Pass

# Sorted failures.
look_at_these_failures = get_relevant_failures(training_day_lower, training_day_upper, failure_collection)

new_day = day.Day(training_day_lower, training_day_upper)
training_data_labels = [is_time_failure(time_of_day,look_at_these_failures) for time_of_day in new_day.datetime_instances]
print(training_data_labels)
print(len(training_data_labels))
print(len(new_day.datetime_instances))
print("Processed training labels")


def get_day_data(lower_bound, upper_bound, machines_to_look_at, writer):
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

with open(os.path.join(NEURAL_NETWORK_DATA_PATH, "training_data.csv"), "w") as csv_fh:
    csv_writer = csv.writer(csv_fh)
    csv_writer.writerow(training_data_labels)
    csv_writer.writerow(['apple'])
    get_day_data(training_day_lower, training_day_upper, machines_to_look_at, csv_writer)



"""
for failure in look_at_failures:

    wrote_times = False

    with open(os.path.join(DATAOUT_PATH, "failure_" + str(failure.id)) + ".csv", 'w') as csv_file:
        writer = csv.writer(csv_file)

        first_row = ''.join(["start time", str(failure.start_time), "," "end time", str(failure.end_time)])


        for machine in relevant_machines:
            relevant_data = machine.get_n_hours(1, failure.end_time)
            if not relevant_data:
                break
            writer.writerow([first_row])

            if not wrote_times:
                timestamps = [str(r[0]) for r in relevant_data]
                writer.writerow(timestamps)
                wrote_times = True

            pi_values = [str(r[1]) for r in relevant_data]

            writer.writerow([machine.code])
            writer.writerow(pi_values)

    print("Wrote failure_%d.csv" % failure.id)
"""
print("End time %s" % (time.time() - start))

