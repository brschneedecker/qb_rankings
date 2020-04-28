"""
This program downloads and combines NFL quarterback data from
multiple sources loads to a SQLite database

Data is read from the following sources:
  - Pro Football Reference
  - Football Outsiders
  - Over The Cap
"""

import pandas as pd
import logging
import os
import re
import click
import datetime
import qbconfig
import db_util


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
    Remaps team names for teams that moved or are 
    named inconsistently across sources

    Args
      - team_orig: Original team name, string

    Returns
      - team: Remapped team name, string
    """
    if team_orig == "STL":
        team = "LAR"
    elif team_orig == "SDG" or team_orig == "SD":
        team = "LAC"
    elif team_orig == "GNB":
        team = "GB"
    elif team_orig == "TAM":
        team = "TB"
    elif team_orig == "KAN":
         team = "KC"
    elif team_orig == "NOR":
        team = "NO"
    elif team_orig == "NWE":
        team = "NE"
    elif team_orig == "SFO":
        team = "SF"
    elif team_orig == "JAC":
        team = "JAX"
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

    # update first name to first initial(s)
    if first_last[0].find(".") != -1 or (len(first_last[0]) == 2 and first_last[0].isupper()):
        first_last[0] = first_last[0].replace(".","")
    else:        
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


def standardize_season(df, columns):
    """
    Standardize column values within a season
    """

    new_df = df.copy()

    for col in columns:
        mean = new_df[col].mean()
        std = new_df[col].std()
        newcol = col + "_stdize"

        new_df[newcol] = (new_df[col] - mean) / std

    return new_df


def scale_for_display(df, columns):
    """
    Rescale standardized values for display
    multiply by the overall SD and add the overall mean.
    """

    new_df = df.copy()

    for col in columns:
        mean = new_df[col].mean()
        std = new_df[col].std()
        newcol = col + "_scaled"
        stdcol = col + "_stdize"
        new_df[newcol] = (new_df[stdcol] * std) + mean

    return new_df


def extract_season_pfr(year: int):
    """
    Extract and clean a single season of Pro Football Reference data

    Args:
      - year: integer representing year of data being cleaned

    Returns:
      - df: Cleaned Pro Football Reference data
    """

    logger = logging.getLogger(__name__)

    df = download_season(qbconfig.pfr_base_html, year)

    logger.info("Dimensions of {} raw PFR DataFrame: {}".format(year, df.shape))
    logger.info("Columns on {} raw PFR DataFrame: {}".format(year, df.columns))

    # drop interior header rows and restrict to starting QBs
    df = df.loc[(df["Tm"] != "Tm") & (df["Pos"] == "QB")]

    # fix team names for teams that moved or are inconsistent across sources
    df["team"] = [fix_team_name(team) for team in df["Tm"]]

    # calculate QB wins
    df["qb_wins"] = [calc_qb_wins(record) for record in df["QBrec"]]

    # remove extra characters so names match across years
    df["Player"] = [re.sub("[*+]", "", player) for player in df["Player"]]

    # fix player names to match Football Outsiders format
    df["PlayerReformat"] = [fix_player_name(player) for player in df["Player"]]

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

    df = download_season(qbconfig.fo_base_html, year)

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

    # fix team names for teams that moved or are inconsistent across sources
    df["team"] = [fix_team_name(team) for team in df["Team"]]

    # remove % symbol from DVOA and VOA so values convert to numeric
    df["DVOA"] = [re.sub("[%]", "", value) for value in df["DVOA"]]
    df["VOA"] = [re.sub("[%]", "", value) for value in df["VOA"]]

    # split DPI into two columns: dpi_count and dpi_yards
    df["dpi_count"] = [value.split("/")[0] for value in df["DPI"]]
    df["dpi_yards"] = [value.split("/")[1] for value in df["DPI"]]

    # remove extra characters so names match across years
    df["player"] = [re.sub("[. ]", "", player) for player in df["Player"]]

    # Rename columns
    df = df.rename(index=str, columns={"EYds": "efctv_yds"})

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

    df = download_season(qbconfig.otc_base_html, year)

    logger.info("Dimensions of {} raw OTC DataFrame: {}".format(year, df.shape))
    logger.info("Columns on {} raw OTC DataFrame: {}".format(year, df.columns))

    # import team name crosswalk
    xwalk_df = import_data(qbconfig.team_name_xwalk)

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
    esf_df = import_data(qbconfig.esf_xwalk)
    esf_df["player"] = [fix_player_name(name) for name in esf_df["player"]]
    merged_df = pd.merge(merged_df, esf_df, how="left", on=["player"])

    try:
        assert(pfr_fo_otc_rows == merged_df.shape[0])
    except AssertionError as err:
        logger.exception("Record count changed after PFR-FO-OTC-ESF merge")
        raise err

    merged_df["year"] = year

    return merged_df


def get_all_seasons(bgn_yr: int, end_yr: int):
    """
    Extract, clean, and combine data for all seasons between start and end year

    Args:
      - bgn_yr: Lower bound of range of seasons to extract
      - end_yr: Upper bound of range of seasons to extract

    Returns: DataFrame with all seasons of data between begin and end year
    """

    columns_to_rescale = ["yds_per_game", "yds_per_att"]

    df_list = [extract_season_all(year) for year in range(bgn_yr, end_yr + 1)]
    df_list = [standardize_season(df, columns_to_rescale) for df in df_list]

    df = pd.concat(df_list, ignore_index=True)
    
    df = scale_for_display(df, columns_to_rescale)

    # Reorder columns
    df = df[["player",
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
        "fraud"]]

    return df


def load_seasons_to_db(df, db_file: str, tbl_name: str):
    """
    Load extracted QB seasons to database

    Args:
      - df: DataFrame to load to the database table
      - db_file: Database file to load to
      - tbl_name: Name of table where data will be loaded

    Returns: None
    """

    logger = logging.getLogger(__name__)

    conn = db_util.create_connection(qbconfig.db_file)
    
    try:
        df.to_sql(tbl_name, con=conn, if_exists='append', index=False)
    except Exception as err:
        logger.exception("Unable to load records to QB season table")
        raise err
    finally:
        conn.close()
        

@click.command()
@click.argument('bgn_yr')
@click.argument('end_yr')
def main(bgn_yr, end_yr):
    """
    Combine all data into QB-season level analytic file

    Args:
      - outfile: Name of cleaned analytic file

    Returns: none
    """

    logger = logging.getLogger(__name__)

    try:
        bgn_yr_int = int(bgn_yr)
        end_yr_int = int(end_yr)
    except ValueError as err:
        logger.exception("Invalid begin year or end year parameter {}, {}".format(bgn_yr, end_yr))
        raise err

    df = get_all_seasons(bgn_yr_int, end_yr_int)

    load_seasons_to_db(df, qbconfig.db_file, "qb_season")


if __name__ == "__main__":

    # All directories in program are relative to repo root directory
    # Verify current working directory is repo root directory before proceeding
    try:
        assert os.getcwd().split(os.sep)[-1] == "qb_rankings"
    except AssertionError as err:
        print("Working directory incorrect")
        print("Programs must be run with working directory set to 'qb_rankings'")
        raise err

    logging.basicConfig(filename=qbconfig.etl_log.format(datetime.datetime.now()),
                        filemode="w",
                        level=logging.DEBUG,
                        format="%(levelname)s: %(asctime)s: %(message)s")

    main()