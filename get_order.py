# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 13:12:15 2020

@author: WZM
"""

import tushare as ts
import pandas as pd
import numpy as np

def get_order(sample_date):
    global order
    stock = pro.query('stock_basic', fields='ts_code')
    date = pro.trade_cal(exchange='', start_date = sample_date[0], end_date = sample_date[1])
    date = date[date['is_open'] == 1]
    stock.ts_code = list(map(lambda x: x[-2:]+x[:6],stock.ts_code))
    order_data = pd.DataFrame()
    for t in date.cal_date:
        print(t)
        for g in stock.ts_code:
            if g[:2] != 'SZ':
                continue
            folder_name = t[:4]+'-'+t[4:6]+'-'+t[6:8]
            try:
                with open('{}\{}\{}\{}.csv'.format(t[0:6],folder_name,folder_name,g[-6:])) as csvfile:
                    order = pd.read_csv(csvfile)
                    order_data.loc[t+g,'date'] = t
                    order_data.loc[t+g,'code'] = g
                    order_data.loc[t+g,'row_count'] = np.size(order,0)
                    order_data.loc[t+g,'order_vol'] = np.sum(order['数量'])/100000
                    order_data.loc[t+g,'B_vol'] = sum(order[order['类型'] == '2B']['数量'])/100000
                    order_data.loc[t+g,'S_vol'] = sum(order[order['类型'] == '2S']['数量'])/100000
                    order_data.loc[t+g,'B_n'] = np.size(order[order['类型'] == '2B'],0)
                    order_data.loc[t+g,'S_n'] = np.size(order[order['类型'] == '2S'],0)
            except:
                continue
    return order_data
if __name__ == "__main__":
    pro = ts.pro_api()
    sample_date = ['20180601','20181031']
    data = get_order(sample_date)
    data.to_csv('order_data {}.csv'.format(sample_date[0][:4]))