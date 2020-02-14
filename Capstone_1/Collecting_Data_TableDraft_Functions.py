### Packages

import pandas as pd
import numpy as np
import seaborn as sns
import requests
import os

from urllib.request import urlopen
import webbrowser as wb
from bs4 import BeautifulSoup
from selenium import webdriver
import time

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)

### Big lists of columns

list_of_draft = ['year','round','pick','player','nfl url','pos','draft age','team',
                                  'entry year','last year','1st team pro select','pro select','weighted career av',
                                  'years as primary starter','games', 'games started',
                                  'rushing attempts','rushing yards','rushing td',
                                  'receiving attemps','receiving yards','receiving td',
                                  'college','cfb url']

list_of_college = ['school','conference','class','pos','games',
                                  'receptions','yards', 'average','td',
                                 'attemps rushing','yards rushing','avg rushing','td rushing',
                                 'scrimmages','yards total','avg total','td total']

list_of_nfl = ['age','team','pos','no','game','game started',
                                 'target','receptions','yards','y/r','td','first downs','longest rec',
                                 'rec per game','yards per game','catch ratio','yards per target',
                                 'rushes','rush yards','rush td','first downs rush','longest rush',
                                 'rush yards per attempt','rush yards per game','rush attempt per games',
                                 'total touches','yards per touch','yards from scrimmage','total td','fumbles','av']

list_of_added_columns = ['cfb school', 'cfb conference', 'cfb class', 'cfb pos', 'cfb games', 'cfb receptions', 'cfb yards',
 'cfb average', 'cfb td', 'cfb attemps rushing', 'cfb yards rushing', 'cfb avg rushing', 'cfb td rushing', 'cfb scrimmages', 'cfb yards total',
 'cfb avg total', 'cfb td total', 'nfl age', 'nfl team', 'nfl pos', 'nfl no', 'nfl game', 'nfl game started', 'nfl target', 'nfl receptions',
 'nfl yards', 'nfl y/r', 'nfl td', 'nfl first downs', 'nfl longest rec', 'nfl rec per game', 'nfl yards per game', 'nfl catch ratio',
 'nfl yards per target', 'nfl rushes', 'nfl rush yards', 'nfl rush td', 'nfl first downs rush', 'nfl longest rush', 'nfl rush yards per attempt',
 'nfl rush yards per game', 'nfl rush attempt per games', 'nfl total touches', 'nfl yards per touch', 'nfl yards from scrimmage', 'nfl total td',
 'nfl fumbles', 'nfl av', 'nfl table type','cfb method', 'nfl method']

### User Defined Functions






### THE SCRAPPING

def tabledraft(soup):
    table_0 = soup.find_all('table')[0] #capture the table from the soup page
    
    table = pd.DataFrame(columns= list_of_draft
                         ,index=range(0,310)) #create a new blank table

    #fill in the blanks of that table using for loop statements
    #note: scrapping nfl url and cfb url using get('href')
    #note: if the nfl football link is missing, simply write 'nfl link is missing
    #note: if the college football link is missing, simply write 'cfb link is missing'
    row_marker = 0
    for row in table_0.find_all('tr')[2:]:
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            if column_marker == 3:
                table.iat[row_marker,column_marker] = column.get_text()
                column_marker += 1
                try:
                    table.iat[row_marker,column_marker] = 'https://www.pro-football-reference.com'+column.find_all('a')[0].get('href')
                except:
                    table.iat[row_marker,column_marker] = 'nfl link is missing'
                column_marker += 1
            elif column_marker == 23:
                lista = column.find_all('a')
                if len(lista) == 0:
                    table.iat[row_marker,column_marker] = 'cfb link is missing' 
                else:
                    table.iat[row_marker,column_marker] = lista[0].get('href') 
                    column_marker += 1
            else:
                table.iat[row_marker,column_marker] = column.get_text()
                column_marker += 1
        row_marker += 1
    
    #drop all rows without a year entry (those are table headers on the webpage)
    table.dropna(subset=['year'],inplace=True)
    return table.reset_index(drop = True)



