from .btStrategy import BTStrategy
import backtrader as bt

class RSIEMAStrategy(BTStrategy):
    params = (('p1',9),('p2',(30,70)),)
    
#     def log(self, txt, dt=None):
#         ''' Logging function fot this strategy'''
#         dt = dt or self.datas[0].datetime.date(0)
#         print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.order = None
#         self.debug = False
        
        if self.params.p1 == -1:
            self.params.p1 = 9
        if self.params.p2 == -1 or type(self.params.p2) is not tuple:
            self.params.p2 = (30,70)
        
        self.rsi = bt.indicators.RelativeStrengthIndex(self.dataclose, )
        self.ema = bt.indicators.EMA(self.dataclose, period=self.params.p1)
        self.rsi_ema = bt.indicators.RSI_EMA(self.dataclose, period=self.params.p1)
    

    def next(self):
        # Simply log the closing price of the series from the reference
#         self.log('Close, %.2f' % self.dataclose[0])
        if self.position:
            if self.rsi[0] > self.params.p2[1]:
                threshold = abs(self.dataclose[0] - self.ema[0]) / self.dataclose[0]
                if threshold >= .1:
                    if self.debug:
                        self.log('SELL CREATE, %.2f' % self.dataclose[0])
                    self.order = self.sell()
        else:
            if self.rsi[0] < self.params.p2[0]:
                threshold = abs(self.dataclose[0] - self.ema[0]) / self.dataclose[0]
                if threshold <= 0.1 and threshold >= .05:
                    if self.debug:
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    self.order = self.buy()
#         else:
            # We are already in the market, look for a signal to CLOSE trades
#             if len(self) >= (self.bar_executed + 5):
#                 self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
#                 self.order = self.close()
                
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if self.debug:
            if order.status in [order.Completed]:
                if order.isbuy():
                    self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
                elif order.issell():
                    self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
                self.bar_executed = len(self)

            elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None
    
    @staticmethod
    def name(p1:int,p2:tuple):
        return f"RSI_{p2[0]}-{p2[1]}_EMA_{p1}"
    
    def __name__(self):
        return f"RSI_{self.params.p2[0]}-{self.params.p2[1]}_EMA_{self.params.p1}"