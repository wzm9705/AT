# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 19:10:54 2020

@author: WZM
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


data = pd.read_csv('Pooldata\\data.csv',index_col=())
hk_chg = pd.DataFrame()
lengh = 5 
for g in tqdm(set(data.code), desc='计算中..', leave=True):
    data_g = data[data.code == g]
    if max(data_g.iv_hk) != min(data_g.iv_hk):
        hk_chg = pd.concat([hk_chg,data_g.loc[:,['code','date','at_volume','at_trades','iv_hk']]],axis = 0)
    continue
hk_chg.index = range(0,np.size(hk_chg,0))
hk_add = pd.DataFrame()
volume_add = [1]
trades_add = [1]
for i in range(lengh,np.size(hk_chg,0)-lengh,1):
    if (hk_chg.iloc[i,-1] ==0 ) & (hk_chg.iloc[i+1,-1] == 1) & (hk_chg.iloc[i,0] == hk_chg.iloc[i+1,0]):
        day = hk_chg[(hk_chg.index <= i+lengh) & (hk_chg.code == hk_chg.loc[i,'code']) ]
        day.loc[:,'day'] = range(lengh+1-np.size(day,0),lengh+1,1)
        day.at_volume = 2- day.at_volume/np.mean(day[day.day <= 0].at_volume)
        day.at_trades = day.at_trades/np.mean(day[day.day <= 0].at_trades) 
        hk_add = pd.concat([hk_add,day],axis = 0)

for i in range(1,lengh+1,1):
    volume_add += [np.mean(hk_add[hk_add.day == i].at_volume)]
    trades_add += [np.mean(hk_add[hk_add.day == i].at_trades)]

fig = plt.figure(figsize=(18,8))
plt.xticks(range(0,lengh+1,1))
plt.xlabel('Entering Days',size = 24)
plt.tick_params(labelsize = 16)
ax1 = fig.add_subplot(111)
ax1.set_title('AT after entering SC ',size = 24)
plt.plot(range(0,lengh+1,1),volume_add,color='r',label='AT_volume')
plt.legend(loc=2,fontsize = 16)

ax2 = ax1.twinx()
plt.plot(range(0,lengh+1,1),trades_add,color='#FFD700',label = 'AT_trades')
plt.tick_params(labelsize = 16)
plt.legend(loc=1,fontsize = 16)
plt.savefig('fig\\fig1 加入深股通后AT变化.png')
plt.show()
'''
at = pd.DataFrame()
for t in list(set(data.date)):
    data_t = data[data.date == t]
    at.loc[t,'MBM_vol'] = np.mean(data_t[data_t.BK == 'MBM'].at_volume)

    at.loc[t,'GEM_vol'] = np.mean(data_t[data_t.BK == 'GEM'].at_volume)
    at.loc[t,'SME_vol'] = np.mean(data_t[data_t.BK == 'SME'].at_volume)
    at.loc[t,'MBM_tra'] = np.mean(data_t[data_t.BK == 'MBM'].at_trades)
    at.loc[t,'GEM_tra'] = np.mean(data_t[data_t.BK == 'GEM'].at_trades)
    at.loc[t,'SME_tra'] = np.mean(data_t[data_t.BK == 'SME'].at_trades)
    at.loc[t,'MBM_otr'] = np.mean(data_t[data_t.BK == 'MBM'].iv_tor)
    at.loc[t,'GEM_otr'] = np.mean(data_t[data_t.BK == 'GEM'].iv_tor)
    at.loc[t,'SME_otr'] = np.mean(data_t[data_t.BK == 'SME'].iv_tor)   

at = at.sort_index()
at.to_csv('fig1.csv')
'''