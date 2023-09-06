from stockalyzer.strategy.AbstractStrategy import Strategy, InvalidStrategy
from stockalyzer.strategy.EMAStrategy import EMAStrategy
from stockalyzer.core.Logger import Logger
from time import perf_counter
from stockalyzer.stats.StatsManager import StatsManager
from stockalyzer.engine.Module import Module, ModuleEnum
from stockalyzer.proto.mdp.MdpMessage import MdpMessage
from stockalyzer.referenceData.ReferenceDataManager import ReferenceDataManager

class StrategyManager(Module):

    __slots__ = '_strategies', '_time_horizons', '_statsMgr', '_marketDataCache'

    """ TODO:
    - Create sub class ActiveStrategyList that handles dispatching of events. So StrategyMgr calls activeStratList.onMdEvent() and dispatches to all strategies for example
        onMarketDataSnapshot - rename funcs
        - getKey(mic, sym) return MIC_SYM - used as map index for any instrument specific data collection
        - calls registerForMarketData
    - StrategyManager should expose API for fetching latest market data for each strategy - getMktData(symbol, market)
        - Let's have StrategyManager maintain map for market Data snapshots instead of StatsMgr (map string - MDM.) Let's make string MarketMic_ExchangeSymbol
            - Do we really even need StatsMgr?
                * Pros: Allows for shared stats across strategies to avoid duplication
                * Cons: Added complexity and overhead

    - How to use a StrategyFactorManager ???

    - Create notify lists for callbacks, including timerNotifyStrategyList, and marketDataStrategyMap (map string to ASL)
    """

    """ Strategy Factory design:
    -StrategyFactoryManager maintains map of string to StrategyFactory. addStrategyFactory func on startup creates map with all possible factories
        - func calls in worker thread constructor - adds based on what stratgies in use in config
        - works bc also provide dynlib shared obj used as entry point, so Mgr doesn't need to know any specifics abt strat
        - Different for my use case since strategies should exist in same module - search up python applciations of dynlib
    - Honestly probably don't need this design pattern. only necessary from c++ bc of dynlib .so

    
    """

    """ TODO NOW:
    1) Market Data Caching [x]
    2) Timer registration for custom callbacks
    3) Worker thread manages strategyManager, NOT service
    4) Worker Thread, move event loop to separate function ie processMarketDataQueue

    * StrategyMgr receives marketDataQueue from worker thread, then calls marketDataMgr->subscribe(marketDataQueue)
        - MarketDataManager is singleton
    """

    def __init__(self, strategies=[]):
        super().__init__(ModuleEnum.StrategyManager)
        self._strategies = strategies
        self._statsMgr = StatsManager()
        self._marketDataCache = dict()

    def initialize(self, config) -> bool:
        Logger().info("Initializing StrategyManager")

        if not ReferenceDataManager.hasInstance():
            Logger().error("Unable to initialize Worker Thread without Reference Data already initialized. Terminating")
            return False

        universeSymbols = ReferenceDataManager().getSymbolList()

        self._strategies = self.create_strategies_from_config(config)
        self._time_horizons = set()

        if not self._statsMgr.initialize(config):
            Logger().error("Unable to initialize StatsManager. Exiting")
            return False

        for sym in universeSymbols:
            self._marketDataCache[sym] = MdpMessage.getNewMdpMessage()
            self._marketDataCache[sym].setSymbol(sym)
            Logger().debug("MD Cache : %s" % self._marketDataCache)

        # TODO change cache logic ! 
        for strategy in self._strategies:
            Logger().info("Creating Strategy: %s " % strategy)
            # for time_horizon, stats in strategy.getStats().items():
            # # for stats in strategy.getStats():
            #     Logger().debug("\tAdding Stat - %s: %s" % (time_horizon, stats))
            #     self._time_horizons.add(time_horizon)
                # FIXME remove this - move logic for time horizons to individual indicators and they can choose frequency at which to sample market data
                # for stat in stats:
                #                  #(stat_name, stat_type, default_value)
                #                  # TODO - stat is type EMAIndicator
                #     # self._statsMgr.registerStatistic(stats[0], stats[1], stats[2])
                #     print(type(stat))
                 
            self._statsMgr.getCache().addUpdateFuncOnMDEvent(strategy.onMDEvent)
                
