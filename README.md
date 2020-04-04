# qb_rankings
NFL QB Analysis using Python 3

### Setup
1. Clone this repo
2. Install packages (see requirements.txt)
---

### Run Instructions
1. Navigate to repo directory
2. Update makefile bgn_yr and end_yr to get desired analysis period
3. Run ```make all``` to clean output directories, extract source data, and build analytic file

------

### TODO

1. Make config.py to store paths
2. Update Makefile process for new database ETL
2. Replace database creation Python with .sql script??
3. Reorganize Makefile. "make db" should delete the existing DB.
3. Set up environment (yaml) file to handle dependencies/reproducibility
4. Make data visualizations (Jupyter notebook?)

---

### Pending Improvements
1. Update plotting to use match preprocessing inputs
2. Update plotting to interactive dashboard
3. Normalize per-game data to control for within-season effects (e.g. rule changes)
4. Elite-system-fraud with multi-category logistic regression
