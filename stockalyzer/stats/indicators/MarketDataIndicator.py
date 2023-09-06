import stockalyzer.core.Event as Event
from stockalyzer.core.Context import Context
from stockalyzer.stats.indicators.AbstractIndicator import AbstractIndicator
from numpy import double

class MarketDataIndicator(AbstractIndicator):

    __slots__ = '_value', '_prevValue', '_sodValue', '_period', '_stratMgr', '_symbols'

    def __init__(self, stratMgr, symbols):
        super().__init__(stratMgr, symbols)

    def onCycle(self, ctx : Context, event: Event) -> bool:
        # TODO update func
        pass

    def onEODEvent(self, ctx: Context, event: Event) -> bool:
        # TODO save value for retreival?
        return True

    def onSODEvent(self, ctx : Context, event: Event) -> bool:
        # TODO download data and set SOD value
        pass

    def name(self) -> str:
        return "MarketDataIndicator"