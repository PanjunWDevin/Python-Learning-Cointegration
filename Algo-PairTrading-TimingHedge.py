# Based on the program PairTradingCointegration.py get the cointegrated stocks and conduct backtesting from
# 2015-01-02 to 2016-07-20
# 30 Jul 2016, consider adding a time hedge strategy using China SME index

import numpy as np
import pandas as pd
import statsmodels.api as sm
import tushare as ts
import matplotlib.pyplot as plt

# two stocks : '002142', '601988'
stock_1 = '002091'
stock_2 = '002096'

coff_regression = 0.6295 #coefficient of stock_1 is 0.179

p = 0.5     # stock_1's portion in the portfolio
q = 1 - p   # stock_2's portion in the portfolio

stock_1_prices = ts.get_hist_data(stock_1,start = '2013-01-01',end = '2016-07-20')['close']
stock_1_b_t = stock_1_prices.loc['2016-07-20':'2014-01-02']

stock_2_prices = ts.get_hist_data(stock_1,start = '2013-01-01',end = '2016-07-20')['close']

#get SME board Index historic data 'zxb'
index_watch = ts.get_hist_data('zxb',start='2013-01-01',end = '2016-07-20')['p_change']

#get signals for the positions changes
def cal_z_score():

    #get the z_score size both backtested stocks should have the same size
    m = stock_1_b_t.size

    #create z_score series
    z_score_s = np.zeros(m)

    #we use 100 days' price data to calculate the z_score
    #initialize the prices
    prices_series = coff_regression * stock_1_prices - stock_2_prices

    #get the z_score_s
    n = m
    i = 0
    while n != 0:
        z_score_s[i] = (prices_series[n-1] - prices_series[n-1:n+99].mean())/prices_series[n-1:n+99].std()
        i += 1
        n -= 1

    return z_score_s, m

z_scores, m = cal_z_score()

#set up initial positions of stock 1 and stock 2
portfolios = np.zeros(m+1)  #portfolio = stock1_positions * stock1_price + stock2_positions * stock2_price + residual

#no transcation fees added, initialize the parameters, considering residual cash in this case

portfolios[0] = 100000      #intial portfolio value set at $100,000
stock1_position = int(p*portfolios[0]/stock_1_prices[m]) #initial position in stock1
stock2_position = int(q*portfolios[0]/stock_2_prices[m]) #initial position in stock2
cash = portfolios[0] - stock1_position*stock_1_prices[m] - stock2_position*stock_2_prices[m]

# input is the signals, calculate the positions changes
def portfolio_positions(z_scores,portfolios,stock1_position,stock2_position,cash):
    count = 1
    pindex = m
    for count in range(1,m+1,1):
        # judege whether the overall market is experiencing a downtrend
        if (index_watch[pindex - 1] < -5):  # SME index drops 5% over a day, cash out all the positions
            portfolios[count] = cash + stock1_position * stock_1_prices[pindex - 1] + stock2_position * stock_2_prices[pindex - 1]  # update portfolio value
            stock1_position = 0 #sell all positions in stock 1
            stock2_position = 0 #sell all positions in stock 2
            cash = portfolios[count] #cash out all the positions thus now cash holding equals to the portfolio
        elif z_scores[count-1] > 1: # full position in stock2
            stock2_added = int((stock1_position*stock_1_prices[pindex-1]+cash)/stock_2_prices[pindex-1]) # sell all stock1 position and buy in stock2
            stock2_position = stock2_position + stock2_added #update stock2 position
            cash = stock1_position*stock_1_prices[pindex]+cash - stock2_added * stock_2_prices[pindex - 1] #calculate the residual cash
            stock1_position = 0 #update stock1 position
            portfolios[count] = cash + stock1_position * stock_1_prices[pindex-1] + stock2_position * stock_2_prices[pindex -1] #update portfolio value
        elif z_scores[count-1] < -1: # full position in stock1
            stock1_added = int((stock2_position * stock_2_prices[pindex - 1] + cash) / stock_1_prices[pindex - 1]) # sell all stock2 position and buy in stock1
            stock1_position = stock1_position + stock1_added #update stock1 position
            cash = stock2_position * stock_2_prices[pindex] + cash - stock1_added * stock_1_prices[pindex - 1] # calculate the residual cash
            stock2_position = 0 # update stock2 position
            portfolios[count] = cash + stock1_position * stock_1_prices[pindex - 1] + stock2_position * stock_2_prices[pindex - 1] #update porfolio
        elif z_scores[count-1] == 0: # if cross the zero point
            if stock1_position == 0 or stock2_position == 0: # whether there is a full position in stock1 or stock2
                temp_portfolio = cash + stock2_position*stock_2_prices[pindex-1] + stock1_position*stock_1_prices[pindex-1]
                stock1_position = int(p*temp_portfolio/stock_1_prices[pindex-1])
                stock2_position = int(q*temp_portfolio/stock_2_prices[pindex-1])
                cash = temp_portfolio - stock1_position * stock_1_prices[pindex-1] - stock2_position * stock_2_prices[pindex-1]
                portfolios[count] = temp_portfolio
        else:
            portfolios[count] = cash + stock_1_prices[pindex-1]*stock1_position + stock_2_prices[pindex-1]*stock2_position #update portfolio
        pindex = pindex - 1
        count = count + 1
    return portfolios

portfolio_values = portfolio_positions(z_scores, portfolios, stock1_position, stock2_position, cash)
#print portfolio_values

#calculate the return plot, incorporating date index
stock_1_b_t['2014-01-01'] = 0

portfolio_output = pd.Series(portfolio_values[::-1],index=stock_1_b_t.keys())
portfolio_output=portfolio_output.iloc[::-1]
portfolio_output.plot()
print portfolio_output
plt.show()
