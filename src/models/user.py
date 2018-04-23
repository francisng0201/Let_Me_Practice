import sqlite3 as sql
import hashlib

import config

def _hash(password):
    return hashlib.sha224(password + config.SALT).hexdigest().encode()

def create_user(username, password, usertype):
    con = sql.connect(config.dbname)
    cur = con.cursor()
    cur.execute('INSERT INTO users2 (username, hash, type, type_id) VALUES (?, ?, ?, ?)', (username, _hash(password), 'usertype', 123))
    con.commit()

def check_credentials(username, password):
    con = sql.connect(config.dbname)
    cur = con.cursor()
    cur.execute('SELECT * FROM users2 WHERE username = ? AND hash = ?',
    (username, _hash(password)))
    users = cur.fetchall()
    if len(users) == 0:
        return False
    return True
