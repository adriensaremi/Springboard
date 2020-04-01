# Capstone Project: Predicting Wide Receivers Performance in the NFL

For more information about the project itself, check out the sub-repository "reports". There are slides (slides.pptx) along with a milestone report which cover the motivations behind this capstone project, our methodology, the data wrangling steps and the statistical tests we used to capture and analyse our data.

You can also check the notebooks in this repository. Each is specifically oriented toward a goal and contains a thorough describtion of the methodology used to collect, clean, verify and test the data. Additionally, useful comments supplement important results throughout each notebook. Chronologically speaking, one should read the notebooks in this order:
-Collecting_Data_TableDraft.ipynb: scrape the pro-football-reference website and collects draft, NFL and CFB data
-Collecting_Data_TableCombine.ipynb: collects NFL combine data
-Collecting_Data_Final.ipynb: merge NFL, CFB, Combine data in a single csv file
-Cleaning_Data.ipynb: cleans our data and exports a usuable csv file
-Exploratory_Data.ipynb: runs basic inferential statistics, generates even more data and explore trends
-Statistical_Data_Analysis.ipynb: runs advanced inferential statistics on data

Some of these notebooks come with a respective module file (filenampe.py) where we define each of the user-defined functions that we use in the corresponding notebook.
