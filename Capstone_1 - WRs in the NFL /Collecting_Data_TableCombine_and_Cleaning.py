### PACKAGES

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


### LISTS OF COLUMNS

list_of_combine_columns = ['combine_player', 'combine_pos', 'combine_ht', 'combine_wt',
 'combine_forty', 'combine_vertical', 'combine_benchreps', 'combine_broadjump', 
 'combine_cone', 'combine_shuttle', 'combine_year', 'combine_pfr_id', 'combine_av',
  'combine_team', 'combine_round', 'combine_pick']


list_of_combine_columns_from_search =  ['combine_pos', 'combine_ht', 'combine_wt','combine_forty',
 'combine_vertical', 'combine_benchreps', 'combine_broadjump', 'combine_cone', 'combine_shuttle', 'combine_year']


### OTHER FUNCTIONS

def generate_all_tables(url):
    '''
    use web.driver chrome to find hidden tables
    '''
    driver = webdriver.Chrome('data_sets/chromedriver') 
    driver.get(url)
    time.sleep(4)
    soup = BeautifulSoup(driver.page_source,'lxml')
    time.sleep(1)
    driver.quit()
    return soup.find_all('table')


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################


### COMBINE MERGING

def merge_combine(td,tc):
    '''
    inputs the draft table and the combine table
    outputs the two merged by condition1: year, round, pick or condition2: year, name
    and a column of combine method indicating if the merge was successful or not
    '''

    td[ list_of_combine_columns+['combine_method'] ] = pd.DataFrame([ [np.nan] * (len(list_of_combine_columns) + 1) ], index=td.index)
    for i, row in td.iterrows():
        year = row.year
        ro = row.round
        pick = row.pick
        name = row.player
        # since the combine table isn't organized as the draft table, for each drafted player, we search through the whole combine table
        condition1 = (tc.loc[:,'Year'] == year) & (tc.loc[:,'Round'] == ro) & (tc.loc[:,'Pick'] == pick)
        condition2 = (tc.loc[:,'Year'] == year) & (tc.loc[:,'Player'] == name)
        l = tc.index[condition1 | condition2  ].tolist()

        # if list is empty
        if not l:
            td.loc[i,'combine_method'] = 'fail from merge'
        else:
           td.loc[i,list_of_combine_columns] = tc.iloc[l[0]].values.tolist()
           td.loc[i,'combine_method'] = 'success from merge'

    return td


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

combine_columns = ['year','pos','height','weight','40yd','bench','broad jump','shuttle','3 cone','vertical']


def combinestats(t): 
    ''' 
    outputs the combine table from the table on the soup document
    '''
    table = pd.DataFrame(columns=combine_columns, index=range(0,10))#create a new blank table
    
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



def row_combine(t):
    '''
    inputs the scrapped table, outputs the row formatted to match with combine data on table draft
    '''
    col = t.iloc[-2]
    val = t.iloc[-1]

    #if the second to last row has inputs of year and vertical proceed
    if (col['year'].lower() == 'year') & (col['vertical'].lower() == 'vertical'): 
        #re-arranging the data
        x = [val['pos'], val['height'], val['weight'], val['40yd'], val['vertical'], val['bench'],
        val['broad jump'], val['3 cone'], val['shuttle'], val['year']] 
        y = 'success from search'

    else:
        x = [np.nan] * len(combine_columns) #if not, the table is good, but the stats need to be re-arranged manually
        y = 'success from search, but needs re-arranging'
    # convert numerical entries from strings to floats and '' to np.nan for missing values
    return [x[0]] + list(map( lambda i: np.nan if i == '' else float(i) , x[1:] )) , y



########################################################
########################################################
########################################################
########################################################
########################################################


### COMBINE SEARCHING

desired_captions = ['Combine Measurements Table']


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





def search_combine(tdc): 
    '''
    inputs the merged draft / combine table
    returns additional combine data from searching on the nfl page of each player
    '''

    # list of rows with missing combine
    missing_combine = tdc.index[tdc.loc[:,'combine_method'] == 'fail from merge'].tolist()

    for i in missing_combine:
        url_nfl = tdc.loc[i,'nfl_url']

        # default value for x
        x = [np.nan] * len(list_of_combine_columns_from_search)
        # if there's no access to the nfl page, can't do more
        if url_nfl == 'nfl link is missing':
            y = 'fail from merge and no nfl link'

        else:
            # generate all tables from page
            all_tables = generate_all_tables(url_nfl)
            # find all captions
            captions_nfl = find_captions_from_list_of_tables(all_tables)

            # if 'Combine Measurements Table' among the captions, store combine data using combinestats and row_combine
            if desired_captions[0] in captions_nfl:
                # store only in the selected combine columns that match with the data coming from search
                # tdc.loc[i, list_of_combine_columns_from_search], tdc.loc[i, 'combine_method'] 
                x, y = scrape_data(all_tables, captions_nfl, desired_captions[0], [combinestats, row_combine])
            
            # otherwise, can't do more
            else:
                y = 'fail from merge and from search'

        tdc.loc[i, list_of_combine_columns_from_search] = x
        tdc.loc[i, 'combine_method'] = y
    return tdc



########################################################
########################################################
########################################################
########################################################
########################################################


### CLEANING SECTION


def mismatch_combine(table):
    '''
    search for mismatches in year between entry from draft and entry from combine data
    '''
    list = []
    for i in table.index:
        if (table.loc[i, 'year'] != table.loc[i, 'combine_year']) and ~(np.isnan(table.loc[i, 'combine_year'])):
            list.append( ( i, table.loc[i, 'year'], table.loc[i, 'combine_year'] ) )

    return list

list_of_columns_selected = ['year', 'round', 'pick', 'player', 
'cfb_url','cfb_table_name', 'cfb_school','cfb_conference', 
'cfb_class','cfb_pos', 'cfb_games', 'cfb_receptions',
'cfb_rec_yards', 'cfb_rec_yards_per_reception', 'cfb_rec_td',
'cfb_rushes', 'cfb_rushing_yards', 'cfb_rushing_yards_per_rush',
'cfb_rushing_td', 'cfb_plays', 'cfb_yards', 'cfb_yards_per_play',
'cfb_td',  
'combine_method', 'draft_age', 'combine_ht','combine_wt', 
'combine_forty', 'combine_vertical', 'combine_benchreps',
'combine_broadjump', 'combine_cone',
'nfl_url','nfl_table_name', 'nfl_yards_per_year']

rename_column = {'draft_age': 'combine_draft_age'}