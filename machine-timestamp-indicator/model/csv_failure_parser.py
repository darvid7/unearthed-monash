"""
@author: David Lei
@since: 18/03/2017
@modified: 

"""
import datetime
from .failure import Failure


class CsvFailureSheetParser:

    """Note: Time is stored differently in this csv file

    Timestamp: 2016-08-05 04:35:00.000
    Date: 2016-08-05
    Time: 04:35:00.000 # already in 24 hour format.
    """

    def __init__(self, csv_array):
        self.csv_array = csv_array
        self.failures = {}

    def _to_int(self, s):
        """Truncates leading 0s from string and casts to integer."""
        try:
            s = int(s.lstrip('0'))
            return s
        except ValueError:
            return 0  # s is of form '00', return int(s) = 0.

    def _process_time(self, time_segment):
        """Process time stamp of form  12:00:00 PM by:
            - removing leading 0s for each unit.
            - casing to int.

        :returns: hours, minutes, seconds as integers in 24 hour format acceptable by datetime.datetime().
        """
        hours, minutes, seconds = time_segment.split(':')
        hours = self._to_int(hours)
        minutes = self._to_int(minutes)
        seconds = int(round(float(seconds), 1))
        if str(seconds)[0] == "0":
            seconds = self._to_int(str(seconds))

        return hours, minutes, seconds

    def parse_timestamp(self, timestamp):
        """Parse timestamp of form:
            - '2016-08-05 04:35:00.000'

        :returns: datetime.datetime() object with timestamp data (sortable).
        """
        date_segment, time_segment = timestamp.split(' ', 1)
        year, month, day = date_segment.split('-')

        year = self._to_int(year)
        day = self._to_int(day)
        month = self._to_int(month)

        hours, minutes, seconds = self._process_time(time_segment)
        # Expected params: datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]]
        datetime_timestamp = datetime.datetime(year, month, day, hours, minutes, seconds)
        return datetime_timestamp

    def parse(self):
        important_columns = {
            "col_start_time": 4,
            "col_end_time": 5,
            "col_actual_mins_downtime": 7,
            "col_effective_mins_downtime": 8,
            "col_unplanned": 10,
            "col_problem_type": 11,
            "col_problem_cause": 12,
            "col_remedy": 13,
            "col_equipment_num": 14,
            "col_description": 15,
            "col_comments": 16
        }

        failure_count = 1

        csv_body = self.csv_array[1:]
        for row in csv_body:
            row_data = row.split(",")
            # Extract relevant information for each row in csv file.
            unplanned = row_data[important_columns["col_unplanned"]]
            if unplanned == "Planned":  # Skip planned failures.
                continue

            start_time = row_data[important_columns["col_start_time"]]
            end_time = row_data[important_columns["col_end_time"]]
            actual_mins_downtime = row_data[important_columns["col_actual_mins_downtime"]]
            effective_mins_downtime = row_data[important_columns["col_effective_mins_downtime"]]
            problem_type = row_data[important_columns["col_problem_type"]]
            problem_cause = row_data[important_columns["col_problem_cause"]]
            remedy = row_data[important_columns["col_remedy"]]
            equipment_num = row_data[important_columns["col_equipment_num"]]
            description = row_data[important_columns["col_description"]]
            comments = row_data[important_columns["col_comments"]]

            # Convert data types.
            start_time = self.parse_timestamp(start_time)
            end_time = self.parse_timestamp(end_time)
            actual_mins_downtime = float(actual_mins_downtime)
            effective_mins_downtime = float(effective_mins_downtime)

            new_failure = Failure(failure_count, start_time, end_time, actual_mins_downtime, effective_mins_downtime,
                                  unplanned, problem_type, problem_cause, remedy, equipment_num, description, comments)
            self.failures[failure_count] = new_failure
            failure_count += 1

        return self.failures
