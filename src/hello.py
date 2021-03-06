from flask import Flask, render_template, make_response, request, url_for, send_from_directory, redirect
from student import render_student
from question import render_question
from werkzeug.utils import secure_filename
import csv
import os
import sqlite3 as sql
import hashlib

SALT = 'cs411'

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

@app.route("/pub/<path:path>")
def pub(path):
    return send_from_directory('static', path)

@app.route('/test', methods=['POST', 'GET'])
def test():
  if not 'username' in request.cookies:
    return render_template('main.html', prompt=True)
  return render_template('test.html', username=request.cookies['username'])

@app.route("/question", methods = ["POST", "GET"])
def question():
  if not 'username' in request.cookies:
    return render_template('main.html', prompt=True)
  return render_question()

@app.route("/student", methods = ["POST", "GET"])
def student():
  if not 'username' in request.cookies:
    return render_template('main.html', prompt=True)
  return render_student()

@app.route('/addquestion',methods = ['POST', 'GET'])
def addquestion():
  if not 'username' in request.cookies:
    return render_template('main.html', prompt=True)
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
  if not 'username' in request.cookies:
    return render_template('main.html', prompt=True)

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
          if "question" in request.referrer:
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

          elif "student_test" in request.referrer:
            cur.execute("INSERT INTO STUDENT_TEST (ITEST_id, actionId, skill, problemId, assignmentId, assistmentId, startTime, endTime, timeTaken, correct, original, scaffold, attemptCount, problemType) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
              (row["ITEST_id"], row["actionId"], row["skill"], row["problemId"], row["assignmentId"], row["assistmentId"], row["startTime"], row["endTime"], row["timeTaken"], row["correct"], row["original"], row["scaffold"], row["attemptCount"], row["problemType"]))

            con.commit()

          elif "student" in request.referrer:
            cur.execute("INSERT INTO Students (first_name, last_name, date_of_birth, grade) VALUES (?, ?, ?, ?, ?)", 
              (row["Qtext"], row["AnsString"], row["Skill"], row["Difficulty"], row["grade"]))

            con.commit()

      msg = "Upload success"
      return render_template("result.html", msg = msg)
  return render_template("result.html", msg = msg)

@app.route('/deletequery', methods = ['POST', 'GET'])
def deletequery():
  if not 'username' in request.cookies:
    return render_template('main.html', prompt=True)
  if request.method == "POST":
    try:
      if "question" in request.referrer:
        q_id = request.form["q_id"]

        with sql.connect("mydb.db") as con:
          cur = con.cursor()
          cur.execute("DELETE FROM Questions WHERE q_id = ?", (q_id,))
          con.commit()
      elif "student" in request.referrer:
        s_id = request.form["s_id"]
        with sql.connect("mydb.db") as con:
          cur = con.cursor()
          cur.execute("DELETE FROM Students WHERE s_id = ?", (s_id,))
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
  if not 'username' in request.cookies:
    return render_template('main.html', prompt=True)
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

@app.route("/showdb", methods = ['POST', 'GET'])
def showdb():
  #if not 'username' in request.cookies:
  #  return render_template('main.html', prompt=True)
  con = sql.connect("mydb.db")
  con.row_factory = sql.Row
  cur = con.cursor()

  q_type = ""
  if request.method == "POST":
    if "question" in request.referrer:
      if request.form["select"] == "all":
        cur.execute("SELECT * FROM Questions")
        q_type = "All"
      elif request.form["select"] == "MC":
        cur.execute("SELECT Questions.*, GROUP_CONCAT(Option_Type.option_string, ' | ') AS options FROM Questions NATURAL JOIN Option_Type GROUP BY Questions.q_id")
        q_type = "MC"
      elif request.form["select"] == "":
        con.close()
        return render_template("list.html")
      else:
        cur.execute("SELECT * FROM Questions WHERE " + request.form["select_type"] + " = ?", (request.form["select"],))
        q_type = "Others"
    elif "student_test" in request.referrer:
      cur.execute("SELECT * FROM STUDENT_TEST")
      q_type = "student_test"
    elif "student" in request.referrer:
      if request.form["select"] == "all":
        cur.execute("SELECT * FROM Students")
        q_type = "student"
      elif request.form["select_type"] == "grade":
        cur.execute("SELECT * FROM Students WHERE grade = ?", (request.form["select"],))
        q_type = "student"

    rows = cur.fetchall()
    con.close()

  return render_template("list.html", rows = rows, q_type = q_type)

@app.route("/showoption", methods = ['POST', 'GET'])
def showoption():
  if not 'username' in request.cookies:
    return render_template('main.html', prompt=True)
  con = sql.connect("mydb.db")

  con.row_factory = sql.Row
  cur = con.cursor()

  if request.method == "POST":
    cur.execute("SELECT * FROM Option_Type")

  rows = cur.fetchall()
  con.close()

  return render_template("list.html", rows = rows, q_type = "options")

def render():
  return render_template("main.html")

