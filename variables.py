# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 12:39:42 2020

@author: WZM
"""
import pandas as pd
import numpy as np
import scipy.stats as st
import time

def df(dataframe):
    df0 = dataframe
    df0.index = df0.iloc[:,0]
    df0 = df0.iloc[:,1:]
    df0 = df0.dropna()
    return df0

def volatility(tick_data,order_data,tushare_data):
    volatility_variables = pd.DataFrame(index = tushare_data.index)
    volatility_variables['volatility_p'] = (tushare_data['high']-tushare_data['low'])*2/(tushare_data['high']+tushare_data['low'])*10000
    volatility_variables['volatility_pct'] = np.abs(tushare_data['pct_chg'])*100
    volatility_variables['volatility_rv'] = tick_data['volatility']*100
    return volatility_variables

def atproxy(tick_data,order_data,tushare_data):
    atproxy_variables = pd.DataFrame(index = tushare_data.index)
    atproxy_variables['date'] = tick_data['date']
    atproxy_variables['at_volume'] = -tick_data['trade_amount']*10/order_data['row_count']
    atproxy_variables['at_trades'] = order_data['row_count']/tick_data['row_count']
    atproxy_variables['at_volume'] = atproxy_variables['at_volume'].map(lambda x: max(x,-200))
    atproxy_variables['at_trades'] = atproxy_variables['at_trades'].map(lambda x: min(x,30))
    for t in set(atproxy_variables.date):
        atproxy_variables.loc[atproxy_variables['date'] == t,'at_mean'] = np.sum(atproxy_variables.loc[atproxy_variables['date'] == t,'at_volume'])
        atproxy_variables.loc[atproxy_variables['date'] == t,'at_iv'] = (-atproxy_variables.loc[atproxy_variables['date'] == t,'at_volume'] + 
                             atproxy_variables.loc[atproxy_variables['date'] == t,'at_mean'])/(np.size(atproxy_variables.loc[atproxy_variables['date'] == t],0)-1)  
    return atproxy_variables.loc[:,['at_volume','at_trades','at_iv']]

def instrument(tick_data,order_data,tushare_data):
    iv = pd.DataFrame(index = tushare_data.index)
    iv['iv_tor'] = order_data['order_vol']/tick_data['trade_vol']
    return iv

def herds(tick_data,order_data,tushare_data):
    start_time = time.time()
    herds_lsv = pd.DataFrame(index = tushare_data.index)
    herds_lsv['date'] = tick_data['date']
    herds_lsv['Pit'] = tick_data['B_vol']/tick_data['trade_vol']
    for t in set(herds_lsv.date):
        herds_lsv.loc[herds_lsv['date'] == t,'Pt'] = np.mean(herds_lsv.loc[herds_lsv['date'] == t,'Pit'])
    g = '20190601' 
    for i in herds_lsv.index:
        
        if herds_lsv.loc[i,'date'] != g:
            print(herds_lsv.loc[i,'date'])
            print('cost_time:',time.time()-start_time)
            g = herds_lsv.loc[i,'date']
            
        s = 0
        n = int(tick_data.loc[i,'B_n']+tick_data.loc[i,'S_n'])
        for k in range(n+1):
            C = st.binom.pmf(k,n,herds_lsv.loc[i,'Pit'])
            s = s + C*np.abs(k/n-herds_lsv.loc[i,'Pt'])
        herds_lsv.loc[i,'herds_lsv'] = np.abs(herds_lsv.loc[i,'Pit'] - herds_lsv.loc[i,'Pt']) - s
    return herds_lsv

def controls(tick_data,order_data,tushare_data):
    controls_variables = pd.DataFrame(index = tushare_data.index)
    controls_variables['controls_depth1'] = tick_data['depth1']
    controls_variables['controls_depth5'] = tick_data['depth5']
    controls_variables['controls_rqs'] = tick_data['rqs']
    controls_variables['controls_lnmv'] = np.log(tushare_data['total_mv'])
    controls_variables['controls_ip'] = np.reciprocal(tushare_data['close'])
    controls_variables['controls_tr'] = tushare_data['turnover_rate']
    controls_variables['controls_vol'] = tick_data['trade_amount']/1000
    return controls_variables

def sentiment(tick_data,order_data,tushare_data):
    sentiment_factor = pd.DataFrame(index = tushare_data.index)
    sentiment_factor['pe'] = tushare_data['pe'] 
    sentiment_factor['tr'] = tushare_data['turnover_rate']
    sentiment_factor['bsi'] = (tick_data['B_vol']-tick_data['S_vol'])/(tick_data['B_vol']+tick_data['S_vol'])
    sentiment_factor['bsi_abs'] = np.abs(tick_data['B_vol']-tick_data['S_vol'])/(tick_data['B_vol']+tick_data['S_vol'])
    return sentiment_factor
    
if __name__ == "__main__":
    sample_date = ['20190601','20191031']
    tick = df(pd.read_csv('tick_data {}.csv'.format(sample_date[0][:4])))
    order = df(pd.read_csv('order_data {}.csv'.format(sample_date[0][:4])))
    tushare = df(pd.read_csv('tushare_data {}.csv'.format(sample_date[0][:4])))
    tick = tick[tick.row_count >= 500]
    order = order[order.row_count >= 1000]
    tushare = tushare[tushare.pct_chg < 11]
    rows = list(set(tushare.index) & set(tick.index) & set(order.index))
    tushare = tushare.loc[rows,:].sort_index()
    order = order.loc[rows,:].sort_index()
    tick = tick.loc[rows,:].sort_index()
    
#    volatility(tick,order,tushare).to_csv('volatility {}.csv'.format(sample_date[0][:4]))
#    atproxy(tick,order,tushare).to_csv('atproxy {}.csv'.format(sample_date[0][:4]))
#    instrument(tick,order,tushare).to_csv('instrument {}.csv'.format(sample_date[0][:4]))
#    herds(tick,order,tushare).to_csv('herds {}.csv'.format(sample_date[0][:4]))
#    controls(tick,order,tushare).to_csv('controls {}.csv'.format(sample_date[0][:4]))
#    sentiment(tick,order,tushare).to_csv('sentiment {}.csv'.format(sample_date[0][:4]))
    
    