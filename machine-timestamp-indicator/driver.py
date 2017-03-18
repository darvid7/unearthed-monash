"""
@author: David Lei
@since: 18/03/2017
@modified: 

"""
import os
import time
import csv
from model import csv_pi_parser
from model import csv_failure_parser

# Constants
PERFORMANCE_INDICATOR_DATA = "/Users/David/Desktop/unearthed-2017/unearthed-monash/unearthed-monash/" \
                             "machine-timestamp-indicator/data/in/perf-indicator"
FAILURE_DATA = "/Users/David/Desktop/unearthed-2017/unearthed-monash/unearthed-monash/machine-timestamp-indicator/" \
               "data/in/failures/"

DATAOUT_PATH = "/Users/David/Desktop/unearthed-2017/unearthed-monash/unearthed-monash/machine-timestamp-indicator/" \
               "data/out/leading-up-to-failures/"

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

start = time.time()

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

relevant_machines = [machines[code] for code in machines.keys()]
# [machines[code] for code in SAG_MILL_MACHINE_CODES]

# Parse unearthed-hackathon/Cadia plant downtime/PPMS/Cadia Sag Mill 2 Years.csv
with open(os.path.join(FAILURE_DATA, "Cadia Sag Mill 2 Years.csv"), "rb") as csv_file:  # Due to encoding need to read as bytes.

    contents = csv_file.readlines()
    # Convert to strings so can process.
    contents = [str(l) for l in contents]

    failure_parser = csv_failure_parser.CsvFailureSheetParser(contents)
    failure_collection = failure_parser.parse()

print("Processed Cadia Sag Mill 2 Years.csv")

print("~~ Outputting stuff...")

for failure_id in failure_collection:

    with open(os.path.join(DATAOUT_PATH, "failure_" + str(failure_id)) + ".csv", 'w') as csv_file:
        writer = csv.writer(csv_file)

        failure = failure_collection[failure_id]
        first_row = ''.join(["start time", str(failure.start_time), "," "end time", str(failure.end_time)])

        writer.writerow([first_row])

        for machine in relevant_machines:

            relevant_data = machine.get_n_hours(1, failure.end_time)
            timestamps = [str(r[0]) for r in relevant_data]
            pi_values = [str(r[1]) for r in relevant_data]

            writer.writerow([machine.code])
            writer.writerow(timestamps)
            writer.writerow(pi_values)
        break





print("End time %s" % (time.time() - start))

