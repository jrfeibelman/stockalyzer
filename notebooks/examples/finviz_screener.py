from finviz import Screener
import argparse

# TABLE_TYPES = {
#     "Overview": "111",
#     "Valuation": "121",
#     "Ownership": "131",
#     "Performance": "141",
#     "Custom": "152",
#     "Financial": "161",
#     "Technical": "171",
# }

def screen(filters=['idx_sp500'], table='Performance', output_name="screened_results", save=False):
    stocks = Screener(filters=filters, table=table)
    if save:
        stocks.to_csv(f"{output_name}.csv")
        
    return stocks

def screen_tickers(tickers:[str], table='Overview', output_name="screened_results", save=False):
    stocks = Screener(tickers=tickers, table=table)
    
    if save:
        stocks.to_csv(f"{output_name}.csv")
        
    return stocks

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--tickers', dest='tickers', help='list of ticker strings <["t1","t2"..."tN"]>')
    parser.add_argument('--filters', dest='filters', default="idx_sp500", help='list of filter strings <["f1","f2"..."fN"]>')
    parser.add_argument('--save', dest='save', default=False, help='save file? True or False')
    parser.add_argument('--output_name', dest='output_name', default="screened_results", help='Output file to save to, must set save=True')
    parser.add_argument('--table', dest='table', default="Overview", help='<"Overview", "Valuation", "Ownership", "Performance", "Custom", "Financial", "Technical"')
    args = parser.parse_args()
    
    if args.tickers:
        tickers = args.tickers.strip('][').split(', ')
        results = screen_tickers(tickers, table=args.table, output_name=args.output_name, save=args.save)
    else:
        filters = args.filters.strip('][').split(', ')
        results = screen(filters=filters, table=args.table, output_name=args.output_name, save=args.save)
    print(results)
