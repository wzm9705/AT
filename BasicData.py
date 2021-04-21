# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 16:14:22 2021

@author: wzm
"""
import pandas as pd
import tushare as ts
import numpy as np
from tqdm import tqdm
from itertools import product

class BasicData(object):
    
    def __init__(self,year):
        
        self.year = year
        self.start_dt = str(year) + '0601'
        self.end_dt = str(year) + '1031'
        self.trade_dt = []
        self.stock_lt = []
        
        #设置Tushare api接口id
        self.pro = ts.pro_api('1c719bc555e3aa647b8e82139f643b8b044fa4339a922c2e3d181d29')
        
        #设置外部数据目录
        self.root = 'D:\\Data\\paper'
        
    #获取交易日列表
    def TradeDate(self):
        
        date = self.pro.trade_cal(exchange='', start_date=self.start_dt, end_date=self.end_dt)
        date = date[date['is_open'] == 1]
        self.trade_dt = list(date.cal_date)
        
    #获取股票列表
    def StockList(self):
        
        stock_L = self.pro.query('stock_basic',list_status='L', fields='ts_code')
        stock_D = self.pro.query('stock_basic',list_status='D', fields='ts_code')
        stock_P = self.pro.query('stock_basic',list_status='P', fields='ts_code')
        stock = pd.concat([stock_L,stock_D,stock_P], axis = 0)
        self.stock_lt = list(map(lambda x: x[-2:] + x[:6], stock.ts_code))
    
    #获取Tushare数据    
    def Get_Tushare(self):
        
        if self.trade_dt == []:
            
            self.TradeDate()
            
        TushareData = pd.DataFrame()
        
        for t in tqdm(self.trade_dt, desc='Tushare数据获取中..', leave=True):
            
            daily_data = self.pro.daily(trade_date = t)
            daily_basic_data = self.pro.daily_basic(
                trade_date = t, 
                fields = 'ts_code,trade_date,turnover_rate,pe,total_share,total_mv,circ_mv'
                )
            daily_data.ts_code = list(map(lambda x: x[-2:] + x[:6], daily_data.ts_code))
            daily_basic_data.ts_code = list(map(lambda x: x[-2:] + x[:6], daily_basic_data.ts_code))            
            daily_basic_data.index = list(str(daily_basic_data.loc[x,'trade_date']) + daily_basic_data.loc[x,'ts_code'] for x in daily_basic_data.index)
            daily_data.index = list(str(daily_data.loc[x,'trade_date']) + daily_data.loc[x,'ts_code'] for x in daily_data.index)
            daily_data = pd.concat([daily_data,daily_basic_data],axis = 1 , sort = False)
            daily_data = daily_data.T.drop_duplicates().T
            daily_data.loc[:,'market'] = list(x[:2] for x in daily_data.ts_code)
            daily_data = daily_data[daily_data['market'] == 'SZ']
            TushareData = pd.concat([TushareData,daily_data])
                
        return TushareData
    
    #整理分时成交数据
    def Get_Tick(self):
        
        if self.trade_dt == []:
            
            self.TradeDate()
            
        if self.stock_lt == []:
            
            self.StockList()
        
        TickData = pd.DataFrame()
        
        for t,g in tqdm(product(self.trade_dt,self.stock_lt), desc='分时数据整理中..', leave=True):
                
            if g[:2] != 'SZ':
                        
                continue
                    
            folder_name = t[:6] + 'SZ股票五档分笔'
            file_name = g[2:] + '_' + t
                    
            try:
                        
                with open(self.root + '\\{}\\{}\\{}\\{}\\{}.csv'.format(self.year,folder_name,folder_name,t,file_name)) as csvfile:
                            
                    tick = pd.read_csv(csvfile)
                    TickData.loc[t+g,'date'] = t
                    TickData.loc[t+g,'code'] = g
                    TickData.loc[t+g,'row_count'] = np.size(tick,0)
                    TickData.loc[t+g,'trade_amount'] = np.sum(tick['额']) / 1000
                    TickData.loc[t+g,'trade_vol'] = list(tick['总量'])[-1] / 1000
                    TickData.loc[t+g,'B_amount'] = sum(tick[tick.BS == 'B']['额']) / 1000
                    TickData.loc[t+g,'S_amount'] = sum(tick[tick.BS == 'S']['额']) / 1000
                    TickData.loc[t+g,'B_n'] = np.size(tick[tick.BS == 'B'],0)
                    TickData.loc[t+g,'S_n'] = np.size(tick[tick.BS == 'S'],0)
                    TickData.loc[t+g,'B_vol'] = sum(tick[tick.BS == 'B']['成交量']) / 1000
                    TickData.loc[t+g,'S_vol'] = sum(tick[tick.BS == 'S']['成交量']) / 1000
                    tick = tick[tick['B1量'] != 0]
                    tick = tick[tick['S1量'] != 0]
                    TickData.loc[t+g,'depth1'] = np.mean(tick['B1量'] + tick['S1量']) / 1000
                    TickData.loc[t+g,'rqs'] = np.mean((tick['S1价'] - tick['B1价']) \
                                                      * 20000 / (tick['S1价']+tick['B1价']))
                    TickData.loc[t+g,'volatility'] = np.std((tick['B1价'] + tick['S1价']) \
                                                            / 2 / list(tick['成交价'])[-1] * 100)
                    tick = tick[tick['B5量'] != 0]
                    tick = tick[tick['S5量'] != 0]
                    TickData.loc[t+g,'depth5'] = np.mean(tick['B1量'] + tick['S1量'] + tick['B2量'] \
                                                         + tick['S2量'] + tick['B3量'] + tick['S3量'] \
                                                             + tick['B4量'] + tick['S4量'] + tick['B5量'] \
                                                                 + tick['S5量']) / 1000  
                    
            except:
                        
                continue
                
        return TickData

    #整理逐笔委托数据    
    def Get_Order(self):

        if self.trade_dt == []:
            
            self.TradeDate()
            
        if self.stock_lt == []:
            
            self.StockList()

        OrderData = pd.DataFrame()
        
        for t,g in tqdm(product(self.trade_dt,self.stock_lt), desc='逐笔委托数据整理中..', leave=True):
                
            if g[:2] != 'SZ':
                    
                continue
                
            folder_name = t[:4] + '-' + t[4:6] + '-' + t[6:8]
                
            try:
                    
                with open(self.root + '\\{}\\{}\\{}\\{}\\{}.csv'.format(self.year,t[0:6],folder_name,folder_name,g[-6:])) as csvfile:
                        
                    order = pd.read_csv(csvfile)
                    OrderData.loc[t+g,'date'] = t
                    OrderData.loc[t+g,'code'] = g
                    OrderData.loc[t+g,'row_count'] = np.size(order,0)
                    OrderData.loc[t+g,'order_vol'] = np.sum(order['数量']) / 100000
                    OrderData.loc[t+g,'B_vol'] = sum(order[order['类型'] == '2B']['数量']) / 100000
                    OrderData.loc[t+g,'S_vol'] = sum(order[order['类型'] == '2S']['数量']) / 100000
                    OrderData.loc[t+g,'B_n'] = np.size(order[order['类型'] == '2B'], 0)
                    OrderData.loc[t+g,'S_n'] = np.size(order[order['类型'] == '2S'], 0)
                        
            except:
                    
                continue
                
        return OrderData