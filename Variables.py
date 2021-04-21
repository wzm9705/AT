# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 12:39:42 2020

@author: WZM
"""
import pandas as pd
import numpy as np
import scipy.stats as st
from tqdm  import tqdm
import Get_basic
import datetime

class Variables(object):
    
    def __init__(self,year):
        
        self.year = year
        
        try:
            
            tick = Get_basic.df(pd.read_csv('Basicdata\\Tick_data {}.csv'.format(self.year)))
            order = Get_basic.df(pd.read_csv('Basicdata\\Order_data {}.csv'.format(self.year)))
            tushare = Get_basic.df(pd.read_csv('Basicdata\\Tushare_data {}.csv'.format(self.year)))
            
        except:
            
            Get_basic.data(year)
            tick = Get_basic.df(pd.read_csv('Basicdata\\Tick_data {}.csv'.format(self.year)))
            order = Get_basic.df(pd.read_csv('Basicdata\\Order_data {}.csv'.format(self.year)))
            tushare = Get_basic.df(pd.read_csv('Basicdata\\Tushare_data {}.csv'.format(self.year)))
        
        tick = tick[tick.row_count >= 500]
        order = order[order.row_count >= 1000]
        tushare = tushare[tushare.pct_chg < 11]
        rows = list(set(tushare.index) & set(tick.index) & set(order.index))
        self.tushare = tushare.loc[rows,:].sort_index()
        self.order = order.loc[rows,:].sort_index()
        self.tick = tick.loc[rows,:].sort_index()
    
    #波动性指标
    def volatility(self):
        
        volatility_var = pd.DataFrame(index = self.tushare.index)
        volatility_var['volatility_p'] = (self.tushare['high'] - self.tushare['low']) \
            * 20000 / (self.tushare['high'] + self.tushare['low'])
        volatility_var['volatility_pct'] = np.abs(self.tushare['pct_chg']) * 100
        volatility_var['volatility_rv'] = self.tick['volatility'] * 100
        
        return volatility_var

    #AT代理变量指标
    def atproxy(self):
        
        atproxy_var = pd.DataFrame(index = self.tushare.index)
        atproxy_var['date'] = self.tick['date']
        atproxy_var['at_volume'] = -self.tick['trade_amount'] * 10 / self.order['row_count']
        atproxy_var['at_trades'] = self.order['row_count'] / self.tick['row_count']
        atproxy_var['at_volume'] = atproxy_var['at_volume'].map(lambda x: max(x,-200))
        atproxy_var['at_trades'] = atproxy_var['at_trades'].map(lambda x: min(x,30))
        
        for t in tqdm(set(atproxy_var.date), desc='基于AT的工具变量构建中..', leave=True):
            
            atproxy_var.loc[atproxy_var['date'] == t,'at_mean'] = \
                np.sum(atproxy_var.loc[atproxy_var['date'] == t,'at_volume'])
            atproxy_var.loc[atproxy_var['date'] == t,'at_iv'] = \
                (-atproxy_var.loc[atproxy_var['date'] == t,'at_volume'] \
                 + atproxy_var.loc[atproxy_var['date'] == t,'at_mean']) \
                    / (np.size(atproxy_var.loc[atproxy_var['date'] == t],0) - 1)  
        
        return atproxy_var.loc[:,['at_volume','at_trades','at_iv']]
    
    #工具变量指标
    def instrument(self):
        
        iv = pd.DataFrame(index = self.tick.index)
        hk = pd.read_excel('Change_of_SZSE_Securities_Lists_c.xls'
                           ,header=3,index_col=0,dtype={1:str})
        iv['iv_hk'] = 0
        iv['iv_sell_only'] = 0
        iv['iv_short_sell'] = 0
        iv['date'] = list(datetime.date(int(str(x)[:4]),int(str(x)[4:6]),int(str(x)[-2:])) for x in self.tick.date)
        iv['code'] = self.tick.code
        hk['code'] = list('SZ'+'0'*(6-len(x))+x for x in hk.iloc[:,0])
        hk = hk.drop(hk[(hk['hk'].isna()) & (hk['sell_only'].isna()) & (hk['short_sell'].isna())].index)
        
        for i in tqdm(hk.index[::-1], desc='深股通名单整理中..', leave=True):

            if hk.loc[i,'code'] not in set(iv.code):
                
                continue
            
            for name in hk.loc[i,:][-4:-1].dropna().index:

                iv.loc[iv[(iv.code == hk.loc[i,'code']) & (iv.date >= hk.loc[i,'生效日期'])].index,'iv_'+name] = hk.loc[i,name]
        
        iv['iv_tor'] = self.order['order_vol'] / self.tick['trade_vol']
        
        return iv.loc[:,['iv_hk','iv_sell_only','iv_short_sell','iv_tor']]

    #羊群指标
    def herds(self):
        
        herds_lsv = pd.DataFrame(index = self.tushare.index)
        herds_lsv['date'] = self.tick['date']
        herds_lsv['Pit'] = self.tick['B_vol'] / self.tick['trade_vol']
        
        for t in tqdm(set(herds_lsv.date), desc='羊群：Pt计算中..', leave=True):
            
            herds_lsv.loc[herds_lsv['date'] == t,'Pt'] = np.mean(herds_lsv.loc[herds_lsv['date'] == t,'Pit'])
        
        for i in tqdm(herds_lsv.index, desc='羊群：羊群指标计算中..', leave=True):
            
            s = 0
            n = int(self.tick.loc[i,'B_n'] + self.tick.loc[i,'S_n'])
            
            for k in range(n+1):
                
                C = st.binom.pmf(k,n,herds_lsv.loc[i,'Pit'])
                s = s + C*np.abs(k/n-herds_lsv.loc[i,'Pt'])
            herds_lsv.loc[i,'herds_lsv'] = (np.abs(herds_lsv.loc[i,'Pit'] - herds_lsv.loc[i,'Pt']) - s) * 10000
        
        return herds_lsv

    #控制变量
    def controls(self):
        
        controls_var = pd.DataFrame(index = self.tushare.index)
        controls_var['controls_depth1'] = self.tick['depth1']
        controls_var['controls_depth5'] = self.tick['depth5']
        controls_var['controls_rqs'] = self.tick['rqs']
        controls_var['controls_lnmv'] = np.log(self.tushare['total_mv'])
        controls_var['controls_ip'] = np.reciprocal(self.tushare['close'])
        controls_var['controls_tr'] = self.tushare['turnover_rate']
        controls_var['controls_vol'] = self.tick['trade_amount'] / 1000
        
        return controls_var
    
    #情绪因子变量
    def sentiment(self):
        
        sentiment_fac = pd.DataFrame(index = self.tushare.index)
        sentiment_fac['pe'] = self.tushare['pe'] 
        sentiment_fac['tr'] = self.tushare['turnover_rate']
        sentiment_fac['bsi'] = (self.tick['B_vol'] - self.tick['S_vol']) \
            / (self.tick['B_vol'] + self.tick['S_vol'])
        sentiment_fac['bsi_abs'] = np.abs(self.tick['B_vol'] - self.tick['S_vol']) \
            / (self.tick['B_vol'] + self.tick['S_vol'])
        
        return sentiment_fac
    


    
    