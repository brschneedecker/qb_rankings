# qb_rankings
NFL QB Analysis

### Repo To-do
1. Add list of package dependencies
2. Add run instructions to README.md

### Pending Improvements
1. Number data processing programs to reflect order?
...1. download.py --> 00_download.py
...2. preprocess.py --> 01_qb_season.py
...3. TBD --> 02_qb_career.py
2. Aggregate QB season stats to overall career
3. Normalize per-game data to control for within-season effects (e.g. rule changes)
4. Add salary data (https://overthecap.com/position/quarterback/2017/)
5. Update how population is limited. Currently limit to primary starter seasons,
...might set a minimum number of total games or limit to DVOA qualifiers
6. Plot QB DVOA, DYAR 
7. Update plotting to use preprocessing program outputs
8. Look into using this for diagnostics: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.value_counts.html
