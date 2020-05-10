"""
This program contains globally used paths and names of external files used in processing.
"""

# HTML paths for data extraction
pfr_base_html = "https://www.pro-football-reference.com/years/{year}/passing.htm"
fo_base_html = "https://www.footballoutsiders.com/stats/nfl/qb/{year}"
otc_base_html = "https://overthecap.com/position/quarterback/{year}/"

# csv crosswalks used in ETL
team_name_xwalk = "xwalks/team_name_xwalk.csv"
esf_xwalk = "xwalks/elite_system_fraud.csv"

# Log files
etl_log = "logs/qb_etl_{:%Y-%m-%d_%H:%M:%S}.log"

# Output Data
wide_af = "data/qb_season_wide.csv"