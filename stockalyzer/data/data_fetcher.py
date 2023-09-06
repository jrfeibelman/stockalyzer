import numpy as np
import pandas as pd
from datetime import datetime, date
from datetime import time as dtime
import abc
import yfinance as yf
import requests
import os
import pytz
from configparser import RawConfigParser

class DataFetcher(metaclass=abc.ABCMeta):
    """
        Abstract base class for aquiring stock data
    """
    def __init__(self, tickers : [str]):
        self.tickers = tickers
        self._data = None
        
    def get_tickers(self):
        return self.tickers
        
    def has_dataframe(self):
        if self._data is None:
            return True
        return False
    
    def get_dataframe(self):
        return self._data
    
    @abc.abstractmethod
    def get_data_for(self, ticker : str):
        pass

    @abc.abstractmethod
    def get_hourly_price_history(self, start_date : datetime, end_date=date.today(),):
        pass
        
    @abc.abstractmethod
    def get_daily_price_history(self, start_date : datetime, end_date=date.today()):
        """
        params:
            - start_date : datetime object
            - end_date : datetime object
        return:
            - dataframe of daily price history
        """
        pass
    

class YFDataFetcher(DataFetcher):
    def __init__(self, tickers : [str]):
        super(YFDataFetcher, self).__init__(tickers)
        self._fetcher = 'yf'
        
    def get_daily_price_history(self, start_date : datetime, end_date=date.today()):
        self._df = yf.download(tickers=self.tickers, start=start_date, end=end_date, interval='1d', group_by = 'ticker')
        return self._df
    
    def get_hourly_price_history(self, start_date : datetime=None, end_date=date.today(), period='2y'):
        if start_date:
            self._df = yf.download(tickers=self.tickers, start=start_date, end=end_date, interval='60m', group_by = 'ticker')
        else:
            self._df = yf.download(tickers=self.tickers, period=period, interval='60m', group_by='ticker')
        return self._df
    
    def get_data_for(self, ticker:str):
        return self._df[ticker]
    
    def get_ticker_objects(self):
        return [yf.Ticker(t) for t in self.tickers]
    
    def get_ticker_object(self, ticker:str):
        return yf.Ticker(ticker)
        
    def __name__(self):
        return "[Yahoo Finance] Data Fetcher"
    
    
class TDDataFetcher(DataFetcher):
    def __init__(self, tickers : [str], config_path = "%s/../config/python/config.ini" % os.getcwd()):
        print("%s/config/python/config.ini" % os.getcwd())
        super(TDDataFetcher, self).__init__(tickers)
        self._fetcher = 'td'
        config = RawConfigParser()
        if config_path == "":
            home_dir = os.path.dirname(os.path.dirname(os.getcwd()))
#             print(home_dir)
            config.read('%s/stockalyzer/%s' % (home_dir, config_path))
        else:
            config.read(config_path)
        self.__apiKey = config.get('TD', 'apiKey') # TODO : tthrow error if no key found
    
    def _get_price_history(self, start_date : datetime, end_date : datetime, params : dict, freq='daily'):
        data = []
        self.first = True
        self._df = pd.DataFrame()
        count = 0
        est = pytz.timezone('US/Eastern')
        fmt = '%m-%d-%Y %H:%M:%S %Z%z'
        for ticker in self.tickers:
            url = "https://api.tdameritrade.com/v1/marketdata/%s/pricehistory" % ticker
            out = requests.get(url=url,params=params).json()
#             print(out)
            if out['empty']:
                # TODO : throw error
#                 print("FALSE")
                self.tickers.remove(ticker)
                continue

            df = pd.DataFrame(out['candles']).rename(columns={'datetime':'Date','close':'Close', 'high':'High', 'low':'Low','open':'Open','volume':'Volume'}).set_index('Date')
            if freq == 'daily':
                df.index = [datetime.fromtimestamp(idx/1000).date() for idx in df.index]
            else:
                # PARSE EXTENDED HOURS DATA
                df.index = [datetime.fromtimestamp(idx/1000) for idx in df.index]
            df = df[['High','Low','Open','Close','Volume']]
#             df.index = pd.to_datetime(df.index)
            if freq == 'hourly':
                df = df[df.index.isin([t for t in df.index if t.time() >= dtime(9,30) and t.time() <= dtime(16,0)])]
            df = df.set_index(pd.to_datetime(df.index))
            df.index = df.index.rename('Date')
#             df = df.reindex( pd.MultiIndex.from_product([[ticker], df.index.tolist()]) )
                
            data.append(df) # TODO MERGE DATAFRAMES
            count += 1
            if count % 110 == 0: # stay below transactions/second limit
                time.sleep(30)
#         datas = map (data, self.tickers)
        
        self._df = pd.concat(data, keys=self.tickers, axis=1)
# keys=list(zip(A, B)), axis=1
#             if self.first:
#                 self._df = df
#                 self.first = False
#             else:
#                 print("Concatenating %s to df%s:" % (ticker, 'first...'))
#                 display(self._df.head())
#                 print("Adding:")
#                 display(df.head())
# #                 self._df = pd.concat([self._df, df],keys=self.tickers, axis=1)
#                 self._df = self._df.append(df)
#                 print("Next")
#                 display(self._df.head())

#         self._df = pd.concat(data, names=['Ticker', 'Date'])
        return self._df
    
    def get_quotes(self):
        params = {'apikey':self.__apiKey, 'symbol':','.join(self.tickers)}
        url = "https://api.tdameritrade.com/v1/marketdata/quotes"
        out = requests.get(url=url,params=params).json()
        df = pd.DataFrame(out)
        if df.empty:
            print("FALSE")
            return None
        return df.transpose()
    
    def get_daily_price_history(self, start_date : datetime, end_date=datetime.today()):
        params = {'apikey':self.__apiKey, 'startDate':int(start_date.timestamp())*1000, 'endDate':int(end_date.timestamp())*1000, 'periodType':'year', 'frequencyType':'daily'}
        return self._get_price_history(start_date, end_date, params)
    
    def get_hourly_price_history(self, start_date : datetime, end_date=datetime.today()):
#         print(int(start_date.timestamp())*1000)
        params = {'apikey':self.__apiKey, 'startDate':int(start_date.timestamp())*1000, 'endDate':int(end_date.timestamp())*1000, 'periodType':'day', 'frequencyType':'minute', 'frequency':30}
        return self._get_price_history(start_date, end_date, params, freq="hourly")
    
    def get_data_for(self, ticker : str):
        if self.has_dataframe():
            print("[ERROR] [TDDataFetcher] fetching dataframe : never fetched pricing data. Ensure to call get_daily_price_history first.")
            return None
        return self._df.loc[ticker]
    
    def get_fundamentals(self):
        params = {'apikey':self.__apiKey, 'projection': 'fundamental', 'symbol':','.join(self.tickers)}
        url = "https://api.tdameritrade.com/v1/instruments"
        out = requests.get(url=url,params=params).json()
        df = pd.DataFrame(out)
        if df.empty:
            # TODO : throw error
            print("FALSE")
            return None
        df = df.transpose()
        fund = pd.DataFrame([data for data in df['fundamental'].values]).set_index('symbol')
        return df.drop('fundamental', axis=1).join(fund)
    
    def __name__(self):
        return "[TD Ameritrade API] Data Fetcher"