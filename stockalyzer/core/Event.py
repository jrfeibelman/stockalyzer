from enum import Enum
from stockalyzer.proto.mdp.MdpMessage import MdpMessage
from stockalyzer.core.Context import Context
from stockalyzer.core.Message import TimerMessage
from numpy import uint32

class Event:
    # TODO make this an abstract class, and subtype Event for each EventTime implementing abstract methods dispatch(), releaseMeToPool()
    __slots__ = '_eventType', '_msg'

    class EventType(Enum):
        InvalidEvent=uint32(0)
        TimerEvent=uint32(1)
        MarketDataEvent=uint32(2)
        TradeEvent=uint32(3)
        SODEvent=uint32(4)
        EODEvent=uint32(5)
        ParameterEvent=uint32(6)
        SODPositionEvent=uint32(7)
        EventTypeLength=uint32(8)
        # New Order & Cancelled events ?? for outstanding orders

    def __init__(self):
        raise RuntimeError('Use Factory Methods Instead')

    @classmethod
    def create_timer_event(cls, time_horizon):
        e =  cls.__new__(cls)
        e._eventType = Event.EventType.TimerEvent
        e._msg = TimerMessage(time_horizon)
        return e

    @classmethod
    def create_market_data_event(cls, md: MdpMessage):
        e =  cls.__new__(cls)
        e._eventType = Event.EventType.MarketDataEvent
        e._msg = md
        return e

    @classmethod
    def create_trade_event(cls, td):
        e =  cls.__new__(cls)
        e._eventType = Event.EventType.TradeEvent
        e._msg = td
        return e
    
    # TODO Make Event an abstract class and make this method virtual
    def clear(self):
        pass

    def getMessage(self):
        return self._msg

    def getEventType(self):
        return self._eventType

    def __str__(self):
        return "(%s) %s" % (self._eventType, self._msg)