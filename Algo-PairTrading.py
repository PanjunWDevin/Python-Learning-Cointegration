#Develop a pair trading framework based on cointegration

# Based on the program PairTradingCointegration.py get the cointegrated stocks and conduct backtesting from
# 2015-07-01 to 2016-07-01

import numpy as np
import pandas as pd
import statsmodels.api as sm
import tushare as ts
import matplotlib.pyplot as plt

# two stocks : '002142', '601988'
portfolio_value = 100000  #intial portfolio value set at $100,000

stock_1 = '002142'
stock_2 = '601988'

coff_regression = 0.179 #coefficient of stock_1 is 0.179

p_stock_1 = 0.5 # stock_1's position in the portfolio
p_stock_2 = 1 - p_stock_1 # stock_1's position in the portfolio


def cal_z_score():

    stock_1_price = ts.get_hist_data(stock_1,start = '2015-07-01',end = '2016-07-01')['close']

    stock_2_price = ts.get_hist_data(stock_1,start = '2015-07-01',end = '2016-07-01')['close']

    stock_series = stock_2_price - coff_regression * stock_1_price

    s_mean = stock_series.mean()

    s_sigma = np.std(stock_series)

    z_score_s = (stock_series - s_mean)/s_sigma

    return z_score_s

z_score_s = cal_z_score()

count = z_score_s.size

#def change_positions():
index = count - 1

while (index != -1):
