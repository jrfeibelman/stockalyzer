
from stockalyzer.stats.StatsCache import StatsCache

from tests.referenceData.ReferenceDataManager_test import mockRefDataMgr

from pytest import fixture

@fixture
def mockStatsCache(cfg_setup, mockRefDataMgr):
    cache = StatsCache()
    print("PASSING")
    print(mockRefDataMgr.getSymbolList())
    assert cache.initialize(mockRefDataMgr.getSymbolList()) == True
    return cache

# ---------------------- END SETUP ----------------------


# ---------------------- START TESTS ----------------------

def test_stats_cache(mockStatsCache):
    # print(mockStatsCache)
    pass