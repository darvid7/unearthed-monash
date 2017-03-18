"""
@author: David Lei
@since: 18/03/2017
@modified: 

"""
import datetime

class Machine:


    def __init__(self, code):
        # Static care only about SQG mill.

        self.code = code
        self.location = None
        self.timestamp_perf_indicator_mapping = {}

    def add_timestamped_perf_indicator(self, datetime_timestamp, perf_indicator):
        if not isinstance(datetime_timestamp, datetime.datetime):
            raise TypeError("Invalid time stamp (%s) type %s" % (datetime_timestamp, datetime_timestamp.__class__))
        self.timestamp_perf_indicator_mapping[datetime_timestamp] = perf_indicator

    def get_daily_data(self, lower_bound, upper_bound):
        """Method to grab data points in a day for Neural Network."""
        results = []  # Should be datetime, pi tuples
        for datetime_object in self.timestamp_perf_indicator_mapping.keys():
            if (datetime_object > lower_bound) and (datetime_object < upper_bound):
                results.append((datetime_object, self.timestamp_perf_indicator_mapping[datetime_object]))
        if len(results) != 1440:
            raise ValueError("bad results len: " + str(len(results)))
        results.sort(key=lambda t: t[0])  # sort by datetime object.
        # print(len(results))
        # print(results)
        return results


    def get_n_hours(self, n, shutdown_time):
        """Returns ordered list of (timestamp, performance_indicator) tuples for the last n hours from the time of a shutdown (shutdown_time)

        :param n: Integer, represents hours.
        :param shutdown_time: datetime.datetime() object, time of a shut down.
                Can compare 2 datetime.datetime() objects using == but not is.

        :return: Array of (datetime.datetime() timestamps, perf_indicator_values) tuples prior to shutdown
            (and including if matched datetime.datetime() timestamp)
        """
        max_records = n * 1 * 60
        timestamps_perf_indicators = self._sort_timestamps()
        for i in range(len(timestamps_perf_indicators)):
            datetime_perf_tuple = timestamps_perf_indicators[i]
            datetime_timestamp = datetime_perf_tuple[0]
            if datetime_timestamp == shutdown_time:  # Get entries looping backwards inclusive.
                truncated = timestamps_perf_indicators[:i+1]
                return self._get_entries_from_shutdown(truncated, True, max_records)
            elif datetime_timestamp > shutdown_time:  # Get entries looping backwards exclusive.
                truncated = timestamps_perf_indicators[:i]
                return self._get_entries_from_shutdown(truncated, False, max_records)
            else:
                pass

    def _get_entries_from_shutdown(self, truncated_array, on_shutdown, max_records):
        """

        :param truncated_array: Array of (datetime.datetime() timestamps, perf_indicator_values) tuples up until
            shutdown entry inclusive.
        :param on_shutdown: Boolean, if shutdown timestamp is matched.
        :param max_records: Integer, max number of records to return.
        :return: Array of (datetime.datetime() timestamps, perf_indicator_values) tuples prior to shutdown
            (and including if matched datetime.datetime() timestamp)
        """
        if max_records >= len(truncated_array):
            if on_shutdown:
                return truncated_array
            else:
                return truncated_array[:-1]
        # Return less than size of truncated_array.
        # Retrieve entries [lower_bound, .., on_shutdown] where len entries == max_records.
        if on_shutdown:
            lower_bound = len(truncated_array) - max_records
            return truncated_array[lower_bound:]
        else:
            lower_bound = len(truncated_array) - max_records - 1
            return truncated_array[lower_bound: -1]

    def _sort_timestamps(self):
        timestamps_perf_indicator_array = list(self.timestamp_perf_indicator_mapping.items())
        timestamps_perf_indicator_array.sort(key=lambda t:t[0])  # Sort by datetime.datetime() objects.
        return timestamps_perf_indicator_array






