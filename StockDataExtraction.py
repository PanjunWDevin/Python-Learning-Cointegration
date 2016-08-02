# A simple python script to download china A shares, detailed documentation pls refer to Tushare.org

import tushare as ts
import pandas as pd

hs_300_list = ts.get_hs300s()
for stock in stock_list:
    temp_s = ts.get_h_data(stock,start='2006-01-01',end = '2016-06-30')
    stock_list.to_csv("/StockListCodes.csv")
