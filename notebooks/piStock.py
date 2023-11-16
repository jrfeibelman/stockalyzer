import pandas as pd
from datetime import datetime, date, timedelta
import time
import requests
import os
# import import_ipynb
from threading import Timer
import abc
from ordered_set import OrderedSet
import configparser
from twilio.rest import Client
# import mplfinance as mpf
# import matplotlib.pyplot as plt
# from IPython.core.interactiveshell import InteractiveShell
# InteractiveShell.ast_node_interactivity = "all"
# %matplotlib inline
# pd.set_option('display.max_rows', None)

class DataGenerator(metaclass=abc.ABCMeta):
    """
        Abstract base class for aquiring stock data
    """
    def __init__(self, tickers : [str]):
        self.tickers = tickers
        self._df = None
    
    def get_tickers(self):
        return self.tickers
        
    def has_dataframe(self):
        if self._df is None:
            return True
        return False
    
    def get_dataframe(self):
        return self._df
    
    @abc.abstractmethod
    def get_data_for(self, ticker : str):
        pass
    
class DataFetcher(DataGenerator):
    """
        Abstract base class for fetching historical stock data from external API's and websites
    """
    def __init__(self, tickers : [str]):
        super(DataFetcher, self).__init__(tickers)
        
    @abc.abstractmethod
    def _get_price_history(self, start_date : datetime, end_date : datetime):
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
    
class TDDataFetcher(DataFetcher):
    def __init__(self, tickers : [str], config_path = ""):
        super(TDDataFetcher, self).__init__(tickers)
        config = configparser.RawConfigParser()
        if config_path is "":
            home_dir = os.path.dirname(os.path.dirname(os.getcwd()))
            config.read('%s/config/config.ini' % home_dir)
        else:
            config.read(config_path)
        self.__apiKey = config.get('TD', 'apiKey') # TODO : tthrow error if no key found
      
    def _get_price_history(self, start_date : datetime, end_date : datetime, params : dict):
        data = []
        count = 0
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
            df.index = [datetime.fromtimestamp(i/1000).date() for i in df.index]
            df = df[['High','Low','Open','Close','Volume']]
            df.index = pd.to_datetime(df.index)
            data.append(df)
            count += 1
            if count % 110 == 0: # stay below transactions/second limit
                time.sleep(30)
        datas = map (data, self.tickers)
        self._df = pd.concat(data, keys=self.tickers, names=['Ticker', 'Date'])
        return self._df   
    
    def get_quotes(self):
        params = {'apikey':self.__apiKey, 'symbol':','.join(self.tickers)}
        url = "https://api.tdameritrade.com/v1/marketdata/quotes"
        out = requests.get(url=url,params=params).json()
        df = pd.DataFrame(out)
        if df.empty:
#             # TODO : throw error
            print("FALSE")
            return None
        return df.transpose()
    
    def get_daily_price_history(self, start_date : datetime, end_date=date.today()):
        params = {'apikey':self.__apiKey, 'startDate':int(start_date.strftime('%s'))*1000, 'endDate':int(end_date.strftime('%s'))*1000, 'periodType':'month', 'frequencyType':'daily'}
        return self._get_price_history(start_date, end_date, params)
    
    def get_data_for(self, ticker : str):
        if self.has_dataframe():
            print("[ERROR] [TDDataFetcher] fetching dataframe : never fetched pricing data. Ensure to call get_daily_price_history first.")
            return None
        return self._df.loc[ticker]
    
class StockAlert:
    def __init__(self, ticker, signal, signal_date, close_price):
        self.ticker = ticker
        self.signal = signal
        self.date = signal_date
        self.price = close_price
        self.strategy = ""
        
        if signal == 1:
            self.strategy = "BUY"
        elif signal == -1:
            self.strategy = "SELL"
        
    def __str__(self):
        return "ALERT [%s]: %s %s at %s" % (self.date, self.strategy, self.ticker, self.price)

class PortfolioAlerter:
    def __init__(self, tickers : [str]):
        self.tickers = tickers
#         self.data = TDStockFetcher(tickers).get_historic_daily_quotes(datetime(2020, 1, 1))
        self.data = TDDataFetcher(tickers).get_daily_price_history(datetime(2020, 1, 1))
#         self.data["20EMA"] = 0.0
#         self.data["50EMA"] = 0.0
        self.data["Signal"] = 0
        self.client = Client("AC069dc7540b34e4d53552123ac96f97ff", "5b460db1d5b41a9436bec81aaaa6d515")
        
        EMA20 = []
        EMA50 = []

        for ticker in OrderedSet(self.data.index.get_level_values(0)):
            close = self.data.loc[ticker, 'Close']
#             df["5EMA"] = df['Close'].ewm(span=5,adjust=False).mean()
#             df["8EMA"] = df['Close'].ewm(span=8,adjust=False).mean()
#             df["13EMA"] = df['Close'].ewm(span=13,adjust=False).mean()
            current_EMA20 = close.ewm(span=20,adjust=False).mean()
            current_EMA50 = close.ewm(span=50,adjust=False).mean()
            EMA20.extend(current_EMA20)
            EMA50.extend(current_EMA50)
#             df["Flag"] = 0
        
            for i in range(1,len(close)):
                if current_EMA50[i] > current_EMA20[i] and current_EMA50[i-1] < current_EMA20[i-1]:
                    if close[i] < current_EMA20[i] and close[i] < current_EMA50[i]:
                        self.data.loc[ticker].iloc[i, self.data.columns.get_loc("Signal")] = -1 # SELL
                elif current_EMA50[i] < current_EMA20[i] and current_EMA50[i-1] > current_EMA20[i-1]:
                    if close[i] > current_EMA20[i] and close[i] > current_EMA50[i]:
                        self.data.loc[ticker].iloc[i, self.data.columns.get_loc("Signal")] = 1 # BUY
        
        self.data["20EMA"] = EMA20
        self.data["50EMA"] = EMA50
        
#         self._computeAlerts()
        
    def computeAlerts(self):
        alerts = []
        
        for ticker in OrderedSet(self.data.index.get_level_values(0)):
            tail = self.data.loc[ticker].tail(3)
            tail = tail.loc[tail["Signal"] != 0]
            
            if tail["Signal"].any():
                row_data = tail.iloc[-1]
                alert = StockAlert(ticker, row_data["Signal"], row_data.name, row_data["Close"])
                alerts.append(str(alert))
        
        if len(alerts) > 0:
            self._sendAlerts(alerts)
                
    def _sendAlerts(self, alerts):
        alert_msg = '\n'.join(alerts)
        print(alert_msg)
        self.client.messages.create(to="+19149800095", from_="+14159388441", body=alert_msg)
    

def main():
    SP500_TICKERS = pd.read_csv("SP500.csv")['Symbol'].tolist()
    pa = PortfolioAlerter(SP500_TICKERS)
    pa.computeAlerts()

# Run at a future date
def run_at_future_date():
    now = datetime.today()
    later = now.replace(day=now.day, hour= 12, minute=15, second=0, microsecond=0) + timedelta(days=1)
    delta = later - now
    secs = delta.total_seconds()

    def main2():
        main()
        run_at_future_date()

    t = Timer(secs, main2)
    t.start()

# Run infinitely
def run_forever():
    # Run infinitely every X amount of time
    sleep_hours = (12) * 60 * 60
            
    while 1: 
        main()
        dt = datetime.now() + timedelta(hours=12) 
        dt = dt.replace(minute=10)
        
        while datetime.now() < dt:
            time.sleep(sleep_hours)
              
run_at_future_date()