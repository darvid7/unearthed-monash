"""
@author: David Lei
@since: 18/03/2017
@modified: 

"""
import datetime
from .machine import Machine


class CsvPISheetParser:
    """Parses a unearthed-hackathon/Cadia plant downtime/PI/*.csv files.

    Reads in first row as machines and aggregates dict of machine component.
    Each col has the PI values for that machine component. Adds each row's timestamp and PI value for each machine
    component to Machine object.

    Note: Machine sometimes used interchangeably with machine component.

    Args:
        csv_array: result of csv_file.readlines()
        parsed_machines: dictionary of machine_code (string): machine (Machine) mappings.
    """
    def __init__(self, csv_array, parsed_machines):
        self.csv_array = csv_array
        self.machines = parsed_machines

    def _to_int(self, s):
        """Truncates leading 0s from string and casts to integer."""
        try:
            s = int(s.lstrip('0'))
            return s
        except ValueError:
            return 0  # s is of form '00', return int(s) = 0.

    def _convert_to_24_hours(self, time_segment):
        """Process time stamp of form  12:00:00 PM by:
            - removing leading 0s for each unit.
            - casing to int.
            - converting to 24 hour format.

        :returns: hours, minutes, seconds as integers in 24 hour format acceptable by datetime.datetime().
        """
        hours, minutes, trailing = time_segment.split(':')
        hours = self._to_int(hours)
        minutes = self._to_int(minutes)
        seconds, cycle = trailing.split()
        seconds = self._to_int(seconds)

        # Convert to 24 hours.
        if cycle == "PM" and hours != 12:
            hours = int(hours) + 12

        return hours, minutes, seconds

    def parse_timestamp(self, timestamp):
        """Parse timestamp of form:
            - '1/03/2015 12:02:00 AM'
            - '1/03/2015 12:00:00 PM'

        :returns: datetime.datetime() object with timestamp data (sortable).
        """
        date_segment, time_segment = timestamp.split(' ', 1)
        day, month, year = date_segment.split('/')
        year = self._to_int(year)
        day = self._to_int(day)
        month = self._to_int(month)

        hours, minutes, seconds = self._convert_to_24_hours(time_segment)
        # Expected params: datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]]

        datetime_timestamp = datetime.datetime(year, month, day, hours, minutes, seconds)
        return datetime_timestamp

    def parse(self):
        headers = self.csv_array[0].split(',')
        machines = headers[1:]

        for m in machines:
            m = m.strip("'\\n\\r")

            if m not in self.machines:
                print("Warn: Machine %s not in machines" % m)
                new_machine = Machine(m)
                self.machines[new_machine.code] = new_machine

        for row in self.csv_array[1:]:
            row_data = row.split(',')
            timestamp = row_data[0]
            datetime_timestamp = self.parse_timestamp(timestamp)
            machine_perf_indicator_values = row_data[1:]
            for i in range(len(machine_perf_indicator_values)):
                machine_code = machines[i].strip("'\\n\\r")
                perf_indicator_value = machine_perf_indicator_values[i].strip("'\\n\\r")  # May be 'No Data'
                machine = self.machines[machine_code]
                machine.add_timestamped_perf_indicator(datetime_timestamp, perf_indicator_value)

        return self.machines
