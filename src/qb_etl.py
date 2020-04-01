"""
This program downloads and combines NFL quarterback data from
multiple sources and outputs a .csv file with the final data

Data is read from the following sources:
  - Pro Football Reference
  - Football Outsiders
  - Over The Cap

External Crosswalks used are:
  - data/external/team_name_xwalk.csv
  - data/external/elite_system_fraud.csv
"""

import pandas as pd
import logging
import os
import re
import glob
import click
import datetime


def download_season(base_html: str, year: int):
    """
    Download a single season of HTML table data and return DataFrame

    Args:
      - base_html: String, path to page with HTML table data
      - year: Year of data being pulled

    Returns:
      - df: DataFrame with extracted data
    """

    logger = logging.getLogger(__name__)

    html_path = base_html.format(year=year)

    try:
        df = pd.read_html(html_path)[0]
    except Exception as err:
        logger.warning("Unsuccessful download from {}".format(html_path))
        raise err
    else:
        logger.info("Download from {} complete".format(html_path))

        return df


def import_data(filepath: str):
    """
    Import data from .csv

    Args:
      - filepath: Path of file to import

    Returns:
      - df: Imported DataFrame
    """

    logger = logging.getLogger(__name__)

    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError as err:
        logger.exception("{} not found".format(filepath))
        raise err
    else:
        logger.info("Read-in of {} was successful".format(filepath))
        return df


def fix_team_name(team_orig: str) -> str:
    """
    Remaps team names for teams that moved

    Args
      - team_orig: Original team name, string

    Returns
      - team: Remapped team name, string
    """
    if team_orig == "STL":
        team = "LAR"
    elif team_orig == "SDG":
        team = "LAC"
    else:
        team = team_orig
    return team


def fix_player_name(full_name: str) -> str:
    """
    Remaps player names to [first initial].[last name]

    Args:
      - full_name: first and last name of player, string

    Returns:
      - first_initial_last_name: Player name reformated as first initial
                                                             and last name
    """

    # split player first and last name into a list
    first_last = full_name.split(" ")

    # update first name to first initial
    first_last[0] = first_last[0][0]

    # combine first initial and last name into single string
    first_initial_last_name = "".join(first_last)

    return first_initial_last_name


def calc_qb_wins(qb_record: str) -> float:
    """
    Calculate QB wins from record. Count ties as 0.5 wins

    Args:
      - qb_record: String in the format W-L-T, where W, L, and T
                               are numbers representing Wins, Losses, and Ties

    Returns:
      - wins: number of wins, float
    """

    logger = logging.getLogger(__name__)

    try:
        W_L_T = [float(value) for value in qb_record.split("-")]
    except ValueError as err:
        logger.exception("Could not convert component of QB record to float")
        raise err

    try:
        wins = W_L_T[0] + (W_L_T[2]*0.5)
        losses = W_L_T[1] + (W_L_T[2]*0.5)
    except IndexError as err:
        logger.exception("Wrong number of components in Win-Loss-Tie")
        raise err

    try:
        assert(1 <= wins + losses <= 16)
    except AssertionError as err:
        logger.exception(
            "Total games in {} outside of valid range, invalid QB record".format(qb_record))
        raise err

    return wins


def extract_season_pfr(year: int):
    """
    Extract and clean a single season of Pro Football Reference data

    Args:
      - year: integer representing year of data being cleaned

    Returns:
      - df: Cleaned Pro Football Reference data
    """

    logger = logging.getLogger(__name__)

    pfr_path = "https://www.pro-football-reference.com/years/{year}/passing.htm"

    df = download_season(pfr_path, year)

    logger.info("Dimensions of {} raw PFR DataFrame: {}".format(year, df.shape))
    logger.info("Columns on {} raw PFR DataFrame: {}".format(year, df.columns))

    # drop interior header rows and restrict to starting QBs
    df = df.loc[(df["Tm"] != "Tm") & (df["Pos"] == "QB")]

    # fix team names for teams that moved
    df["team"] = [fix_team_name(team) for team in df["Tm"]]

    # calculate QB wins
    df["qb_wins"] = [calc_qb_wins(record) for record in df["QBrec"]]

    # remove extra characters so names match across years
    df["Player"] = [re.sub("[*+]", "", player) for player in df["Player"]]

    # fix player names to match Football Outsiders format
    df["PlayerReformat"] = [fix_player_name(player) for player in df["Player"]]

    #df = df

    df = df.rename(index=str, columns={
        "PlayerReformat": "player",
        "Player": "player_full_name",
        "4QC": "fourth_qtr_comebacks",
        "ANY/A": "adj_net_yds_per_att",
        "AY/A": "adj_yds_per_att",
        "Age": "age",
        "Att": "att",
        "Cmp": "cmp",
        "Cmp%": "cmp_pct",
        "G": "games",
        "GS": "games_started",
        "GWD": "game_winning_drives",
        "Int": "int",
        "Int%": "int_pct",
        "NY/A": "net_yds_per_att",
        "Rate": "qb_rating",
        "Sk": "sacks",
        "Sk%": "sack_pct",
        "Yds.1": "sack_yds",
        "TD": "td",
        "TD%": "td_pct",
        "Y/A": "yds_per_att",
        "Y/C": "yds_per_cmp",
        "Y/G": "yds_per_game",
        "Yds": "yds"
    }).drop(["Rk", "Tm", "Pos", "QBrec"], axis=1)

    # convert columns with numeric data to numeric object type
    df = df.apply(pd.to_numeric, errors="ignore")

    logger.info("Dimensions of cleaned PFR DataFrame: {}".format(df.shape))
    logger.info("Columns on cleaned PFR DataFrame: {}".format(df.columns))

    return df


