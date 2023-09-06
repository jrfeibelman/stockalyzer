from stockalyzer.proto.mdp.MdpMessage import MdpMessage
from time import sleep
from stockalyzer.core.Logger import Logger
from random import choice, uniform
from stockalyzer.core.Event import Event
from threading import Thread
from multiprocessing import Process
from stockalyzer.math.brownian.GBM import BrownianSimulator
from numpy import uint64
from enum import Enum

class MdpSender:
    """
    Class used for mocking the receival of MDP messages
    """
    __slots__ = '_symbolPriceTuples', '_waitMillis', '_cache', '_simulator', '_strategy'

    class Strategy(Enum):
        DefaultSpread=uint64(0)
        GbmStrategy=uint64(1)
        InvalidStrategy=uint64(2)

    @classmethod
    def getStrategyFromString(cls, strat):
        if strat == "default":
            return cls.Strategy.DefaultSpread
        if strat == "gbm":
            return cls.Strategy.GbmStrategy
    
        Logger().error("Received invalid strategy %s" % strat)
        return cls.Strategy.InvalidStrategy

    def __init__(self, symbolPriceTuples, waitMillis, strategy):
        """
        @Param symbolPriceTuples : list of tuples for (symbol, basePrice, spread)
                        - symbol is string ticker
                        - basePrice is float price 
                        - spread is float percentage to apply to basePrice
        """
        self._waitMillis = waitMillis
        self._symbolPriceTuples = symbolPriceTuples
        self._cache = dict()
        self._simulator = BrownianSimulator()
        self._strategy  = self.getStrategyFromString(strategy)
        # Logger().info("Initialized MdpSender with strategy [%s] - [%s]" % (strategy, self._strategy.name)) FIXME
        Logger().info("Initialized MdpSender with strategy [%s] - [%s]" % (strategy, self._strategy.name))

    def generate_market_data_message(self) -> MdpMessage:
        sleepTime = float(self._waitMillis) / 1000.0
        sleep(sleepTime)
        symTuple = choice(self._symbolPriceTuples)

        if self._strategy is self.Strategy.DefaultSpread:
            return self.generate_market_data_message_default(symTuple)
        elif self._strategy is self.Strategy.GbmStrategy:
            return self.generate_market_data_message_gbm(symTuple)

        # ().error("Cannot generate market data message for INVALID STRATEGY") FIXME
        Logger().error("Cannot generate market data message for INVALID STRATEGY")
        return MdpMessage.getNewMdpMessage()

    def generate_market_data_message_gbm(self, symTuple) -> MdpMessage:
        mdm = MdpMessage.getNewMdpMessage()
        mdm.setSymbol(symTuple[0])

        if symTuple[0] in self._cache:
            price = self._cache[symTuple[0]]
        else:
            price = symTuple[1]
        
        mdm.setPrice(self._simulator.sim_single_gbm_increment(price, symTuple[2], symTuple[3]))
        self._cache[symTuple[0]] = mdm.getPrice()

        return mdm

    def generate_market_data_message_default(self, symTuple) -> MdpMessage:
        sleepTime = float(self._waitMillis) / 1000.0
        sleep(sleepTime)

        mdm = MdpMessage.getNewMdpMessage()
        mdm.setSymbol(symTuple[0])
        spread = uniform(-1.0*symTuple[2], symTuple[2])
        newPrice =  symTuple[1] * (1.0 - spread)
        mdm.setPrice(newPrice)

        return mdm

    def generate_market_data_event(self) -> Event:
        return Event.create_market_data_event(self.generate_market_data_message())

class MdpSenderThread(Thread):
    """
    Class for MdpSenderThread to simulate dummy live market data for testing and push it onto a queue
    """
    __slots__ = 'waitMillis', '_strategy', '_queue'

    def __init__(self, queue, waitMillis, symbolPriceTuples, strategy):
        super().__init__()
        self._queue = queue
        self._waitMillis = waitMillis
        self._symbolPriceTuples = symbolPriceTuples
        self._strategy = strategy

    def run(self):
        sender = MdpSender(self._symbolPriceTuples, self._waitMillis, self._strategy)

        while 1:
            event = sender.generate_market_data_event()
            self._queue.put(event)