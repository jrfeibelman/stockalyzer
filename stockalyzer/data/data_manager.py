from .data_fetcher import DataFetcher
from datetime import datetime
import os
import pandas as pd
import backtrader as bt
from typing import List
from IPython.display import display, Image

# from .data/data_fetcher.py import DataFetcher

class StockDataManager():
    """
    For Interday trading

    Caution: Assumes we have the same amount of data points for all given tickers
    """
    def __init__(self, data, tickers : [str], start_date : datetime, debug:bool, fetcher=""):
        self._data = data
        self.tickers = tickers
        self.start_date = start_date
        self.results = []
        self.debug = debug
        self._fetcher = fetcher
        
        if not os.path.isdir('output'):
            os.makedirs('output')
            os.makedirs('output/graphs')
            os.makedirs('output/data')
        elif not os.path.isdir('output/graphs'):
            os.makedirs('output/graphs')
        if not os.path.isdir('output/data'):
            os.makedirs('output/data')
        
    @classmethod
    def load_from_data_fetcher(cls, data_fetcher : DataFetcher, start_date : datetime=None, interval='1d', debug=False):
        fetcher = data_fetcher._fetcher
        if interval == '1d':
            data = data_fetcher.get_daily_price_history(start_date)
            tickers = data_fetcher.get_tickers()
            return cls(data, tickers, start_date, debug, fetcher=fetcher)
        elif interval == '1h':
            data = data_fetcher.get_hourly_price_history(start_date)
            tickers = data_fetcher.get_tickers()
            return cls(data, tickers, start_date, debug, fetcher=fetcher)
        else:
            raise Exception('invalid args')

    @classmethod
    def load_from_csv(cls, path_to_csv : str, start_date : datetime, debug=False):
        data = pd.read_csv(path_to_csv)    
        tickers = list(set(data['Ticker']))
        data.set_index(['Ticker','Date'], inplace=True)
        data.index = data.index.set_levels([data.index.levels[0], pd.to_datetime(data.index.levels[1])])
        return cls(data, tickers, start_date, debug)
         
    def get_data(self):
        return self._data
    
    def get_data_for(self, ticker : str):
        try:
            return self._data[ticker]
        except KeyError:
            print(f"{ticker} was not passed to the StockDataManager upon construction")
            return pd.DataFrame()
    
    def __name__(self):
        return ''.join(self.tickers)
    
    def export_data(self, path='data.csv'):
#         for ticker in self.tickers:
        self._data.to_csv(path)
    
    def run_strat(self, strategy : bt.Strategy, p1=-1, p2=-1, start_cash = 100000.0, plot=False, rfr=0.0):
        for ticker in self.tickers:
            if self.debug:
                print(f"[{ticker}-{strategy.__name__}]")
            results, pnl  = self._run_for(ticker, strategy, p1, p2, start_cash, plot, rfr)
            self.get_perf_for(ticker, results, pnl)
        
    def _run_for(self, ticker: str, strategy : bt.Strategy, p1:int, p2:int, start_cash : float, plot : bool, rfr:float):
        # Create a cerebro entity
        cerebro = bt.Cerebro(stdstats=True)
        
        # Add a strategy
        cerebro.addstrategy(strategy, p1=p1, p2=p2)
        
        if self.debug:
            strategy.debug_on()

        data = bt.feeds.PandasData(dataname=self._data[ticker], timeframe=bt.TimeFrame.Days, openinterest=None)
        # Add the Data Feed to Cerebro
        cerebro.adddata(data, name=ticker)
        
        # Set our desired cash start & comission rate
        cerebro.broker.setcash(start_cash)
        cerebro.broker.setcommission(commission=0.0)
        
        # TODO: Change position sizes!
        cerebro.addsizer(bt.sizers.FixedSize, stake=1)
        
        # Analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Months, riskfreerate=rfr, annualize=True)
        cerebro.addanalyzer(bt.analyzers.VWR, timeframe=bt.TimeFrame.Years)
        cerebro.addanalyzer(bt.analyzers.DrawDown)
        cerebro.addanalyzer(bt.analyzers.Returns, timeframe=bt.TimeFrame.NoTimeFrame, _name='returns_ann')
        cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, data=data, _name='buyandhold')
        
        start_cash = cerebro.broker.getvalue()
        
        # Print out the starting conditions
#         print('Starting Portfolio Value: %.2f' % start_cash)
        
        # Run over everything
        result = cerebro.run()
        
        end_cash = cerebro.broker.getvalue()
        pnl = end_cash - start_cash
        
        # Print out the final result
#         print('Final Portfolio Value: %.2f' % end_cash)
#         print('PnL Value: %.2f' % pnl)

        if plot:
            fig = cerebro.plot(iplot=False)[0][0] #style='candlestick', 
            fig.savefig('%s-%s.png' % (ticker, strategy.name(p1,p2)))
            
        return result, pnl
    
    def get_perf_for(self, ticker: str, results: List[List[bt.cerebro.OptReturn]], pnl : float)->pd.DataFrame:
        stats = []
        for j in results:
#             print(j.analyzers.sharperatio.get_analysis())
    #         for i in j:
            stats.append(
                {'ticker': f'{ticker}',
                 'strategy': j.__name__(),
                 'pnl': '{0:.2f}'.format(pnl),
                 'sharpe_ratio': j.analyzers.sharperatio.get_analysis()['sharperatio'],
                 'max_drawdown': '{0:.2f}%'.format(j.analyzers.drawdown.get_analysis()['max']['drawdown']*100),
                 'returns_ann': '{0:.4f}%'.format(list(j.analyzers.returns_ann.get_analysis().values())[0] * 100),
                 'buy_and_hold_return': '{0:.4f}%'.format(list(j.analyzers.buyandhold.get_analysis().values())[0] * 100),
                 'vwr': j.analyzers.vwr.get_analysis()['vwr'],
                }
            )
        df = pd.DataFrame(stats)
#         df.set_index('ticker', inplace=True)
        df.set_index(['ticker','strategy'], inplace=True)
        self.results.append(df)
                
    def get_results(self, to_print=False, ipython=False, graphs=False):
        self.results_df = pd.concat(self.results)
        if to_print:
            if ipython:
                display(self.results_df)
            else:
                print(self.results_df)
        
        if graphs:
            for strat, row in self.results_df.iterrows():
                file = '%s-%s.png'% (row.name[0], strat[1])
                display(file)
                if os.path.exists(file):
                    print(file)
                    display(Image(filename=file))
                    
        self.results_df.sort_values(by='sharpe_ratio', ascending=False, inplace=True)
        return self.results_df