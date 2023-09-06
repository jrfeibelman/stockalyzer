
from stockalyzer.marketData.MarketDataFeedManager import MarketDataFeedManager
from stockalyzer.proto.mdp.MdpMessage import MdpMessage
from tests.referenceData.ReferenceDataManager_test import mockRefDataMgr
from stockalyzer.core.Event import Event
from pytest import fixture
from stockalyzer.stats.StatsManager import StatsManager
from stockalyzer.strategy.StrategyManager import StrategyManager
from tests.engine.StockalyzerService_test import testMarketDataQueue, mockMarketDataMgr, mockMarketDataThread

# ---------------------- END SETUP ----------------------



# ---------------------- START TESTS ----------------------

def test_MarketDataFeedInit(mockMarketDataMgr):
    # TODO - test construction of feeds via MarketDataFeedManager.initialize
    print(mockMarketDataMgr)
    assert True == True

def test_MarketDataFeedHandler(mockMarketDataMgr):
    # TODO - test feed handler functionality
    pass

def test_MarketDataFetchers(mockMarketDataMgr):
    # TODO - test MarketDataFetcher functionality
    pass