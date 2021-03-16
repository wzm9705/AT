# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 12:35:57 2020

@author: WZM
"""

import tushare as ts
import pandas as pd


def get_tushare(sample_date):
    date = pro.trade_cal(exchange='', start_date = sample_date[0], end_date = sample_date[1])
    date = date[date['is_open'] == 1]
    tushare_data = pd.DataFrame()
    for t in date.cal_date:
        print(t)
        daily_data = pro.daily(trade_date = t)
        daily_basic_data = pro.daily_basic(trade_date = t, fields='ts_code,trade_date,turnover_rate,pe,total_share,total_mv,circ_mv')
        daily_data.ts_code = list(map(lambda x: x[-2:]+x[:6],daily_data.ts_code))
        daily_basic_data.ts_code = list(map(lambda x: x[-2:]+x[:6],daily_basic_data.ts_code))
        
        daily_basic_data.index = list(str(daily_basic_data.loc[x,'trade_date']) + daily_basic_data.loc[x,'ts_code'] for x in daily_basic_data.index)
        daily_data.index = list(str(daily_data.loc[x,'trade_date']) + daily_data.loc[x,'ts_code'] for x in daily_data.index)
        daily_data = pd.concat([daily_data,daily_basic_data],axis = 1 , sort = False)
        daily_data = daily_data.T.drop_duplicates().T
        daily_data.loc[:,'market'] = list(x[:2] for x in daily_data.ts_code)
        daily_data = daily_data[daily_data['market'] == 'SZ']
        tushare_data = pd.concat([tushare_data,daily_data])
            
    return tushare_data
if __name__ == "__main__":
    pro = ts.pro_api()
    sample_date = ['20181001','20181031']
    data = get_tushare(sample_date)
    data.to_csv('tushare_data {}.csv'.format(sample_date[0][:4]))