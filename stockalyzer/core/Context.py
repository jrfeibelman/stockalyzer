
from datetime import datetime
from numpy import uint64
from stockalyzer.strategy.TimeHorizon import TimeHorizon

class Context:
    __slots__ = '_time', '_seq_num','_count', '_time_horizon'
    SEQ_NUM = uint64(0)

    def __init__(self, time_horizon=TimeHorizon.Day1):
        self._time = datetime.now()
        self._seq_num = self.get_seq_num()
        self._time_horizon = time_horizon

    def reset_time(self):
        self._time = datetime.now()

    def get_time(self):
        return self._time

    @classmethod
    def get_seq_num(cls):
        cls.SEQ_NUM += uint64(1)
        return cls.SEQ_NUM

    def get_time_horizon(self) -> TimeHorizon:
        return self._time_horizon