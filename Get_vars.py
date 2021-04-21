# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 20:58:51 2021

@author: wzm
"""

from Variables import Variables

#按年份变量指标计算
def var(year):
    
    data = Variables(year)
    Volatility_var = data.volatility()
    Volatility_var.to_csv('Vardata\\Volatility {}.csv'.format(year))
    
    Atproxy = data.atproxy()
    Atproxy.to_csv('Vardata\\Atproxy {}.csv'.format(year))
    
    Instrument_var = data.instrument()
    Instrument_var.to_csv('Vardata\\Instrument {}.csv'.format(year))
    
    Herds = data.herds()
    Herds.to_csv('Vardata\\Herds {}.csv'.format(year))
    
    Control_var = data.controls()
    Control_var.to_csv('Vardata\\Control {}.csv'.format(year))
    
    Sentment_fac = data.sentiment()
    Sentment_fac.to_csv('Vardata\\Sentiment_fac {}.csv'.format(year))
    
if __name__ == "__main__":
    
    var(2018)
    var(2019)