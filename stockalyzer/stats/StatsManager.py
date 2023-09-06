from stockalyzer.core.Logger import Logger
from stockalyzer.stats.StatsCache import StatsCache
from stockalyzer.proto.mdp.MdpMessage import MdpMessage
from stockalyzer.engine.Module import Module, ModuleEnum
from stockalyzer.referenceData.ReferenceDataManager import ReferenceDataManager

"""
TODO:
- change cache access for stats to combination of _stats + market data manager
- change strategy to leverage indicators instead of in process logic
- ensure calling onCycle and other functions with new context instead of cache
- ensure strategy & indicators are MULTI stock - need to add some sort of dict 
- Move latest market data cache persistance to StrategyManager
- 2 Threads:
    1) MarketDataThread
        -
    2) WorkerThread
        -
"""



""" TODO cache only supports unique instrument. Cannot have two different markets with same instrument. Support querying by sym + market.

TODO Is this class necessary? On first look no, but if want to convert code to c++ this would be a prime candidate and to use a common API like StatsManager for all computation heavy calculations for strategies then use of this class seems warranted
"""

class StatsManager(Module):

    __slots__ = '_cache', '_symbols'

    def __new__(cls):
        if not cls.hasInstance():
            cls._instance = super(StatsManager, cls).__new__(cls)
            cls._instance._cache = StatsCache()
        return cls._instance

    def __init__(self):
        super().__init__(ModuleEnum.StatsManager)

    @classmethod
    def hasInstance(cls) -> bool:
        return hasattr(cls, '_instance')

    def initialize(self, config):
        Logger().info("Initializing StatsManager")

        if not ReferenceDataManager.hasInstance():
            Logger().error("Unable to initialize Worker Thread without Reference Data already initialized. Terminating")
            return False

        self._symbols = ReferenceDataManager().getSymbolList()
        Logger().info("SymbolList: %s" % self._symbols)

        # TODO on startup get all historic MD needed ... keep in memory? NO - use then discard ... ? - strateMgr

        return self._cache.initialize(self._symbols)

    def registerStatistic(self, stat_name, stat_type, default_value):
        self._cache.add_stat(stat_name, stat_type, default_value)

    def getCache(self):
        return self._cache

    def download(self) -> bool:
        return self._cache.download_cache_data()

    def onMDEvent(self, event) -> bool:
        mdm = event.getMessage()
        sym = mdm.getSymbol()

        # if sym not in self._marketDataCache:
        #     print("Invalid symbol [%s] provided" % sym)
        #     return False

        # FIXME seq num check
        # if self._marketDataCache[sym].getSeqNum() >= mdm.getSeqNum():
        #     print("Received out of sequence market data [%s]. Not processing %s" % (mdm.getSeqNum(), mdm))
        #     return False

        return True
