"""
This program creates a database for storing QB data

References
  - https://www.sqlitetutorial.net/sqlite-python/creating-database/
  - https://www.sqlitetutorial.net/sqlite-python/create-tables/
"""

import sqlite3
from sqlite3 import Error
 
 
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
 
 
if __name__ == '__main__':
    create_connection(r"data/qb_sqlite.db")