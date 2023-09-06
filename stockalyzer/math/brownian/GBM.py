from math import exp, sqrt, pi
from time import time
from numpy import exp as npexp
from numpy import sqrt as npsqrt
from numpy import log, zeros_like, cumsum, arange
from numpy.random import normal, seed, standard_normal
from pandas import DatetimeIndex, date_range, DataFrame

class BrownianSimulator:

    def __init__(self):
        seed(int(time()))

    def randomNormal(self, lower=0, upper=1):
        ''' Randomly distributed normal number between 0 and 1 '''
        return normal(0)

    def dN(self, x):
        ''' dN(x) : Probability density function of standard normal random variable x. '''
        return exp(-0.5 * x ** 2) / sqrt(2 * pi)

    # def N(self, d): # requires scipy...
    #     ''' N(x) : Cumulative density function of standard normal random variable x. '''
    #     return quad(lambda x: dN(x), -20, d, limit=50)[0]

    def sim_brownian_motion_interval(self, T, dt=1):
        N = int(T / dt)
        sqrdt = sqrt(dt)
        bm = 0
        for i in range(N):
            bm = bm + sqrdt * normal(0, 1)
            
        return bm

    def sim_geometric_brownian_motion_interval(self, S0, mu, sigma, T, dt=1):
        N = int(T / dt)
        sigsqrdt = sigma * sqrt(dt)
        drift = (mu - .5 * sigma * sigma) * dt
        logS = log(S0)
        
        for i in range(N):
            logS = logS + drift + sigsqrdt * normal(0, 1)
            yield npexp(logS)

    def sim_single_gbm_increment(self, S0, mu, sigma, dt=1):
        sigsqrdt = sigma * sqrt(dt)
        drift = (mu - .5 * sigma * sigma) * dt
        logS = log(S0) + drift + sigsqrdt * normal(0, 1)
        return npexp(logS)






def sim_geometric_brownian_motion_for_interval(S0, T, r, vol, start_date_str='30-09-2004', end_date_str='30-09-2014'):
    # model parameters ^
    
    # simulation parameters
    seed(time())
    gbm_dates = DatetimeIndex(date_range(start=start_date_str, end=end_date_str))
    M = len(gbm_dates) # time steps
    I = 1 # index level paths
    dt = 1 / 252. # fixed for simplicity
    df = exp(-r * dt) # discount factor
    
    # stock price paths
    rand = standard_normal((M, I)) # random numbers 
    S = zeros_like(rand) # stock matrix
    S[0] = S0 # initial values
    for t in range(1, M): # stock price paths
        S[t] = S[t - 1] * npexp((r - vol ** 2 / 2) * dt + vol * rand[t] * sqrt(dt))
        
    gbm = DataFrame(S[:, 0], index=gbm_dates, columns=['index'])
    gbm['returns'] = log(gbm['index'] / gbm['index'].shift(1))
    
    # Realized Volatility (eg. as defined for variance swaps)
    gbm['rea_var'] = 252 * cumsum(gbm['returns'] ** 2) / arange(len(gbm)) 
    gbm['rea_vol'] = npsqrt(gbm['rea_var'])
    gbm = gbm.dropna()
    return gbm