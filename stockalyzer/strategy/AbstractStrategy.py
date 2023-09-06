from abc import abstractmethod, ABCMeta
from stockalyzer.core.Context import Context
import stockalyzer.core.Event as Event # Circular Import Guard
from stockalyzer.strategy.TimeHorizon import TimeHorizon
from stockalyzer.referenceData.ReferenceDataManager import ReferenceDataManager
from numpy import zeros
from numpy import int8

class Strategy(metaclass=ABCMeta):

    __slots__ = '_indicators', '_printStats', '_isEnabled', '_strategyMgr', '_symbols', '_signals'

    def __init__(self, params_config, strategyMgr): 
        self._indicators = [] # dict{str:set(Indicator)}
        self._printStats = True if params_config.get_value("PrintStats", "false").lower() == 'true' else False
        self._isEnabled = False
        self._strategyMgr = strategyMgr
        symbols = params_config.get_value("Symbols", "INVALID")
        if symbols == "INVALID":
            self._symbols = ReferenceDataManager().getSymbolList()
        else:
            self._symbols = symbols.split(',')

        self._symbols = sorted(self._symbols)
        self._signals = zeros(len(self._symbols), dtype=int8)


    """ Other Abstract Methods to eventually add down the road
    - onRestarted() - for handling intraday container restarts

    """

    @abstractmethod
    def trigger(self) -> None:
        """ TODO:
        - Trigger an indicator for whether a security should be bought or sold based on a larger strategy
        """
        pass

    @abstractmethod
    def checkTriggerCondition(self) -> bool:
        """ 
        - Checks whether a strategy's trigger condition on its indicator has been met for whether a security should be bought or sold
        """

    @abstractmethod
    def onCycle(self, event: Event) -> bool:
        """
        Grid timer for triggering stats update & calling onCycle of strats
        """
        # Check if need to update (dirty)? Only if onCycle should also be triggered by something other than grid timer
        # Evaluate: 1) strategies for triggers, 2) circuit breakers?
        pass

    # @abstractmethod
    # def onTimerEvent(self, event: Event) -> bool:
    #     """
    #     - Used for strategy specific custom timer events. Not required
    #     - Trigger functionality on receiving timer event to calculate whether cb breach ? really?
    #     - @Returns bool whether successful or error
    #     - @Param ctx Context object with time info
    #     - @Param event timer event
    #     """
    #     pass

    @abstractmethod
    def onTDEvent(self, event: Event) -> bool:
        pass

    @abstractmethod
    def onMDEvent(self, event: Event):
        pass

    @abstractmethod
    def onEODEvent(self, event: Event) -> bool:
        pass

    @abstractmethod
    def onSODEvent(self, event: Event) -> bool:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def downloadHistoricalData(self) -> bool:
        pass

    @abstractmethod
    def log_stats(self, event : Event):
        pass

    def getIsEnabled(self):
        return self._isEnabled
    
    def addIndicator(self, indicator):
        self._indicators.append(indicator)

    # def getStats(self):
    #     return self._indicators

    # def getStatsFor(self, time_horizon: TimeHorizon):
    #     if time_horizon in self._stats:
    #         return self._stats[time_horizon]
    #     return set()

    # def addStat(self, time_horizon : TimeHorizon, stat):
    #     if time_horizon not in self._stats:
    #         self._stats[time_horizon] = set()
    #     self._stats[time_horizon].add(stat)

class InvalidStrategy(Strategy):
    def __init__(self):
        pass

    def trigger(self) -> None:
        raise Exception('Invalid Strategy')
    
    def onCycleEvent(self, event) -> bool:
        raise Exception('Invalid Strategy')

    def onTDEvent(self, event) -> bool:
        raise Exception('Invalid Strategy')

    def onMDEvent(self, event):
        raise Exception('Invalid Strategy')

    def onEODEvent(self, event) -> bool:
        raise Exception('Invalid Strategy')

    def onSODEvent(self, event) -> bool:
        raise Exception('Invalid Strategy')
    
    def log_stats(self, event):
        raise Exception('Invalid Strategy')

    # def onTimerEvent(self, event) -> bool:
    #     raise Exception('Invalid Strategy')

    def name(self) -> str:
        return "Invalid Strategy"