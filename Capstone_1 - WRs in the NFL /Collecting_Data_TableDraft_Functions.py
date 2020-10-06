### PACKAGES

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

### LISTS OF COLUMNS

list_of_draft = ['year','round','pick','player','nfl_url','pos','draft_age','draft_team','entry_year','last_year',
                                  'first_team_all_pro_select','pro_bowl_select','years_as_primary_starter', 'weighted_career_av', 
                                  'games', 'games_started',
                                  'rushes','rushing_yards','rushing_td',
                                  'receptions','rec_yards','rec_td',
                                  'college','cfb_url']

list_of_cfb = ['cfb_school','cfb_conference','cfb_class','cfb_pos','cfb_games',
                                 'cfb_receptions','cfb_rec_yards', 'cfb_rec_yards_per_reception','cfb_rec_td',
                                 'cfb_rushes','cfb_rushing_yards','cfb_rushing_yards_per_rush','cfb_rushing_td',
                                 'cfb_plays','cfb_yards','cfb_yards_per_play','cfb_td']

list_of_nfl = ['nfl_yards_per_year','nfl_yards']


int_columns_draft = ['year', 'round', 'pick', 'draft_age', 'entry_year', 'last_year',
       'first_team_all_pro_select', 'pro_bowl_select','years_as_primary_starter']

float_columns_draft = ['weighted_career_av', 'games', 'games_started', 'rushes',
       'rushing_yards', 'rushing_td', 'receptions', 'rec_yards', 'rec_td']

float_columns_cfb = ['cfb_games','cfb_receptions','cfb_rec_yards', 'cfb_rec_yards_per_reception','cfb_rec_td',
        'cfb_rushes','cfb_rushing_yards','cfb_rushing_yards_per_rush','cfb_rushing_td','cfb_plays',
        'cfb_yards','cfb_yards_per_play','cfb_td']

list_of_possible_cfb_captions = ['Receiving & Rushing Table', 'Rushing & Receiving Table','Passing Table',
'Defense & Fumbles Table','Punt & Kick Returns Table','Kick & Punt Returns Table']


### OTHER FUNCTIONS

def url_testing(url):
    try:
        response = requests.get(url)
        x = 'valid'
    except requests.ConnectionError as exception:
        x = 'invalid'
    return x


def generate_all_tables(url):
    '''
    use web.driver chrome to find hidden tables
    '''
    driver = webdriver.Chrome('data_sets/chromedriver') 
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source,'lxml')
    time.sleep(1)
    driver.quit()
    return soup.find_all('table')



###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################


### DRAFT SCRAPPING

