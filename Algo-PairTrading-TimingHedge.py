# Based on the program PairTradingCointegration.py get the cointegrated stocks and conduct backtesting from
# 2014-07-02 to 2016-07-30
# 30 Jul 2016, consider adding a time hedge strategy using China SZ50 index
# should have stop loss line
import numpy as np
import pandas as pd
import statsmodels.api as sm
import tushare as ts
import matplotlib.pyplot as plt

# two stocks : '002142', '601988'
stock_1 = '601800'
stock_2 = '601818'

coff_regression = 0.7745 # stock_2 = 0.7745 * stock_1 + e

p = 0.5     # stock_1's portion in the portfolio
q = 1 - p   # stock_2's portion in the portfolio

stock_prices = pd.read_csv('/Users/panjunwang/PycharmProjects/PythonWork/PairTradingFrameWork/pairstockprices.csv')

#print stock_prices.loc[509,'date']
#stock price ranges from 2016-07-30 to 2014-07-02, totaling 510 numbers
#stock_prices['601800'] = X,  stocks['601818'] = Y
stock1_prices = stock_prices.loc[0:509,'601800']
stock2_prices = stock_prices.loc[0:509,'601818']
#print stock1_prices #print stock2_prices.size
#print stock1_prices print stock2_prices
#print stock_prices

#print stock_prices.shape[0]

#get 'sz50' board Index historic data 'sz50'
index = ts.get_hist_data('sz50',start='2013-01-01',end = '2016-07-30')
index_watch = index['p_change']

#print index_watch

index_p = index['close'].loc['2016-07-30':'2014-07-02']
#print index_p.size

#get signals for the positions changes
def cal_z_score():

    #get the z_score size both backtested stocks should have the same size
    m = stock1_prices.size

    #create z_score series
    z_score_s = np.zeros(m)

    #we use 100 days' price data to calculate the z_score
    #initialize the prices
    prices_series = coff_regression * stock_prices['601800'] - stock_prices['601818']

    #get the z_score_s
    n = m
    i = 0
    while n != 0:
        z_score_s[i] = (prices_series[n-1] - prices_series[n-1:n+99].mean())/prices_series[n-1:n+99].std()
        i += 1
        n -= 1

    return z_score_s, m

z_scores, m = cal_z_score()

#print z_scores
#plt.plot(z_scores)
#plt.axhline(z_scores.mean(), color="black")
#plt.axhline(1.0, color="red", linestyle="--")
#plt.axhline(-1.0, color="green", linestyle="--")
#plt.legend(["z-scores", "mean", "+1", "-1"])
#plt.show()

#print m
#print z_scores.size
#set up initial positions of stock 1 and stock 2
#portfolio = stock1_positions * stock1_price + stock2_positions * stock2_price + residual

portfolios = np.zeros(m+1) #initial point is right before 2014-07-02

stock1_prices[m] = stock_prices.loc[m,'601800']
stock2_prices[m] = stock_prices.loc[m,'601818']

#intial portfolio value set at $100,000
portfolios[0] = 100000
stock1_position = int(p*portfolios[0]/stock1_prices[m]) #initial position in stock1
#print stock1_prices[m]
#print stock1_position*stock1_prices[m]
stock2_position = int(q*portfolios[0]/stock2_prices[m]) #initial position in stock2
#print stock2_prices[m]
#print stock2_position*stock2_prices[m]
cash = portfolios[0] - stock1_position*stock1_prices[m] - stock2_position*stock2_prices[m]
#print 'initial cash:',cash


# input is the signals, calculate the positions changes
def portfolio_positions(z_scores,portfolios,stock1_position,stock2_position,cash):
    pindex = m
    for count in range(1,m+1,1):
        # judege whether the overall market is experiencing a downtrend
        # SZ50 index drops 5% over a day, cash out all the positions, or continousy drop 3 days every day over 2%
        if (index_watch[pindex - 1] < -5):
            portfolios[count] = cash + stock1_position * stock1_prices[pindex - 1] + stock2_position * stock2_prices[pindex - 1]  # update portfolio value
            stock1_position = 0 #sell all positions in stock 1
            stock2_position = 0 #sell all positions in stock 2
            cash = portfolios[count] #cash out all the positions thus now cash holding equals to the portfolio

        elif z_scores[count - 1] > 1: # full position in stock2
            stock2_added = int((stock1_position*stock1_prices[pindex-1]+cash)/stock2_prices[pindex-1]) # sell all stock1 position and buy in stock2
            stock2_position = stock2_position + stock2_added #update stock2 position
            cash = stock1_position*stock1_prices[pindex]+cash - stock2_added * stock2_prices[pindex - 1] #calculate the residual cash
            stock1_position = 0 #update stock1 position
            portfolios[count] = cash + stock1_position * stock1_prices[pindex-1] + stock2_position * stock2_prices[pindex -1] #update portfolio value

        elif z_scores[count - 1] < -1: # full position in stock1
            stock1_added = int((stock2_position * stock2_prices[pindex - 1] + cash) / stock1_prices[pindex - 1]) # sell all stock2 position and buy in stock1
            stock1_position = stock1_position + stock1_added #update stock1 position
            cash = stock2_position * stock2_prices[pindex-1] + cash - stock1_added * stock1_prices[pindex - 1] # calculate the residual cash
            stock2_position = 0 # update stock2 position
            portfolios[count] = cash + stock1_position * stock1_prices[pindex - 1] + stock2_position * stock2_prices[pindex - 1] #update porfolio

        elif z_scores[count-1] == 0: # if cross the zero point
            if stock1_position == 0 or stock2_position == 0: # whether there is a full position in stock1 or stock2
                temp_portfolio = cash + stock2_position*stock2_prices[pindex-1] + stock1_position*stock1_prices[pindex-1]
                stock1_position = int(p*temp_portfolio/stock1_prices[pindex-1])
                stock2_position = int(q*temp_portfolio/stock2_prices[pindex-1])
                cash = temp_portfolio - stock1_position * stock1_prices[pindex-1] - stock2_position * stock2_prices[pindex-1]
                portfolios[count] = temp_portfolio

        else:
            portfolios[count] = cash + stock1_prices[pindex-1]*stock1_position + stock2_prices[pindex-1]*stock2_position #update portfolio

        pindex = pindex - 1
    return portfolios


portfolio_values = portfolio_positions(z_scores, portfolios, stock1_position, stock2_position, cash)
#print portfolio_values

#calculate the return plot, incorporating date index
stock_prices.loc[m,'date'] = '2014-07-01'
date_range = stock_prices.loc[0:m,'date']
#print date_range

portfolio_output = pd.Series(portfolio_values[::-1],index=date_range)
portfolio_output=portfolio_output.iloc[::-1]
portfolio_output = 100*(portfolio_output/portfolio_output[0])
print portfolio_output
portfolio_output.plot()
#benchmark1.plot()
#benchmark2.plot()
plt.show()

#benchmark1 = stock_1_b_t.iloc[::-1]
#benchmark1 = 100*(benchmark1/benchmark1[0])
#print benchmark1

#benchmark2 = stock_2_b_t.iloc[::-1]
#benchmark2 = 100*(benchmark2/benchmark2[0])
#print benchmark2 - benchmark1

#index_watch_output = index_watch_slice.iloc[::-1]
#print index_watch_output
#index_watch_output.plot()
#plt.show()

#stock_1_b_t = stock_1_b_t.iloc[::-1]
#stock_1_b_t.plot()
#print stock_1_b_t
#plt.show()

#stock_2_b_t = stock_2_b_t.iloc[::-1]
#stock_2_b_t.plot()
#print stock_2_b_t
#plt.show()
