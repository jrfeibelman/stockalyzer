from stockalyzer.strategy.TimeHorizon import TimeHorizon
from stockalyzer.core.Context import Context
from stockalyzer.core.Event import Event
from stockalyzer.core.Logger import Logger
from threading import Timer as Thread_Timer
from numpy import uint8

class TimerManagerNew:
    # TODO create one loop that checks how many secs have passed, and calls correct callbacks every interval for single timer loop
    __slots__ = '_callbacks'

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance._callbacks = dict()
        return cls._instance

    def start_timers(self) -> None:
        pass #TODO
        # for t in self._timers.values():
        #     t.start()

    def stop_timers(self) -> None:
        pass #TODO
        # Logger().info("Joining Timers.........")
        # for t in self._timers.values():
        #     Logger().info(t)
        #     t.cancel()
        # Logger().info("All Timers Joined.........")

    def add_timer(self, time_horizon: TimeHorizon, callback_func, override=False) -> bool:
        if override: # What is this???
            return False
        self._timers[time_horizon] = Thread_Timer(TimeHorizon.getTimeHorizonNumInSecs(time_horizon), self._callback_func, [time_horizon])

        if time_horizon not in self._callbacks:
            self._callbacks[time_horizon] = [callback_func]
        else:
            self._callbacks[time_horizon].append(callback_func)

        return True
    
    def _callback_func(self, time_horizon : TimeHorizon):
        for clbk in self._callbacks[time_horizon]:
            clbk(time_horizon)

    def reset_timer(self, time_horizon : TimeHorizon) -> bool:
        if time_horizon in self._timers:
            self._timers[time_horizon] = Thread_Timer(TimeHorizon.getTimeHorizonNumInSecs(time_horizon), self._callback_func, [time_horizon])
            self._timers[time_horizon].start()
            return True
        return False

    def timer_callback(func):
        """
        A decorator for callback functions from timers 
        """
        def wrapper(self, time_horizon : TimeHorizon):
            e = Event.create_timer_event(time_horizon)
            # Logger().debug("JRF Event Created: %s" % e)
            func(self, e)
            TimerManager().reset_timer(time_horizon)
        return wrapper