# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 13:52:56 2020

@author: WZM
"""
import pandas as pd
from Get_basic import df
from datetime import date

#单个变量数据汇总
def con(var_name):
    
    data1 = pd.read_csv('Vardata\\{} 2018.csv'.format(var_name))
    data2 = pd.read_csv('Vardata\\{} 2019.csv'.format(var_name))
    data1 = df(data1)
    data2 = df(data2)
    data = pd.concat([data1,data2])
    data.to_csv('Vardata\\{}.csv'.format(var_name))

#总数据汇总
def datacon(data0,var):
    
    data1 = pd.read_csv('Vardata\\{}.csv'.format(var))
    data1 = df(data1)
    
    if var =='Herds':
        
        data1 = data1.loc[:,'herds_lsv'] * 10000
        
    if var == 'Sentiment_pcr':
        
        data1 = data1.loc[:,'FAC1_1']
        data1.name = 'sentiment'
        
    data = pd.concat([data0,data1],axis = 1,sort = True)
    return data

#生成板块代码
def bk(code):
    i = code[2:5]
    if i == '000' or i == '001':
        return 'MBM'
    else:
        if i == '002' or i == '003':
            return 'SME'
        else:
            return 'GEM'

    
def var_pool():
    
    for i in ['Atproxy','Control','Herds','Instrument','Sentiment_fac','Volatility']:
        con(i)
 
def main():
    
    var_pool()
    data = pd.DataFrame()
    for i in ['Atproxy','Control','Herds','Instrument','Sentiment_pcr','Volatility']:
        data = datacon(data,i)
        
    data.insert(0,'date',list(date(int(x[:4]),int(x[4:6]),int(x[6:8])) for x in data.index))
    data.insert(1,'code',list(x[-8:] for x in data.index))
    data['year'] = list(x[:4] for x in data.index)
    data['D_year'] = list(2019 - int(x) for x in data['year'])
    data['BK'] = list(bk(x) for x in data.code)
    data_2019 = data[data['year'] == '2019']
    data_2018 = data[data['year'] == '2018']
    data.to_csv('Pooldata\\data.csv')
    data_2019.to_csv('Pooldata\\data_2019.csv')
    data_2018.to_csv('Pooldata\\data_2018.csv')    
 
if __name__ == "__main__":
    
    main()
    
    