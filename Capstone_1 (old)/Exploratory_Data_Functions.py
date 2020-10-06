import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import os
import csv

from urllib.request import urlopen
import webbrowser as wb
from bs4 import BeautifulSoup
from selenium import webdriver
import time

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)



list_of_nfl = ['age','team','pos','no','game','game started',
                                 'target','receptions','yards','y/r','td','first downs','longest rec',
                                 'rec per game','yards per game','catch ratio','yards per target',
                                 'rushes','rush yards','rush td','first downs rush','longest rush',
                                 'rush yards per attempt','rush yards per game','rush attempt per games',
                                 'total touches','yards per touch','yards from scrimmage','total td','fumbles','av']


def find_caption(table):
    try:
        x=table.find_all('caption')[0].get_text()
    except:
        x=''
    return x

def overall_nfl_index(t):#find the index for the 'overall' row of the nfl table
    try:
        i = ((t.iloc[:,0:3] == ['']*3).all(axis = 1)).tolist().index(True)
                #are the first 3 entries empty
                #create boolean if all are
                #convert to list and find the row
    except:
        i = len(t)-1 #if not, simply pick the last one
    return i

def shift_nfl_row (row,start,end,shift): #shift a range of rows by the amount 'shift'
    x = row[start:end]
    row[start+shift:end+shift] = x
    return row

def nflstats(table_0): #extract the nfl table by providing the table_soup document
    table_caption = find_caption(table_0)
    
    table = pd.DataFrame(columns=list_of_nfl,
                         index=range(0,30))#create a new blank table
    
    row_marker = 0
    for row in table_0.find_all('tr'):
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            table.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        row_marker += 1

    table.dropna(axis=0, how='all', inplace = True) #remove all with rows with nan everywhere
    table = table.reset_index(drop = True)
    i = overall_nfl_index(table)

    for j in range(i,len(table)):
        shift_nfl_row(table.loc[j],0,len(table.columns)-1,1) #the rows beyond overall are shifted w.r.t to the year ones.
                                                             #we take care of it here

    table['table type'] = [table_caption]*len(table) #we add the caption at the end

    return table



def generate_all_nfl_tables(url): #use web.driver chrome to find hidden tables
    driver = webdriver.Chrome('/Users/adriensaremi/Documents/School and Employment/SpringBoard Course/Springboard/Capstone_1/data_sets/chromedriver')
    driver.get(url)
    soup = BeautifulSoup(driver.page_source,'lxml')
    driver.quit()
    return soup.find_all('table')


def find_nfl_table(table_list, sentence):# inputs all the tables found on a web page using driver method
                                 #returns the table with caption matching 'sentence'
    for x in table_list:
        if find_caption(x) == sentence:
            r = x
            break
    return r  

def switch_rushing_receiving (table): #switch rush data and receiving data if needed
    for i,row in table.iterrows():
        rush = table.iloc[i,6:14]
        receiving = table.iloc[i,14:25]

        table.iloc[i,6:17] = receiving.tolist()
        table.iloc[i,17:25] = rush.tolist()

    return table 

def main(table, col):
    r_list = []
    for i, row in table.iterrows():
        url = row['nfl url']
        conda = (row['nfl method'] == 'success from main')
        cond1b = (row['nfl table type'] == 'Receiving & Rushing Table')
        cond2b = (row['nfl table type'] != 'Receiving & Rushing Table')
        cond3 = row['nfl method'] == 'success from main1'
        cond4 = (row['nfl method'] == 'success from main2') | (row['nfl method'] == 'success from main3')
        cond5 = (row['nfl method'] == 'fail after main1')
        cond6 = (row['nfl method'] == 'fail (eg link broken)')

        if conda & cond1b:
            soup = BeautifulSoup(urlopen(url),'html.parser')
            table_0_soup = soup.find_all('table')[0]
            table_nfl = nflstats(table_0_soup)
            r = pd.to_numeric(table_nfl.loc[0:overall_nfl_index(table_nfl)-1,col], errors='coerce').fillna(0.0).tolist()


        elif conda & cond2b:
            r = [0]

        elif cond3:
            time.sleep(10)
            table_list = generate_all_nfl_tables(url)
            table_0_soup = find_nfl_table(table_list, 'Receiving & Rushing Table')
            table_nfl = nflstats(table_0_soup)
            r = pd.to_numeric(table_nfl.loc[0:overall_nfl_index(table_nfl)-1,col], errors='coerce').fillna(0.0).tolist()

        elif cond4:
            time.sleep(10)
            table_list = generate_all_nfl_tables(url)
            table_0_soup = find_nfl_table(table_list, 'Rushing & Receiving Table')
            table_nfl = nflstats(table_0_soup)
            table_nfl = switch_rushing_receiving(table_nfl)
            r = pd.to_numeric(table_nfl.loc[0:overall_nfl_index(table_nfl)-1,col], errors='coerce').fillna(0.0).tolist()

        elif cond5 | cond6:
            r = [0]

        r_list.append(r)


    return r_list