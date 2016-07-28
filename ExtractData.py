import tushare as ts

sz_50_list = ts.get_sz50s()
stock_list = sz_50_list['code']
print stock_list
print stock_list.size

for i in range(0,stock_list.size,1):
    print stock_list[i]
    df = ts.get_hist_data(stock_list[i],start='2012-01-01',end='2013-01-01')
    df.to_csv("path"+stock_list[i]+".csv",columns=['close'])

