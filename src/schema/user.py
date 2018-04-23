import csv
import os
import sqlite3 as sql

def create_users():
  con = sql.connect("mydb.db")
  cur = con.cursor()

  #cur.execute('CREATE TABLE if not exists Users ( s_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, hash TEXT NOT NULL)')
  cur.execute('CREATE TABLE if not exists users2 (s_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, hash TEXT NOT NULL, type TEXT NOT NULL, type_id INTEGER)')

  con.commit()

create_users()