@app.route('/addstudent',methods = ['POST', 'GET'])
def addstudent():
  if not 'username' in request.cookies:
    return render_template('main.html', prompt=True)
  if request.method == "POST":
    try:
      first_name = request.form["first_name"]
      last_name = request.form["last_name"]
      d_o_b = request.form["date_of_birth"]
      grade = request.form["grade"]

      with sql.connect("mydb.db") as con:
        cur = con.cursor()

        cur.execute("INSERT INTO Students (first_name, last_name, date_of_birth, grade) VALUES (?, ?, ?, ?)", 
        (first_name, last_name, d_o_b, grade))
        con.commit()

        msg = "Record successfully added"
    except:
      con.rollback()
      msg = "Error in insert operation"

    finally:
      con.close()
      return render_template("result.html", msg = msg)

@app.route('/updatestudent', methods = ['POST', 'GET'])
def updatestudent():
  if not 'username' in request.cookies:
    return render_template('main.html', prompt=True)
  if request.method == "POST":
    try:
      s_id = request.form["s_id"]
      first_name = request.form["first_name"]
      last_name = request.form["last_name"]
      d_o_b = request.form["date_of_birth"]
      grade = request.form["grade"]

      with sql.connect("mydb.db") as con:
        cur = con.cursor()

        cur.execute("UPDATE Students SET s_id = ?, first_name = ?, last_name = ?, date_of_birth = ?, grade = ?, WHERE q_id = ?", 
          (s_id, first_name, last_name, d_o_b, grade, s_id))

        con.commit()

        msg = "Record successfully updated"
    except:
      con.rollback()
      msg = "Error in update operation"

    finally:
      con.close()
      return render_template("result.html", msg = msg)

@app.route('/advanced', methods = ['POST', 'GET'])
def advanced():
  if not 'username' in request.cookies:
    return render_template('main.html', prompt=True)
  con = sql.connect("mydb.db")
  cur = con.cursor()
  cur.execute("DROP TABLE Students_tests")

  cur.execute('''CREATE TABLE if not exists Students_tests (
    s_id INTEGER,
    test_id INTEGER NOT NULL,
    score INT NOT NULL DEFAULT 0
    )'''
  )
  cur.execute("INSERT INTO Students_tests (s_id, test_id, score) VALUES (?, ?, ?)", (1, 1, 13))
  cur.execute("INSERT INTO Students_tests (s_id, test_id, score) VALUES (?, ?, ?)", (2, 1, 17))
  cur.execute("INSERT INTO Students_tests (s_id, test_id, score) VALUES (?, ?, ?)", (3, 1, 12))
  cur.execute("INSERT INTO Students_tests (s_id, test_id, score) VALUES (?, ?, ?)", (4, 1, 15))
  cur.execute("INSERT INTO Students_tests (s_id, test_id, score) VALUES (?, ?, ?)", (5, 1, 18))
  cur.execute("INSERT INTO Students_tests (s_id, test_id, score) VALUES (?, ?, ?)", (1,2,21))
  cur.execute("INSERT INTO Students_tests (s_id, test_id, score) VALUES (?, ?, ?)", (2,2,20))
  cur.execute("INSERT INTO Students_tests (s_id, test_id, score) VALUES (?, ?, ?)", (3,2,18))
  cur.execute("INSERT INTO Students_tests (s_id, test_id, score) VALUES (?, ?, ?)", (4,2,15))
  cur.execute("INSERT INTO Students_tests (s_id, test_id, score) VALUES (?, ?, ?)", (5,2,21))

  con.commit()

  con.row_factory = sql.Row

  cur.execute("SELECT max(total) AS total, p.s_id AS s_id, s.first_name AS first_name FROM Students s, (select sum(score) as total, s_id from Students_tests st group by s_id) as p where p.s_id = s.s_id")
  
  rows = cur.fetchall()

  return render_template("advance.html", rows = rows)

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
  if request.method == 'GET':
    return render_template('signup2.html', failure=False)
  if not request.form or not 'username' in request.form or not 'password' in request.form:
    return render_template('signup2.html', failure=True)
  if len(request.form['username']) < 3 or len(request.form['password']) < 3:
    return render_template('signup2.html', failure=True)
  con = sql.connect('mydb.db')
  cur = con.cursor()
  # TODO sql injection, etc.
  cur.execute("SELECT MAX(s_id) FROM Users")
  s_id = cur.fetchall()[0][0] + 1
  cur.execute('INSERT into Users VALUES (?, ?, ?)', (s_id, request.form['username'], hashlib.sha224(request.form['password'].encode()).hexdigest()))
  con.commit()
  return render_template('signup2.html', failure=False, success=True)

@app.route('/signin', methods = ['GET', 'POST'])
def signin():
  if request.method == 'GET':
    return render()
  if not request.form or not 'username' in request.form or not 'password' in request.form:
    return render_template('signin.html', failure=True)
  if len(request.form['username']) < 3 or len(request.form['password']) < 3:
    return render_template('signin.html', failure=True)
  con = sql.connect('mydb.db')
  cur = con.cursor()
  # TODO
  cur.execute('SELECT * FROM Users WHERE username = ? AND hash = ?', (request.form['username'],hashlib.sha224(request.form['password'].encode()).hexdigest()))
  users = cur.fetchall()
  if len(users) == 0:
    return render_template('main.html', failure=True)
  resp = make_response(render_template('main.html', success=True))
  resp.set_cookie('username', request.form['username'])
  return resp

@app.route('/student_test', methods = ['POST', 'GET'])
def student_test():
  return render_template("student_test.html")


if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port=5001)
