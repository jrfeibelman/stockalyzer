from abc import abstractmethod, ABCMeta
import stockalyzer.core.Event as Event
from stockalyzer.core.Context import Context
from numpy import double, isreal, zeros
# from functools import total_ordering

# @total_ordering
class AbstractIndicator(metaclass=ABCMeta):
    """
    Indicator class contains indicator values for all symbols.

    self._values is a dictionary
        - key is symbol
        - value is tuple of currentValue, previousValue, sodValue
                                # (value,     prevValue, sodValue)

    Indicator should be indexible where you can do indicator[sym] to get the value.
    Also should support indicator.getPrevValue(sym) and indicator.getSodValue(sym)
    """

    __slots__ = '_values', '_prevValues', '_sodValues', '_symbols', '_stratMgr'

    def __init__(self, strategyMgr, symbols):
        self._symbols = symbols
        self._stratMgr = strategyMgr

        self._values = zeros(len(self._symbols), dtype=double)
        self._prevValues = zeros(len(self._symbols), dtype=double)
        self._sodValues = zeros(len(self._symbols), dtype=double)

    def _is_valid_operand(self, other):
        return isreal(other) or isinstance(other, AbstractIndicator) # isabstract(other) or 

    # def __eq__(self, other):
    #     if not self._is_valid_operand(other):
    #         return NotImplemented
    #     if isinstance(other, AbstractIndicator):
    #         return (self._value == other._value)
    #     return (self._value == other)

    # def __lt__(self, other):
    #     if not self._is_valid_operand(other):
    #         return NotImplemented
    #     if isinstance(other, AbstractIndicator):
    #         return (self._value < other._value)
    #     return (self._value < other)

    @abstractmethod
    def onCycle(self, event: Event) -> bool:
        pass

    @abstractmethod
    def onEODEvent(self, event: Event) -> bool:
        # FIXME is this necessary ?
        pass

    @abstractmethod
    def onSODEvent(self, event: Event) -> bool:
        # FIXME is this necessary ?
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    def getPreviousValue(self, ticker):
        return self._values[ticker][0]
    
    def getCurrentValue(self, ticker):
        return self._values[ticker][1]
    
    def getSODValue(self, ticker):
        return self._values[ticker][2]
    
    def getSymbols(self):
        return self._symbols
    
    def getSymbol(self, idx) -> str:
        return self._symbols[idx]
    
    def setSodValue(self, idx, value):
        self._sodValues[idx] = value

class InvalidIndicator(AbstractIndicator):

    def __init__(self):
        pass

    def onEODEvent(self, event) -> bool:
        raise Exception('Invalid Strategy')

    def onSODEvent(self, event) -> bool:
        raise Exception('Invalid Strategy')

    def onCycle(self, event) -> bool:
        raise Exception('Invalid Strategy')

    def name(self) -> str:
        return "Invalid Strategy"