# def registerStatistic(self, stat_name, stat_type, default_value):


        if not self._statsMgr.download():
            Logger().error("Unable to Populate Cache for StatsManager. Exiting")
            return False

        return True

    # def on_start(self):
    #     pass

    # def on_stop(self):
    #     pass

    def notify(self):
        pass

    def getTimeHorizons(self):
        """
        @Return a set of TimeHorizons that are being used by all the different strategies constructed
        """
        return self._time_horizons

    def getStrategies(self):
        return self._strategies

    def addStrategy(self, strategy: Strategy):
        self._strategies.append(strategy)

    def log_stats(self):
        for strat in self._strategies:
            strat.log_stats()

    def onTimerEvent(self, event) -> bool:
        start = perf_counter()

        """ TODO
        Issues: 
            - Say two strategies use EMA(10) - they both would try to update it since it gets added with same name. need way to ensure no duplicate updates if more than one strategy with stat
            - EMA(0) should just track price
        """
        # TODO optimize (parallelize?)
        for s in self._strategies:
            # print("onGridTimer strategy: %s" % s)
            s.onTimerEvent(event)

        dt = perf_counter() - start
        Logger().info("OnTimerEvent[%s] took %s per update" % (event.getMessage().get_time_horizon(), dt))

    def onTDEvent(self, event) -> bool:
        # optimize (parallelize?)
        for s in self._strategies:
            s.onTDEvent(event)

    def onMDEvent(self, event):
        Logger().debug("Received onMDEvent : %s" % event.getMessage())
        # TODO First call function to update internal market Data Map. If successful, then notify strategies through ActiveStrategyList
        if not self.updateMarketDataCache(event.getMessage()):
            Logger().error("Not updating market data cache or dispatching event - received invalid MDP message : %s" % event)
            return

        self._statsMgr.onMDEvent(event)
        # optimize (parallelize?)
        for s in self._strategies:
            s.onMDEvent(event)

    def onCycle(self, event):
        start = perf_counter()

        for s in self._strategies:
            s.onCycle(event)

        dt = perf_counter() - start
        Logger().debug("StrategyManager onCycle took [%s] seconds " % dt)

    def updateMarketDataCache(self, mdm): # pass market too since only get symbol in mdm...?
        if not mdm.isValid():
            Logger().error("Invalid market data message : %s" % mdm)
            return False

        if mdm.getSymbol() not in self._marketDataCache:
            Logger().error("Received market data for invalid symbol " << mdm.getSymbol())
            return False

        if mdm.getSeqNum() <= self._marketDataCache[mdm.getSymbol()].getSeqNum():
            Logger().error("Received out of sequence market data message (%s <= %s). Not processing" % (mdm.getSeqNum(), self._marketDataCache[mdm.getSymbol()].getSeqNum()))
            return False

        self._marketDataCache[mdm.getSymbol()] = mdm
        return True
    
    def getMarketDataCache(self):
        return self._marketDataCache

    def getMarketDataSnapshot(self, symbol):
        if symbol not in self._marketDataCache:
            Logger().warn("Symbol %s not found in marketDataCache. Returning empty MdpMessage" % symbol)
            return MdpMessage.getNewMdpMessage()

        mdm = self._marketDataCache[symbol]

        if not mdm.isValid():
            Logger().warn("No market data received yet for symbol %s.  Returning empty MdpMessage" % symbol)
            return MdpMessage.getNewMdpMessage()

        # Logger().debug("Retrieving market data for [%s] : [%s]" % (symbol, mdm))
        return mdm

    def create_strategies_from_config(self, config):
        strats = set()
        Logger().info("Creating strategies from config:\n%s" % config)
        for stratName in config.getDict():
            # TODO need way of defaulting param if doesnt exist
            strat_config = config.expand(stratName)

            strategyFunc = self.getStrategyFunc(strat_config.get_value('StrategyFactory', ''))

            if strategyFunc is self.getInvalidStrategy:
                continue

            strats.add(strategyFunc(strat_config.expand('Params')))

        return strats
    

    def getEMAStrategy(self, params) -> Strategy:
        return EMAStrategy(params, self) 

    def getInvalidStrategy(self, params) -> Strategy:
        return InvalidStrategy()

    def getStrategyFunc(self, factoryFunc):
        if factoryFunc == "getEMAStrategy": return self.getEMAStrategy
        else: return self.getInvalidStrategy

    def __str__(self):
        return "StrategyManager@[%s]:\n%s" % (hex(id(self)), self._strategies)
