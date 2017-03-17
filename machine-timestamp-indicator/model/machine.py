"""
@author: David Lei
@since: 18/03/2017
@modified: 

"""
import os
import datetime
from collections import defaultdict



class Machine:

    def __init__(self, code, location):
        self.code = code
        self.location = location
        self.timestamp_perf_indicator_mapping = {}

    def add_timestamped_perf_indicator(self, timestamp, perf_indicator):
        self.timestamp_perf_indicator_mapping[timestamp] = perf_indicator






