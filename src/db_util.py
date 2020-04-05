""" Database utility functions """

import sqlite3
from sqlite3 import Error
import logging


def create_connection(db_file):
    """ 
    Create a database connection to the SQLite 
    database specified by db_file
    
    Args:
      - db_file: database file
    
    Returns: 
       - Connection object or None
    """
    logger = logging.getLogger(__name__)

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as err:
        logger.exception("Unable to make connection to db {}".format(db_file))
        raise err


def create_table(conn, create_table_sql):
    """ 
    Create a table from the create_table_sql statement
    
    Args:
      - conn: Connection object
      - create_table_sql: a CREATE TABLE statement
    
    Returns: none
    """
    logger = logging.getLogger(__name__)

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as err:
        logger.exception("Unable to create table")
        raise err
 