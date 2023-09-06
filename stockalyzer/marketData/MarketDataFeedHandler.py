from stockalyzer.marketData.MarketDataFetcher import YFDataFetcher, TDDataFetcher
from stockalyzer.core.Logger import Logger
from stockalyzer.core.Event import Event
from threading import Timer as Thread_Timer

class MarketDataFeedHandler:
    """
        Abstract base class for aquiring stock data
    """

    __slots__ = '_symbols', '_fetcher', '_timer', '_cycleSecs'

    def __init__(self, symbols, fetcher, cycleSecs=60, retrySecs=10):
        self._symbols = symbols
        self._fetcher = fetcher
        self._cycleSecs = cycleSecs
        self._retrySecs = retrySecs

    def get_tickers(self):
        return self.tickers
        
    def setup_feed_connection(self):
        self._fetcher.setup_feed_connection()

    def requiresApiKey(self) -> bool:
        return self._fetcher.requiresApiKey()

    def do_subscription(self, queue):
        """ Queries feed for data every second"""
        try:
            for mdm in self._fetcher.get_marketdata_snapshot():
                queue.put(Event.create_market_data_event(mdm))
        except:
            Logger().debug("Connection Error for feed [%s] - sleeping for %s seconds..." % (self._fetcher._feedName, self._retrySecs))
            self._timer = Thread_Timer(self._retrySecs, self.do_subscription, (queue,))
            self._timer.start()
            return

        self._timer = Thread_Timer(self._cycleSecs, self.do_subscription, (queue,))
        self._timer.start()

class MarketDataFeedHandlerFactory:
    @classmethod
    def getFeedHandler(cls, handler):
        if handler == 'getYFFeedHandler':
            return MarketDataFeedHandlerYF
        elif handler == 'getTDFeedHandler':
            return MarketDataFeedHandlerTD
        else:
            Logger().error("Handler %s not supported. Try getYFFeedHandler or getTDFeedHandler")
            raise ValueError(handler)

"""
TODO: should have a separate application that continously pulls live market data from YF and puts onto feed?
Or should do this in own thread ...
- Let's put in own thread for now and can eventually move to separate app
- THUS, should have functionality for both market data feeds over ip/port and over fetchers


- Also lets add more nodes/processes for fetching MD for many symbols
"""
    
class MarketDataFeedHandlerYF(MarketDataFeedHandler):
    """
        Abstract base class for acquiring stock data
    """

    __slots__ = '_symbols', '_fetcher', '_timer', '_cycleSecs', '_retrySecs'

    def __init__(self, symbols, feedName, apiKey="", cycleSecs=60, retrySecs=10):
        super().__init__(symbols, YFDataFetcher(symbols, feedName), cycleSecs=cycleSecs, retrySecs=retrySecs)

class MarketDataFeedHandlerTD(MarketDataFeedHandler):
    """
        Abstract base class for acquiring stock data
        TODO currently functionality not supported for TD
    """

    __slots__ = '_symbols', '_fetcher', '_timer', '_cycleSecs', '_retrySecs'

    def __init__(self, symbols, feedName, apiKey, cycleSecs=60, retrySecs=10):
        if apiKey == '':
            err = "MDFeedHandlerTD requires an apiKey. Pass in markets.yaml under a given market's optional ApiKey field"
            Logger().error(err)
            raise Exception(err)
        super().__init__(symbols, TDDataFetcher(symbols, feedName, apiKey), cycleSecs=cycleSecs, retrySecs=retrySecs)