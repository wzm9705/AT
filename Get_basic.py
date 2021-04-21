# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 16:53:17 2021

@author: wzm
"""
from BasicData import BasicData

#按年份数据整理
def data(year):
    Data = BasicData(year)
    Tushare_data = Data.Get_Tushare()
    Tushare_data.to_csv('Basicdata\\Tushare_data {}.csv'.format(year))
    Tick_data = Data.Get_Tick()
    Tick_data.to_csv('Basicdata\\Tick_data {}.csv'.format(year))
    Order_data = Data.Get_Order()
    Order_data.to_csv('Basicdata\\Order_data {}.csv'.format(year))
    
def df(dataframe):
    df0 = dataframe.copy()
    df0.index = df0.iloc[:,0]
    df0 = df0.iloc[:,1:]
    return df0.dropna()    
    
    
if __name__ == "__main__":
    
    data(2018)
    data(2019)