def cfb_url_fill_in(table): #fill in cfb url
    list_of_missing_index = table.index[table.loc[:,'cfb url'] == 'cfb link is missing'].tolist() #rows with cfb link missing
    table_edit = table

    for i in list_of_missing_index: #the url can be generated from the player's name:
        #link = 'https://www.sports-reference.com/cfb/players/firstname-lastname-1.html
        #watch as not all links are in comission
        x = table.loc[i,'player'].lower().split(' ')
        table_edit.loc[i,'cfb url'] = 'https://www.sports-reference.com/cfb/players/'+x[0]+'-'+x[1]+'-1.html'
    
    return table_edit

def expend_draft_table(table): #create additional columns
    table[list_of_added_columns] = pd.DataFrame([ [""] * 51], index=table.index)
    return table







    

def collegestats(soup):
    table_0 = soup.find_all('table')[0]#capture the table from the soup page
    table = pd.DataFrame(columns=list_of_college,
                         index=range(0,15)) #create a new blank table
    
    row_marker = 0
    for row in table_0.find_all('tr'):
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            table.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        row_marker += 1
    
    table.dropna(subset=['school'],inplace=True)  

    return table.reset_index(drop = True)  

def overall_cfb_index(t): #which row is the overall stats. Needed for players with multiple teams
    try: #attemps to find a 'overall' row
        list = [x.lower() for x in t['school'].tolist()]
        i = list.index('overall')
    except:#if not, simply pick the last one
        i = len(t)-1
    return i

def row_cfb(t):#picks the overall row of the college tabler and adds data from the year right before (team, age, pos)
    i = overall_cfb_index(t)
    return t.loc[i-1][0:4].tolist() + [str(t['games'].apply(pd.to_numeric).iloc[:i].sum())] + t.iloc[i][5:].tolist()











def find_caption(table):
    try:
        x=table.find_all('caption')[0].get_text()
    except:
        x=''
    return x

def overall_nfl_index(t):#same as overall_cfb_index but for nfl
    try:
        i = ((t.iloc[:,0:3] == ['']*3).all(axis = 1)).tolist().index(True)
                #are the first 3 entries empty
                #create boolean if all are
                #convert to list and find the row
    except:
        i = len(t)-1 #if not, simply pick the last one
    return i


def shift_nfl_row (row,start,end,shift):
    x = row[start:end]
    row[start+shift:end+shift] = x
    return row

def nflstats(soup):
    table_0 = soup.find_all('table')[0]#capture the first table from the soup page
    table_caption = find_caption(table_0)
    
    table = pd.DataFrame(columns=list_of_nfl,
                         index=range(0,25))#create a new blank table
    
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

def row_nfl(t):   
    i = overall_nfl_index(t)     
    return t.iloc[i-1][0:4].tolist() + t.iloc[i][4:].tolist() 





### And the main (check notebook)

def main(url_draft):
    soup_draft = BeautifulSoup(urlopen(url_draft),'html.parser')
    table_draft0 = tabledraft(soup_draft)
    table_draft1 = cfb_url_fill_in(table_draft0)
    table_draft = expend_draft_table(table_draft1)
        
    for i in table_draft.index:
    
        url_cfb = table_draft.loc[i]['cfb url']
        url_nfl = table_draft.loc[i]['nfl url']
        time.sleep(2)
        try:
            soup_cfb = BeautifulSoup(urlopen(url_cfb),'html.parser')
            table_cfb = collegestats(soup_cfb)
            table_draft.loc[i,24:41] = row_cfb(table_cfb)
            table_draft.iloc[i,73] = 'success'
        except:
            table_draft.loc[i,24:41] = ['fail']*17
            table_draft.iloc[i,73] = 'fail (eg link broken)'

        
        try:
            soup_nfl = BeautifulSoup(urlopen(url_nfl),'html.parser')
            table_nfl = nflstats(soup_nfl)
            table_draft.loc[i,41:73] = row_nfl(table_nfl)
            table_draft.iloc[i,74] = 'success from main'
        except:
            table_draft.loc[i,41:73] = ['fail']*32
            table_draft.iloc[i,74] = 'fail (eg link broken)'
              
    return table_draft







