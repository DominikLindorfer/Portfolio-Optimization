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
                "idtype=Morningstar&priceType=&frequency=weekly&startDate={start_date}&"
                "endDate={end_date}&outputType=COMPACTJSON").format(fond_id = fond_id, 
                                                                    start_date = start_date, 
                                                                    end_date = end_date)  

    result = requests.get(data_url).json()

    #-----Convert from Unix-Time to usable Time Format-----
    conv_time = lambda x: datetime.datetime.fromtimestamp(int(x/1000)).strftime('%Y-%m-%d %H:%M:%S')
    rendite_ts = pd.DataFrame([ [ conv_time(i[0]), i[1]] for i in result ], columns = ["date", "y"])
    
    return rendite_ts
    

if __name__ == "__main__":
    
    #-----Set Start & End Date
    start_date = "1900-01-01"
    end_date = str(datetime.datetime.today().date())
    
    #-----Set Fond ids----
    #fond_ids = [""]
    
    #-----Loop over all fonds and collect data-----
#    for i in fond_ids:
#        all_rendite = pd.DataFrame