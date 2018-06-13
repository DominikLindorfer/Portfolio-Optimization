#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 10:12:31 2018

@author: lindorfer
"""

import pandas as pd
import numpy as np
import datetime, requests, re, time
from functools import reduce
from sqlalchemy import create_engine
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select


def get_fond_dataframes(start_date, end_date, fond_id):
    
    #-----Get data from Morningstar-Tool-----
    data_url = ("http://tools.morningstar.at/api/rest.svc/timeseries_price/"
                "5370efewxk?id={fond_id}%5D2%5D1%5D&currencyId=EUR&"
                "idtype=Morningstar&priceType=&frequency=monthly&startDate={start_date}&"
                "endDate={end_date}&outputType=COMPACTJSON").format(fond_id = fond_id, 
                                                                    start_date = start_date, 
                                                                    end_date = end_date)  

    result = requests.get(data_url).json()

    #-----Convert from Unix-Time to usable Time Format-----
    conv_time = lambda x: datetime.datetime.fromtimestamp(int(x/1000)).strftime('%Y-%m-%d %H:%M:%S')
    fond_prices = pd.DataFrame([ [ conv_time(i[0]), i[1]] for i in result ], columns = ["date", "price"])
    #rendite_ts = [ [ conv_time(i[0]), i[1]] for i in result ]
    
    return fond_prices
    

if __name__ == "__main__":
    
    #-----Set Start & End Date
    start_date = "2017-01-01"
    end_date = str(datetime.datetime.today().date())
    
    #-----Set Fond ids----
    
    fond_ids = ["F0GBR052SY","0P0000VHOL","0P0000JNCV"]
    
    
#    fond_ids = ["F0GBR052SY","F00000X0M9","0P0000VHOL","0P0000JNCV","F000002J6W","F0000045M3","F0GBR04LVP",
#                "F0GBR04FOH","F0000020MG","F00000W0YC","F00000MGKD","F000000ECJ","F00000OQ2I","F000000PWQ",
#                "F0GBR04D0X","0P0000M7TK","F0GBR04D20","F00000JRBY","F0GBR04PMR","F000005KE0","F0GBR04CIW"]

    all_prices = []
    
    #-----Loop over all fonds and collect data-----
    for i in fond_ids:
        print("i = ", i)
        all_prices.append ( get_fond_dataframes(start_date, end_date, i) )
       # all_rendite.append( get_fond_dataframes(start_date, end_date, i) )  
    
    
    #-----calculate the covariance Matrix-----
    all_prices_frame = pd.DataFrame()
    
    for i in fond_ids:
        print("i = ", i)
        all_prices_frame[i] = get_fond_dataframes(start_date, end_date, i).price.pct_change(1).values
        
    all_prices_frame.cov()
    
    
    #-----Test Stuff-----    
        
    
    
    p1 = np.array(all_prices[0].price.pct_change(1).values)
    p2 = np.array(all_prices[1].price.pct_change(1).values)

    testframe = pd.DataFrame(np.transpose([p1,p2]))
        
    p3 = np.array(all_prices[2].price.pct_change(1).values)
    
    testframe[2] = p3
    
    testframe.cov()
    
    
    test2frame = pd.DataFrame([],index = all_prices[0].date)
    
    for i in all_prices:
        a = np.array(i.price.pct_change(1).values)
        #test2frame(a , ignore_index=True)
        
    
    
    test3frame = all_prices[0].price
    test3frame.append(all_prices[1].price)
    
    all_prices[0].price
    
    all_prices[0].price.pct_change(1).mean()
    all_prices[0].price.pct_change(1).var()
    
    all_prices[0].price.pct_change(1)
    all_prices[1].price.pct_change(1)
        


    np.cov(p1,p2)

    

    
    testframe[1]    


    exam_data  = {'name': ['Anastasia', 'Dima', 'Katherine', 'James', 'Emily', 'Michael', 'Matthew', 'Laura', 'Kevin', 'Jonas'],
            'score': [12.5, 9, 16.5, np.nan, 9, 20, 14.5, np.nan, 8, 19],
            'attempts': [1, 3, 2, 3, 2, 3, 1, 1, 2, 1],
            'qualify': ['yes', 'no', 'yes', 'no', 'no', 'yes', 'yes', 'no', 'no', 'yes']}
    labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    df = pd.DataFrame(exam_data , index=labels)
    print("Orginal rows:")
    print(df)
    color = ['Red','Blue','Orange','Red','White','White','Blue','Green','Green','Red']
    df['color'] = color
    print("\nNew DataFrame after inserting the 'color' column")
    print(df)


#
#    
#    test = pd.DataFrame([np.array([1, 3/2]), np.array([2, 11])])
#    
#    test.cov()
#    np.cov(np.array([1, 3/2]), np.array([2, 11]))
#    
#    np.array(all_prices[0].price)
