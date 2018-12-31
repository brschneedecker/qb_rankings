"""
preprocess.py

Read in downloaded data and clean for analysis
"""

import pandas as pd
import logging
import os
import re
import glob
import click

def import_data(filepath: str):
	"""
	Import data from .csv
	"""
	try:
		df = pd.read_csv(filepath)
	except FileNotFoundError as err:
		logger.info("{} not found".format(filepath))
		raise err
	else:
		logger.info("Read-in of {} was successful".format(filepath))
		return df


def fix_team_name(row):
	"""
	Remaps team names for teams that moved
	"""
	if row["Tm"] == "STL":
		team = "LAR"
	elif row["Tm"] == "SDG":
		team = "LAC"
	else:
		team = row["Tm"]
	return team


def fix_player_name(row):
	"""
	Remaps player names to [first initial].[last name]
	"""

	# split player first and last name into a list
	first_last = row["Player"].split(" ")

	# update first name to first initial
	first_last[0] = first_last[0][0]

	# combine first initial and last name into single string
	first_initial_last_name = "".join(first_last)

	return first_initial_last_name


def clean_pfr(src_df, year: int):
	"""
	Clean Pro Football Reference data

	Args:
	  - src_df: Raw Pro Football Reference data

	Returns:
	  - df: Cleaned Pro Football Reference data
	"""

	df = src_df.copy()
	logger.info("Dimensions of {} raw PFR DataFrame: {}".format(year, df.shape))
	logger.info("Columns on {} raw PFR DataFrame: {}".format(year, df.columns))

	# drop interior header rows
	df = df[df["Tm"] != "Tm"]

	# Restrict to primary starting QBs
	df = df[df["Pos"] == "QB"]

	# convert columns with numeric data to numeric object type
	df = df.apply(pd.to_numeric, errors="ignore")

	# fix team names for teams that moved
	df["Tm"] = df.apply(fix_team_name, axis = 1)

	# remove extra characters so names match across years
	df["Player"] = [re.sub("[*+]", "", player) for player in df["Player"]]

	# fix player names to match Football Outsiders format
	df["Player"] = df.apply(fix_player_name, axis = 1)

	# add column for year
	df["year"] = year

	logger.info("Dimensions of cleaned PFR DataFrame: {}".format(df.shape))
	logger.info("Columns on cleaned PFR DataFrame: {}".format(df.columns))

	return df


def clean_fo(src_df, year: int):
	"""
	Clean Football Outsiders data

	Args:
	  - src_df: Raw Football Outsiders data

	Returns:
	  - df: Cleaned Football Outsiders data
	"""

	df = src_df.copy()
	logger.info("Dimensions of {} raw FO DataFrame: {}".format(year, df.shape))
	logger.info("Columns on {} raw FO DataFrame: {}".format(year,df.columns))

	# rename columns
	if list(df.columns)[0] != "Player":
		df.columns = list(df.iloc[0,])
		logger.info("Columns on {} FO DataFrame after rename: {}".format(year, df.columns))
	else:
		logger.info("Columns were not renamed")

	# limit to columns of interest
	df = df[["Player", "DYAR", "YAR", "DVOA", "VOA", "EYds", "DPI"]]

	# remove rows with columns names
	df = df[df["Player"] != "Player"]

	# convert columns with numeric data to numeric object type
	df = df.apply(pd.to_numeric, errors="ignore")
	
	# remove extra characters so names match across years
	df["Player"] = [re.sub("[.]", "", player) for player in df["Player"]]

	# add column for year
	df["year"] = year

	logger.info("Dimensions of cleaned FO DataFrame: {}".format(df.shape))
	logger.info("Columns on cleaned FO DataFrame: {}".format(df.columns))
	
	return df

def clean_stack(clean_func, file_pattern: str):
	"""
	Clean yearly files and stack into aggregate file
	"""

	# get list of files to import
	raw_files = glob.glob(file_pattern)

	# loop through PFR files to import and clean
	clean_list = []
	for file in raw_files:
		raw_df = import_data(file)
		clean_df = clean_func(raw_df, file[-8:-4])
		clean_list.append(clean_df)

	clean_stack = pd.concat(clean_list, ignore_index=True)

	return clean_stack


def merge_all(df_list: list):
	"""
	Merge a list of QB-season level DataFrames

	Args:
	  - df_list: List of QB-season level DataFrames to merge

	Returns:
	  - merged_df: Merged DataFrame at the QB-season level
	"""

	for df in df_list:
		logger.info("Dimensions of input DataFrame".format(df.shape))

	# base of merged DataFrame is first DataFrame in the list
	merged_df = df_list[0]

	# merge all DataFrames in the list
	for i in range(1,len(df_list)):
		merged_df = pd.merge(merged_df, df_list[i], on=["Player","year"])
		logger.info("Dimensions of DataFrame after merge {}: {}".format(i, df.shape))

	logger.info("Dimensions of final merged DataFrame: {}".format(merged_df.shape))

	return merged_df


def output_analytic(src_df, outfile: str):
	"""
	Output analytic file DataFrame as a .csv file
	"""
	try:
		src_df.to_csv(outfile, index=False)
	except FileNotFoundError as err:
		logger.exception("Error saving file {}".format(outfile))
		raise err
	else:
		logger.info("{} created successfully".format(outfile))


@click.command()
@click.argument('outfile', type=click.Path())
def main(outfile):
	"""
	Combine all data into QB-season level analytic file

	Args:
	  - outfile: Name of cleaned analytic file

	Returns: none
	"""

	# import raw data, clean, and stack
	pfr_clean = clean_stack(clean_pfr, "data/raw/qb_season_pfr*.csv")
	fo_clean = clean_stack(clean_fo, "data/raw/qb_season_fo*.csv")

	# merge data
	clean_df_list = [pfr_clean, fo_clean]
	merged_df = merge_all(clean_df_list)

	# output final DataFrame to .csv file
	output_analytic(merged_df, outfile)


if __name__ == "__main__":

	# All directories in program are relative to repo root directory
	# Verify current working directory is repo root directory before proceeding
	try:
		assert os.getcwd().split(os.sep)[-1] == "qb_rankings"
	except AssertionError as err:
		print("Working directory incorrect")
		print("Programs must be run with working directory set to 'qb_rankings'")
		raise err

	# set name of log file
	log_filename = "src/data/preprocess.log"

	# overwite any existing log file
	if os.path.exists(log_filename):
		print("Overwriting log {}".format(log_filename))
		os.remove(log_filename)

	# set up logger
	logging.basicConfig(filename=log_filename,
						filemode="w",
						level=logging.DEBUG,
						format="%(levelname)s: %(asctime)s: %(message)s")

	logger = logging.getLogger(__name__)

	main()