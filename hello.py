from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import csv
import os
import sqlite3 as sql

UPLOAD_FOLDER = "csv/"
ALLOWED_EXTENSIONS = set(["csv"])

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
	return render()

@app.route('/addquestion',methods = ['POST', 'GET'])
def addquestion():
	if request.method == "POST":
		try:
			q = request.form["question"]
			a = request.form["answer"]
			skill = request.form["skill"]
			difficulty = request.form["difficulty"]
			weigntage = request.form["weigntage"]
			q_type = request.form["type"]
			test_id = request.form["test_id"]

			with sql.connect("mydb.db") as con:
				cur = con.cursor()

				cur.execute("INSERT INTO Questions (question, answer, skill, difficulty_level, type, weigntage, test_id) VALUES (?, ?, ?, ?, ?, ?, ?)", 
					(q, a, skill, difficulty, q_type, weigntage, test_id))

				con.commit()

				msg = "Record successfully added"
		except:
			con.rollback()
			msg = "Error in insert operation"

		finally:
			con.close()
			return render_template("result.html", msg = msg)

@app.route("/addmultiple", methods = ["POST", "GET"])
def addmultiple():
	if request.method == "POST":
		# check if the post request has the file part
		if "file" not in request.files:
			msg = "No file part"
			return render_template("result.html", msg = msg)

		file = request.files["file"]

		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == "":
			msg = "No selected file"
			return render_template("result.html", msg = msg)

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)

			path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

			file.save(path)

			con = sql.connect("mydb.db")
			
			with open(path, "rb") as file:
				reader = csv.DictReader(file)
				for row in reader:
					cur = con.cursor()

					#cur.execute("SELECT MAX(test_id) FROM Questions")
					#test_id = cur.fetchall()[0][0] + 1

					cur.execute("INSERT INTO Questions (question, answer, skill, difficulty_level, type, weigntage, test_id) VALUES (?, ?, ?, ?, ?, ?, ?)", 
						(row["Qtext"], row["AnsString"], row["Skill"], row["Difficulty"], row["Qtype"], row["Weightage"], 1))

					cur.execute("SELECT MAX(q_id) FROM Questions")

					q_id = cur.fetchall()[0][0]

					if row["Qtype"] == "MC":
						cur.execute("INSERT INTO Option_Type (q_id, option_no, option_string) VALUES (?, ?, ?)",
							(q_id, "a", row["optionA"]))
						cur.execute("INSERT INTO Option_Type (q_id, option_no, option_string) VALUES (?, ?, ?)",
							(q_id, "b", row["optionB"]))
						cur.execute("INSERT INTO Option_Type (q_id, option_no, option_string) VALUES (?, ?, ?)",
							(q_id, "c", row["optionC"]))
						cur.execute("INSERT INTO Option_Type (q_id, option_no, option_string) VALUES (?, ?, ?)",
							(q_id, "d", row["optionD"]))

					con.commit()
					
			msg = "Upload success"
			return render_template("result.html", msg = msg)
	return render_template("result.html", msg = msg)

@app.route('/deletequestion', methods = ['POST', 'GET'])
def deletequestion():
	if request.method == "POST":
		try:
			q_id = request.form["qid"]

			with sql.connect("mydb.db") as con:
				cur = con.cursor()
				cur.execute("DELETE FROM Questions WHERE q_id = ?", (q_id,))
				con.commit()

				msg = "Record successfully deleted"
		except:
			con.rollback()
			msg = "Error in delete operation"

		finally:
			con.close()
			return render_template("result.html", msg = msg)

@app.route('/updatequestion', methods = ['POST', 'GET'])
def updatequestion():
	if request.method == "POST":
		try:
			q_id = request.form["qid"]
			q = request.form["question"]
			a = request.form["answer"]
			skill = request.form["skill"]
			difficulty = request.form["difficulty"]
			weigntage = request.form["weigntage"]
			q_type = request.form["type"]
			test_id = request.form["test_id"]

			with sql.connect("mydb.db") as con:
				cur = con.cursor()

				cur.execute("UPDATE Questions SET q_id = ?, question = ?, answer = ?, skill = ?, difficulty_level = ?, type = ?, weigntage = ?, test_id = ? WHERE q_id = ?", 
					(q_id, q, a, skill, difficulty, q_type, weigntage, test_id, q_id))

				con.commit()

				msg = "Record successfully updated"
		except:
			con.rollback()
			msg = "Error in update operation"

		finally:
			con.close()
			return render_template("result.html", msg = msg)

@app.route("/showquestion", methods = ['POST', 'GET'])
def showquestion():
	con = sql.connect("mydb.db")
	con.row_factory = sql.Row
	cur = con.cursor()

	q_type = ""
	if request.method == "POST":
		if request.form["select"] == "all":
			cur.execute("SELECT * FROM Questions")
			q_type = "All"
		elif request.form["select"] == "MC":
			cur.execute("SELECT Questions.*, GROUP_CONCAT(Option_Type.option_string, ' | ') AS options FROM Questions NATURAL JOIN Option_Type GROUP BY Questions.q_id")
			q_type = "MC"
		elif request.form["select"] == "":
			return render_template("list.html")
		else:
			cur.execute("SELECT * FROM Questions WHERE " + request.form["select_type"] + " = ?", (request.form["select"],))
			q_type = "Others"

		rows = cur.fetchall()

		con.close()

	return render_template("list.html", rows = rows, q_type = q_type)

@app.route("/showoption", methods = ['POST', 'GET'])
def showoption():
	con = sql.connect("mydb.db")
	con.row_factory = sql.Row
	cur = con.cursor()

	if request.method == "POST":
		cur.execute("SELECT * FROM Option_Type")

	rows = cur.fetchall()
	con.close()

	return render_template("list.html", rows = rows, q_type = "options")

def render():
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

	cur.execute('''CREATE TABLE if not exists Students (
		s_id INTEGER PRIMARY KEY AUTOINCREMENT, 
		t_id INTEGER NOT NULL)'''
	)

	cur.execute('''CREATE TABLE if not exists Teachers (
		t_id INTEGER PRIMARY KEY AUTOINCREMENT)'''
	)

	cur.execute('''CREATE TABLE if not exists Students_answers (
		s_id INTEGER PRIMARY KEY AUTOINCREMENT,
		q_id INTEGER NOT NULL,
		s_answer TEXT NOT NULL DEFAULT "",
		score INT NOT NULL DEFAULT 0
		)'''
	)

	cur.execute('''CREATE TABLE if not exists Students_tests (
		s_id INTEGER PRIMARY KEY AUTOINCREMENT,
		test_id INTEGER NOT NULL,
		score INT NOT NULL DEFAULT 0
		)'''
	)

	con.close()

	return render_template("main.html")

if __name__ == "__main__":
	app.run(debug = True)