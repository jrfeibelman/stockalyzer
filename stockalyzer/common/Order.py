from stockalyzer.common.Position import Side

class Order:

    def __init__(self, symbol: str, qty, price, side: Side, account):
        self._qty = qty
        self._symbol = symbol
        self._price = price
        self._side = side
        self._accountId = account