#1 cleaning: wrong nfl tables

acceptable_words = ['receiving','rushing','fail','games']
def check_nfl_table(table):#did we get the proper nfl tables?
    bad_rows=[]
    for index, row in table.iterrows():
        caption_words = [x.lower() for x in row['nfl table type'].split()]
        if any(x in caption_words for x in acceptable_words): #if any of the keywords is included, move on
            pass
        else:
            bad_rows.append(index) #those are of our interest
    return bad_rows


def generate_all_nfl_tables(url): #use web.driver chrome to find hidden tables
    driver = webdriver.Chrome('/Users/adriensaremi/Documents/School and Employment/SpringBoard Course/Springboard/Capstone_1/data_sets/chromedriver')
    driver.get(url)
    soup = BeautifulSoup(driver.page_source,'lxml')
    driver.quit()
    return soup.find_all('table')



def find_nfl_table(table_list):# inputs all the tables found on a web page using driver method
                                 #returns the proper table
    for x in table_list:
        caption_words = [y.lower() for y in find_caption(x).split()]
        if any(z in caption_words for z in acceptable_words):
            r = x
            break
        else:
            pass
    return r   


def nflstats1(table_0): #same as nflstats except we feed the table, not the soup object
    table_caption = find_caption(table_0)
    
    table = pd.DataFrame(columns=list_of_nfl,
                         index=range(0,25))#create a new blank table
    
    row_marker = 0
    for row in table_0.find_all('tr')[0:]:
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            table.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        row_marker += 1

    table.dropna(axis=0, how='all', inplace = True)
    table = table.reset_index(drop = True)
    i = overall_nfl_index(table)

    for j in range(i,len(table)):
        shift_nfl_row(table.loc[j],0,len(table.columns)-1,1)

    table['table type'] = [table_caption]*len(table)

    return table


def main1(t): #main will read a pd file from now on, imported from csv file
    bad_nfl_tables = check_nfl_table(t)
    for i in bad_nfl_tables:
        try:
            table_list = generate_all_nfl_tables(t.loc[i]['nfl url'])
            time.sleep(10)
            table_soup = find_nfl_table(table_list)
            table_nfl = nflstats1(table_soup)
            t.iloc[i,41:73] = row_nfl(table_nfl)
            t.iloc[i,74] = 'success from main1'
        except:
            t.iloc[i,74] = 'fail after main1'
    return t









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

def identifier_for_main2(table): #which rows have mismatches between 
    c1 = convert(table['receiving yards']) #receiving yards from draft table
    c2 = convert(table['nfl yards']) #receiving yards from nfl table
    df = pd.DataFrame({'1':c1,'2':c2})
    return df.index[df['1'] != df['2']].tolist()

def switch_rushing_receiving (table): #switch rush data and receiving data if needed
    for i,row in table.iterrows():
        rush = table.iloc[i,6:14]
        receiving = table.iloc[i,14:25]

        table.iloc[i,6:17] = receiving.tolist()
        table.iloc[i,17:25] = rush.tolist()

    return table


def nflstats_flip(url): #do it quickly from the url
    html =urlopen(url)
    soup = BeautifulSoup(html,'html.parser')
    table=nflstats(soup)
    return switch_rushing_receiving(table)


def main2(t, recovered_mismatch, all_mismatch): #from all row mismatches, use the flip method on those need
    for i in all_mismatch:
        if i in recovered_mismatch:
            new_table = nflstats_flip(t.loc[i,'nfl url'])
            t.iloc[i,41:73] = row_nfl(new_table)
            t.iloc[i,74] = 'success from main2'

        else:
            t.iloc[i,74] = 'fail after main2'

    return t







def main3(t, manual_mismatch, manual_tables): #feed the table manually to each mismatch
    for index, i in enumerate(manual_mismatch):
        t.iloc[i,41:73] = row_nfl(manual_tables[index])
        t.iloc[i,74] = 'success from main3'

    return t