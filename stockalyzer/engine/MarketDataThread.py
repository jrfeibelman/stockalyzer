from threading import Thread
from stockalyzer.core.Logger import Logger

class MarketDataThread(Thread):

    __slots__ ='_mdm'

    def __init__(self, market_data_mgr, queue):
        super().__init__()
        self._mdm = market_data_mgr
        self._mdm.setQueue(queue)

    def run(self):
        self._mdm.run()