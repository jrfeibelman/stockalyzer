

from stockalyzer.stats.StatsCache import StatsCache
from time import perf_counter
from stockalyzer.core.Logger import Logger
from stockalyzer.engine.Module import Module, ModuleEnum

class StockalyzerControls(Module):

    __slots__ = '_enforceControls'

    def __init__(self):
        super().__init__(ModuleEnum.Controls)
        self._enforceControls = False

    def initialize(self, config) -> bool:
        Logger().info("Initializing Controls")
        self._enforceControls = True if config.get_value('EnforceControls', 'false').lower() == 'true' else False
        return True

    def start(self):
        # TODO if implement this method, must check if initialized since controls is optional
        pass

    # def on_start(self):
    #     pass

    # def on_stop(self):
    #     pass

    def log_stats(self, ctx):
        Logger().info("Logging Stats")
        # TODO

    # def onMDEvent(self, event) -> bool:
    #     Logger().info("Received Market Data: %s" % event._msg)
    #     start = perf_counter()
    #     self._cache.updateOnMDEvent(event)
    #     dt = perf_counter() - start
    #     Logger().info("New Cache: %s" % self._cache)
    #     # print("OnMDEvent took %s per update" % dt)
    #     return True


    def onTimerEvent(self, event) -> bool:
        return True

    def onTDEvent(self, event) -> bool:
        return True

    def __str__(self) -> str:
        return "StockalyzerControls"

    __repr__ = __str__
