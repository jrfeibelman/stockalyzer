from enum import Enum
from numpy import uint8
from stockalyzer.core.Logger import Logger

class Side(Enum):
    BUY=0
    SELL=1

class Position:

    def __init__(self, symbol: str, qty, costBasis, side: Side):
        self._symbol = symbol
        self._qty = qty
        self._costBasis = costBasis
        self._side = side

    def updatePosition(self, qty, price, side: Side):
        curWeight = -1 * uint8(self._side) if side is Side else uint8(1)
        newWeight = -1 * uint8(side) if side is Side else uint8(1)
        newCostBasis = qty * price * newWeight

        if self._qty < qty:
            self._side = Side.BUY if self._side is Side.SELL else Side.SELL

        if self._side is side:
            self._qty += qty * newWeight
            self._costBasis += newCostBasis * newWeight
    
    def close(self, price): # TODO
        """
        @params:
        price: the price at which to close out the current position

        @return:
        return an order to close out the position
        """
        pass
    
class PositionsDict:
    __slots__ = '_positionDictOnSymbol'

    def __init__(self, positions=[]):
        self._positionDictOnSymbol = { p._symbol : p for p in positions }

    def updatePosition(self, symbol: str, qty, price, side: Side):
        Logger().info(self._positionDictOnSymbol)
        if symbol not in self._positionDictOnSymbol:
            Logger().error("Symbol [%s] not in positionDict [%s]" % (symbol, self._positionDictOnSymbol))
            return False
        self._positionDictOnSymbol[symbol].update(qty, price, side)

    def getPositionForSymbol(self, symbol):
        return self._positionDictOnSymbol[symbol]

    def getPositionsDict(self):
        return self._positionDictOnSymbol