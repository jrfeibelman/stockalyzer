
from pytest import fixture
from tests.engine.StockalyzerService_test import mockRefDataMgr

# ---------------------- END SETUP ----------------------


# ---------------------- START TESTS ----------------------

def test_refDataMgrInit(mockRefDataMgr):
    universeSymbols = mockRefDataMgr.getSymbolList()
    assert universeSymbols == ['AAPL','AMZN','MSFT','TSLA']
    assert mockRefDataMgr.getInstrumentDataSetSortedOnLocalID()[1].getSymbol() == 'AMZN'
    assert mockRefDataMgr.getInstrumentDataSetSortedOnLocalID()[3].getMarket() == 'NSDQ'
    assert mockRefDataMgr.getInstrumentDataDictBySymbol()['TSLA'].getSymbol() == 'TSLA'
    assert mockRefDataMgr.getInstrumentDataDictByCusip()['594918104'].getSymbol() == 'MSFT'
    assert len(mockRefDataMgr.getSymbolListForAssociatedMarket('YFTestMarket')) == len(universeSymbols)

    assert mockRefDataMgr.getSecExchInfoForMarketMic('TEST') is None
    assert mockRefDataMgr.getSecExchInfoForMarketMic('NSDQ').getMicCode() == 'NSDQ'
    assert len(mockRefDataMgr.getSecExchInfoSetSortedOnLocalID()) == 1
    assert mockRefDataMgr.getSecExchInfoSetSortedOnLocalID()[0].getMicCode() == 'NSDQ'
    assert len(mockRefDataMgr.getSecExchInfoMicToInsDataSetDict()['NSDQ']) == len(universeSymbols)