# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import datetime

hk = pd.read_excel('Change_of_SZSE_Securities_Lists_c.xls',header=3,index_col=0,dtype={1:str})
data = pd.read_csv('data.csv',index_col=0,dtype={'date':str})
data['iv_hk'] = 0
data['iv_sell_only'] = 0
data['iv_short_sell'] = 0
data.date = list(datetime.date(int(x[:4]),int(x[4:6]),int(x[-2:])) for x in data.date)
hk['code'] = list('SZ'+'0'*(6-len(x))+x for x in hk.iloc[:,0])
hk = hk.drop(hk[(hk['hk'].isna())&(hk['sell_only'].isna())&(hk['short_sell'].isna())].index)
for i in hk.index[::-1]:
    print(i)
    if hk.loc[i,'code'] not in set(data.code):
        continue
    for iv in hk.loc[i,:][-4:-1].dropna().index:
        data.loc[data[(data.code == hk.loc[i,'code']) & (data.date >= hk.loc[i,'生效日期'])].index,'iv_'+iv] = hk.loc[i,iv]