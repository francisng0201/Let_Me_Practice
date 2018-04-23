from flask import Flask, render_template, request, url_for, Blueprint
from werkzeug.utils import secure_filename
import csv
import os
import sqlite3 as sql

# question_page = Blueprint("question_page", __name__, template_folder = "templates")

# @question_page.route("/showquestion", methods = ['POST', 'GET'])
# def showquestion():
# 	con = sql.connect("mydb.db")
# 	con.row_factory = sql.Row
# 	cur = con.cursor()

# 	q_type = ""
# 	if request.method == "POST":
# 		if request.form["select"] == "all":
# 			cur.execute("SELECT * FROM Questions")
# 			q_type = "All"
# 		elif request.form["select"] == "MC":
# 			cur.execute("SELECT Questions.*, GROUP_CONCAT(Option_Type.option_string, ' | ') AS options FROM Questions NATURAL JOIN Option_Type GROUP BY Questions.q_id")
# 			q_type = "MC"
# 		elif request.form["select"] == "":
# 			return render_template("list.html")
# 		else:
# 			cur.execute("SELECT * FROM Questions WHERE " + request.form["select_type"] + " = ?", (request.form["select"],))
# 			q_type = "Others"

# 		rows = cur.fetchall()

# 		con.close()

# 	return render_template("list.html", rows = rows, q_type = q_type)

def render_question():
	con = sql.connect("mydb.db")
	cur = con.cursor()

	cur.execute('''CREATE TABLE if not exists Questions (
		q_id INTEGER PRIMARY KEY AUTOINCREMENT, 
		skill TEXT NOT NULL,
		question TEXT NOT NULL, 
		answer TEXT NOT NULL, 
		difficulty_level INT NOT NULL, 
		type TEXT NOT NULL, 
		weigntage INT NOT NULL, 
		test_id INT NOT NULL DEFAULT 1)'''
	)

	cur.execute('''CREATE TABLE if not exists Option_Type (
		q_id INTEGER NOT NULL, 
		option_no TEXT NOT NULL,  
		option_string TEXT NOT NULL)'''
	)

	cur.execute('''CREATE TABLE if not exists Tests (
		test_id INTEGER PRIMARY KEY AUTOINCREMENT, 
		name TEXT NOT NULL,  
		total_marks TEXT NOT NULL)'''
	)

	cur.execute('''CREATE TABLE if not exists Students_answers (
		s_id INTEGER PRIMARY KEY AUTOINCREMENT,
		q_id INTEGER NOT NULL,
		s_answer TEXT NOT NULL DEFAULT "",
		score INT NOT NULL DEFAULT 0
		)'''
	)

	cur.execute('''CREATE TABLE if not exists Students_tests (
		s_id INTEGER,
		test_id INTEGER NOT NULL,
		score INT NOT NULL DEFAULT 0
		)'''
	)

	con.close()

	return render_template("question.html")