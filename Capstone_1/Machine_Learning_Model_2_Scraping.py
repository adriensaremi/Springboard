import pandas as pd
import numpy as np
from urllib.request import urlopen
import webbrowser as wb
from bs4 import BeautifulSoup
from selenium import webdriver
import time


list_of_draft = ['year','round','pick','player','nfl url','pos','draft age','team',
                                  'entry year','last year','1st team pro select','pro select','weighted career av',
                                  'years as primary starter','games', 'games started',
                                  'rushing attempts','rushing yards','rushing td',
                                  'receiving attemps','receiving yards','receiving td','college','cfb url']
           

list_of_college = ['cfb school', 'cfb conference', 'cfb class', 'cfbpos', 'cfb games', 'cfb receptions', 
                         'cfb yards','cfb average', 'cfb td', 'cfb attemps rushing', 'cfb yards rushing', 
                         'cfb av grushing', 'cfb td rushing', 'cfb scrimmages', 'cfb yards total',
                         'cfb avg total', 'cfb td total']                       


list_of_combine = ['combine year', 'combine pos','combine ht','combine wt','combine forty',
                         'combine bench','combine broad jump','combine shuttle', 'combine three cone','combine vertical']

list_of_added_columns = list_of_college + list_of_combine


drop_columns = ['year','pos','cfb school','cfbpos','draft age','entry year','last year',
       '1st team pro select','pro select','weighted career av',
       'years as primary starter','games', 'games started',
       'rushing attempts','rushing yards','rushing td','receiving attemps',
       'receiving yards','receiving td','combine year','combine pos']

reorder_columns = ['player', 'nfl url' ,'cfb url','team', 'college', 'round', 'pick', 
		'cfb conference', 'cfb class', 'cfb games', 'cfb receptions','cfb yards',
        'cfb average', 'cfb td','cfb attemps rushing', 'cfb yards rushing', 
        'cfb av grushing', 'cfb td rushing','cfb scrimmages', 'cfb yards total', 
        'cfb avg total', 'cfb td total','combine ht', 'combine wt', 'combine forty',
        'combine vertical','combine bench','combine broad jump', 'combine three cone', 'combine shuttle']
       
renaming_dict = {
    'nfl url':'nflurl',
    'cfburl':'cfburl',
    'team':'nflteam',
    'cfb conference':'cfbconference',
    'cfb class':'cfbclass',
    'cfb games':'cfbgames',
    'cfb receptions':'cfbreceptions',
    'cfb yards':'cfbrecyards',
    'cfb average':'cfbrecyardsperreception',
    'cfb td':'cfbrectd',
    'cfb attemps rushing':'cfbrushattempts',
    'cfb yards rushing':'cfbrushyards',
    'cfb av grushing':'cfbrushyardsperattempt',
    'cfb td rushing':'cfbrushtd',
    'cfb scrimmages':'cfbscrimmages',
    'cfb yards total': 'cfbyards',
    'cfb avg total':'cfbyardsfromscrimmage',
    'cfb td total':'cfbtd',
    'combine ht':'combineht',
    'combine wt':'combinewt',
    'combine forty':'combineforty',
    'combine vertical':'combinevertical',
    'combine bench':'combinebenchreps',
    'combine broad jump':'combinebroadjump',
    'combine three cone':'combinecone',
    'combine shuttle':'combineshuttle'}



def main(url_draft):
    soup_draft = BeautifulSoup(urlopen(url_draft),'html.parser')
    table_draft = tabledraft(soup_draft)
    table_draft = expend_draft_table(table_draft)
        
    for i in table_draft.index:
    
        url_cfb = table_draft.loc[i]['cfb url']
        url_nfl = table_draft.loc[i]['nfl url']
        time.sleep(1)
        try:
            soup_cfb = BeautifulSoup(urlopen(url_cfb),'html.parser')
            table_cfb = collegestats(soup_cfb)
            table_draft.loc[i,24:41] = row_cfb(table_cfb)
        except:
            table_draft.loc[i,24:41] = [np.nan]*17

        
        try:
            soup_nfl = BeautifulSoup(urlopen(url_nfl),'html.parser')
            all_tables = generate_all_nfl_tables(url_nfl)
            time.sleep(2)
            combine_table = find_combine_table(all_tables)
            combine_stats = combine_nfl(combine_table)
            table_draft.loc[i,41:] = row_combine(combine_stats)
        except:
            table_draft.loc[i,41:] = [np.nan]*10
              
    return table_draft






def tabledraft(soup):
    table_0 = soup.find_all('table')[0] #capture the table from the soup page
    
    table = pd.DataFrame(columns= list_of_draft
                         ,index=range(0,310)) #create a new blank table

    #fill in the blanks of that table using for loop statements
    #note: scrapping nfl url and cfb url using get('href')
    #note: if the nfl football link is missing, simply add np.nan
    #note: if the college football link is missing, simply add np.nan
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
                    table.iat[row_marker,column_marker] = np.nan
                column_marker += 1
            elif column_marker == 23:
                lista = column.find_all('a')
                if len(lista) == 0:
                    table.iat[row_marker,column_marker] = np.nan
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


def expend_draft_table(table): #create additional columns
    table[list_of_added_columns] = pd.DataFrame(   np.full( (len(table),len(list_of_added_columns)) , np.nan )     )
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
    
    table.dropna(subset=['cfb school'],inplace=True)  

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
    return t.loc[i-1][0:4].tolist() + [str(t['cfb games'].apply(pd.to_numeric).iloc[:i].sum())] + t.iloc[i][5:].tolist()









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
    table = pd.DataFrame(columns = list_of_combine,
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
        val = t.iloc[-1].values

    except:
    	val = [np.nan]*10

    return val


def correct_switch(table, l):
	for i in l:
		l1 = table.iloc[l,9:13].values
		l2 = table.iloc[l,13:17].values
		table.iloc[l,9:13] = l2
		table.iloc[l,13:17] = l1

	return table
