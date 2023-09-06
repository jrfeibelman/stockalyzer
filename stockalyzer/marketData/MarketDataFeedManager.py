from stockalyzer.core.Logger import Logger
from stockalyzer.marketData.MarketDataFeedHandler import MarketDataFeedHandlerFactory
from stockalyzer.referenceData.ReferenceDataManager import ReferenceDataManager

class MarketDataFeedManager:
    # TODO switch to spin up thread for every conn instead of one for all

    __slots__ = '_feeds', '_queue', '_config'
    
    def __init__(self):
        self._feeds = []

    @classmethod
    def hasInstance(cls) -> bool:
        return hasattr(cls, '_instance')
   
    def setQueue(self, queue):
        self._queue = queue

    def getQueue(self):
        return self._queue

    def initialize(self, markets_config):
        self._config = markets_config
        Logger().info("Initializing MarketDataFeedManager")

        if markets_config.isEmpty():
            Logger().error("No markets configured. Exiting.")
            return False

        for mkt in markets_config.getDict():
            Logger().info("Initializing market [%s]" % mkt)
            feed_config = markets_config.expand(mkt).expand('FeedHandler')

            if feed_config.isEmpty():
                Logger().error("FeedHandler not configured for %s" % mkt)
                return False

            # check custom or factory
            factoryMethod = feed_config.get_value("Factory", "")
            ip = feed_config.get_value("IP", "")
            port = feed_config.get_value("Port", "")
            apiKey = feed_config.get_value("ApiKey", "")
            cycleSecs = feed_config.get_value("CycleSecs", "15")

            if factoryMethod:
                feedHandlerType = MarketDataFeedHandlerFactory.getFeedHandler(factoryMethod)
                symbolList = ReferenceDataManager().getSymbolListForAssociatedMarket(mkt)
                # symbolList = ReferenceDataManager.getSymbolListFromSecDefFile(sec_def) // would also probably work
                # FIXME think about tightly coupling ref data mgr and md mgr so that rdm initializes feeds when it processes markets yaml - eh not great idea
                feed = feedHandlerType(symbolList, mkt, apiKey, cycleSecs=int(cycleSecs))
                feed.setup_feed_connection()
                self._feeds.append(feed)
            elif ip and port:
                # TODO support custom feeds
                Logger().error("Custom IP/Port FeedHandlers not yet implemented")
                raise Exception('Not yet implemented')
            else:
                Logger().error("FeedHandler not configured properly for %s. Needs IP + Port or factory method" % mkt)
                return False
        
        if len(self._feeds) == 0:
            Logger.error("Received no feeds to fetch market data from. Exiting.")
            return False
            
        return True

    def run(self):
        Logger().info("Running MarketDataFeedManager Subscriptions")
        for feed in self._feeds:
            feed.do_subscription(self._queue)