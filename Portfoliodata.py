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
# from sqlalchemy import create_engine
from selenium import webdriver
from bs4 import BeautifulSoup
from autograd import value_and_grad

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
    

def get_Optimized_Portfolio( Covar_Mat, MeanVals, Exp_Value ):
    
    constraints1 = ({'type': 'eq', 'fun': lambda weights:  np.sum(weights) - 1})
    constraints2 = ({'type': 'ineq', 'fun': lambda weights:  weights @ Exp_Ret - Exp_Value})
    constraints = [constraints1, constraints2]
    
    bounds = [(0,1)] * len(MeanVals)
    
    #-----Define minimization Problem for Modern-Portfolio-Theory-----
    def min_markowitz(weights, cov_mat):
        return weights @ (cov_mat @ weights)  
    
    def target_func(weights):
        return min_markowitz(weights, Covar_Mat)
    
    target_with_grad = value_and_grad(target_func)
    
    
    #-----Do the Minimization with ScipY-----
#    result = minimize(target_with_grad, x0, jac = True, method='SLSQP', bounds = bounds, constraints = constraints, tol = 1e-30, options = {"maxiter": 1500})
    result = minimize(target_func, x0, jac = False, method='SLSQP', bounds = bounds, constraints = constraints, tol = 1e-30, options = {"maxiter": 3500})
    return result

if __name__ == "__main__":
    
    #-----Set Start & End Date
    start_date = "2012-01-01"
    end_date = str(datetime.datetime.today().date())
    
    
    #-----Set Fond ids----
    fond_ids = ["F0GBR06DWD","F00000T4KE","F000000255","F00000QLUP",
                "0P0000VHOL","0P0000JNCV","F000002J6W","F0GBR04LVP","F0GBR04FOH","F0GBR04D0X","0P0000M7TK",
                "F0GBR04D20","F0GBR04PMR","F000005KE0","F0GBR04CIW","F0GBR064OK","F0000020H2"]
    #"F0000007LD","F00000LNTR"
    all_prices = []
    
    #-----Loop over all fonds and collect data-----
#    for i in fond_ids:
#        print("i = ", i)
#        all_prices.append ( get_fond_dataframes(start_date, end_date, i) )    
    
    #-----calculate the covariance Matrix and Expected Returns-----
    R_frame = pd.DataFrame()
    
    
    #-----pct_change(1) gives back: list[i + 1] / list[i] to calculate the returns-----
    for i in fond_ids:
        print("i = ", i)
        R_frame[i] = get_fond_dataframes(start_date, end_date, i).price.pct_change(1).values + 1.0
        
    Covar_Mat = R_frame.cov()
    MeanVals  = R_frame.mean()        
    Exp_Ret = MeanVals.values
    
    #-----Optimize the Weights for different Fonds-----
    from scipy.optimize import minimize
    x0 = (lambda x: x/np.sum(x))(np.random.uniform(low = 0, high = 1, size = len(MeanVals)))
    
   # x0 = np.linspace(1 / len(MeanVals), 1 / len(MeanVals), num = len(MeanVals))
    
    #-----Set Constraints: Only Long Portfolios sum(w_i) == 1 && Expected Return > value-----
    
    constraints1 = ({'type': 'eq', 'fun': lambda weights:  np.sum(weights) - 1})
    constraints2 = ({'type': 'ineq', 'fun': lambda weights:  weights @ Exp_Ret - 1.001})
    constraints = [constraints1, constraints2]
    
    bounds = [(0,1)] * len(MeanVals)
    
    #-----Define minimization Problem for Modern-Portfolio-Theory-----
    def min_markowitz(weights, cov_mat):
        return weights @ (cov_mat @ weights)  
    
    def target_func(weights):
        return min_markowitz(weights, Covar_Mat)
    
    #-----Do the Minimization with ScipY-----
    res = minimize(target_func, x0, jac = False, method='SLSQP', bounds = bounds, constraints = constraints)
    
    #-----Set the expected return 'Exp_Value' that the portfolio should yield in 1 year-----
    #-----Choose wether the data was gathered daily, weekly or monthly-----
    weekly  = 1.0 / 52
    daily   = 1.0 / 251
    monthly = 1.0 / 12  
    
    Exp_Ret_List = np.linspace(1.02, 1.20, num = 20)
    
    fond_list = []
    
    for i in Exp_Ret_List:
        
        Exp_Value = i**(monthly)        
        fond_list.append( get_Optimized_Portfolio( Covar_Mat, MeanVals, Exp_Value ) )

    x_axis = []
    
    for i in fond_list:
        x_axis.append(i.fun * np.sqrt(12))
    
    
    #-----Plot the Efficiency Frontier-----    
    import matplotlib.pyplot as plt    
    
    plt.plot(x_axis, Exp_Ret_List)
    plt.ylabel('Expected Return')
    plt.xlabel('Standard Deviation')
    plt.title('MPT Efficiency Frontier')
    plt.grid(True)
    plt.show()
  
    #-----Print out Fonds between 1.08 and 1.16 Expected return
    np.set_printoptions(precision=4)  
    for i in range(5,20):
        print(i, np.round(fond_list[i].x, 5), Exp_Ret_List[i])
        #print("{:.1f} {:.1f}".format(i, fond_list[i].x))
        #print("{:.4f} {:.4f} {:.4f}".format(i, fond_list[i].x, Exp_Ret_List[i]))    
    
    np.round(fond_list[10].x, 5)
    Exp_Ret
    
    np.round(fond_list[10].x, 5) * Exp_Ret
    
    (np.sum(np.round(fond_list[10].x, 5) * Exp_Ret))**12
    
    
