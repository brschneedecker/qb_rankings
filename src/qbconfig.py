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

# Output Data File
wide_af = "data/qb_season_wide.csv"
long_af = "data/qb_season_long.csv"

# ID columns
id_columns = ["player",
        "player_full_name",
        "year",
        "team",
        "division"]

# Value Columns
value_columns = ["age",
        "games",
        "games_started",
        "qb_wins",
        "att",
        "cmp",
        "cmp_pct",
        "yds",
        "yds_per_game",
        "yds_per_game_scaled",
        "yds_per_att",
        "yds_per_att_scaled",
        "yds_per_cmp",
        "sacks",
        "sack_yds",
        "sack_pct",
        "dpi_count",
        "dpi_yards",
        "adj_yds_per_att",
        "net_yds_per_att",
        "adj_net_yds_per_att",
        "td",
        "td_pct",
        "int",
        "int_pct",
        "fourth_qtr_comebacks",
        "game_winning_drives",
        "qb_rating",
        "QBR",
        "DYAR",
        "YAR",
        "DVOA",
        "VOA",
        "efctv_yds",
        "salary_cap_value",
        "elite",
        "system",
        "fraud"]

all_columns = id_columns + value_columns