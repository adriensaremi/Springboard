### PACKAGES


import pandas as pd
pd.set_option('mode.chained_assignment', None)
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)


from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, recall_score, precision_score
from sklearn.metrics import roc_curve, roc_auc_score, log_loss, precision_recall_curve
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate, GridSearchCV

from sklearn.linear_model import LinearRegression, Ridge, ElasticNet, LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier

from sklearn import preprocessing
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# entries that had no cfb and no combine data. Found from notebook #3
list_of_incomplete_rows = [27, 58, 151, 153, 255, 286, 307, 316, 347, 369, 370, 381, 408, 410, 411, 437, 438, 440, 444, 450, 464, 472, 474, 483, 486]

# numerical features we saved after feature selection
num_features = ['cfb_td', 'cfb_yards', 'cfb_receptions', 'cfb_plays','cfb_yards_per_play', 'cfb_games', 
'combine_wt', 'combine_cone','combine_vertical', 'combine_broadjump', 'combine_forty','combine_draft_age']

# categorical features, turned from pandas's get_dummies, and dropping one column (to avoid colinearity)
cat_features_1 = ['cfb_conference_Big 12', 'cfb_conference_Big East', 'cfb_conference_Big Ten', 
'cfb_conference_CUSA', 'cfb_conference_Ind', 'cfb_conference_MAC', 'cfb_conference_MWC', 
'cfb_conference_Pac-10', 'cfb_conference_Pac-12', 'cfb_conference_SEC', 'cfb_conference_Sun Belt', 'cfb_conference_WAC']
cat_features_2 = ['cfb_class_JR', 'cfb_class_SO', 'cfb_class_SR']

### USER-DEFINED FUNCTIONS

def confclass_tonumerical_2(table):
    '''
    transform categories 'cfb_conference' and 'cfb_class' 
    into multiples boolean columns
    '''
    for feature in cat_features_1:
        table[feature] = (table.cfb_conference == feature[15:])*1
    for feature in cat_features_2:
        table[feature] = (table.cfb_class == feature[10:])*1
    return table.drop(['cfb_conference', 'cfb_class'], axis = 1)

def success_function(table, column, thresh):
    '''
    transform linear regression into classification: 
    success vs bust depending on threshold
    re-write the pdf so the new target is the first column
    '''
    cols = table.columns.tolist()
    table['success'] = (table[column] >= thresh)*1
    cols.remove(column)
    cols = ['success'] + cols
    return table[cols]

def normalizeX(X0, cols_list, normalize_strategy):
    '''
    normalize all the columns of cols_list using the strategy normalize_strategy
    '''
    X = X0[cols_list]
    X_others = X0.drop(cols_list, axis = 1)
    trans = normalize_strategy()
    Xp = pd.DataFrame(trans.fit_transform(X) , columns = X.columns.tolist())
    return pd.concat([Xp, X_others], axis = 1)

def transformingX(X, missing_strategy, normalize_strategy):
    '''
    Replace missing values by missing_strategy
    Normalize the numerical columns
    '''
    imp = SimpleImputer(missing_values= np.nan, strategy = missing_strategy)
    imp.fit(X)
    Xp = pd.DataFrame(imp.transform(X), columns = X.columns.tolist())

    # Normalize all feature numerical data (except the dummy columns associated with conference and class)
    Xp = normalizeX(Xp, num_features, normalize_strategy)
    return Xp