def tabledraft(soup):
    '''
    capture the draft table using the soup document
    '''
    table_0 = soup.find_all('table')[0] #it's always the first table
    
    table = pd.DataFrame(columns= list_of_draft+list_of_cfb+['cfb_table_name']+list_of_nfl+['nfl_table_name']
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
                try:
                    table.iat[row_marker,column_marker] = column.find_all('a')[0].get('href')
                except:
                    table.iat[row_marker,column_marker] = 'cfb link is missing' 
                    column_marker += 1
            else:
                table.iat[row_marker,column_marker] = column.get_text()
                column_marker += 1
        row_marker += 1
    
    #drop all rows without a year entry (those are table headers on the webpage)
    table.dropna(subset=['year'],inplace=True)
    #convert numerical entries from strings to int or floats and '' to zeros
    table.loc[:,int_columns_draft] = table.loc[:,int_columns_draft].applymap(lambda x: 0 if x == '' else int(x))
    table.loc[:,float_columns_draft] = table.loc[:,float_columns_draft].applymap(lambda x: 0.0 if x == '' else float(x))
    return table.reset_index(drop = True)


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################


def cfbstats(table_0):
    '''
    outputs the cfb table from the table on the soup document
    '''
    table = pd.DataFrame(columns=list_of_cfb,
                         index=range(0,15)) #create a new blank table
    row_marker = 0
    for row in table_0.find_all('tr'):
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            table.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        row_marker += 1
    
    table.dropna(subset=['cfb_school'],inplace=True)  

    return table.reset_index(drop = True)  


def cfbstats_invert(table_0):
    '''
    same as cfbstats, but inverts rushing and receiving stats
    '''
    table = cfbstats(table_0)
    real_rush_stats = table.loc[:,['cfb_receptions','cfb_rec_yards','cfb_rec_yards_per_reception','cfb_rec_td']].values
    real_rec_stats = table.loc[:,['cfb_rushes','cfb_rushing_yards','cfb_rushing_yards_per_rush','cfb_rushing_td']].values
    table.loc[:,['cfb_rushes','cfb_rushing_yards','cfb_rushing_yards_per_rush','cfb_rushing_td']] = real_rush_stats
    table.loc[:,['cfb_receptions','cfb_rec_yards','cfb_rec_yards_per_reception','cfb_rec_td']] = real_rec_stats
    return table

def overall_cfb_index(t): 
    '''
    returns which row is the overall stats. Needed for players with multiple teams
    '''
    try: #attemps to find a 'overall' row
        list = [x.lower() for x in t['cfb_school'].tolist()]
        i = list.index('overall')
    except:#if not, simply pick the last one
        i = len(t)-1
    return i

def row_cfb(t):
    '''picks the overall row of the college tabler and 
    adds data from the year right before (team, age, pos)
    will be stored in the draft table
    '''
    i = overall_cfb_index(t)
    return t.loc[i-1][0:4].tolist() + [str(t['cfb_games'].apply(pd.to_numeric).iloc[:i].sum())] + t.iloc[i][5:].tolist()


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################


nfl_columns = ['age','team','pos','no','games','games_started',
                                 'targets','receptions','rec_yards','rec_yards_per_reception','rec_td','rec_first_downs','rec_longest',
                                 'receptions_per_game','rec_yards_per_game','rec_catch_ratio','rec_yards_per_target',
                                 'rushes','rushing_yards','rushing_td','rushing_first_downs','rushing_longest',
                                 'rushing_yards_per_rush','rushing_yards_per_game','rushes_per_game',
                                 'plays','yards_per_play','yards','td','fumbles','approximate_value']


def shift_nfl_row (row,start,end,shift):
    '''
    will shift the nfl overall row
    '''
    x = row[start:end]
    row[start+shift:end+shift] = x
    return row

def nflstats(table_0): 
    '''
    outputs the nfl table from the table on the soup document
    '''
    table = pd.DataFrame(columns=nfl_columns,
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

    return table


def nflstats_invert(table_0):
    '''
    does the same as nfl stats but invert switching and receiving
    '''
    table = nflstats(table_0)
    real_rush_stats = table.loc[:,['targets','receptions','rec_yards','rec_yards_per_reception',
                                'rec_td','rec_first_downs','rec_longest','receptions_per_game']].values
    real_rec_stats = table.loc[:,['rec_yards_per_game','rec_catch_ratio','rec_yards_per_target',
                                'rushes','rushing_yards','rushing_td','rushing_first_downs','rushing_longest',
                                'rushing_yards_per_rush','rushing_yards_per_game','rushes_per_game']].values
    table.loc[:,['targets','receptions','rec_yards','rec_yards_per_reception','rec_td','rec_first_downs',
                                'rec_longest','receptions_per_game','rec_yards_per_game','rec_catch_ratio',
                                'rec_yards_per_target']] = real_rec_stats
    table.loc[:,['rushes','rushing_yards','rushing_td','rushing_first_downs','rushing_longest',
                                'rushing_yards_per_rush','rushing_yards_per_game','rushes_per_game']] = real_rush_stats
    return table


def list_of_rec_yards(t):
    '''
    scrape the list of nfl receiving yards per season
    '''
    df = {t.iloc[i].age : t.iloc[i].rec_yards   for i in range(len(t))}
    l = []
    for key, value in df.items():
        if key.isdigit():
            l.append(value)
    return list(map(float,l))


def overall_nfl_index(t):
    '''
    same as overall_cfb_index but for nfl
    '''
    try:
        i = ((t.iloc[:,0:3] == ['']*3).all(axis = 1)).tolist().index(True)
                #are the first 3 entries empty
                #create boolean if all are
                #convert to list and find the row
    except:
        i = len(t)-1 #if not, simply pick the last one
    return i

def row_nfl(t):
    '''
    picks the nfl data that will be stored in the draft table
    '''
    i = overall_nfl_index(t)     
    return [list_of_rec_yards(t), float(t.loc[i,'rec_yards'])] 


########################################################
########################################################
########################################################
########################################################
########################################################


### OUR MAIN FUNCTION

desired_captions = ['Receiving & Rushing Table','Rushing & Receiving Table']

def find_captions_from_list_of_tables(all_tables):
    '''
    once provided with all tables from the soup document
    return all the captions
    '''
    list = []
    for t in all_tables:
        try:
            list.append(t.find_all('caption')[0].get_text() )
        except:
            list.append([''])
    return list

def scrape_data(all_tables, captions, desired_caption, functions):
    '''
    inputs all tables, their respective captions, the desired caption
    use the two appropriate functions (eg nflstats and row_nfl)
    in order to select the correct table from the soup document 
    and then to return the appropriate data to be stored in the draft table
    '''
    good_table_index = captions.index(desired_caption)
    good_table = all_tables[good_table_index]
    table = functions[0](good_table)
    return functions[1](table)


def draft_nfl_cfb_scrap(url_draft):
    '''
    inputs the draft url
    returns the draft + cfb stats + nfl stats for each player
    '''
    
    # soup document and table draft from soup
    soup_draft = BeautifulSoup(urlopen(url_draft),'html.parser')
    table_draft = tabledraft(soup_draft) 
    #iterate over all rows
    for i in table_draft.index:
        url_cfb = table_draft.loc[i]['cfb_url']
        url_nfl = table_draft.loc[i]['nfl_url']

########################################################

        # if cfb link is missing, leave cfb data np.nan and update cfb_table_name accordingly
        if url_cfb == 'cfb link is missing':
            x, y = [np.nan]*len(list_of_cfb), 'cfb link is missing'
        
        else: 

            # this try / except allows to account for unexpected errors
            try:
                # soup document, all cfb tables and all cfb captions
                soup_cfb = BeautifulSoup(urlopen(url_cfb),'html.parser')
                all_tables_cfb = soup_cfb.find_all('table')
                captions_cfb = find_captions_from_list_of_tables(all_tables_cfb)

                # if 'Receiving & Rushing Table' among the captions, store cfb data using cfbstats and row_cfb
                # x = cfb data and y = caption table
                if desired_captions[0] in captions_cfb:
                    x, y = scrape_data(all_tables_cfb, captions_cfb, desired_captions[0], [cfbstats, row_cfb]), desired_captions[0].lower()
                # if not, if 'Rushing & Receiving Table' among the captions, store cfb data using cfbstats_invert and row_cfb
                elif desired_captions[1] in captions_cfb:
                    x, y = scrape_data(all_tables_cfb, captions_cfb, desired_captions[1], [cfbstats_invert, row_cfb]), desired_captions[0].lower() + ' inverted'

                # if not, use Chrome Webdriver and repeat process
                else:
                    all_tables = generate_all_tables(url_cfb)
                    captions = find_captions_from_list_of_tables(all_tables)

                    if desired_captions[0] in captions:
                        x, y = scrape_data(all_tables, captions, desired_captions[0], [cfbstats, row_cfb]), desired_captions[0].lower() + ' webdriver'
                    elif desired_captions[1] in captions:
                        x, y = scrape_data(all_tables, captions, desired_captions[1], [cfbstats_invert, row_cfb]), desired_captions[0].lower() + ' webdriver inverted'
                    # if still not, use another message for y
                    else:
                        x, y = [np.nan]*len(list_of_cfb), 'failed after webdriver'

            except:
                x, y = [np.nan]*len(list_of_cfb), 'unexpected error'

        table_draft.loc[i,list_of_cfb] = x
        table_draft.loc[i,'cfb_table_name'] = y

########################################################

        # if rec_yards = 0, store zeros, update nfl_table_name accordingly
        if table_draft.loc[i]['rec_yards'] == 0:
            x, y  = [[0.0], 0], desired_captions[0].lower()
            

        # otherwise, if nfl link is missing, leave nfl data np.nan and update nfl_table_name accordingly
        elif url_nfl == 'nfl link is missing':
            x, y = [[np.nan], np.nan], 'nfl link is missing'

        else:        
            # this try / except allows to account for unexpected errors
            try:
                # soup document, all nfl tables and all nfl captions
                soup_nfl = BeautifulSoup(urlopen(url_nfl),'html.parser')
                all_tables_nfl = soup_nfl.find_all('table')
                captions_nfl = find_captions_from_list_of_tables(all_tables_nfl)

                # if 'Receiving & Rushing Table' among the captions, store nfl data using nflstats and row_nfl
                # x = nfl data and y = caption table
                if desired_captions[0] in captions_nfl:
                    x, y = scrape_data(all_tables_nfl, captions_nfl, desired_captions[0], [nflstats, row_nfl]), desired_captions[0].lower()
                # if not, if 'Rushing & Receiving Table' among the captions, store nfl data using nflstats_invert and row_nfl
                elif desired_captions[1] in captions_nfl:
                    x, y = scrape_data(all_tables_nfl, captions_nfl, desired_captions[1], [nflstats_invert, row_nfl]), desired_captions[0].lower() + ' inverted'

                # if not, use Chrome Webdriver and repeat process
                else:
                    all_tables = generate_all_tables(url_nfl)
                    captions = find_captions_from_list_of_tables(all_tables)

                    if desired_captions[0] in captions:
                        x, y = scrape_data(all_tables, captions, desired_captions[0], [nflstats, row_nfl]), desired_captions[0].lower() + ' webdriver'
                    elif desired_captions[1] in captions:
                        x, y = scrape_data(all_tables, captions, desired_captions[1], [nflstats_invert, row_nfl]), desired_captions[0].lower() + ' webdriver inverted'
                    # if still not, use another message for y
                    else:
                        x, y = [ [np.nan], np.nan ], 'failed after webdriver'

            except:
                x, y = [ [np.nan], np.nan ], 'unexpected error'

        table_draft.loc[i,list_of_nfl] = x
        table_draft.loc[i,'nfl_table_name'] = y

    # convert cfb entries to floats and '' to zero's
    table_draft.loc[:,float_columns_cfb] = table_draft.loc[:,float_columns_cfb].applymap( lambda x: 0.0 if x == '' else float(x)  )         
    return table_draft


def mismatch_cfb(table):
    '''
    search for mismatches in school name from draft and from cfb data
    '''
    list = []
    for i in table.index:
        if (table.loc[i, 'college'] != table.loc[i, 'cfb_school']) and type(table.loc[i].cfb_school) == str:
            list.append( ( i, table.loc[i, 'college'], table.loc[i, 'cfb_school'] ) )

    return list


def mismatch_nfl(table):
    '''
    search for mismatches in rec_yards from draft, from nfl stats
    '''
    l = []
    for i in table.index:
        # the lists in nfl_yards_per_year may be stored as '[year1, year2, ...]'
        # # create a list of strings
        # lstring = table.loc[i,'nfl_yards_per_year'][1:-1].split(",")
        # # convert each string to float
        # lfloat = [float(j) for j in lstring]
        lfloat = table.loc[i,'nfl_yards_per_year']

        if ( table.loc[i].rec_yards == table.loc[i].nfl_yards) and (table.loc[i].rec_yards == np.sum(lfloat) ):
            pass
        else:
            l.append( (i, table.loc[i].rec_yards, table.loc[i].nfl_yards, table.loc[i].nfl_yards_per_year) )

    return l