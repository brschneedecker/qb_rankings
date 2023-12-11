# -*- coding: utf-8 -*-
"""
# Quarterback Analysis

## TODO

### For finishing this notebook-based analysis
- Implement rate limits: https://pypi.org/project/ratelimit/
- Additional cleaning for matrix represenatation
  - Rescale dimensions
  - Normalize within years
  - one-hot encode teams??
- Unsupervised learning
- Supervised learning

### If converting to an application
 - convert to classes for each data type
 - make data integration class to combine all data
 - make a Python package; the notebook builds package / instantiates objects

## Imports
"""

!pip install ratelimit

import pandas as pd
import re
import inspect
import sys
import numpy as np

import seaborn as sns
import plotly.express as px
import plotly as py
import plotly.graph_objs as go

import scipy.stats as stats

from ratelimit import limits, sleep_and_retry

"""## Parameters"""

start_year = 2022
end_year = 2022
year_range = range(start_year, end_year+1)

FIFTEEN_MINUTES = 900

"""## Data Preparation

### Pro Football Reference Data

Extract, clean, and combine datasets from Pro Football Reference

#### Data Extraction
"""

@limits(calls=15, period=FIFTEEN_MINUTES)
def extract_pfr_table(year, stat_type, table_num=0):
  """
  Extract one table of one season of pro football reference data
  """
  html_path = f"https://www.pro-football-reference.com/years/{year}/{stat_type}.htm"

  # Read statistics table from webpage
  df = pd.read_html(html_path, displayed_only=False)[table_num]

  if stat_type.lower() == 'passing':
    df['season'] = year
  
  return df

def extract_pfr_all(yr):
  pages = ["passing", "rushing", "passing_advanced"]

  adv_passing_dict = {
      "air_yards": (0, 2018),
      "accuracy": (1, 2018),
      "pressure": (2, 2018),
      "play_type": (3, 2019),
  }

  dfs = dict()

  for page in pages:
    if page == "passing_advanced":
      for key in adv_passing_dict:
        if yr >= adv_passing_dict[key][1]:
          dfs[key] = extract_pfr_table(yr, page, table_num = adv_passing_dict[key][0])
        else:
          dfs[key] = None
    else:
      dfs[page] = extract_pfr_table(yr, page)

  return dfs

"""#### Data Cleaning"""

def fix_team_name(team_orig: str) -> str:
    """
    Remaps team names for teams that moved or are 
    named inconsistently across sources
    Args
      - team_orig: Original team name, string
    Returns
      - team: Remapped team name, string
    """
    
    team_fix_map = {
      "STL" : "LAR",
      "SDG" : "LAC",
      "SD"  : "LAC",
      "GNB" : "GB",
      "TAM" : "TB",
      "KAN" : "KC",
      "NOR" : "NO",
      "NWE" : "NE",
      "SFO" : "SF",
      "JAC" : "JAX",
      "OAK" : "LV",
      "LVR" : "LV",
    }

    if team_orig in team_fix_map.keys():
      team = team_fix_map[team_orig]
    else:
      team = team_orig

    return team

def team_mascot(team: str) -> str:
  """
  Maps team names to team mascots

  Args:
    - team: 3-character team abbreviation

  returns:
    - Team mascot
  """

  mascot_map = {
      'ARI': 'Cardinals',
      'ATL': 'Falcons',
      'BAL': 'Ravens',
      'BUF': 'Bills',
      'CAR': 'Panthers',
      'CHI': 'Bears',
      'CIN': 'Bengals',
      'CLE': 'Browns',
      'DAL': 'Cowboys',
      'DEN': 'Broncos',
      'DET': 'Lions',
      'GB' : 'Packers',
      'HOU': 'Texans',
      'IND': 'Colts',
      'JAX': 'Jaguars',
      'KC' : 'Chiefs',
      'LAC': 'Chargers',
      'LAR': 'Rams',
      'LV' : 'Raiders',
      'MIA': 'Dolphins',
      'MIN': 'Vikings',
      'NE' : 'Patriots',
      'NO' : 'Saints',
      'NYG': 'Giants',
      'NYJ': 'Jets',
      'PHI': 'Eagles',
      'PIT': 'Steelers',
      'SEA': 'Seahawks',
      'SF' : '49ers',
      'TB' : 'Buccaneers',
      'TEN': 'Titans',
      'WAS': 'Commanders',
      '2TM': 'Multiple Teams'
  }

  return mascot_map[team]

