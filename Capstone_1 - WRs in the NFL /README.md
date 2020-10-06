# Capstone Project: Predicting Wide Receivers Performance in the NFL

### Quick Summary

The best college football athletes get a chance to be selected by professional teams during the annual NFL draft. Wide Receivers (WR's) are no exceptions, and each General Manager (GM) establishes a ranking of the players available to fill for the team's needs at this position. A substantial amount of WR's end up performing poorly in the league, while others exceed at their position.

But what do we mean by **performance**? For a WR, the number of receiving yards throughout a season is critical to the success of the player and the team. For a GM, it is important to know the expected performances throughout the first contract (roughly the first 5 years in the league after being drafted). Hence, our goal will be to build a model that predicts whether a player is a **success or bust** depending on whether the **total receiving yards during the first 5 years** is greater or less than a set **threshold**. We build the model based on the collegiate and NFL combine achievements of players drafted between 2000 and 2014.

However, because the data was limited (only 393 rows), incomplete (75% of those being complete), and heavily zero-inflated, the first model produced unsatisfactory levels of predictions. I then decided to turn this project into a classification one, where the algorithm predicts the **chance of success in the league**, a proability that the receiving yards exceed a certain threshold. This method was far more successful: the model was 80% accurate and was used against the 2020 class to rank the WR's that were going to be drafted this year.

### Organization of the Directory

For more information about the project itself, check out the sub-repository "reports". There are slides (slides.pptx) along with a final report which covers the motivations behind this capstone project, our methodology, the data wrangling steps, the statistical tests we used to analyse our data and the development of a machine learning based predictive algorithm.

You can also check the notebooks in this repository. Each is specifically oriented toward a goal and contains a thorough describtion of the methodology used to collect, clean, verify and test the data. Chronologically speaking, one should read the notebooks in this order:

1) Collecting_Data_TableDraft.ipynb: scrape the pro-football-reference website and collects draft, NFL and CFB data
2) Collecting_Data_TableCombine.ipynb: collects NFL combine data
3) Collecting_Data_Final.ipynb: merge NFL, CFB, Combine data in a single csv file
4) Cleaning_Data.ipynb: cleans our data and exports a usuable csv file
5) Exploratory_Data.ipynb: runs basic inferential statistics, generates even more data and explore trends
6) Statistical_Data_Analysis.ipynb: runs advanced inferential statistics on data
7) and 8) Machine_Learning_Model_Regressor and Logistic: build two predictive models. The first one produced unsatisfactory predictions with regard to our target (the number of receiving yards during the first 5 years in the NFL) and was based solely on a linear regression method. The second is a classifier which instead predicts the chance of a player being successful in the league, a model which turns out to be far more profitable and reliable.

Some of these notebooks come with a respective module file (filename.py) where we define each of the user-defined functions that we use in the corresponding notebook.
