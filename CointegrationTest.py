# this framework provides a way to do pair trading using co-integration
import numpy as np
import pandas as pd
import statsmodels.api as sm
import seaborn as sns
import tushare as ts
import matplotlib.pyplot as plt

# input is a DataFrame, Stock's Daily price
# initialize a functoin to find cointegration

def find_cointegration_pairs(dataframe):
    # get its length
    n = dataframe.shape[1]

    #initialize p - value matrix
    pvalue_mat = np.ones((n,n))

    # get the name of each column
    keys = dataframe.keys()

    # initilize the cointegration pairs
    pairs = []

    for i in range(n):
        for j in range(i+1,n,1):
            stock_1 = dataframe[keys[i]]
            stock_2 = dataframe[keys[j]]

            result = sm.tsa.stattools.coint(stock_1,stock_2)
            #get pvale
            pvalue = result[1]
            pvalue_mat[i,j]=pvalue
            if pvalue < 0.02: #only retain very significant cointegrated stocks
                # record the stock and corresponding p-value
                pairs.append((keys[i],keys[j],pvalue))

    return pvalue_mat, pairs

# find shang zheng 50 stocks
stock_list = ts.get_sz50s()['code']

#read data from tushare and store as csv file named stockprices.csv
#for code in stock_list:
#    price_df = ts.get_hist_data(code,start='2013-07-01',end='2014-07-01')
#    prices_df[code]=price_df['close']

#prices_df.to_csv('/Users/panjunwang/PycharmProjects/PythonWork/PairTradingFrameWork/stockprices.csv')

prices_df = pd.read_csv('/Users/panjunwang/PycharmProjects/PythonWork/PairTradingFrameWork/StockPrices_Pool.csv')

#clean the data, fill up the missing values
#'601985' all prices are not avaiable so drop this stock
prices_df = prices_df.drop('601985', 1)
# fill the missing values by method = pad, fill values forward
prices_df = prices_df.fillna(method= 'pad')
# drop the first column 'date'
prices_df = prices_df.drop('date',1)
# reverse the order of the prices
prices_df = prices_df.iloc[::-1]

pvalues, pairs = find_cointegration_pairs(prices_df)

print pairs

#choose the pair with the smallest value
p_ini = pairs[0][2]
stock_s1 = pairs[0][0]
stock_s2 = pairs[0][1]

for item in pairs:
    if item[2] < p_ini:
        stock_s1 = item[0]
        stock_s2 = item[1]

print(stock_s1)
print(stock_s2)

#run the regression on the tested pairs
#just to note, we still use stock_s1 = '601800', stock_s1 = '601818'
stock_s1 = '601800'
stock_s2 = '601818'

x = prices_df[stock_s1]
y = prices_df[stock_s2]

x.plot()
y.plot()
plt.show()

X = sm.add_constant(x)
result = (sm.OLS(y,X)).fit()
print (result.summary())

#beta coefficient 0.7745

#fig, ax = plt.subplots(figsize=(8,6))
#ax.plot(x, y, 'o', label="data")
#ax.plot(x, result.fittedvalues, 'r', label="OLS")
#ax.legend(loc='best')
#plt.show()

#plt.plot(0.6174*x-y)
#plt.axhline((0.6174*x-y).mean(), color="red", linestyle="--")
#plt.xlabel("Time"); plt.ylabel("Stationary Series")
#plt.legend(["Stationary Series", "Mean"])
#plt.show()

#def cal_z_score(series):
#    return (series - series.mean())/np.std(series)

#get z_score series
#z_score_s = cal_z_score(0.179*x - y)

#print z_score_s


#plt.plot(z_score_s)
#plt.axhline(z_score_s.mean(), color="black")
#plt.axhline(1.0, color="red", linestyle="--")
#plt.axhline(-1.0, color="green", linestyle="--")
#plt.legend(["z-score", "mean", "+1", "-1"])
#plt.show()

#Back_testing
#trading strategy implementation
