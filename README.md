# qb_rankings
NFL QB Analysis using Python 3

### Setup
1. Clone this repo
2. Install packages (see requirements.txt)
---

### Run Instructions
1. Navigate to repo directory
2. Update makefile bgn_yr and end_yr to get desired analysis period
3. Run ```make all``` to clean output directories, download source data, and build analytic file

------

### TODO

1. Combine download and preprocess into a single ETL script
2. Put all code directly in src
3. Refactor to loop by year, merging all data sources within a given year. Long run goal is to load 1 year of data into a database at a time as it becomes available
4. Build small database to store data and dummy folder to store it
5. Connect ETL script to database
6. Set up environment (yaml) file to handle dependencies/reproducibility 

---

### Pending Improvements
1. Update plotting to use match preprocessing inputs
2. Update plotting to interactive dashboard
3. Normalize per-game data to control for within-season effects (e.g. rule changes)
4. Elite-system-fraud with multi-category logistic regression
