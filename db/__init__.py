
from conf.config import LOG, DATABASE
from db.database import create_connection, create_table, drop_table, add_astronauts_bulk
from db.dummy import ASTRONAUTS

sql_drop_users = "DELETE FROM users;"
sql_drop_astronauts = "DELETE FROM astronauts;"

sql_create_users_table = """CREATE TABLE IF NOT EXISTS users (
                                id_ text PRIMARY KEY UNIQUE,
                                username text NOT NULL,
                                password int NOT NULL
); """

sql_create_astronauts_table = """CREATE TABLE IF NOT EXISTS astronauts (
                                id_ text PRIMARY KEY,
                                active int NOT NULL,
                                firstName text NOT NULL,
                                lastName text NOT NULL,
                                skills text NOT NULL,
                                hoursInSpace int NOT NULL,
                                picture text NOT NULL,
                                UNIQUE(firstName,lastName)
);"""

def init_session():
    conn = create_connection(DATABASE)
    if conn is not None:
        drop_table('users')
        drop_table('astronauts')
        create_table(conn, sql_create_users_table)
        create_table(conn, sql_create_astronauts_table)
        add_astronauts_bulk(ASTRONAUTS)
    else:
        message = "Cannot create database connection!"
        LOG.error(message)
        raise Exception(message)
    
    conn.close()
