from stockalyzer.strategy.AbstractStrategy import Strategy, TimeHorizon
from numpy import uint16, single, int8
from datetime import datetime, timedelta
from stockalyzer.core.Logger import Logger
from stockalyzer.stats.indicators.EMAIndicator import EMAIndicator
from stockalyzer.stats.indicators.MarketDataIndicator import MarketDataIndicator
from stockalyzer.stats.indicators.AbstractIndicator import InvalidIndicator
from stockalyzer.strategy.StrategySignal import Signal
from stockalyzer.marketData.MarketDataFetcher import YFDataFetcher
from enum import Enum

class EMAStrategy(Strategy):

    __slots__ = '_symbols', '_indicators', '_timeIntervals', '_decayFactorType', '_decayFactors', '_printStats', '_isEnabled', '_strategyMgr', '_timeHorizon', '_signals'

    class DecayFactorType(Enum):
        span = 1
        com = 2
        halflife = 3
        alpha = 4

    def __init__(self, params_config, strategyMgr):
        """
        @Param: params : expected params are of format "<TimeHorizonString>: <CommaSeparatedTimeIntervals>" 
                        defaults to TimeHorizon.Day1 if no <TimeHorizonString>: provided
        """
        super().__init__(params_config, strategyMgr)
        self._timeHorizon = TimeHorizon.getTimeHorizon(params_config.get_value("TimeHorizon", "Day1"))
        # t_value("TimeHorizon", "Day1"))
        self._timeIntervals = [int(i) for i in params_config.get_value("TimeIntervals", "0,20").split(",")]

        decayFactorType = params_config.get_value("DecayFactorType", "INVALID")
        decayFactor = params_config.get_value("DecayFactors", "INVALID")

        if ',' not in decayFactor:
            self._decayFactors = [int(decayFactor) for i in range(len(self._timeIntervals))]
        else:
            self._decayFactors = [int(d) for d in decayFactor.split(',')]
            if len(self._decayFactors) != len(self._timeIntervals):
                Logger().error("Invalid number of EMA DecayFactors [%s] passed. Expected %s but received %s decay factors. Failed to initialize strategy %s" % (decayFactorType, len(self._decayFactors), len(self._indicators), self))
                return
            
        if decayFactorType == 'span':
            self._decayFactorType = self.DecayFactorType.span
            self._decayFactors = self._timeIntervals
        elif decayFactorType == 'com':
            self._decayFactorType = self.DecayFactorType.com
        elif decayFactorType == 'halflife':
            self._decayFactorType = self.DecayFactorType.halflife
        elif decayFactorType == 'alpha':
            self._decayFactorType = self.DecayFactorType.alpha
            self._decayFactors = int(decayFactor) if decayFactor != "INVALID" else 0
        else:
            Logger().error("Invalid EMA DecayFactor [%s] passed. Failed to initialize strategy %s" % (decayFactorType, self))
            return
        
        # decayFactor = single(2.0/(1.0+TimeHorizon.getTimeHorizonNumInDays(self._timeHorizon))) if decayFactor == "INVALID" else single(decayFactor)
        # decayFactor = single(2.0/(1.0+1.0)) if decayFactor == "INVALID" else single(decayFactor)
        # self._decayFactor = single(1.0) if decayFactor > 1.0 else single(abs(decayFactor))


        if not self.setupIndicators(self._timeIntervals):
            Logger().error("Invalid Indicator setup. Failed to initialize strategy %s" % self)
            return

        self._indicators = sorted(self._indicators, key=lambda x: x.getPeriod())
        
        if not self.downloadHistoricalData():
            Logger().error("Unable to download historical data. Failed to initialize strategy %s" % self)
            return

    def setupIndicators(self, periods : list[str]) -> bool:
        """ Method to instantiate all Indicators needed for strategy. This method should be overriden for subclasses """
        if len(periods) > 2 or len(periods) == 0:
            Logger().error("Base EMAStrategy is only set up for 1 or 2 time periods. Consider implementing a subclass")
            return False

        for i in range(len(periods)):
                  #(stat_name, stat_type, default_value, ... stat_interval)
            # stat = ("EMA(%s)" % p, single, single(0),    uint16(p))
            self.addIndicator(EMAIndicator(self._strategyMgr, self._symbols, periods[i], self._decayFactors[i]))

        # if len(periods) == 1:
        #     self.addIndicator(MarketDataIndicator(self._strategyMgr, self._symbols))

        return True

    def trigger(self, signal : Signal) -> None:
        # TODO publish to Kafka topic
        Logger().info("BREACH triggered from Strategy %s with signal %s" % (self, signal))

    # def getMDStats(self):
    #     return self._md_stats

    # def getTDStats(self):
    #     return self._td_stats

    # def getTimeStats(self):
    #     return self._time_stats

    def log_stats(self, event):
        Logger().debug("Logging stats for strategy %s" % self)

    def onCycle(self, event) -> bool:
        Logger().debug("EMAStrategy::onCycle()")
        # for time_horizon, stats in self._stats.items(): # FIXME loop bad
        # for i in self._indicators:
        #     i.onCycle(event)

        self.checkTriggerCondition()

        # TODO check for triggering indicator
        # if self._low.getValue() > self._high.getValue():
        #     # trigger
        #     pass
        # else:
        #     # trigger ?
        #     pass

        # ctx = event.getMessage()
        # for stat in self._stats:
        #     name, stat_type, _, intervalNum = stat
        #     if name in cache._dict:
        #         cache[name] = stat_type(cache['price'] * self._decayFactors + cache[name] * (1.0 - self._decayFactors))
        if self._printStats: 
            self.log_stats(event)

        return True
    
    def checkTriggerCondition(self):
        """ Method to trigger signal dispatch if certain condition is met. This method should be overriden for subclasses"""
        # pass
        # low = self._indicators[0]
        # high = self._indicators[1] # TODO use market data indicator ?????
        # if len(self._indicators) == 1:
        #     md_cache = self._strategyMgr.getMarketDataCache()
        #     signals = {key : self._indicators[0].getCurrentValue(key) - md_cache[key] for key in set(md_cache)}
        # elif len(self._indicators) == 2:
        #     signals = {key : self._indicators[0].getCurrentValue(key) - self._indicators[1].getCurrentValue(key) for key in set(self._indicators[0])}
        # else:
        #     signals = {}
        #     Logger.error("checkTriggerCondition called for invalid number of indicators [%s]" % len(self._indicators))
        #     return

        # signals = dict()
        # for key in self._symbols:
        #     if len(self._indicators) == 1:
        #         other = self._strategyMgr.
        #     sub = self._indicators[0].getCurrentValue(key) - 
        #     ._indicators[1].getCurrentValue(key)


        # if self._indicators[0] > self._indicators[1]:
        #     self.trigger(Signal.BuySignal)
        # elif self._indicators[0] < self._indicators[1]:
        #     self.trigger(Signal.SellSignal)

        for i in range(len(self._symbols)):
            for ind in self._indicators:
                ind.onSingleCycle(i)

            signal = self._indicators[0][i] - self._indicators[1][i]
            # self._signals[i] = signal

    def onMDEvent(self, event) -> bool:
        # TODO implement market data listener registration so custom classes can receive market data callbacks
        # md = event.getMessage()
        #
        # for stat in self.getStatsFor(TimeHorizon.MDEventDriven):
        #     Logger().info(stat)
        #     # name, stat_type, _, intervalNum = stat
        #     Logger().info("%s : Updating Stat [%s]:[]" % (self, event.getType()))
            # cache[name] = stat_type(md._price * self._decayFactors + cache[name] * (1.0 - self._decayFactors))
        return True

    def onTDEvent(self, cache, event) -> bool:
        for stat in self.getStatsFor(TimeHorizon.TDEventDriven):
            pass
        return True

    def onEODEvent(self, cache, event) -> bool:
        # TODO
        return True

    def onSODEvent(self, cache, event) -> bool:
        return True
    
    def downloadHistoricalData(self) -> bool:
        data_fetcher = YFDataFetcher(self._symbols, str(self))
        maxDays = max(self._timeIntervals)
        start_date = datetime.today() - timedelta(days = maxDays * 2)
        data = data_fetcher.get_daily_price_history(start_date)

        # TODO move SOD generation logic to StrategyManager so same dataset can be shared across all strategies
        for i in range(len(self._indicators)):
            ind = self._indicators[i]
            period_str = '%s EMA' % ind.getPeriod()
            for j in range(len(ind.getSymbols())):
                sym = ind.getSymbol(j)
                sodValue = 0
                print(self._decayFactorType)
                decayFactor = self._decayFactors[i]
                if self._decayFactorType == self.DecayFactorType.span:
                    data[sym, period_str] = data[sym, 'Adj Close'].ewm(span=decayFactor, min_periods=1, adjust=False).mean()
                    # key2= "JRF_%s" % period_str
                    # data[sym, key2] = data[sym, 'Adj Close'].ewm(span=decayFactor, min_periods=1, adjust=False).mean()
                elif self._decayFactorType == self.DecayFactorType.com:
                    data[sym, period_str] = data[sym, 'Adj Close'].ewm(com=decayFactor, min_periods=1, adjust=False).mean()
                elif self._decayFactorType == self.DecayFactorType.halflife:
                    data[sym, period_str] = data[sym, 'Adj Close'].ewm(alpha=decayFactor, min_periods=1, adjust=False).mean()
                elif self._decayFactorType == self.DecayFactorType.alpha:
                    data[sym, period_str] = data[sym, 'Adj Close'].ewm(halflife=decayFactor, min_periods=1, adjust=False).mean()
        
                sodValue = data[sym, period_str][-1]
                ind.setSodValue(j, sodValue)
                # print("sym %s, indicator %s, start val %s" % (sym, period_str, sodValue))
            # print(data['AMZN'])
        Logger().log_data("Printing SOD Data (using decayFactor=%s):\n%s" % (decayFactor,data.to_string()))
        return True

    def __str__(self) -> str:
        return "EMAStrategy[%s], Decay[%s:%s], &[%s]" % (self._timeIntervals, self._decayFactorType ,self._decayFactors, hex(id(self)))

    def name(self) -> None:
        pass
