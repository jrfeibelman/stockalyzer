from enum import Enum
from stockalyzer.core.Logger import Logger
from numpy import uint32, single

class SecurityType(Enum):
    SecurityTypeStart = 0,
    Stock = SecurityTypeStart,
    Bond = 1,
    Undefined = 2,
    SecurityTypeSize = 3

    @classmethod
    def getSecurityType(cls, secType: str):
        if secType == "Stock": return SecurityType.Stock
        if secType == "Bond": return SecurityType.Bond
        else: return SecurityType.Undefined

    @classmethod
    def getSecurityTypeStr(cls, secType) -> str:
        if secType == SecurityType.Stock: return "Stock"
        if secType == SecurityType.Bond: return "Bond"
        else: return "Undefined"


""""
can zip header and row so have dict we can pass to InsData cls func

"""
SYMBOL = "SYMBOL"
CUSIP = "CUSIP"
CLOSE = "CLOSE"
SEC_TYPE = "SECURITYTYPE"
UND_INS = "UNDERLYINGINSTRUMENT"
MKT = 'MARKET'

class SecurityExchangeInfo:

    __slots__ = '_localId', '_micCode'

    localIdCount = 0

    def __init__(self, marketMic):
        self._localId = self._getNewLocalID()
        self._micCode = marketMic

    @classmethod
    def _getNewLocalID(cls) -> uint32:
        tmp = cls.localIdCount
        cls.localIdCount += 1
        return tmp

    def getMicCode(self):
        return self._micCode


class InstrumentData:
    
    __slots__= '_localId', '_symbol', '_cusip', '_securityType', '_closingPrice', '_underlyingInstrument', '_marketMic', '_associatedMarket', '_secExchInfo'

    localIdCount = 0

    @classmethod
    def from_dict(cls, data_dict): # TODO - should this be cls._instance???
        cls._instance = super().__new__(cls)
        cls._instance._symbol = data_dict[SYMBOL]
        cls._instance._cusip = data_dict[CUSIP]
        cls._instance._marketMic = data_dict[MKT]
        cls._instance._securityType = SecurityType.getSecurityType(data_dict[SEC_TYPE])
        cls._instance._closingPrice = single(data_dict[CLOSE])
        cls._instance._underlyingInstrument = data_dict[UND_INS]
        cls._instance._localId = cls._getNewLocalID()
        cls._instance._secExchInfo = None
        return cls._instance

    def __init__(self, symbol: str, cusip: str, securityType: SecurityType, closingPrice: single, underlyingInstrument: str, market: str, associatedMarket: str):
        self._symbol = symbol
        self._cusip = cusip
        self._securityType = securityType
        self._closingPrice = closingPrice
        self._underlyingInstrument = underlyingInstrument
        self._marketMic = market
        self._associatedMarket = associatedMarket
        self._localId = self._getNewLocalID()
        self._secExchInfo = None

    def getSymbol(self) -> str:
        return self._symbol

    def getCusip(self) -> str:
        return self._cusip

    def getLocalID(self) -> uint32:
        return self._localId

    def getMarket(self) -> str:
        """ return market the security is traded on from reference data """
        return self._marketMic

    def getAssociatedMarket(self) -> str:
        """ return associated market name based on markets config whose feed handler was used to fetch prices"""
        return self._associatedMarket

    @classmethod
    def _getNewLocalID(cls) -> uint32:
        tmp = cls.localIdCount
        cls.localIdCount += 1
        return tmp
    
    def setAssociatedMarket(self, mkt):
        self._associatedMarket = mkt

    def setSecurityExchInfo(self, secExchInfo):
        self._secExchInfo = secExchInfo

    def __str__(self):
        return  "%s\n" % ",".join([str(self._localId), self._symbol, self._cusip, str(self._closingPrice), SecurityType.getSecurityTypeStr(self._securityType)])