#this is framework for testing cointegration
#China A shares data package using Tushare

import numpy as np
import pandas as pd
import statsmodels.api as sm
import seaborn as sns
import tushare as ts

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
            if pvalue < 0.05:
                # record the stock and corresponding p-value
                pairs.append((keys[i],keys[j],pvalue))

    return pvalue_mat, pairs

stock_list = ['600000', '600015', '600016', '600036', '601009','601166', '601169', '601328', '601398', '601988', '601998']

price_df = ts.get_hist_data('002142',start='2014-01-01',end='2015-01-01')
prices_df = pd.DataFrame(price_df['close'])
prices_df.rename(columns = {'close':'002142'},inplace = True)

#print prices_df

for code in stock_list:
    price_df = ts.get_hist_data(code,start='2014-01-01',end='2015-01-01')
    prices_df[code]=price_df['close']

pvalues, pairs = find_cointegration_pairs(prices_df)

stock_list_full = stock_list = ['002142','600000', '600015', '600016', '600036', '601009','601166', '601169', '601328', '601398', '601988', '601998']
ax = sns.heatmap(1-pvalues,xticklabels=stock_list_full,yticklabels=stock_list_full,cmap='RdYlGn_r',mask = (pvalues==1))
ax.show()

print pairs