def extract_season_fo(year: int):
    """
    Extract and clean a single season of Football Outsiders data

    Args:
      - year: integer representing year of data being cleaned

    Returns:
      - df: Cleaned Football Outsiders data
    """

    logger = logging.getLogger(__name__)

    fo_path = "https://www.footballoutsiders.com/stats/qb{year}"

    df = download_season(fo_path, year)

    logger.info("Dimensions of {} raw FO DataFrame: {}".format(year, df.shape))
    logger.info("Columns on {} raw FO DataFrame: {}".format(year, df.columns))

    # rename columns
    if list(df.columns)[0] != "Player":
        df.columns = list(df.iloc[0, ])
        logger.info(
            "Columns on {} FO DataFrame after rename: {}".format(year, df.columns))
    else:
        logger.info("Columns were not renamed")

    # remove rows with columns names
    df = df.loc[df["Player"] != "Player"]

    # remove % symbol from DVOA and VOA so values convert to numeric
    df["DVOA"] = [re.sub("[%]", "", value) for value in df["DVOA"]]
    df["VOA"] = [re.sub("[%]", "", value) for value in df["VOA"]]

    # split DPI into two columns: dpi_count and dpi_yards
    df["dpi_count"] = [value.split("/")[0] for value in df["DPI"]]
    df["dpi_yards"] = [value.split("/")[1] for value in df["DPI"]]

    # remove extra characters so names match across years
    df["Player"] = [re.sub("[.]", "", player) for player in df["Player"]]

    # Rename columns
    df = df.rename(index=str, columns={
        "Player": "player",
        "Team": "team",
        "EYds": "efctv_yds"
    })

    # limit to columns of interest
    df = df[["player",
             "team",
             "DYAR",
             "YAR",
             "DVOA",
             "VOA",
             "efctv_yds",
             "dpi_count",
             "dpi_yards"]]

    # convert columns with numeric data to numeric object type
    df = df.apply(pd.to_numeric, errors="ignore")

    logger.info("Dimensions of cleaned FO DataFrame: {}".format(df.shape))
    logger.info("Columns on cleaned FO DataFrame: {}".format(df.columns))

    return df


def extract_season_otc(year: int):
    """
    Extract and clean a single season of Over The Cap data

    Args:
      - year: integer representing year of data being cleaned

    Returns:
      - df: Cleaned Over The Cap data
    """

    logger = logging.getLogger(__name__)

    otc_path = "https://overthecap.com/position/quarterback/{year}/"

    df = download_season(otc_path, year)

    logger.info("Dimensions of {} raw OTC DataFrame: {}".format(year, df.shape))
    logger.info("Columns on {} raw OTC DataFrame: {}".format(year, df.columns))

    # import team name crosswalk
    xwalk_df = import_data("data/external/team_name_xwalk.csv")

    # merge crosswalk to get standardized team name for later merges
    df = pd.merge(df, xwalk_df, how="left", left_on="Team", right_on="mascot")

    # find a way to print this to log
    team_map = df[["Team", "team"]].drop_duplicates()

    # fix player names to match Football Outsiders format
    df["player"] = [fix_player_name(player) for player in df["Player"]]

    # remove [$,] symbols from Salary Cap Value for conversion to numeric
    df["salary_cap_value"] = [re.sub("[$,]", "", value)
                              for value in df["Salary Cap Value"]]

    # limit to desired columns
    df = df[["player", "team", "salary_cap_value"]]

    # get row with maximum salary within a given player-team-year combo
    df = df.groupby(["player", "team"], as_index=False)[
        "salary_cap_value"].max()

    # convert columns with numeric data to numeric object type
    df = df.apply(pd.to_numeric, errors="ignore")

    logger.info("Dimensions of cleaned OTC DataFrame: {}".format(df.shape))
    logger.info("Columns on cleaned OTC DataFrame: {}".format(df.columns))

    return df


