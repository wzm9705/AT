# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 13:52:56 2020

@author: WZM
"""
import pandas as pd
from variables import df

def con(variables):
    data1 = pd.read_csv('{} 2018.csv'.format(variables))
    data2 = pd.read_csv('{} 2019.csv'.format(variables))
    data1 = df(data1)
    data2 = df(data2)
    data = pd.concat([data1,data2])
    data.to_csv('{}.csv'.format(variables))

def datacon(variables):
    global data
    data1 = pd.read_csv('{}.csv'.format(variables))
    data1 = df(data1)
    if variables =='herds':
        data1 = data1.loc[:,'herds_lsv']*10000
    if variables == 'sentiment_pcr':
        data1 = data1.loc[:,'FAC1_1']
        data1.name = 'sentiment'
    data = pd.concat([data,data1],axis = 1,sort = True)

def bk(code):
    i = code[2:5]
    if i == '000' or i == '001':
        return 'ZB'
    else:
        if i == '002' or i == '003':
            return 'ZXB'
        else:
            return 'CYB'
    
    
if __name__ == "__main__":
    for i in ['atproxy','controls','herds','instrument','sentiment','volatility']:
        con(i)
    data = pd.DataFrame()
    for i in ['atproxy','controls','herds','instrument','sentiment_pcr','volatility']:
        datacon(i)
    data.insert(0,'date',list(x[:8] for x in data.index))
    data.insert(1,'code',list(x[-8:] for x in data.index))
    data['year'] = list(x[:4] for x in data.date)
    data['D_year'] = list(int(x)-2018 for x in data['year'])
    data['BK'] = list(bk(x) for x in data.code)
    data_2019 = data[data['year'] == '2019']
    data_2018 = data[data['year'] == '2018']
    data.to_csv('data.csv')
    data_2019.to_csv('data_2019.csv')
    data_2018.to_csv('data_2018.csv')
    
    
    