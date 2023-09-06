import backtrader as bt

class BTStrategy(bt.Strategy):
    debug = False
    
    @classmethod
    def debug_on(cls):
        cls.debug = True

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))