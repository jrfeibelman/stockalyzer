import finviz
import yfinance as yf

class Stock:
    
    def __init__(self, ticker, **kwargs):
        
        self.ticker = ticker
        
        # Backtrader
#         self.strategy_perf = kwargs.get('strategy_perf',None)
        
        # TDAmeritrade
        self.fundamentals = kwargs.get('fundamentals',dict())
        
        # FINVIZ
        self.finviz = kwargs.get('finviz',False)
        if self.finviz:
            self.stats = finviz.get_stock(self.ticker)
            self.news = finviz.get_news(self.ticker)
            self.ratings = finviz.get_analyst_price_targets(self.ticker,last_ratings=8)
            self.insider_trades = finviz.get_insider(self.ticker)

            self.company_name = self.stats['Company']
            self.sector = self.stats['Sector'] 
            self.industry = self.stats['Industry']
            self.country = self.stats['Country']
            self.index = self.stats['Index']
            
        self.yahoo = kwargs.get('yahoo',False)
        if self.yahoo:
            self.yf_ticker = yf.Ticker(self.ticker)

            
        # Basic info
#         self.sector = kwargs.get('sector',self.sector)
#         self.industry = kwargs.get('industry',self.industry)
        
        
#     def get_perf(self):
#         return self.strategy_perf
    
    def get_fundamentals(self):
        return self.fundamentals
    
    def get_fundamental(self, metric:str):
        return self.fundamentals[metric]
    
    def __str__(self):
        return f"{self.ticker}"
        
#     @classmethod
#     def load_stocks_from(cls, tickers:[str], strat_perf:pd.DataFrame, fundamentals:dict):            
#         return [cls(t, strat_perf=strat_perf.loc[t], fundamentals=fundamentals.loc[t].to_dict()) for t in tickers]
        
        
        
        
        