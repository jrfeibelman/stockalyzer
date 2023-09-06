from abc import abstractmethod, ABCMeta
from stockalyzer.core.Context import Context
from stockalyzer.strategy.TimeHorizon import TimeHorizon
from datetime import datetime

class Message(metaclass=ABCMeta):

    def __init__(self):
        pass
    
class TimerMessage(Message):
    __slots__ = '_ctx', '_time_horizon'

    def __init__(self, time_horizon):
         self._time_horizon = time_horizon
         self.reset_context()

    def reset_context(self):
        self._ctx = Context(self._time_horizon)

    def get_time(self):
        return self._time

    def get_context(self):
        return self._ctx

    def get_time_horizon(self) -> TimeHorizon:
        return self._time_horizon