def calc_qb_wins(starts: int, qb_record: str, season: int) -> float:
    """
    Calculate QB wins from record. Count ties as 0.5 wins
    Args:
      - qb_record: String in the format W-L-T, where W, L, and T
                               are numbers representing Wins, Losses, and Ties
    Returns:
      - wins: number of wins, float
    """

    # handle out of range data
    if starts == 0 or pd.isna(qb_record):
      return np.nan

    # Split record into components
    try:
        W_L_T = [float(value) for value in qb_record.split("-")]
    except (ValueError, AttributeError) as err:
        print(f"Could not convert component of QB record '{qb_record}' to float")
        raise err

    try:
        wins = W_L_T[0] + (W_L_T[2]*0.5)
        losses = W_L_T[1] + (W_L_T[2]*0.5)
    except IndexError as err:
        print("Wrong number of components in Win-Loss-Tie")
        raise err

    if season <= 2020:
      max_games = 16
    else:
      max_games = 17

    try:
        assert(1 <= wins + losses <= max_games)
    except AssertionError as err:
        print(f"Total games in {qb_record} outside of valid range, invalid QB record")
        raise err

    return wins

def fix_columns_v1(columns):
  new_columns = []
  for col in columns.values:
    if "Unnamed" in col[0]:
      new_columns.append(col[1])
    else:
      new_columns.append("_".join(col))
  return new_columns

def fix_columns_v2(columns):
  return [col[1] for col in columns.values]

def clean_pfr_general(df):

  # Convert all columns to lowercase
  df.columns = [x.lower() for x in df.columns]

  # Drop intermediate header rows
  df = df[(df['player'] != 'Player')]
  df = df.dropna(subset=['player'])

  # Remove extraneous text from QB name
  df['player'] = df['player'].apply(lambda x: re.sub("[*+]", "", x))

  # Standarize team names
  df['tm'] = df["tm"].apply(fix_team_name)

  return df

def clean_pfr_passing(df):
  df['pro_bowl'] = df['Player'].apply(lambda x: 1 if (x.find("*") > 0) else 0)
  df['all_pro'] = df['Player'].apply(lambda x: 1 if (x.find("+") > 0) else 0)
  df = clean_pfr_general(df)

  # convert games started to numeric
  df['gs'] = df['gs'].apply(pd.to_numeric, errors="coerce")

  # filter to non-null QB records and QBs starting at least 1 game
  df = df[(df['gs'] > 0) & df['qbrec'].notna()]

  # QB wins and win percent
  df['qb_wins'] = df.apply(lambda r: calc_qb_wins(r['gs'], r['qbrec'], r['season']), axis=1)
  df['qb_win_pct'] = 100 * (df['qb_wins'] / df['gs'])

  # Last name
  df['last_name'] = df['player'].apply(lambda x: x.split(" ")[1])

  # team mascot
  df['mascot'] = df['tm'].apply(team_mascot)

  keep_cols = ['player', 'season', 'tm', 'mascot', 'last_name', 'age', 
               'g', 'gs', 'qbrec', 'cmp', 'att', 'cmp%', 'yds', 'td', 'td%',  
               'int', 'int%', '1d', 'lng', 'y/a', 'ay/a', 'y/c', 'y/g', 'rate',   
               'sk', 'yds.1', 'sk%', 'ny/a', 'any/a', '4qc', 'gwd', 'pro_bowl', 
               'all_pro', 'qb_wins', 'qb_win_pct']

  if df['season'].loc[df.index[0]] >= 2006:
    keep_cols.append('qbr')

  df = df[keep_cols]
  return df

