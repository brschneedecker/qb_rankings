"""
qb_compare_plot.py

Create plots to compare QBs
"""


def make_comp_plot(player_name: str, column_name: str, qb_data, plot_path: str):
	"""
	Given a specific player, a dataset with QB data, and a column
	name create a plot showing the values of the column for the
	selected player and the average values of the column for 
	all other players

	Args:
	  player_name: Name of the player to compare to averages
	  column_name: Column name of statistic to plot
	  qb_data: DataFrame with data to plot
	  plot_path: string representing directory to save plots

	Returns:
	  no objects returned

	Makes: Image file with name "[player_name] [column_name].png" 
	"""

	df = qb_data.copy()

	# get selected stat for selected player
	player_df = df[df["Player"] == player_name]
	player_df = player_df[["Player", "year", column_name]]

	# get years player was active
	min_yr = player_df['year'].min()
	max_yr = player_df['year'].max()

	# get averages excluding selected player
	other_df = df[df["Player"] != player_name]
	other_df = other_df[other_df["year"].isin(range(min_yr, max_yr+1))]
	other_df = other_df[["year", column_name]].groupby(["year"], as_index=False).mean()

	# create name of plot
	plot_name = "{} {}.png".format(player_name, column_name)
	plot_name = re.sub("/", "per", plot_name)

	pylab.title("{} vs. Everybody".format(player_name))
	pylab.xlabel("Year")
	pylab.ylabel(column_name)
	pylab.plot(other_df["year"], other_df[column_name], label = "All others")
	pylab.plot(player_df["year"], player_df[column_name], label = player_name)
	pylab.legend(loc='upper right')
	pylab.savefig(plot_path + "/" + plot_name)
	pylab.close()


def multiplayer_comp_plot(player_list: list, column_name: str, qb_data, plot_path: str):
	"""
	Takes a list of players, a column name and a dataset with QB data
	as input. Makes a plot with a line for each player's values
	for the select column
	Args:
	  player_list: List of player names to compare stats
	  column_name: Column name of statistic to plot
	  qb_data: DataFrame with data to plot
	  plot_path: string representing directory to save plots

	Returns:
	  no objects returned

	Makes: Image file with name "Compare [column_name] Across Players.png" 
	"""

	df = qb_data.copy()

	# create name of plot
	plot_name = "Compare {} Across Players".format(column_name)
	plot_name = re.sub("/", "per", plot_name)

	pylab.title(plot_name)
	pylab.xlabel("Year")
	pylab.ylabel(column_name)

	for player in player_list:
		player_df = df[df["Player"] == player]
		pylab.plot(player_df["year"], player_df[column_name], label = player)

	pylab.legend(loc='upper right')
	pylab.savefig(plot_path + "/" + plot_name + ".png")
	pylab.close()

def main():
	players = ["EManning",
	           "PRivers",
	           "BRoethlisberger"]

	plot_cols = ["Y/A", "Y/G", "Rate", "QBR", "ANY/A", "TD%", "Int%", "DYAR"]
    
	# set path to output plot
	plot_path = re.sub("/programs", "/graphs", os.getcwd())
	logging.info("Plots will be saved to {}".format(plot_path))

	for col in plot_cols:

		multiplayer_comp_plot(players, col, df, plot_path)

		for player in players:
			try:
			    make_comp_plot(player, col, df, plot_path)
			except:
				logging.error("Plot creation failed for {}, {}".format(player, col))
			else:
				logging.info("Making plot for {}, {}".format(player, col))


if __name__ == "__main__":
	main()