#    #-----Test Minimization Function-----
#    from scipy.optimize import minimize
#    def func(x):
#        return x[0]*x[1]
#    
#    bnds=((0,5),(0,5))
#    
#    cons=({'type':'eq','fun':lambda x: x[0] + x[1] - 5})
#
#    x0=[0.2 , 0.9]
#    
#    res = minimize(func,x0,method='SLSQP',bounds=bnds,constraints=cons)
#    
#    x0 = (lambda x: x/np.sum(x))(np.random.uniform(low = 0, high = 1, size = 2))
#    
#    ER = np.array([1.07814, 1.09291])
#    
#    constraints1 = ({'type': 'eq', 'fun': lambda weights:  np.sum(weights) - 1})
#    constraints2 = ({'type': 'ineq', 'fun': lambda weights:  weights @ ER - 1.085})
#    constraints = [constraints1, constraints2]
#    
#    bounds = [(0,1)] * 2
#    
#    
#    a = np.array( [[0.000927742, -0.0000847965], [-0.0000847965, 0.0231523]])
#    b = np.array([1 , 1])
#    
#    print(b @ (a @ b))
#    
#    def min_markowitz(weights, cov_mat):
#        return weights @ (cov_mat @ weights)
#    
#    min_markowitz(b , a)    
#    
#    def target_func(weights):
#        return min_markowitz(weights, a)
#    
#    target_func(b)
#    
#    res = minimize(target_func, x0, method='SLSQP', bounds = bounds, constraints = constraints)
#    
#    
#    
#    
#    
#    #-----Test the Mathematica Example in Python-----
#    R = np.array([[1.075, 1.084, 1.061, 1.052, 1.055, 1.077, 1.109, 1.127, 1.156, 
#  1.117, 1.092, 1.103, 1.08, 1.063, 1.061, 1.071, 1.087, 1.08, 1.057, 
#  1.036, 1.031, 1.045], [0.942, 1.02, 1.056, 1.175, 1.002, 0.982, 
#  0.978, 0.947, 1.003, 1.465, 0.985, 1.159, 1.366, 1.309, 0.925, 
#  1.086, 1.212, 1.054, 1.193, 1.079, 1.217, 0.889], [0.852, 0.735, 
#  1.371, 1.236, 0.926, 1.064, 1.184, 1.323, 0.949, 1.215, 1.224, 
#  1.061, 1.316, 1.186, 1.052, 1.165, 1.316, 0.968, 1.304, 1.076, 1.1, 
#  1.012], [0.815, 0.716, 1.385, 1.266, 0.974, 1.093, 1.256, 1.337, 
#  0.963, 1.187, 1.235, 1.03, 1.326, 1.161, 1.023, 1.179, 1.292, 0.938,
#   1.342, 1.09, 1.113, 0.999], [0.698, 0.662, 1.318, 1.28, 1.093, 
#  1.146, 1.307, 1.367, 0.99, 1.213, 1.217, 0.903, 1.333, 1.086, 0.959,
#   1.165, 1.204, 0.83, 1.594, 1.174, 1.162, 0.968], [1.023, 1.002, 
#  0.123, 1.156, 1.03, 1.012, 1.023, 1.031, 1.073, 1.311, 1.08, 1.15, 
#  1.213, 1.156, 1.023, 1.076, 1.142, 1.083, 1.161, 1.076, 1.11, 
#  0.965], [0.851, 0.768, 1.354, 1.025, 1.181, 1.326, 1.048, 1.226, 
#  0.977, 0.981, 1.237, 1.074, 1.562, 1.694, 1.246, 1.283, 1.105, 
#  0.766, 1.121, 0.878, 1.326, 1.078], [1.677, 1.722, 0.76, 0.96, 1.2, 
#  1.295, 2.212, 1.296, 0.688, 1.084, 0.872, 0.825, 1.006, 1.216, 
#  1.244, 0.861, 0.977, 0.922, 0.958, 0.926, 1.146, 0.99]])
#    
#    names = ["3m T-bill", "long T-bond", "SP500", "Wiltshire 5000", "Corporate \
#Bond", "NASDQ", "EAFE", "Gold"]
#    
#    R_DataFrame = pd.DataFrame(R.transpose(), columns = names)
#    
#    covmat = R_DataFrame.cov()
#    meanval = R_DataFrame.mean()    
#    
#    #-----Minimize the Mathematica Problem-----
#    
#    x0 = (lambda x: x/np.sum(x))(np.random.uniform(low = 0, high = 1, size = len(meanval)))
#    
#    ER = meanval.values
#    
#    constraints1 = ({'type': 'eq', 'fun': lambda weights:  np.sum(weights) - 1})
#    constraints2 = ({'type': 'ineq', 'fun': lambda weights:  weights @ ER - 1.04})
#    constraints = [constraints1, constraints2]
#    
#    bounds = [(0,1)] * len(meanval)
#        
#    def min_markowitz(weights, cov_mat):
#        return weights @ (cov_mat @ weights)  
#    
#    def target_func(weights):
#        return min_markowitz(weights, covmat)
#    
#    res = minimize(target_func, x0, jac = False, method='SLSQP', bounds = bounds, constraints = constraints)
#    
#    
#    #-----Test Stuff-----    
#    
#    p1 = np.array(all_prices[0].price.pct_change(1).values)
#    p2 = np.array(all_prices[1].price.pct_change(1).values)
#
#    testframe = pd.DataFrame(np.transpose([p1,p2]))
#        
#    p3 = np.array(all_prices[2].price.pct_change(1).values)
#    
#    testframe[2] = p3
#    
#    testframe.cov()
#    
#    
#    test2frame = pd.DataFrame([],index = all_prices[0].date)
#    
#    for i in all_prices:
#        a = np.array(i.price.pct_change(1).values)
#        #test2frame(a , ignore_index=True)
#        
#    
#    
#    test3frame = all_prices[0].price
#    test3frame.append(all_prices[1].price)
#    
#    all_prices[0].price
#    
#    all_prices[0].price.pct_change(1).mean()
#    all_prices[0].price.pct_change(1).var()
#    
#    all_prices[0].price.pct_change(1)
#    all_prices[1].price.pct_change(1)
#        
#
#
#    np.cov(p1,p2)
#
#    
#
#    
#    testframe[1]    
#
#
#    exam_data  = {'name': ['Anastasia', 'Dima', 'Katherine', 'James', 'Emily', 'Michael', 'Matthew', 'Laura', 'Kevin', 'Jonas'],
#            'score': [12.5, 9, 16.5, np.nan, 9, 20, 14.5, np.nan, 8, 19],
#            'attempts': [1, 3, 2, 3, 2, 3, 1, 1, 2, 1],
#            'qualify': ['yes', 'no', 'yes', 'no', 'no', 'yes', 'yes', 'no', 'no', 'yes']}
#    labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
#    df = pd.DataFrame(exam_data , index=labels)
#    print("Orginal rows:")
#    print(df)
#    color = ['Red','Blue','Orange','Red','White','White','Blue','Green','Green','Red']
#    df['color'] = color
#    print("\nNew DataFrame after inserting the 'color' column")
#    print(df)
#
#
##
#    
#    test = pd.DataFrame([np.array([1, 3/2]), np.array([2, 11])])
#    
#    test.cov()
#    np.cov(np.array([1, 3/2]), np.array([2, 11]))
#    
#    np.array(all_prices[0].price)
