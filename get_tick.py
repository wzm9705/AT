# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 16:05:11 2020

@author: WZM
"""
import tushare as ts
import pandas as pd
import numpy as np

def get_tick(sample_date):
    global tick
    stock = pro.query('stock_basic', fields='ts_code')
    date = pro.trade_cal(exchange='', start_date = sample_date[0], end_date = sample_date[1])
    date = date[date['is_open'] == 1]
    stock.ts_code = list(map(lambda x: x[-2:]+x[:6],stock.ts_code))
    tick_data = pd.DataFrame()
    for t in date.cal_date:
        print(t)
        for g in stock.ts_code:
            if g[:2] != 'SZ':
                continue
            folder_name = t[:6]+'SZ股票五档分笔'
            file_name = g[2:]+'_'+t
            try:
                with open('{}\{}\{}\{}.csv'.format(folder_name,folder_name,t,file_name)) as csvfile:
                    tick = pd.read_csv(csvfile)
                    tick_data.loc[t+g,'date'] = t
                    tick_data.loc[t+g,'code'] = g
                    tick_data.loc[t+g,'row_count'] = np.size(tick,0)
                    tick_data.loc[t+g,'trade_amount'] = np.sum(tick['额'])/1000
                    tick_data.loc[t+g,'trade_vol'] = list(tick['总量'])[-1]/1000
                    tick_data.loc[t+g,'B_amount'] = sum(tick[tick.BS == 'B']['额'])/1000
                    tick_data.loc[t+g,'S_amount'] = sum(tick[tick.BS == 'S']['额'])/1000
                    tick_data.loc[t+g,'B_n'] = np.size(tick[tick.BS == 'B'],0)
                    tick_data.loc[t+g,'S_n'] = np.size(tick[tick.BS == 'S'],0)
                    tick_data.loc[t+g,'B_vol'] = sum(tick[tick.BS == 'B']['成交量'])/1000
                    tick_data.loc[t+g,'S_vol'] = sum(tick[tick.BS == 'S']['成交量'])/1000
                    tick = tick[tick['B1量'] != 0]
                    tick = tick[tick['S1量'] != 0]
                    tick_data.loc[t+g,'depth1'] = np.mean(tick['B1量']+tick['S1量'])/1000
                    tick_data.loc[t+g,'rqs'] = np.mean((tick['S1价']-tick['B1价'])*2/(tick['S1价']+tick['B1价']))*10000
                    tick_data.loc[t+g,'volatility'] = np.std((tick['B1价']+tick['S1价'])/2/list(tick['成交价'])[-1]*100)
                    tick = tick[tick['B5量'] != 0]
                    tick = tick[tick['S5量'] != 0]
                    tick_data.loc[t+g,'depth5'] = np.mean(tick['B1量']+tick['S1量']+tick['B2量']+tick['S2量']+
                                 tick['B3量']+tick['S3量']+tick['B4量']+tick['S4量']+tick['B5量']+tick['S5量'])/1000  
            except:
                continue
    return tick_data
if __name__ == "__main__":
    pro = ts.pro_api()
    sample_date = ['20180601','20181031']
    data = get_tick(sample_date)
    data.to_csv('tick_data {}.csv'.format(sample_date[0][:4]))