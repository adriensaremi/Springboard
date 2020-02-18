### Packages

import pandas as pd
import numpy as np
import os

from urllib.request import urlopen
import webbrowser as wb
from bs4 import BeautifulSoup
from selenium import webdriver
import time


pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)



#############
list_of_added_columns = ['combine player', 'combine pos', 'combine ht', 'combine wt',
 'combine forty', 'combine vertical', 'combine benchreps', 'combine broadjump', 
 'combine cone', 'combine shuttle', 'combine year', 'combine pfr_id', 'combine av',
  'combine team', 'combine round', 'combine pick', 'combine method']

def add_combine (td,tc): #inputs the draft table and the combine table
    td[list_of_added_columns] = pd.DataFrame([ [""] * 17], index=td.index)
    for i, row in td.iterrows():
        year = row['year']
        ro = row['round']
        pick = row['pick']
        name = row['player']
        condition1 = (tc.loc[:,'Year'] == year) & (tc.loc[:,'Round'] == float(ro)) & (tc.loc[:,'Pick'] == float(pick)) #does a search by year and round and pick
        condition2 = (tc.loc[:,'Year'] == year) & (tc.loc[:,'Player'] == name) #or does a search by year and name
        try:
            td.iloc[i,75:91] = tc.loc[condition1 | condition2].values.tolist()[0]
            td.iloc[i,91] = 'success from merge'
        except:
            td.iloc[i,91] = 'fail after merge'

    return td














def generate_all_nfl_tables(url): #use web.driver chrome to find hidden tables
    driver = webdriver.Chrome('/Users/adriensaremi/Documents/School and Employment/SpringBoard Course/Springboard/Capstone_1/data_sets/chromedriver')
    driver.get(url)
    soup = BeautifulSoup(driver.page_source,'lxml')
    driver.quit()
    return soup.find_all('table')



def find_caption(table):
    try:
        x=table.find_all('caption')[0].get_text()
    except:
        x=''
    return x

acceptable_words = ['combine','measurements']
def find_combine_table(table_list):# inputs all the tables found on a web page using driver method
                                 #returns the proper table
    for x in table_list:
        caption_words = [y.lower() for y in find_caption(x).split()]
        if any(z in caption_words for z in acceptable_words):
            r = x
            break
        else:
            pass
    return r  



def combine_nfl(t): #accept table instead of soup
    table = pd.DataFrame(columns=['year','pos','height','weight','40yd','bench',
                              'broad jump','shuttle','3 cone','vertical'],
                         index=range(0,10))#create a new blank table
    
    row_marker = 0 #capture the header of the table
    for row in t.find_all('tr')[0:1]:
        column_marker = 0
        columns = row.find_all('th')
        for column in columns:
            table.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        row_marker += 1


    for row in t.find_all('tr')[1:]: #capture the rest of the data
        column_marker = 0
        columns = row.find_all('th') #capture the year
        for column in columns:
            table.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        columns = row.find_all('td') #capture the stats
        for column in columns:
            table.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        row_marker += 1

    table.dropna(axis=0, how='all', inplace = True)
    table = table.reset_index(drop = True)
    return table



def row_combine(t): #inputs the table
    try:
        col = t.iloc[-2]
        val = t.iloc[-1]
        if (col['year'].lower() == 'year') & (col['vertical'].lower() == 'vertical'): #if entries match with expected values, good to go
            el1 = [val['pos'], val['height'], val['weight'], val['40yd'], val['vertical'], val['bench'],
            val['broad jump'], val['3 cone'], val['shuttle'], val['year']] #re-arranging the data
            el2 = 'success from search' #success
        else:
            el1 = ['']*10 #if not, the table is good, but the stats need to be re-arranged manually
            el2 = 'fail after search (good table, wrong data)'
    except:
        el1 = ['']*10 #rare case where the table lacks 2 rows
        el2 = 'fail after search (bad table)'

    return el1, el2




def search_combine(tdc): #inputs the merged table
    missing_combine = tdc.index[tdc.loc[:,'combine method'] == 'fail after merge'].tolist()
    for i in missing_combine:
        if tdc.loc[i,'nfl url'] == 'nfl link is missing':
            tdc.iloc[i,91] = 'fail after search (missing link)'
        else:
            try:
                table_list = generate_all_nfl_tables(tdc.loc[i]['nfl url'])
                time.sleep(10)
                table = find_combine_table(table_list)
                combine_stats = combine_nfl(table)
                el1, el2 = row_combine(combine_stats)

                tdc.loc[i,'combine player'] = tdc.loc[i,'player']
                tdc.loc[i,'combine pfr_id'] = ''
                tdc.loc[i,'combine av'] = ''
                tdc.loc[i,'combine team'] = ''

                tdc.loc[i,'combine round'] = tdc.loc[i,'round']
                tdc.loc[i,'combine pick'] = tdc.loc[i,'pick']

                tdc.iloc[i,76:86] = el1
                tdc.loc[i,'combine method'] = el2
            except:
                tdc.iloc[i,91] = 'fail after search (missing table)'

    return tdc





############ Others

def first_word(sentence):
	list = sentence.split()
	return list[0]


def convert(series): #convert all imaginable entries to float
    l = []
    for x in series:
        
        if isinstance(x, float):
            if np.isnan(x):
                l.append(0)
            else:
                l.append(x)
    
        if isinstance(x, str):
            try:
                l.append(float(x))
            except:
                l.append(0)      
    return l
