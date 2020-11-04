# Capstone Project: Predicting Wide Receivers Performance in the NFL

### Quick Summary

The best college football athletes get a chance to be selected by professional teams during the annual NFL draft. Wide Receivers (WR's) are no exceptions, and each General Manager (GM) establishes a ranking of the players available to fill for the team's needs at this position. A substantial amount of WR's end up performing poorly in the league, while others exceed at their position.

But what do we mean by **performance**? For a WR, the number of receiving yards throughout a season is critical to the success of the player and the team. For a GM, it is important to know the expected performances throughout the first contract (roughly the first 5 years in the league after being drafted). Hence, our goal will be to build a model that predicts whether a player is a **success or bust** depending on whether the **total receiving yards during the first 5 years** is greater or less than a set **threshold**. This project is a follow-up of an older version, more accurate, more complete and more carefully written. Originally, the idea was to predict for the number of yards itself, but because the data is still limited and incomplete, this task is far too complex.

We build the model based on the collegiate and NFL combine achievements of players drafted between 2000 and 2014. In the end, the f1-score of our Random Forest model was **70% accurate** for a threshold of _200 yards_. We use it to rank the 2020 class of receivers (on notebook 4).

### Organization of the Repository

For more information about the project itself, check out the sub-repository "reports". There are slides (slides.pptx) along with a final report which covers the motivations behind this capstone project, our methodology, the data wrangling steps, the statistical tests we used to analyse our data and the development of a machine learning based predictive algorithm.

You can also check the notebooks in this repository. Each is specifically oriented toward a goal and contains a thorough describtion of the methodology used to collect, clean, verify and test the data. Chronologically speaking, one should read the notebooks in this order:

1) Collecting_Data_TableDraft.ipynb: scrape the pro-football-reference website and collects draft, NFL and CFB data
2) Collecting_Data_TableCombine_and_Cleaning.ipynb: collects NFL combine data and clean dataframe, ready for analysis
3) Exploratory_Data.ipynb: runs basic inferential statistics and advanced inferential statistics
4) Machine_Learning_Model: build a classifier which predicts the chance of a player being successful in the league, a model which turns out to be far more profitable and reliable.

Some of these notebooks come with a respective module file (filename.py) where we define each of the user-defined functions that we use in the corresponding notebook.
