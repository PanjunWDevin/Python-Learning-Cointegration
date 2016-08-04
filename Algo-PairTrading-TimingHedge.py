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
#stock price ranges from 2016-07-30 to 2014-07-02, amounting to 510 numbers
#stock_prices['601800'] = X,  stocks['601818'] = Y
stock1_prices = stock_prices.loc[0:509,'601800']
stock2_prices = stock_prices.loc[0:509,'601818']

#per_change of stock1 and stock2
p_change_1 = stock_prices.loc[0:513,'601800'].iloc[::-1].pct_change()
p_change_2 = stock_prices.loc[0:513,'601818'].iloc[::-1].pct_change()

#get 'sz50' board Index historic data 'sz50'
index = ts.get_hist_data('sz50',start='2013-01-01',end = '2016-07-30')
index_watch = index['p_change']

index_test = index['close'].loc['2016-06-30':'2014-07-02']

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
    prices_series = stock_prices['601818'] - coff_regression * stock_prices['601800']

    #get the z_score_s
    n = m
    i = 0

    #consider changing to rollign window function
    #Remark: the current stock price should use the past 100 days (excluding today's) price history
    while n != 0:
        z_score_s[i] = (prices_series[n] - prices_series[n:n+100].mean())/prices_series[n:n+100].std()
        i += 1
        n -= 1

    return z_score_s, m

z_scores, m = cal_z_score()

#set up initial positions of stock 1 and stock 2
#portfolio = stock1_positions * stock1_price + stock2_positions * stock2_price + residual
portfolios = np.zeros(m+1) #initial point is right before 2014-07-01
#price on 2014-07-01 corresponding to row m and column 'stock code'
stock1_prices[m] = stock_prices.loc[m,'601800']
stock2_prices[m] = stock_prices.loc[m,'601818']
#intial portfolio value set at CNY100,000, beginning at 2014-07-01 with p% on stock_1, q% on stock_2
portfolios[0] = 100000
stock1_position = int(p*portfolios[0]/stock1_prices[m]) #initial position in stock1
stock2_position = int(q*portfolios[0]/stock2_prices[m]) #initial position in stock2
cash = portfolios[0] - stock1_position*stock1_prices[m] - stock2_position*stock2_prices[m]

# input is the signals, calculate the positions changes, assuming no transaction fees
def portfolio_positions(z_scores,portfolios,stock1_position,stock2_position,cash):
    pindex = m
    for count in range(1,m+1,1):
        # judege whether the overall market is experiencing a downtrend
        # SZ50 index drops 5% over a day, cash out all the positions
        # SZ50 continouely drop for three days cash out the position
        # if the holding stock declines over 2% in subsequent 3 days, cash out all positions

        if  (p_change_1[pindex-1]< 0 and p_change_1[pindex]<0 and p_change_1[pindex+1]<0) or (p_change_2[pindex-1]< 0 and p_change_2[pindex]<0 and p_change_2[pindex+1]<0):
            portfolios[count] = cash + stock1_position * stock1_prices[pindex - 1] + stock2_position * stock2_prices[pindex - 1]  # update portfolio value
            stock1_position = 0 #sell all positions in stock 1
            stock2_position = 0 #sell all positions in stock 2
            cash = portfolios[count] #cash out all the positions thus now cash holding equals to the portfolio

        if (z_scores[count - 1] < -1): # full position in stock2
            stock2_added = int((stock1_position*stock1_prices[pindex-1]+cash)/stock2_prices[pindex-1]) # sell all stock1 position and buy in stock2
            stock2_position = stock2_position + stock2_added #update stock2 position
            cash = stock1_position*stock1_prices[pindex]+cash - stock2_added * stock2_prices[pindex - 1] #calculate the residual cash
            stock1_position = 0 #update stock1 position
            portfolios[count] = cash + stock1_position * stock1_prices[pindex-1] + stock2_position * stock2_prices[pindex -1] #update portfolio value

        elif (z_scores[count - 1] > 1): # full position in stock1
            stock1_added = int((stock2_position * stock2_prices[pindex - 1] + cash) / stock1_prices[pindex - 1]) # sell all stock2 position and buy in stock1
            stock1_position = stock1_position + stock1_added #update stock1 position
            cash = stock2_position * stock2_prices[pindex-1] + cash - stock1_added * stock1_prices[pindex - 1] # calculate the residual cash
            stock2_position = 0 # update stock2 position
            portfolios[count] = cash + stock1_position * stock1_prices[pindex - 1] + stock2_position * stock2_prices[pindex - 1] #update porfolio

        elif (z_scores[count-1] == 0): # if cross the zero point
            if (stock1_position == 0) or (stock2_position == 0): # whether there is a full position in stock1 or stock2
                temp_portfolio = cash + stock2_position*stock2_prices[pindex-1] + stock1_position*stock1_prices[pindex-1]
                stock1_position = int(p*temp_portfolio/stock1_prices[pindex-1])
                stock2_position = int(q*temp_portfolio/stock2_prices[pindex-1])
                cash = temp_portfolio - stock1_position * stock1_prices[pindex-1] - stock2_position * stock2_prices[pindex-1]
                portfolios[count] = temp_portfolio

        else:
            portfolios[count] = cash + stock1_prices[pindex-1]*stock1_position + stock2_prices[pindex-1]*stock2_position #update portfolio
        #print stock1_position;print stock2_position
        pindex = pindex - 1
    return portfolios


portfolio_values = portfolio_positions(z_scores, portfolios, stock1_position, stock2_position, cash)
#print portfolio_values

#calculate the return plot, incorporating date index
stock_prices.loc[m,'date'] = '2014-07-01'
date_range = stock_prices.loc[0:m,'date']
#print date_range

portfolio_output = pd.Series(portfolio_values[::-1],index=date_range)
portfolio_output= portfolio_output.iloc[::-1]
#index_benchmark = index.loc['2016-06-30':'2014-07-01','close'].iloc[::-1]
#index_benchmark = 100*(index_benchmark/index_benchmark[0])
portfolio_output = 100*(portfolio_output/portfolio_output[0])

#index_benchmark.plot(color = 'r')
portfolio_output.plot(color = 'b')
plt.show()
plt.xlabel('date')
plt.ylabel('Performance')

#calculate backwardation of the portfolio
backward = portfolio_output.pct_change()*100
print type(backward)
backward.plot(color = 'r')
plt.show()
#output the maximum backwardation
print backward.max() #this portfolio's maximum backwardation is 10.14%


#benchmark1.plot()
#benchmark2.plot()

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


## test z_scores
#print z_scores
#plt.plot(z_scores)
#plt.axhline(z_scores.mean(), color="black")
#plt.axhline(1.0, color="red", linestyle="--")
#plt.axhline(-1.0, color="green", linestyle="--")
#plt.legend(["z-scores", "mean", "+1", "-1"])
#plt.show()
#print m
#print z_scores.size
