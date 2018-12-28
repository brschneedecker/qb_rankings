"""
download.py

Download HTML tables with QB season summary statistics from Pro Football
Reference and Football Outsiders and store as .csv files
"""

def get_all_seasons(bgn_yr: int, end_yr: int, base_html: str):
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

	# Generate list of years
	year_list = [year for year in range(bgn_yr, end_yr + 1)]

	# Get data for all years and store in list of DataFrames
	df_list = [pd.read_html(base_html.format(year)) for year in year_list]

	# Stack data
	df = pd.concat(df_list, ignore_index = True)

    # diagnostic prints
	df.info()
	df.head(n=10)

	# save DataFrame as .csv file
	df.to_csv(outfile)


def main():
	"""
	Download QB data for a given year range from Pro Football Reference
	and Football Outsiders and store as .csv files
	"""

	# set name of log file
	log_filename = "download.log"

	# set path to output data
	datapath = re.sub("/src", "/data/raw/{filename}", os.getcwd())

	# set up logging
	logging.basicConfig(filename=log_filename,
		                filemode="w",
						level=logging.DEBUG,
						format="%(levelname)s: %(asctime)s: %(message)s")

	logging.info("Running {}".format(re.sub(".log", ".py", log_filename)))


    # HTML path templates
    pfr_path = "https://www.pro-football-reference.com/years/{}/passing.htm"
    fo_path = "https://www.footballoutsiders.com/stats/qb{}"

    # download data
    get_all_seasons(2002,
    	            2017,
    	            pfr_path,
    	            datapath.format(filename="qb_season_pfr.csv"))

    
    get_all_seasons(2002,
    	            2017,
    	            fo_path,
    	            datapath.format(filename="qb_season_fo.csv"))

    logging.info("Program Complete")

if __name__ == "__main__":
	main()

