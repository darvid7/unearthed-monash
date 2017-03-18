"""
@author: David Lei
@since: 18/03/2017
@modified: 

"""
import datetime

class Day:
    """Precondition: because day bounds are set, assume will never get the last day of the month."""
    def __init__(self, datetime_lower_bound, datetime_upper_bound):
        self.lower = datetime_lower_bound
        self.upper = datetime_upper_bound
        self.datetime_instances =  self._populate()

    def _populate(self):
        year = self.lower.year  # stay the same.
        month = self.lower.month  # stay the same.
        day = self.lower.day + 1  # + 1.
        datetime_instances = []
        time_s = 0
        for time_h in range(24):
            for time_m in range(60):
                new_dt = datetime.datetime(year, month, day, time_h, time_m, time_s)
                datetime_instances.append(new_dt)
        if len(datetime_instances) != 1440:
            raise ValueError("Bad date_timeinstances len: " + str(len(datetime_instances)))
        return datetime_instances

if __name__ == "__main__":
    # We want Jan 2.
    training_day_lower = datetime.datetime(2016, 1, 1, 23, 59, 59)  # Last second of Jan 1.
    training_day_upper = datetime.datetime(2016, 1, 3, 0, 0, 0)  # First second of Jan 2.

    d = Day(training_day_lower, training_day_upper)



