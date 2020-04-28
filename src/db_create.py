""" This program creates a database for storing QB data """

import click
import logging
import os
import datetime
import db_util
import qbconfig

@click.command()
def main():
 
    logger = logging.getLogger(__name__)

    sql_create_qb_season_table = """ CREATE TABLE IF NOT EXISTS qb_season (
                                        player                  TEXT NOT NULL,
                                        player_full_name        TEXT NOT NULL,
                                        year                    INTEGER NOT NULL,
                                        team                    TEXT NOT NULL,
                                        age                     INTEGER NOT NULL,
                                        games                   INTEGER NOT NULL,
                                        games_started           INTEGER NOT NULL,
                                        qb_wins                 REAL NOT NULL,
                                        att                     INTEGER NOT NULL,
                                        cmp                     INTEGER NOT NULL,
                                        cmp_pct                 REAL NOT NULL,
                                        yds                     INTEGER NOT NULL,
                                        yds_per_game            REAL NOT NULL,
                                        yds_per_game_scaled     REAL NOT NULL,
                                        yds_per_att             REAL NOT NULL,
                                        yds_per_att_scaled      REAL NOT NULL,
                                        yds_per_cmp             REAL NOT NULL,
                                        sacks                   INTEGER NOT NULL,
                                        sack_yds                INTEGER NOT NULL,
                                        sack_pct                REAL NOT NULL,
                                        dpi_count               INTEGER NULL,
                                        dpi_yards               INTEGER NULL,
                                        adj_yds_per_att         REAL NOT NULL,
                                        net_yds_per_att         REAL NOT NULL,
                                        adj_net_yds_per_att     REAL NOT NULL,
                                        td                      INTEGER NOT NULL,
                                        td_pct                  REAL NOT NULL,
                                        int                     INTEGER NOT NULL,
                                        int_pct                 REAL NOT NULL,
                                        fourth_qtr_comebacks    REAL NULL,
                                        game_winning_drives     REAL NULL,
                                        qb_rating               REAL NOT NULL,
                                        QBR                     REAL NULL,
                                        DYAR                    INTEGER NULL,
                                        YAR                     INTEGER NULL,
                                        DVOA                    REAL NULL,
                                        VOA                     REAL NULL,
                                        efctv_yds               INTEGER NULL,
                                        salary_cap_value        INTEGER NULL,
                                        elite                   REAL NULL,
                                        system                  REAL NULL,
                                        fraud                   REAL NULL,

                                        PRIMARY KEY(player,year,team)
                                        UNIQUE(player,year,team)
                                    ); """
 
    # create a database connection
    conn = db_util.create_connection(qbconfig.db_file)
 
    # create QB season table
    try:
        db_util.create_table(conn, sql_create_qb_season_table)
    except Exception as err:
        logger.exception("Unable to create QB season table")
        raise err
    finally:
        conn.close()
 
 
if __name__ == '__main__':

    # All directories in program are relative to repo root directory
    # Verify current working directory is repo root directory before proceeding
    try:
        assert os.getcwd().split(os.sep)[-1] == "qb_rankings"
    except AssertionError as err:
        print("Working directory incorrect")
        print("Programs must be run with working directory set to 'qb_rankings'")
        raise err

    logging.basicConfig(filename=qbconfig.db_create_log.format(datetime.datetime.now()),
                        filemode="w",
                        level=logging.DEBUG,
                        format="%(levelname)s: %(asctime)s: %(message)s")
                        
    main()