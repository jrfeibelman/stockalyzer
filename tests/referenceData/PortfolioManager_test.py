from tests.engine.StockalyzerService_test import mockPortfolio
from pytest import fixture

# ---------------------- END SETUP ----------------------


# ---------------------- START TESTS ----------------------

def test_position_update(mockPortfolio):
    aapl = mockPortfolio.getPositionForSymbolWithAccount(1, 'AAPL')
    assert aapl._symbol == 'AAPL'
