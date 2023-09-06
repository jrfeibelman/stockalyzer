from abc import abstractmethod, ABCMeta
from stockalyzer.core.Logger import Logger
from threading import Thread
from stockalyzer.strategy.StrategyManager import StrategyManager
from stockalyzer.core.Timer import TimerManager
from stockalyzer.engine.StockalyzerControls import StockalyzerControls

class WorkerThread(Thread):
    """
    Class for WorkerThreads to pull market data off queue and update the cache
    """

    __slots__ = '_strat_mgr', '_queue', '_controls'

    def __init__(self, queue, config):
        super().__init__()
        self._queue = queue
        self._controls = None

        Logger().info("Initializing StrategyManager")
        self._strat_mgr = StrategyManager()
        if not self._strat_mgr.initialize(config.expand('StrategyConfiguration')):
            Logger().error("Strategy Manager failed to initialize. Terminating")
            return False

        if config.expand('Resources').expand('Modules').contains('Controls'):
            Logger().info("Initializing StockalyzerControls")
            self._controls = StockalyzerControls() # TODO implement circuit breakers
            if not self._controls.initialize(config.expand('Resources').expand('Modules').expand('Controls')):
                Logger().instance.error("Stockalyzer Controls failed to initialize. Terminating")
                return False

    def get_strategy_manager(self):
        return self._strat_mgr

    def pollForMarketData(self):
        while 1:
            event = self._queue.get()
            if event is None:
                Logger().error('%s: Exiting' % self)
                self._queue.task_done()
                break

            Logger().debug('%s - Consumed MDEvent : %s' % (self, event))
            self._strat_mgr.onMDEvent(event)
            self._queue.task_done()

    def run(self):
        if self._controls:
            self._controls.start()
        self.pollForMarketData()

    @TimerManager.timer_callback
    def onTimerEvent(self, event):
        # print("onTimerEvent: %s" % event._msg.get_time_horizon())
        self._strat_mgr.onTimerEvent(event)

    @TimerManager.timer_callback
    def on_grid_timer(self, event):
        Logger().debug("On_Timer[GRID:15s]") # TODO replace w timer event time horizon
        self._strat_mgr.onCycle(event)

    @TimerManager.timer_callback
    def on_timer_10_sec(self, event):
        Logger().debug("On_Timer[10s]")
        self.onTimerEvent(event)
        # print(" ON 10 [%s] : %s" % (hex(id(self._controls)), self._controls))

    @TimerManager.timer_callback
    def on_timer_60_sec(self, event):
        Logger().debug("On_Timer[60s]")
        # self.onTimerEvent(event) # this timer used for triggering 60 sec time horizon callbacks
        self._strat_mgr.log_stats(event.getMessage())
        self._controls.log_stats(event.getMessage())