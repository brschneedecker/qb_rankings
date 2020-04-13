"""
This program contains globally used paths and names of external files used in processing.

TODO: Convert to YAML config
"""

# HTML paths for data extraction
pfr_base_html = "https://www.pro-football-reference.com/years/{year}/passing.htm"
fo_base_html = "https://www.footballoutsiders.com/stats/qb{year}"
otc_base_html = "https://overthecap.com/position/quarterback/{year}/"

# csv crosswalks used in ETL
team_name_xwalk = "xwalks/team_name_xwalk.csv"
esf_xwalk = "xwalks/elite_system_fraud.csv"

# Log files
etl_log = "logs/qb_etl_{:%Y-%m-%d_%H:%M:%S}.log"
db_create_log = "logs/db_create_{:%Y-%m-%d_%H:%M:%S}.log"

# Database file
db_file = "data/qb_sqlite.db"