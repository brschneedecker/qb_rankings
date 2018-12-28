"""
download.py

Download HTML tables with QB season summary statistics from Pro Football
Reference and Football Outsiders and store as .csv files
"""

import pandas as pd
import re
import os
import logging

def get_season(base_html: str, year: int):
	"""
	Download a single season of HTML table data and return DataFrame

	Args:
	  - base_html: String, path to page with HTML table data
	  - year: Year of data being pulled

	Returns:
	  - df: DataFrame with extracted data
	"""

	html_path = base_html.format(year=year)

	try:
		df = pd.read_html(html_path)[0]
	except Exception as err:
		logger.warning("Unsuccessful download from {}".format(html_path))
	else:
		logger.info("Download from {} complete".format(html_path))

		return df


def export_season(df, outfile: str):
	"""
	Export single season of data to .csv file
	"""

	logger.info("Creating {}".format(outfile))

	if os.path.exists(outfile):
		logger.info("{} already exists, deleting".format(outfile))
		os.remove(outfile)

	try:
		df.to_csv(outfile, index=False)
	except FileNotFoundError as err:
		logger.exception("Error saving file {}".format(outfile))
		raise err
	else:
		logger.info("{} created successfully".format(outfile))
		logger.info("Dimensions of {} are {}".format(outfile, df.shape))


def get_all_seasons(bgn_yr: int, end_yr: int, base_html: str, outfile: str):
	"""
	Get all seasons of QB data for a given range of years

	Args:
	  - bgn_yr: First year for which to download data
	  - end_yr: Last year for which to download data
	  - base_html: Template for HTML path
	  - outfile: name of exported .csv file

	Return:
	  - df: DataFrame object with downloaded data
	"""

	# Generate list of years for which to download data
	year_list = [year for year in range(bgn_yr, end_yr + 1)]

	# Get data for all years and store in list of DataFrames
	df_list = [get_season(base_html, year) for year in year_list]

	# Create list of unsuccessful downloads
	df_fail = [check for check in df_list if check is None]

	# Verify all downloads were successful
	try:
		assert(len(df_fail) == 0)
	except AssertionError as err:
		logger.exception("Missing {} datasets".format(len(df_fail)))
		raise err

	# save DataFrames as .csv files
	for i in range(0, len(df_list)):
		export_season(df_list[i], outfile.format(year=year_list[i]))
		

def main():
	"""
	Download QB data for a given year range from Pro Football Reference
	and Football Outsiders and store as .csv files
	"""

	logger.info("Starting program execution")

	# set path to output data
	datapath = re.sub("/src/data", "/data/raw/{filename}", os.getcwd())
	logger.info("Output files will be directed to {}".format(datapath))

	# HTML path templates
	pfr_path = "https://www.pro-football-reference.com/years/{year}/passing.htm"
	fo_path = "https://www.footballoutsiders.com/stats/qb{year}"

	# download Pro Football Reference data
	get_all_seasons(2002,
					2017,
					pfr_path,
					datapath.format(filename="qb_season_pfr_{year}.csv"))

	# download Football Outsiders data
	get_all_seasons(2002,
					2017,
					fo_path,
					datapath.format(filename="qb_season_fo_{year}.csv"))

	logger.info("End program execution")

if __name__ == "__main__":

	# set name of log file
	log_filename = "download.log"

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