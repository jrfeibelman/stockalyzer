from multiprocess import Manager
from stockalyzer.core.Logger import Logger
from memory_profiler import profile
from copy import copy
from stockalyzer.core.Event import Event
from numpy import single
from stockalyzer.core.Cache import Cache

class StatsCache(Cache):
    __slots__ = '_dict'
    
    def __init__(self):
        self._dict = dict()

    def initialize(self, symbolUniverse) -> bool:
        self._dict = {sym:StatsCacheEntry(sym) for sym in symbolUniverse}
        return True

    def update(self):
        pass

    def updateOnEvent(self, event: Event) -> bool:
        """
        TODO:
        - combine timer, trade, and market event functions into one function 
        - instead of passing ctx or md or td, pass an event object that has this data
        """
        if event._eventType is Event.EventType.MarketDataEvent:
            self.updateOnMDEvent(event)
        elif event._eventType is Event.EventType.TimerEvent:
            self.updateOnTimerEvent(event)
        elif event._eventType is Event.EventType.TradeEvent:
            self.onTDEvent(event)
        else:
            Logger().error("Invalid Event Type.")
            return False

        return True

    def updateOnMDEvent(self, event):
        """
        Called on every Market Data Event
        @Param: md : MarketDataEvent
        """
        md = event.getMessage()
        symbol = md._symbol
        if symbol not in self._dict:
            Logger().error("Symbol [%s] not in universe [%s]" % (symbol, self._dict.keys()))
            return False

        self._dict[symbol].updateOnMDEvent(event)
        
        return True

    def addUpdateFuncOnMDEvent(self, update_func):
        for entry in self._dict.values():
            entry.addUpdateFuncOnMDEvent(update_func)

    def add_stat(self, stat_name, stat_type, default_value):
        # print("Adding Stat: %s: %s = %s" % (stat_name, stat_type, default_value))
        # print("To cache: %s" % self._dict.values())
        for entry in self._dict.values():
            # print("CacheEntry: %s" % entry)
            entry.add_stat(stat_name, stat_type, default_value)

    def download_cache_data(self):
        return True #FIXME

class StatsCacheEntry(Cache):
    def __init__(self, symbol):
        m = Manager()
        super().__init__(cache_dict=m.dict(), lock=m.Lock())
        self._symbol: str = symbol
        self._updateFuncsOnMD = set() # TODO need to use multiprocess manager?
        # TODO: use cython and numpy for all of these
        # need a list of tuples, first value is variable storage vs second is function to call
                # or maybe use a dict of stat_name: (value, update_func())
        # This should all be initialized properly on init
        self.add_stat('price', single, 0.0)
        self.add_stat('last_price', single, 0.0)

    def initialize(self) -> bool:
        return super().initialize()

    def updateOnMDEvent(self, md):
        with self.Lock:
            Logger().debug("Updating %s from %s to %s" % (self._symbol, self._dict['price'], md._msg))
            self.update_base_stats(md)
            for func in self._updateFuncsOnMD:
                func(self, md) # TODO 
            
            Logger().debug("%s : %s " % (self._symbol, self._dict))

    def update(self):
        return super().update()
    
    def update_base_stats(self,  md):
        self._dict['last_price'] = copy(self._dict['price'])
        self._dict['price'] = md._msg._price

    def __str__(self):
        stats = ", ".join(["%s: %s" % (k,v) for k,v in self._dict.items()])
        return "%s: [ %s]\n" % (self._symbol, stats)

    __repr__ = __str__

    def add_stat(self, stat_name, stat_type, default_value) -> bool:
        try:
            self._dict[stat_name] = stat_type(default_value)
            return True
        except:
            return False

    def addUpdateFuncOnMDEvent(self, update_func):
        self._updateFuncsOnMD.add(update_func)