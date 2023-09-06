import stockalyzer.core.Event as Event
from stockalyzer.core.Context import Context
from stockalyzer.stats.indicators.AbstractIndicator import AbstractIndicator
from stockalyzer.stats.StatsManager import StatsManager
from stockalyzer.core.Logger import Logger
from numpy import double, ushort, array

"""
TODO: design
- all indicator variables have a value variable 
- in strategy code check indicator against predetermined condition
    - for example, for EMAIndicator can check if indicator > 0
    - or for RSIIndicator can check if indicator > 40 or any other value

init func should register onCycle callback timer based on params passed
    - what if multiple time horizons needed??
    - Simple, init func for that given strategy can just register an extra timer

Is it bad to have so many timers?
    - Would having one timer for each interval calling each clients callback in for loop be better than having multiple classes use timers of same length
    - both are bad
    - should switch to using task scheduling via a priority queue
        - Queue.PriorityQueue
    * For now, think we should go through timer manager to use shared timers (PRIORITY QUEUE so can control whose callbacks executed first)
        * python asynchronously pushes event to strategy manager, which receives it and calls the c++ code 
    *** SOLUTION: use one onCycle timer, and instead of strategies having their own timers they can just do lastTime - nowTime < cycleTime to mock timer func
        TODO implement above

Eventually should have python strategy manager and c++ strategies that have all computation heavy code    
"""

class EMAIndicator(AbstractIndicator):

    __slots__ = '_values', '_symbols', '_period', '_decayFactor', '_statsMgr', '_stratMgr'

    def __init__(self, stratMgr, symbols, period, decayFactor):
        super().__init__(stratMgr, symbols)
        self._period = ushort(period)
        self._decayFactor = decayFactor
        self._statsMgr = StatsManager()

        # for i in range(len(self._symbols)):
        #     self._values[i] = (double(0), double(0), double(0))
                            # (value,     prevValue, sodValue)
            # dt = dtype([('value', double, 0.0), ('prevValue', double, 0.0), ('sodValue', double, 0.0)])
            # self._values[t] = dt

        for i in range(len(self._symbols)):
            sym = self._symbols[i]
            mdm = self._stratMgr.getMarketDataSnapshot(sym)

            if mdm.isEmpty():
                Logger().error("During Initialization Market Data hasn't been received for [%s]" % sym)
                continue

            self._values[i] = mdm.getPrice()
            self._sodValues[i] = mdm.getPrice()

    def onCycle(self, event: Event.Event) -> bool:
        for i in range(len(self._symbols)):
            # TODO update func
            mdm = self._stratMgr.getMarketDataSnapshot(t)
            
            if mdm.isEmpty():
                Logger().warn("Warning : Market Data hasn't been received for [%s]" % sym)
                continue

            value = self._values[i]
            sodValue = self._sodValues[i]

            newValue = double(mdm.getPrice() * self._decayFactor + sodValue * (1.0 - self._decayFactor))

            self._prevValues[i] = value
            self._values[i] = newValue
        return True
    
    def onSingleCycle(self, idx):
        sym = self._symbols[idx]
        mdm = self._stratMgr.getMarketDataSnapshot(sym)
        
        if mdm.isEmpty():
            Logger().warn("Warning : Market Data hasn't been received for [%s]" % sym)
            return

        value = self._values[idx]
        sodValue = self._sodValues[idx]

        newValue = double(mdm.getPrice() * self._decayFactor + sodValue * (1.0 - self._decayFactor))

        self._prevValues[idx] = value
        self._values[idx] = newValue
    
    def __getitem__(self, idx) -> double:
        return self._values[idx]

    def onEODEvent(self, event: Event.Event) -> bool:
        # TODO save value for retreival?
        return True

    def onSODEvent(self, event: Event.Event) -> bool:
        sod_values = dict()
        # TODO download data and set SOD value
        
        for t in self._symbols:
            val = self._values[t]
            self._values[t] = (val[0], val[1], sod_values[t])

        return True

    def name(self) -> str:
        return "EMAIndicator[%s]" % self._period

    def getPeriod(self):
        return self._period