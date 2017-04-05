"""
@author: David Lei
@since: 19/03/2017
@modified: 

"""
import os
import csv

FACTOR = 100000

class GraphMachineComponents:
    def __init__(self, code, descr, simple_descr, dt_lt_eq_value, greater_machine, samples):
        self.code = code
        self.descr = descr
        self.simple_descr = simple_descr
        self.greater_machine = greater_machine
        self.dt_lt_eq_value = str(float(dt_lt_eq_value)/float(FACTOR))
        self.samples = samples
        self.PI_DATA = [] # in order insertion.

GRAPH_DIR = "/Users/David/Desktop/unearthed-2017/unearthed-monash/unearthed-monash/graphs-dt-params"
DT_RELEVANT_MACHINE_COMPONENTS = "dt-values.csv"
PI_MACHINE_HEADERS = "machine-headers.csv"
PI_MACHINE_DATA = "pre-down-6-43-pm.csv"
WRITE_OUT_CSV = "out-graphme.csv"

# Format = code: [Greater Machine, PI Description,  Simplified Description]
machine_code_mappings =  {
    "3311JI612B.PV": ["HPGR", "HPGR FltRlr Drv Pwr", " HPGR floating roller power	"],
    "FY22302CL2.CPV1": ["SAG", " ML001 Fd Wtr %Sol Fdbk CALC CPV1 	", ""],
    "JIC22366.PV": ["SAG", " ML001 Power Cntrl PV	", " ML001 power	"],
    "3311WIC540.PV": ["HPGR", " HPGR Fd Bn Wght Cntl 	", ""],
    "3311WI331.PV": ["HPGR", " HPGR Fd Xfr CV Feedrate 	", " CV2010 feedrate	"],
    "FD2013VSD.MV":  ["HPGR", "  HPGR Bypass Feeder MV 	", " FD2013 HPGR bypass bin feeder speed	"],
    "3311LI540.PV": ["HPGR", " HPGR Bin level 	", " HPGR feed bin level	"],
    "WIC22026A.PV": ["SAG", " ML001 Weight --> Feed Cntrl PV	", " ML001 weight	"]
}

graph_these_machine_components = {}

with open(os.path.join(GRAPH_DIR, DT_RELEVANT_MACHINE_COMPONENTS), 'r') as csv_fh:
    contents = csv_fh.readlines()
    for row in contents:
        data = row.split()
        machine_code = data[0].lstrip().rstrip()
        dt_lt_eq_value = data[2]
        samples_pert = data[5]
        print(machine_code)
        m_tag_mapping_data = machine_code_mappings[machine_code]
        greater_machine = m_tag_mapping_data[0].lstrip().rstrip()
        descr = m_tag_mapping_data[1].lstrip().rstrip()
        simple_descr = m_tag_mapping_data[2].lstrip().rstrip()

        new_mac_comp = GraphMachineComponents(machine_code, descr, simple_descr, dt_lt_eq_value, greater_machine, samples_pert)
        graph_these_machine_components[machine_code] = new_mac_comp

machine_tag_indexes = {}

with open(os.path.join(GRAPH_DIR, PI_MACHINE_HEADERS), 'r') as csv_fh:
    contents = csv_fh.readlines()
    data = contents[0]
    data = data.split(",") # Index 1 = time stamp, rest are machine tags
    index = 0
    for m_tag in data:
        m_tag = m_tag.strip("\n\r, ")
        m_tag = m_tag.lstrip().rstrip()
        if m_tag in graph_these_machine_components: # care about this index
            machine_tag_indexes[index] = m_tag
        # Else don't need this data.
        index += 1

# Get actual PI data
with open(os.path.join(GRAPH_DIR, PI_MACHINE_DATA), 'r') as csv_fh:
    contents = csv_fh.readlines()
    for csv_string in contents:
        csv_data = csv_string.split(",")
        for i in range(len(csv_data)):
            if i in machine_tag_indexes:
                machine_pi_col = csv_data[i]
                machine_tag = machine_tag_indexes[i]
                machine_comp_obj = graph_these_machine_components[machine_tag]
                machine_comp_obj.PI_DATA.append(machine_pi_col)
            # Else don't care about it

with open(os.path.join(GRAPH_DIR, WRITE_OUT_CSV), 'w') as csv_fh:
    w = csv.writer(csv_fh)
    for machine_tag, machine_comp_obj in graph_these_machine_components.items():
        row = [machine_tag] + machine_comp_obj.PI_DATA
        w.writerow(row)

    for _, machine_comp_obj in graph_these_machine_components.items():
        m_data = ','.join([machine_comp_obj.code, machine_comp_obj.descr, machine_comp_obj.simple_descr,
                           machine_comp_obj.greater_machine,
                           machine_comp_obj.dt_lt_eq_value,
                           machine_comp_obj.samples])
        print(m_data)
        w.writerow([m_data])