from enum import Enum
from numpy import uint16

class Signal(Enum):
    InvalidSignal=uint16(0)
    BuySignal=uint16(1)
    SellSignal=uint16(2)
    SignalTypeLength=uint16(3)