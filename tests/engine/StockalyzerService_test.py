from pytest import fixture
from queue import Queue
from stockalyzer.engine.WorkerThread import WorkerThread
from stockalyzer.strategy.StrategyManager import StrategyManager
from stockalyzer.engine.MarketDataThread import MarketDataThread
from stockalyzer.referenceData.PortfolioManager import PortfolioManager
from stockalyzer.referenceData.ReferenceDataManager import ReferenceDataManager
from stockalyzer.marketData.MarketDataFeedManager import MarketDataFeedManager
from stockalyzer.common.Position import Side

@fixture(scope="session")
def mockRefDataMgr(cfg_setup):

    if ReferenceDataManager.hasInstance():
        return ReferenceDataManager()

    refDataMgr = ReferenceDataManager()
    assert refDataMgr.initialize(cfg_setup.expand('Resources').expand('Modules').expand('ReferenceDataManager')) == True
    return refDataMgr

@fixture(scope="session")
def mockPortfolio(cfg_setup):
    portfolioManager = PortfolioManager()
    assert portfolioManager.initialize(cfg_setup.expand('Resources').expand('Modules').expand('PortfolioManager')) == True

    portfolioManager.updatePosition(1, 'AAPL', 300, 125.51, Side.BUY)
    portfolioManager.updatePosition(2, 'AMZN', 20, 2210.34, Side.BUY)
    portfolioManager.updatePosition(1, 'FB', 70, 192.94, Side.SELL) # Should fail
    return portfolioManager

@fixture(scope="session")
def testMarketDataQueue():
    return Queue()

# @fixture(scope="session")
# def mockStrategyMgr(cfg_setup, mockRefDataMgr):
#     strategyMgr = StrategyManager()
#     assert strategyMgr.initialize(cfg_setup.expand('Modules').expand('Strategy'), mockRefDataMgr.getSymbolList()) == True
#     return strategyMgr

@fixture(scope="session")
def mockWorkerThread(testMarketDataQueue, cfg_setup):
    wt = WorkerThread(testMarketDataQueue, cfg_setup)
    if not wt.is_alive():
        wt.start()
    yield wt
    testMarketDataQueue.put(None)
    
@fixture(scope="session")
def mockMarketDataMgr(cfg_setup):
    if MarketDataFeedManager.hasInstance():
        return MarketDataFeedManager()

    feedMgr = MarketDataFeedManager()
    assert feedMgr.initialize(cfg_setup.expand('Resources').expand('Modules').expand('ReferenceDataManager').expand('Markets')) == True
    return feedMgr

@fixture(scope="session")
def mockMarketDataThread(mockMarketDataMgr, testMarketDataQueue):
    mt = MarketDataThread(testMarketDataQueue)
    if not mt.is_alive():
        mt.start()
    yield mt
    # mt.join() - need to kill thread ?