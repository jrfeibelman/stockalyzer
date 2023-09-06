from stockalyzer.core.Message import Message
from numpy import single, uint64, double, right_shift
from time import time
from stockalyzer.core.Logger import Logger
from time import perf_counter_ns

class MdpMessage(Message):
    __slots__ = '_symbol', '_price', '_seqNum', '_high', '_low', '_volume', '_div', '_splits', 
    
    @classmethod
    def getNewMdpMessage(cls):
        return MdpMessage()

    def __init__(self):
        self._symbol = ""
        self._price = None

        # to = perf_counter_ns()
        seqNum = uint64(float(str(time())[3:]) * 100) # TODO this isn't great
        # seqNum = double(time()).right_shift()
        # te = (perf_counter_ns()-to)/1000
        # print("JRF timed sqNum [%s] calc [%d] microsecs" % (seqNum, te))

        self._seqNum = seqNum # uint64(time()*10) # TODO confirm max range of uint64 and what would happen when integer overflow occurs
        # Logger().info("JRF seq num [%s] time [%s]" % (self._seqNum, time()*10))
        self._high = None
        self._low = None
        self._vol = None
        self._div = None
        self._splits = None

    def set(self, symbol, price, seqNum, high, low, vol, div, splits):
        self._symbol = symbol
        self._price = price
        self._seqNum = seqNum
        self._high = high
        self._low = low
        self._vol = vol
        self._div = div
        self._splits = splits

    def resetSeqNum(self):
        self._seqNum = uint64(time())

    def getSymbol(self):
        return self._symbol

    def getPrice(self):
        return self._price

    def getSeqNum(self):
        return self._seqNum

    def setSymbol(self, symbol):
        self._symbol = symbol

    def setPrice(self, price):
        self._price = price

    def setVolume(self, volume):
        self._volume = volume

    def setSeqNum(self, seqNum: uint64):
        self._seqNum = seqNum

    def getSeqNum(self):
        return self._seqNum

    def __str__(self):
        return "[%s: %s]" % (self._symbol, self._price)

    def isEmpty(self):
        return self._symbol == ""

    def isValid(self):
        return not self.isEmpty() and self._price != None