import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd




def get_data(start_date, end_date, symbols):
    timeofday = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(start_date, end_date, timeofday)

    dataobj = da.DataAccess('Yahoo')
    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    data = dataobj.get_data(timestamps, symbols, keys)
    prices = dict(zip(keys, data))

    close_price = prices['close'].values
    
    return close_price

def simulate(start_date, end_date, symbols, allocations):
    daily_close = get_data(start_date, end_date, symbols)


    # Standard deviation of daily returns of the total portfolio
    norm_prices = daily_close / daily_close[0, :]
    daily_returns = norm_prices.copy()
    tsu.returnize0(daily_returns)
    
    print daily_returns
    
    portfolio = daily_close * allocations
    
    print portfolio
    
    
    # Average daily return of the total portfolio
    # Sharpe ratio (Always assume you have 252 trading days in an year. And risk free rate = 0) of the total portfolio
    # Cumulative return of the total portfolio    


symbols = ["XOM", "JNJ", "GE", "NFLX"]
allocations = [0.30, 0.2, 0.25, 0.25]
start_date = dt.datetime(2010, 1, 1)
end_date = dt.datetime(2011, 12, 31)

simulate(start_date, end_date, symbols, allocations)