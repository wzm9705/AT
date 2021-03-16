# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 13:28:58 2020

@author: WZM
"""

import tushare as ts
import pandas as pd
import numpy as np
pro = ts.pro_api()
sample_date = ['20190601','20191031']

date = pro.trade_cal(exchange='', start_date = sample_date[0], end_date = sample_date[1])
date = date[date['is_open'] == 1]

data = pd.read_csv('2019data.csv')
data.index = list(str(data.iloc[x,0])+str(data.iloc[x,1]) for x in range(np.size(data,0)))
for t in date.cal_date:
    print(t)
    volume = pro.daily(trade_date = t,fields='ts_code,amount,vol,high,low,pre_close,close,pct_chg' )
    volume.index = list('SZ'+x[:6] for x in volume.ts_code)
    for g in set(data.iloc[:,0]):
        if volume.loc[g,'high'] > volume.loc[g,'pre_close']*1.095 or volume.loc[g,'low'] < volume.loc[g,'pre_close']*0.905:
            data = data.drop(index = g+t)
        
data.index = data.iloc[:,0]
data = data.iloc[:,1:]
data.to_csv('2019data_drop.csv')