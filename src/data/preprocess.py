"""
preprocess.py

Read in downloaded data and clean for analysis
"""

import pandas as pandas
import logging

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


def clean_pfr(src_df):
	"""
	Clean Pro Football Reference data
	"""

	df = src_df.copy()

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

	return df


def clean_fo(src_df):
	"""
	Clean Football Outsiders data
	"""

	# rename columns
	df.columns = list(df.iloc[0,])

	# limit to columns of interest
	df = df[["Player", "DYAR", "YAR", "DVOA", "VOA", "EYds", "DPI"]]

	# remove rows with columns names
	df = df[df["Player"] != "Player"]

	# convert columns with numeric data to numeric object type
	df = df.apply(pd.to_numeric, errors="ignore")
    
    # remove extra characters so names match across years
	df["Player"] = [re.sub("[.]", "", player) for player in df["Player"]]
	
	return df


def merge_all(df_list: list):

	for df in df_list:
		logger.info("Dimensions of {}: {}".format(df.__name__, df.shape))

	# base of merged DataFrame is first DataFrame in the list
    merge_df = df_list[0]

	# merge all DataFrames in the list
	for i in range(1,len(df_list))
		merge_df = pd.merge(merge_df, df_list[i], on=["Player","year"])

	return merged_df


def main():
	"""
	Combine all data into QB-season level analytic file
	"""
	
	# set paths to input and output data
	raw_datapath = re.sub("/src/data", "/data/raw/{filename}", os.getcwd())
	processed_datapath = re.sub("/src/data", "/data/processed/{filename}", os.getcwd())

	# import data
	pfr_raw = import_data(raw_datapath.format(filename="qb_season_pfr.csv"))
	fo_raw = import_data(raw_datapath.format(filename="qb_season_fo.csv"))

	# clean data
	prf_clean = clean_pfr(pfr_raw)
	fo_clean = clean_fo(fo_raw)

	# merge data
	clean_df_list = [prf_clean, fo_clean]
	merged_df = merge_all(clean_df_list)

	# output final DataFrame to .csv file

if __name__ == "__main__":

	# set name of log file
	log_filename = "preprocess.log"

	# overwite any existing log file
	if os.path.exists(log_filename):
		os.remove(log_filename)

	# set up logger
	logging.basicConfig(filename=log_filename,
						filemode="w",
						level=logging.DEBUG,
						format="%(levelname)s: %(asctime)s: %(message)s")

	logger = logging.getLogger(__name__)

	# begin execution
	main()