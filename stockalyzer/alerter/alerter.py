import pandas as pd
from stockalyzer.data import TDDataFetcher
from twilio.rest import Client
from ordered_set import OrderedSet
from threading import Timer
from datetime import datetime, timedelta



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
        self.data = TDDataFetcher(tickers).get_daily_price_history(datetime(2020, 1, 1))
        self.data["Signal"] = 0
        self.client = Client("AC069dc7540b34e4d53552123ac96f97ff", "5b460db1d5b41a9436bec81aaaa6d515")
        
        EMA20 = []
        EMA50 = []

        count = 0

        # Assuming we have same # of data points for every stock !!
        for ticker in OrderedSet(self.data.index.get_level_values(0)):
            close = self.data.loc[ticker, 'Close']
            current_EMA20 = close.ewm(span=20,adjust=False).mean()
            current_EMA50 = close.ewm(span=50,adjust=False).mean()
            EMA20.extend(current_EMA20)
            EMA50.extend(current_EMA50)


            for i in range(1,len(close)):
                if current_EMA50[i] > current_EMA20[i] and current_EMA50[i-1] < current_EMA20[i-1]:
                    if close[i] < current_EMA20[i] and close[i] < current_EMA50[i]:
        #                 data.loc[ticker].iloc[i, data.columns.get_loc("Signal")] = -1 # SELL
                        self.data.iloc[i + count * int(len(self.data)/len(tickers)), self.data.columns.get_loc("Signal")] = -1 # SELL
                elif current_EMA50[i] < current_EMA20[i] and current_EMA50[i-1] > current_EMA20[i-1]:
                    if close[i] > current_EMA20[i] and close[i] > current_EMA50[i]:
        #                 self.data.loc[ticker].iloc[i, self.data.columns.get_loc("Signal")] = 1 # BUY
                        self.data.iloc[i + count * int(len(self.data)/len(tickers)), self.data.columns.get_loc("Signal")] = 1 # BUY

            count += 1
        
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
        
# Methods to run the alerter:
        
# Run at a future date
def main_alert():
        SP500_TICKERS = pd.read_csv("SP500.csv")['Symbol'].tolist()[20:50]
        pa = PortfolioAlerter(SP500_TICKERS)
        pa.computeAlerts()
            
def run_at_future_date():
    while True:
        now = datetime.today()
        later = now.replace(day=now.day, hour= 2, minute=0, second=0, microsecond=0) #+ timedelta(days=1)
        delta = later - now
        secs = delta.total_seconds()

        t = Timer(secs, main_alert)
        t.start()
        
# Run infinitely every X amount of time
def run_every_time_interval():
    sleep_hours = (12) * 60 * 60

    while 1: 
        main_alert()
        dt = datetime.now() + timedelta(hours=12) 
        dt = dt.replace(minute=10)

        while datetime.now() < dt:
            time.sleep(sleep_hours)