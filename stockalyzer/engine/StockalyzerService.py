from stockalyzer.referenceData.ReferenceDataManager import ReferenceDataManager
from stockalyzer.referenceData.PortfolioManager import PortfolioManager
from stockalyzer.strategy.AbstractStrategy import TimeHorizon
from stockalyzer.engine.Service import Service
from stockalyzer.core.Logger import Logger
from stockalyzer.engine.WorkerThread import WorkerThread
from stockalyzer.marketData.MdpSender import MdpSenderThread
from stockalyzer.marketData.MarketDataFeedManager import MarketDataFeedManager
from stockalyzer.engine.MarketDataThread import MarketDataThread
from stockalyzer.core.Config import YamlLoader
from stockalyzer.core.Timer import TimerManager
from stockalyzer.kafka.KafkaManager import KafkaManager
from stockalyzer.engine.ConfigurationManager import ConfigurationManager

from queue import Queue
from ast import literal_eval
from os import system, getpid
from time import perf_counter

"""
TODO:
-replace Singletons with Dependency injection or maybe Borg for RDM
"""
# TODO change naming conventions from camel case to snake case .....

class StockalyzerService(Service):
    __slots__ = '_ref_data_mgr', '_portfolio_mgr', '_config', '_timerMgr', '_threads', '_mkt_data_queue', '_mkt_data_mgr', '_worker_thread'

    def __init__(self, config):
        # Initialize Logger w config for FIRST time
        self._config = YamlLoader.load(config)
        self._mkt_data_queue = Queue()
        Logger(self._config.expand("Logger")).info("Stockalyzer Genesis")

    def on_init(self) -> bool:
        if not ConfigurationManager().initialize(self._config.expand('ConfigurationManager')):
            Logger().error('Configuration Manager failed to initialize. Exiting')
            return False

        # TODO Start kafka subscriptions
        kafka_config = self._config.expand('KafkaConfiguration')
        self._kafkaMgr = KafkaManager()
        if not self._kafkaMgr.initialize(kafka_config):
            Logger().error("Kafka Manager failed to initialize")
            # return False # FIXME

        modules_config = self._config.expand('Resources').expand('Modules')

        self._ref_data_mgr = ReferenceDataManager()
        if not self._ref_data_mgr.initialize(modules_config.expand('ReferenceDataManager')):
            Logger().error("Reference Data Manager failed to initialize. Terminating")
            return False
 
        self._mkt_data_mgr = MarketDataFeedManager() # TODO consider combining with RDM - not a good idea since ref data + market data should be independent
        if not self._mkt_data_mgr.initialize(modules_config.expand('ReferenceDataManager').expand("Markets")):
            Logger().error("Market Data Manager failed to initialize. Terminating")
            return False

        portfolio_cfg = modules_config.expand('PortfolioManager') # Optional
        self._portfolio_mgr = PortfolioManager()
        if not portfolio_cfg.isEmpty():
            if not self._portfolio_mgr.initialize(modules_config.expand('PortfolioManager')): # TODO create user data
                Logger().error("Portfolio Manager failed to initialize. Terminating")
                return False

        # TODO Initialize Price Feed Handler subscriptions and provide call backs for controls - done ?

        # TODO Initialize Trade Feed Handler and provide call backs for controls --> Kafka?
        # --> lazy I/O
        
        Logger().info("Initializing Threads")
        self.init_threads(self._config.expand('Threads'))

        Logger().info("Initializing Timers")
        self.init_timers(self._worker_thread.get_strategy_manager().getTimeHorizons())

        return True
        
    def on_start(self):
        Logger().info("Starting Stockalyzer Service")
        # TODO Init Controls Loop ?
        self._kafkaMgr.subscribe()

        self.start_threads()
        Logger().info("Started Threads")
        self.start_timers()
        Logger().info("Started Timers")
        self._portfolio_mgr.start() # initiate timer function to print out stats every X seconds
        Logger().info("Started Stockalyzer")

    def on_stop(self):
        Logger().info("Terminating Stockalyzer Service")
        self.stop_threads()
        self.stop_timers()

    def init_threads(self, config):
        self._threads = set()
        Logger().info("Initializing Threads")

        marketDataQueue = Queue()

        for thread_name in config.getDict():
            thread_config = config.expand(thread_name)
            Logger().debug("Creating thread %s" % (thread_config))

            if thread_name == "MainThread":
                cpuAffinity = thread_config.get_value('CpuAffinity','').split(',')
                if len(cpuAffinity) > 0:
                    self.set_main_thread_affinity(cpuAffinity)
            if thread_name == "MarketDataThread":
                self._threads.add(MarketDataThread(self._mkt_data_mgr, marketDataQueue))
            elif thread_name == "WorkerThread":
                self._worker_thread = WorkerThread(marketDataQueue, self._config)
                self._threads.add(self._worker_thread)
            elif thread_name == "MdpSender":
                waitMillis = int(thread_config.get_value('WaitMillis',1000))
                strategy = thread_config.get_value('Strategy','default')
                symPriceSpreads = []
                for data in literal_eval(thread_config.get_value("SymbolsPricesSpreads", "[]")):
                    sym, price, mu, sigma = data.split(',')
                    symPriceSpreads.append((sym,float(price),float(mu),float(sigma)))
                self._threads.add(MdpSenderThread(marketDataQueue, waitMillis, symPriceSpreads, strategy))

    def start_threads(self):
        for t in self._threads:
            Logger().info("   Starting Thread : %s" % t)
            t.start()

    def stop_threads(self):
        for t in self._threads:
            Logger().info(t)
            t.join()

    def set_main_thread_affinity(self, coreNums):
        if len(coreNums) == 0:
            Logger().error("Received no cores")
            return
        coreNums=str(coreNums).replace(" ", "")[1:-1]
        system("taskset -p -c %s %d" % (coreNums, getpid()))

    ### TIMERS

    def init_timers(self, timeHorizons):
        self._timerMgr = TimerManager()

        # self._timerMgr.add_timer(TimeHorizon.Sec10, self._worker_thread.on_timer_10_sec)
        self._timerMgr.add_timer(TimeHorizon.Min1, self._worker_thread.on_timer_60_sec) # FIXME make this stats printer
        self._timerMgr.add_timer(TimeHorizon.Sec10, self._worker_thread.on_grid_timer) # FIXME change grid timer to 15 min

        # for t in timeHorizons:
        #     if t is TimeHorizon.Sec1 or t is TimeHorizon.Sec10 or t is TimeHorizon.Min1:
        #         continue
        #     self._timerMgr.add_timer(t, self._worker_thread.onTimerEvent)

    def start_timers(self):
        self._timerMgr.start_timers()

    def stop_timers(self):
        self._timerMgr.stop_timers()