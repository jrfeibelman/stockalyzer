from datetime import datetime, date
from datetime import time as dtime
from abc import ABCMeta, abstractmethod
from yfinance import Ticker, download
from numpy import uint64
from requests import get
from pytz import timezone
from pandas import read_csv, to_datetime, concat, DataFrame
from time import time
from stockalyzer.proto.mdp.MdpMessage import MdpMessage
from stockalyzer.core.Logger import Logger

class DataFetcher(metaclass=ABCMeta):
    """
        Abstract base class for aquiring stock data
    """
    def __init__(self, tickers, feedName):
        self.tickers = tickers
        self._data = None
        self._apiKey = None
        self._feedName = feedName
        
    def get_tickers(self):
        return self.tickers
        
    def has_dataframe(self):
        if self._data is None:
            return True
        return False
    
    def get_dataframe(self):
        return self._data

    @abstractmethod
    def requiresApiKey(self) -> bool:
        pass

    def setApiKey(self, key):
        self._apiKey = key

    @abstractmethod
    def get_marketdata_snapshot(self):
        pass

    @abstractmethod
    def get_data_for(self, ticker : str):
        pass

    @abstractmethod
    def get_hourly_price_history(self, start_date : datetime, end_date=date.today(),):
        pass
        
    @abstractmethod
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

    __slots__ = '_fetcher', '_df', '_yfTickers', '_seqNum', '_feedName'

    def __init__(self, tickers, feedName):
        super(YFDataFetcher, self).__init__(tickers, feedName)
        self._fetcher = 'yf'
        self._yfTickers = dict()
        self._seqNum = uint64(time())

    def setup_feed_connection(self):
        for sym in self.tickers:
            self._yfTickers[sym] = Ticker(sym)

    def get_marketdata_snapshot(self):
        for sym in self.tickers:
            try:
                snapshot = self._yfTickers[sym].history(period='1d').iloc[0]
            except:
                raise Exception
            mdm = MdpMessage.getNewMdpMessage()
            mdm.setSymbol(sym)
            mdm.setPrice(snapshot['Close'])
            mdm.setSeqNum(self._seqNum)
            mdm.setVolume(snapshot['Volume'])
            yield mdm
            self._seqNum += 1

    def get_daily_price_history(self, start_date : datetime, end_date=date.today()):
        self._df = download(tickers=self.tickers, start=start_date, end=end_date, interval='1d', group_by = 'ticker')
        return self._df
    
    def get_hourly_price_history(self, start_date : datetime=None, end_date=date.today(), period='2y'):
        if start_date:
            self._df = download(tickers=self.tickers, start=start_date, end=end_date, interval='60m', group_by = 'ticker')
        else:
            self._df = download(tickers=self.tickers, period=period, interval='60m', group_by='ticker')
        return self._df
    
    def get_data_for(self, ticker:str):
        return self._df[ticker]
    
    def get_ticker_objects(self):
        return [Ticker(t) for t in self.tickers]
    
    def get_ticker_object(self, ticker:str):
        return Ticker(ticker)

    def requiresApiKey(self) -> bool:
        return False
        
    def __name__(self):
        return "[Yahoo Finance] Data Fetcher"
    
    
class TDDataFetcher(DataFetcher):

    __slots__ = '_fetcher', '_df', '_seqNum', '_feedName'

    def __init__(self, tickers, feedName, apiKey):
        super(TDDataFetcher, self).__init__(tickers, feedName)
        self._fetcher = 'td'
        self._apiKey = apiKey
        self._seqNum = uint64(time())

    def get_marketdata_snapshot(self):
        # TODO
        pass
        # for sym in self.tickers:
        #     try:
        #         snapshot = self._yfTickers[sym].history(period='1d').iloc[0]
        #     except:
        #         raise Exception
        #     mdm = MdpMessage.getNewMdpMessage()
        #     mdm.setSymbol(sym)
        #     mdm.setPrice(snapshot['Close'])
        #     mdm.setSeqNum(self._seqNum)
        #     mdm.setVolume(snapshot['Volume'])
        #     yield mdm
        #     self._seqNum += 1

    def _get_price_history(self, start_date : datetime, end_date : datetime, params : dict, freq='daily'):
        data = []
        self.first = True
        self._df = DataFrame()
        count = 0
        est = timezone('US/Eastern')
        fmt = '%m-%d-%Y %H:%M:%S %Z%z'
        for ticker in self.tickers:
            url = "https://api.tdameritrade.com/v1/marketdata/%s/pricehistory" % ticker
            out = get(url=url,params=params).json()
            if out['empty']:
                # TODO : throw error
