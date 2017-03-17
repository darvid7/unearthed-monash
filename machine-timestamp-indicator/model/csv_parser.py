"""
@author: David Lei
@since: 18/03/2017
@modified: 

"""
class CsvSheetParser:
    """Parses

    Args:
        csv_data:
        parsed_machines: collections.defaultdict(list), maps String (machine code) to list of timesamp PI values.

    """

    def __init__(self, csv_data, parsed_machines):
        self.csv_data = csv_data
        self.machines = parsed_machines

    def parse(self):
        headers = self.csv_data[0]
        machines = headers[1:]

        for m in machines:
            if not m in self.machines:
                print("Warn: Machine %s not in machines", m)
                new_machine = Machine()
                self.machines[new_machine.code] = new_machine

        for row in self.csv_data:
            row_data = row.split(',')
            timestamp = row_data[0]
            machine_perf_indicator_values = row_data[1:]
            for i in range(len(machine_perf_indicator_values)):
                machine_code = machines[i]
                perf_indicator_value = machine_perf_indicator_values[i]
                machine = self.machines[machine_code]
                machine.add_timestamped_perf_indicator(timestamp, perf_indicator_value)

        return self.machines