def clean_pfr_rushing(df):
  df.columns = fix_columns_v1(df.columns)
  df = clean_pfr_general(df)
  df = df[['player', 'tm', 'rushing_att', 'rushing_yds', 'rushing_td',  
           'rushing_1d', 'rushing_lng', 'rushing_y/a', 'rushing_y/g', 'fmb']]
  return df

def clean_pfr_air_yards(df):
  df.columns = fix_columns_v2(df.columns)
  df = clean_pfr_general(df)
  df = df[['player', 'tm', 'iay', 'iay/pa', 'cay', 'cay/cmp', 'cay/pa', 'yac', 'yac/cmp']]
  return df

def clean_pfr_accuracy(df):
  df.columns = fix_columns_v2(df.columns)
  df = clean_pfr_general(df)
  desired_cols = ['player', 'tm', 'bats', 'thawy', 'spikes', 'drops', 'drop%', 'badth', 'bad%', 'ontgt', 'ontgt%']
  actual_cols = list(set(list(df.columns)).intersection(set(desired_cols)))
  df = df[actual_cols]
  return df

def clean_pfr_pressure(df):
  df.columns = fix_columns_v2(df.columns)
  df = clean_pfr_general(df)
  df = df[['player', 'tm', 'pkttime', 'bltz', 'hrry', 'hits', 'prss', 'prss%', 'scrm', 'yds/scr']]
  return df

def clean_pfr_play_type(df):
  df.columns = fix_columns_v1(df.columns)
  df = clean_pfr_general(df)
  df = df[['player', 'tm', 'rpo_plays', 'rpo_yds', 'rpo_passatt', 'rpo_passyds', 'rpo_rushatt', 'rpo_rushyds', 'playaction_passatt', 'playaction_passyds']]
  return df

def create_clean_func_map():

  prefix = 'clean_pfr_'

  func_map = dict()

  for name, obj in inspect.getmembers(sys.modules[__name__]):
    if (inspect.isfunction(obj) and name.startswith(prefix) and obj.__module__ == __name__):
      key = name.replace(prefix,'')
      func_map[key] = obj
                                      
  return func_map

def clean_pfr_all(dfs):

  clean_dfs = dict()
  func_map = create_clean_func_map()
  for key in dfs.keys():
    if dfs[key] is not None:
      clean_dfs[key] = func_map[key](dfs[key])
    else:
      clean_dfs[key] = None

  return clean_dfs

"""#### Combine Data"""

def merge_pfr(dfs):
  merge_df = None

  for key in dfs.keys():

    if dfs[key] is not None:
      df = dfs[key]

      if merge_df is None:
        merge_df = df
      else:
        merge_df = merge_df.merge(df, 
                                  how='left', 
                                  on = ['player', 'tm'], 
                                  validate = 'one_to_one')

  merge_df = merge_df.apply(pd.to_numeric, errors="ignore")

  return merge_df

def prep_pfr_season(yr):

  # Pull data
  dfs = extract_pfr_all(yr)

  # Clean data
  clean_dfs = clean_pfr_all(dfs)

  # Combine Data
  pfr_merge_df = merge_pfr(clean_dfs)
  pfr_merge_df['season'] = yr

  return pfr_merge_df

def prep_pfr_all(yr_range):
  return pd.concat([prep_pfr_season(yr) for yr in yr_range], ignore_index=True)

"""### Salary Cap Data

Extract, clean, and combine datasets related to player and team salary cap information.

#### Data Extraction
"""

def extract_otc_table(yr):
  return pd.read_html(f"https://overthecap.com/position/quarterback/{yr}")[0]

def extract_spotrac():
  return pd.read_html("https://www.spotrac.com/nfl/cba")[0]

"""#### Data Cleaning"""

def clean_dollar_amt(amt):
  try:
    amt_clean = float(re.sub("[$,]", "", amt))
  except:
    amt_clean = np.nan
  return amt_clean

def clean_otc(df):
  out_df = df.copy()
  out_df.columns = [col.replace(" ", "_").lower() for col in out_df.columns]

  dollar_amt_cols = ["cap_number", "cash_spent"]

  for col in dollar_amt_cols:
    out_df[col] = out_df[col].apply(clean_dollar_amt)

  # Last name
  out_df['last_name'] = out_df['player'].apply(lambda x: x.split(" ")[1])

  return out_df