#                 print("FALSE")
                self.tickers.remove(ticker)
                continue

            df = DataFrame(out['candles']).rename(columns={'datetime':'Date','close':'Close', 'high':'High', 'low':'Low','open':'Open','volume':'Volume'}).set_index('Date')
            if freq == 'daily':
                df.index = [datetime.fromtimestamp(idx/1000).date() for idx in df.index]
            else:
                # PARSE EXTENDED HOURS DATA
                df.index = [datetime.fromtimestamp(idx/1000) for idx in df.index]
            df = df[['High','Low','Open','Close','Volume']]

            if freq == 'hourly':
                df = df[df.index.isin([t for t in df.index if t.time() >= dtime(9,30) and t.time() <= dtime(16,0)])]
            df = df.set_index(to_datetime(df.index))
            df.index = df.index.rename('Date')

            data.append(df)
            count += 1
            if count % 110 == 0: # stay below transactions/second limit
                time.sleep(30)
        
        self._df = concat(data, keys=self.tickers, axis=1)
        return self._df

    def setup_feed_connection(self):
        for sym in self.tickers:
            # self._yfTickers[sym] = Ticker(sym)
            pass

    def get_quotes(self):
        params = {'apikey':self._apiKey, 'symbol':','.join(self.tickers)}
        url = "https://api.tdameritrade.com/v1/marketdata/quotes"
        out = get(url=url,params=params).json()
        df = DataFrame(out)
        if df.empty:
            Logger().error("No quotes received!")
            return None
        return df.transpose()

    def requiresApiKey(self) -> bool:
        return True
    
    def get_daily_price_history(self, start_date : datetime, end_date=datetime.today()):
        params = {'apikey':self._apiKey, 'startDate':int(start_date.timestamp())*1000, 'endDate':int(end_date.timestamp())*1000, 'periodType':'year', 'frequencyType':'daily'}
        return self._get_price_history(start_date, end_date, params)
    
    def get_hourly_price_history(self, start_date : datetime, end_date=datetime.today()):
#         print(int(start_date.timestamp())*1000)
        params = {'apikey':self._apiKey, 'startDate':int(start_date.timestamp())*1000, 'endDate':int(end_date.timestamp())*1000, 'periodType':'day', 'frequencyType':'minute', 'frequency':30}
        return self._get_price_history(start_date, end_date, params, freq="hourly")
    
    def get_data_for(self, ticker : str):
        if self.has_dataframe():
            Logger().error("Fetching dataframe : never fetched pricing data. Ensure to call get_daily_price_history first.")
            return None
        return self._df.loc[ticker]
    
    def get_fundamentals(self):
        params = {'apikey':self._apiKey, 'projection': 'fundamental', 'symbol':','.join(self.tickers)}
        url = "https://api.tdameritrade.com/v1/instruments"
        out = get(url=url,params=params).json()
        df = DataFrame(out)
        if df.empty:
            # TODO : throw error
            Logger().error("Fundamentals retrieval failed.")
            return None
        df = df.transpose()
        fund = DataFrame([data for data in df['fundamental'].values]).set_index('symbol')
        return df.drop('fundamental', axis=1).join(fund)
    
    def __name__(self):
        return "[TD Ameritrade API] Data Fetcher"

# class FeedHandler:

#     @classmethod
#     def load_from_data_fetchers(cls, data_fetcher : DataFetcher, start_date : datetime=None, interval='1d', debug=False):
#         fetcher = data_fetcher._fetcher
#         if interval == '1d':
#             data = data_fetcher.get_daily_price_history(start_date)
#             tickers = data_fetcher.get_tickers()
#             return cls(data, tickers, start_date, debug, fetcher=fetcher)
#         elif interval == '1h':
#             data = data_fetcher.get_hourly_price_history(start_date)
#             tickers = data_fetcher.get_tickers()
#             return cls(data, tickers, start_date, debug, fetcher=fetcher)
#         else:
#             raise Exception('invalid args')

#     @classmethod
#     def load_from_csv(cls, path_to_csv : str, start_date : datetime, debug=False):
#         data = read_csv(path_to_csv)    
#         tickers = list(set(data['Ticker']))
#         data.set_index(['Ticker','Date'], inplace=True)
#         data.index = data.index.set_levels([data.index.levels[0], to_datetime(data.index.levels[1])])
#         return cls(data, tickers, start_date, debug)