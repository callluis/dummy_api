from contextlib import suppress

import sqlite3
from sqlite3 import Error

from conf.config import LOG, DATABASE

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as ex:
        LOG.error(ex)
        raise Exception(ex)
    return None


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as ex:
        LOG.error(ex)
        raise Exception(ex)

def replace_user_info(id_, username, password):
    conn = create_connection(DATABASE)
    c = conn.cursor()
    try:
        c.execute(f"DELETE FROM users WHERE username=?", (username, ))
        c.execute(
            "INSERT INTO users(id_, username, password) VALUES(?, ?, ?)", (id_, username, password))
        conn.commit()
    except sqlite3.IntegrityError as ex:
        LOG.error(ex)
        raise Exception(ex)
    conn.close()

def create_user(id_, username, password):
    conn = create_connection(DATABASE)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users(id_, username, password) VALUES(?, ?, ?)", (id_, username, password))
        conn.commit()
    except sqlite3.IntegrityError as ex:
        LOG.error(ex)
        raise Exception(ex)
    conn.close()

def fetch_users(username=None, user_id=None, hide_pass=None):
    conn = create_connection(DATABASE)
    c = conn.cursor()
    if username and user_id:
        c.execute("SELECT id_, username, password FROM users WHERE id_=? AND username=?", (user_id, username))
    elif user_id:
        c.execute("SELECT id_, username, password FROM users WHERE id_=?", (user_id, ))
    elif username:
        c.execute("SELECT id_, username, password FROM users WHERE username=?", (username, ))
    else:
        c.execute("SELECT id_, username, password FROM users")
    rows = c.fetchall()
    users = []
    for user in rows:
        username = {
            'id': user[0],
            'username': user[1]
        }
        if not hide_pass:
            username['password'] = user[2]
        users.append(username)
    conn.close()
    return users

def update_password(id_, password):
    conn = create_connection(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE id_ = ?", (password, id_))
    conn.commit()
    conn.close()

def delete_from_table(id_):
    conn = create_connection(DATABASE)
    c = conn.cursor()
    c.execute(f"DELETE FROM users WHERE id_=?", (id_, ))
    conn.commit()
    conn.close()

def drop_table(table):
    conn = create_connection(DATABASE)
    c = conn.cursor()
    c.execute(f"DROP TABLE IF EXISTS {table};")
    conn.commit()
    conn.close()

# def delete_from_table(id_, table):
#     conn = create_connection(DATABASE)
#     c = conn.cursor()
#     c.execute(f"DELETE FROM {table} WHERE id_ = {id_}")
#     conn.commit()
#     conn.close()

# def fetch_colors(sid):
#     conn = create_connection(database)
#     c = conn.cursor()
#     c.execute("SELECT name, role_id FROM colors WHERE sid=?", (sid, ))
#     rows = c.fetchall()
#     colors = {}
#     for role in rows:
#         colors[role[0]] = role[1]
#     conn.close()
#     return colors

# def delete_guild(sid):
#     conn = create_connection(database)
#     c = conn.cursor()
#     c.execute("DELETE FROM guilds WHERE sid=?", (sid, ))
#     c.execute("DELETE FROM colors WHERE sid=?", (sid, ))
#     c.execute("DELETE FROM autoroles WHERE sid=?", (sid, ))
#     conn.commit()
#     conn.close()


# # Color area

# def create_color(sid, name, role_id):
#     conn = create_connection(database)
#     c = conn.cursor()
#     c.execute("INSERT OR REPLACE INTO colors(uid, sid, name, role_id) VALUES(?, ?, ?, ?)",
#               (sid + role_id, sid, name, role_id))
#     conn.commit()
#     conn.close()


# def delete_color(sid, name, role_id):
#     conn = create_connection(database)
#     c = conn.cursor()
#     c.execute("DELETE FROM colors WHERE sid=? AND name=? AND role_id=?",
#               (sid, name, role_id))
#     conn.commit()
#     conn.close()

# # Autorole area

# def create_autorole(sid, role_id):
#     conn = create_connection(database)
#     c = conn.cursor()
#     c.execute("INSERT OR REPLACE INTO autoroles(uid, sid, role_id) VALUES(?, ?, ?)",
#               (sid + role_id, sid, role_id))
#     conn.commit()
#     conn.close()


# def delete_autorole(sid, role_id):
#     conn = create_connection(database)
#     c = conn.cursor()
#     c.execute("DELETE FROM autoroles WHERE sid=? AND role_id=?", (sid, role_id))
#     conn.commit()
#     conn.close()


# def fetch_autoroles(sid):
#     conn = create_connection(database)
#     c = conn.cursor()
#     c.execute("SELECT role_id FROM autoroles WHERE sid=?", (sid, ))
#     rows = c.fetchall()
#     autoroles = []
#     for r in rows:
#         autoroles.append(r[0])
#     conn.close()
#     return autoroles


# # Prefix area

# def change_prefix(sid, prefix):
#     conn = create_connection(database)
#     c = conn.cursor()
#     c.execute("UPDATE guilds SET prefix = ? WHERE sid=?",
#               (prefix, sid))
#     conn.commit()
#     conn.close()


# def fetch_prefix(sid):
#     conn = create_connection(database)
#     c = conn.cursor()
#     c.execute("SELECT prefix FROM guilds WHERE sid=?", (sid, ))
#     prefix = c.fetchone()[0]
#     conn.close()
#     return prefix


# def fetchall_prefix():
#     conn = create_connection(database)
#     c = conn.cursor()
#     c.execute("SELECT name, prefix FROM guilds")
#     rows = c.fetchall()
#     guild_prefix_dict = {}
#     for r in rows:
#         guild_prefix_dict[r[0]] = r[1]
#     conn.close()
#     return guild_prefix_dict
