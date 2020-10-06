### PACKAGES


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)

import statsmodels.api as sm
from statsmodels.formula.api import ols


from sklearn.metrics import mean_squared_error, classification_report, confusion_matrix
from sklearn.metrics import roc_curve, roc_auc_score, log_loss, precision_recall_curve
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LinearRegression, Ridge, ElasticNet, LogisticRegression

from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.impute import SimpleImputer as Imputer
from sklearn.pipeline import Pipeline


### USER-DEFINED FUNCTIONS

def dropthenan(table):
    cond1 = table[table.cfbconference == 'Other'].index.tolist()
    cond2 = table[table.cfbtd.isna()].index.tolist()
    cond3 = table[table.combineforty.isna()].index.tolist()
#    cond = np.unique(cond1+cond2+cond3)
    cond = np.intersect1d(np.intersect1d(cond1,cond2),cond3)
    return table.drop(cond, axis = 0).reset_index(drop = True)

def confclass(table):
    table.loc[table.cfbconference == 'Other','cfbconference'] = np.nan
    table.loc[table.cfbclass == 'Non Declared','cfbclass'] = np.nan
    table = pd.get_dummies(table, prefix=['cfbconference','cfbclass'])
    return table

# def splitter(table, col, thresh):
#     table['target'] = table[col].apply(lambda x: 1 if x > thresh else 0)
#     return table.drop(col, axis = 1)

def splitter(arr, thresh):
    return arr.apply(lambda x: 1 if x > thresh else 0)

def normalizeX(X, cols_list):
    x = X[cols_list]
    X_others = X.drop(cols_list, axis = 1)
    trans = preprocessing.MinMaxScaler()
    #trans = preprocessing.StandardScaler()
    x_scaled = trans.fit_transform(x)
    X_new = pd.DataFrame(x_scaled , columns = X[cols_list].columns.tolist())
    return pd.concat([X_new, X_others], axis = 1) #pd.concat([X_new + X_others], axis = 1)