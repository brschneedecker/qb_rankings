""" Database utility functions """

import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ 
    Create a database connection to the SQLite 
    database specified by db_file
    
    Args:
      - db_file: database file
    
    Returns: 
       - Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return conn


def create_table(conn, create_table_sql):
    """ 
    Create a table from the create_table_sql statement
    
    Args:
      - conn: Connection object
      - create_table_sql: a CREATE TABLE statement
    
    Returns: none
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
 