def clean_spotrac(df):
  out_df = df.copy()
  out_df.columns = [col.lower().replace(' ', '_') for col in out_df.columns]
  out_df['cap_maximum'] = out_df['cap_maximum'].apply(clean_dollar_amt)
  out_df = out_df[['year', 'cap_maximum']]
  return out_df

"""#### Combine Data"""

def prep_otc_season(yr):

  # Pull Data
  otc_raw_df = extract_otc_table(yr)

  # Clean Data
  otc_df = clean_otc(otc_raw_df)

  otc_df['season'] = yr

  return otc_df

def prep_cap_data(yr_range):
  otc_df = pd.concat([prep_otc_season(yr) for yr in yr_range], ignore_index=True)
  spotrac_raw_df = extract_spotrac()
  spotrac_clean_df = clean_spotrac(spotrac_raw_df)

  salary_cap_df = pd.merge(left=otc_df, 
                           right=spotrac_clean_df, 
                           how='left', 
                           left_on='season', 
                           right_on='year',
                           validate = 'one_to_one')
  
  salary_cap_df['cap_pct'] = 100 * (salary_cap_df['cap_number'] / salary_cap_df['cap_maximum'])
  salary_cap_df['cap_pct'] = salary_cap_df['cap_pct'].round(2)

  salary_cap_df = salary_cap_df[['player', 'last_name', 'team', 'season', 
                                 'cap_number', 'cash_spent', 'cap_maximum', 'cap_pct']]

  salary_cap_df.rename({'player': 'player_name'}, axis=1, inplace=True)
  
  return salary_cap_df

"""### Workflow

#### Pull All Required Years of PFR Data
"""

pfr_df = prep_pfr_all(year_range)

"""#### Pull All Required Years of Salary Cap Data"""

salary_cap_df = prep_cap_data(year_range)

"""#### Combine PFR and Salary Cap Data"""

# Initial merge attempt
merged_df1 = pd.merge(left=pfr_df,
                     right=salary_cap_df,
                     how='left',
                     left_on = ['last_name', 'mascot', 'season'],
                     right_on = ['last_name', 'team', 'season'],
                     validate = 'one_to_one',
                     indicator=True)

# Save counts of merge results
merge_check_df1 = merged_df1.groupby(['_merge']).size()

# Get PFR obs that did not link to salary cap data
left_only = merged_df1[merged_df1['_merge'] == 'left_only'][['player', 'season', 'tm']]

# Filter PFR to non-matching obs
pfr_subset_df = pd.merge(left=pfr_df,
                         right=left_only,
                         on=['player', 'season', 'tm'],
                         how='inner',
                         validate='one_to_one')

# Second attempt at merging: mismatches from first attempt only
merged_df2 = pd.merge(left=pfr_subset_df,
                      right=salary_cap_df,
                      how='left',
                      left_on = ['player', 'last_name', 'season'],
                      right_on = ['player_name', 'last_name', 'season'],
                      indicator=True)

# Filter first attempt to matches
merged_df1 = merged_df1[merged_df1['_merge'] == 'both']

# Combine results of first and second merge attempts
merged_df = pd.concat([merged_df1, merged_df2], ignore_index=True)

# Save counts of stacked merge results
merge_check_df = merged_df.groupby(['_merge']).size()

# Verify results are correct
assert(merge_check_df['left_only'] == 0)
assert(merge_check_df['both'] == merge_check_df1['left_only'] + merge_check_df1['both'])

merged_df.info(verbose=True)

"""## Data Visualization"""

sns.countplot(x="age", data=pfr_merge_df, color='#dddddd')

test = pfr_merge_df[pfr_merge_df['att'] > 100].reset_index()

zcols = ['td%', 'int%', 'qbr']


for col in zcols:
  test[f'{col}_zscore'] = stats.zscore(test[f'{col}'])

px.scatter_3d(test, x='td%_zscore', y="int%_zscore", z="qbr_zscore", color = 'player', template='plotly_dark' )