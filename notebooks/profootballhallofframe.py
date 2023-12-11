# -*- coding: utf-8 -*-
"""
# Pro Football Hall of Fame

## Setup
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

"""## Data Prep

### Extract and Clean Position Reference Data
"""

def extract_pos_ref():
  out_df = pd.read_html("https://www.pro-football-reference.com/about/positions.htm")[0]
  out_df.columns = [col.lower() for col in out_df.columns]
  return out_df

def clean_pos_ref(df):
  out_df = df.copy()
  out_df.rename({'meaning': 'pos_name'}, axis=1, inplace=True)
  return out_df

"""### Extract and Clean Hall of Fame Data"""

def extract_hof():
  out_df = pd.read_html("https://www.pro-football-reference.com/hof/index.htm")[0]
  out_df.columns = [_[1].lower() for _ in out_df.columns.values]
  return out_df

def clean_hof(df):
  out_df = df.copy()
  out_df = out_df[['player','pos','indct','from','to','ap1','pb','st','wav']]
  out_df['wait_time'] = out_df['indct'] - out_df['to']
  out_df['years_active'] = out_df.apply(lambda r: range(r['from'], r['to']), axis=1)
  return out_df

"""### Extract and Clean Hall of Fame Monitor Data"""

def extract_hof_monitor(pos):
  out_df = pd.read_html(f"https://www.pro-football-reference.com/hof/hofm_{pos}.htm")[0]
  out_df.columns = [_[1].lower() for _ in out_df.columns.values]
  out_df['pos'] = pos
  return out_df

def clean_hof_monitor(df):
  out_df = df.copy()

  # Drop intermediate header rows
  out_df = out_df[(out_df['player'] != 'Player')]
  out_df = out_df.dropna(subset=['player'])

  out_df = out_df[['player','pos','hofm','chmp','from','to','ap1','pb','wav']]
  return out_df

def combine_hof_monitor():
  positions = ['QB', 'RB' ,'WR', 'TE', 'G', 'T', 'C', 'DT', 'DE', 'ILB', 'OLB', 'DB', 'K', 'P']
  dfs = [clean_hof_monitor(extract_hof_monitor(pos)) for pos in positions]
  out_df = pd.concat(dfs).reset_index()
  return out_df

"""### Combine Data Sources"""

def find_column_overlap(hof_df, hofm_df):
  remove = {'player', 'pos'}
  hof_cols = set(hof_df.columns).difference(remove)
  hofm_cols = set(hofm_df.columns).difference(remove)
  return hof_cols.intersection(hofm_cols)

def rename_overlap_cols(df, overlap, suffix):
  rename_dict = {col:f"{col}_{suffix}" for col in overlap}
  out_df = df.rename(rename_dict, axis=1)
  return out_df

def combine_hof_hofm(hof_df, hofm_df):

  # Rename overlapping column names with suffix
  overlap = find_column_overlap(hof_df, hofm_df)
  hof_rename = rename_overlap_cols(hof_df, overlap, "hof")
  hofm_rename = rename_overlap_cols(hofm_df, overlap, "hofm")

  # Merge
  merge_df = pd.merge(left=hof_rename,
                      right=hofm_rename,
                      how='outer',
                      on=['player', 'pos'],
                      # validate="one_to_one",
                      indicator=True)

def combine_hof_pos_ref(hof_df, pos_df):

  # merge datasets
  merged_df = pd.merge(left=hof_df,
                       right=pos_df,
                       how='left',
                       on=['pos'],
                       indicator=True,
                       validate='many_to_one')

  # verify all Hall of Fame records map to a position name
  merge_check = merged_df.groupby(['_merge']).size()
  assert(merge_check['left_only'] == 0)

  merged_df.drop('_merge', axis=1, inplace=True)

  return merged_df

"""### Data Prep Workflow"""

def data_prep():

  # Pull Data
  hof_df = clean_hof(extract_hof())
  hofm_df = combine_hof_monitor()
  pos_ref_df = clean_pos_ref(extract_pos_ref())

  # Combine HoF and HoFm
  hof_comb_df = combine_hof_hofm(hof_df, hofm_df)

  # Add reference info
  add_ref_info_df = combine_hof_pos_ref(hof_comb_df, pos_ref_df)

  return add_ref_info_df

df = data_prep()

df.info(verbose=True)

"""## Analysis

### Count of Hall of Fame Inductees by Position
"""

count_by_pos_df = df.groupby(['pos_name'], as_index=False).size().sort_values('size', ascending=False)

sns.set_theme(style="whitegrid")

# Initialize the matplotlib figure
f, ax = plt.subplots(figsize=(10, 10))

# Plot the total crashes
sns.set_color_codes("deep")
sns.barplot(x="size",
            y="pos_name",
            data=count_by_pos_df,
            label="Count",
            color="b")

# Add an informative axis label
ax.set(ylabel="Position",
       xlabel="Count of Hall of Fame Inductees")

sns.despine(left=True, bottom=True)

"""### Count Active Hall of Famers by Year and Position"""

sns.set_theme(style="ticks")

# Make one record per year played for each player
explode_df = (df[['player', 'pos', 'years_active']]
              .explode('years_active')
              .rename({'years_active': 'year'}, axis=1, inplace=False))

explode_df = explode_df[explode_df['year'] >= 1966]

# Count players active in each year
active_by_year_df = (explode_df.groupby(['pos', 'year'], as_index=False).size()
                               .sort_values(['pos', 'year'])
                               .rename({'pos': 'Position', 'size': 'player_count'}, axis=1, inplace=False))


# Initialize a grid of plots with an Axes for each walk
grid = sns.FacetGrid(active_by_year_df,
                     col="Position",
                     hue="Position",
                     palette="tab20c",
                     col_wrap=6,
                     height=3)

# Draw a horizontal line to show the starting point
grid.refline(y=0, linestyle=":")

# Draw a line plot to show the trajectory of each random walk
grid.map(plt.plot, "year", "player_count", marker="o")

# Adjust the tick positions and labels
grid.set(xticks=[1970, 1980, 1990, 2000, 2010, 2020], yticks=[0, 5, 10, 15, 20])

# Adjust the arrangement of the plots
# grid.fig.tight_layout(w_pad=1)

"""## Testing"""