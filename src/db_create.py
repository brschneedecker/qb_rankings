"""
This program creates a database for storing QB data

References
  - https://www.sqlitetutorial.net/sqlite-python/creating-database/
  - https://www.sqlitetutorial.net/sqlite-python/create-tables/
"""

import click
import db_util
import qbconfig

@click.command()
def main():
 
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
                                        yds_per_att             REAL NOT NULL,
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
                                    ); """
 
    # create a database connection
    conn = db_util.create_connection(qbconfig.db_file)
 
    # create tables
    if conn is not None:
        # create QB season table
        db_util.create_table(conn, sql_create_qb_season_table)
    else:
        print("Error! cannot create the database connection.")

    conn.close()
 
 
if __name__ == '__main__':
    main()