def extract_season_all(year: int):
    """
    Extract, clean, and combine data for a single season

    Args:
      - pfr_df: Pro football reference data for a single year
      - fo_df: Football Outsiders data for a single year
      - otc_df: Over the Cap data for a single year

    Returns:
      - merged_df: Single season of QB data, all sources merged
    """

    logger = logging.getLogger(__name__)

    pfr_df = extract_season_pfr(year)
    fo_df = extract_season_fo(year)
    otc_df = extract_season_otc(year)

    merged_df = pd.merge(pfr_df, fo_df, how="left", on=["player", "team"])

    pfr_fo_rows = merged_df.shape[0]

    try:
        assert(pfr_df.shape[0] == pfr_fo_rows)
    except AssertionError as err:
        logger.exception("Record count changed after PFR-FO merge")
        raise err

    merged_df = pd.merge(merged_df, otc_df, how="left", on=["player", "team"])

    pfr_fo_otc_rows = merged_df.shape[0]

    try:
        assert(pfr_fo_rows == pfr_fo_otc_rows)
    except AssertionError as err:
        logger.exception("Record count changed after PFR-FO-OTC merge")
        raise err

    # import, prep, and merge elite-system-fraud finder file
    esf_df = import_data("data/external/elite_system_fraud.csv")
    esf_df["player"] = [fix_player_name(name) for name in esf_df["player"]]
    merged_df = pd.merge(merged_df, esf_df, how="left", on=["player"])

    try:
        assert(pfr_fo_otc_rows == merged_df.shape[0])
    except AssertionError as err:
        logger.exception("Record count changed after PFR-FO-OTC-ESF merge")
        raise err

    merged_df["year"] = year

    # Reorder columns
    merged_df = merged_df[["player",
        "player_full_name",
        "year",
        "team",
        "age",
        "games",
        "games_started",
        "qb_wins",
        "att",
        "cmp",
        "cmp_pct",
        "yds",
        "yds_per_game",
        "yds_per_att",
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
        "fraud"]]

    return merged_df


def get_all_seasons(bgn_yr: int, end_yr: int):
    """
    Extract, clean, and combine data for all seasons between start and end year

    Args:
      - bgn_yr: Lower bound of range of seasons to extract
      - end_yr: Upper bound of range of seasons to extract

    Returns: DataFrame with all seasons of data between begin and end year
    """
    return pd.concat([extract_season_all(year) for year in range(bgn_yr, end_yr + 1)], ignore_index=True)


def output_analytic(src_df, outfile: str):
    """
    Output analytic file DataFrame as a .csv file

    Args:
      - src_df: DataFrame to export

    Returns:
      - outfile: filepath of exported file
    """

    logger = logging.getLogger(__name__)

    try:
        src_df.to_csv(outfile, index=False)
    except FileNotFoundError as err:
        logger.exception("Error saving file {}".format(outfile))
        raise err
    else:
        logger.info("{} created successfully".format(outfile))


@click.command()
@click.argument('bgn_yr')
@click.argument('end_yr')
@click.argument('outfile', type=click.Path())
def main(bgn_yr, end_yr, outfile):
    """
    Combine all data into QB-season level analytic file

    Args:
      - outfile: Name of cleaned analytic file

    Returns: none
    """

    df = get_all_seasons(bgn_yr, end_yr)
    output_analytic(df, outfile)


if __name__ == "__main__":

    # All directories in program are relative to repo root directory
    # Verify current working directory is repo root directory before proceeding
    try:
        assert os.getcwd().split(os.sep)[-1] == "qb_rankings"
    except AssertionError as err:
        print("Working directory incorrect")
        print("Programs must be run with working directory set to 'qb_rankings'")
        raise err

    logging.basicConfig(filename="logs/qb_etl_{:%Y-%m-%d_%H:%M:%S}.log".format(datetime.datetime.now()),
                        filemode="w",
                        level=logging.DEBUG,
                        format="%(levelname)s: %(asctime)s: %(message)s")

    main()