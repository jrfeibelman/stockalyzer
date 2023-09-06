from pytest import fixture
from stockalyzer.proto.mdp.MdpMessage import MdpMessage
from stockalyzer.core.Event import Event
from stockalyzer.stats.StatsManager import StatsManager
from tests.engine.StockalyzerService_test import mockWorkerThread, testMarketDataQueue, mockRefDataMgr
from time import sleep

# ---------------------- END SETUP ----------------------



# # ---------------------- START TESTS ----------------------

def test_onMDEventCacheUpdate(mockWorkerThread):
    assert mockWorkerThread.get_strategy_manager().getMarketDataSnapshot('TEST').isEmpty() == True
    assert mockWorkerThread.get_strategy_manager().getMarketDataSnapshot('TEST').isValid() == False
    assert mockWorkerThread.get_strategy_manager().getMarketDataSnapshot('AAPL').isEmpty() == True
    assert mockWorkerThread.get_strategy_manager().getMarketDataSnapshot('AAPL').isValid() == False

    mdm = MdpMessage.getNewMdpMessage()
    mdm.setSymbol('AAPL')
    mdm.setPrice(125.25)
    mdm.setVolume(1000000)
    mockWorkerThread._queue.put(Event.create_market_data_event(mdm))
    sleep(.1)

    newMdm = mockWorkerThread.get_strategy_manager().getMarketDataSnapshot('AAPL')
    assert newMdm.getPrice() == 125.25
    assert newMdm.isValid() == True