"""
@author: David Lei
@since: 18/03/2017
@modified: 

"""
import datetime


class Failure:
    """Represents a failure in the SAG mill."""
    def __init__(self, id, start_time, end_time, actual_mins_downtime, effective_mins_downtime, unplanned,
                 problem_type, problem_cause, remedy, equipment_num, description, comments):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.actual_mins_downtime = actual_mins_downtime
        self.effective_mins_downtime = effective_mins_downtime
        self.unplanned = unplanned
        self.problem_type = problem_type
        self.problem_cause = problem_cause
        self.remedy = remedy
        self.equipment_num = equipment_num
        self.description = description
        self.comments = comments

