from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
import csv
import os
import sqlite3 as sql

def render_student():
  con = sql.connect("mydb.db")
  cur = con.cursor()  

  cur.execute('''CREATE TABLE if not exists Students (
    s_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    grade INT NOT NULL
    )'''
  )

  cur.execute('''CREATE TABLE if not exists Teachers (
    t_id INTEGER PRIMARY KEY AUTOINCREMENT)'''
  )

  con.commit()
  return render_template("student.html")
