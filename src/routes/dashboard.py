from flask import *
from require_signin import *
import sqlite3 as sql
import config
import models.graph as graph

def get_data(username):
	con = sql.connect(config.dbname)
	cur = con.cursor()
	cur.execute("SELECT type,s_id FROM users2 WHERE username = ?", (session["username"],))
	result = cur.fetchall()[0]
	user_type = result[0]
	user_id = result[1]

	if user_type == "student":
		cur.execute("SELECT assignmentId, count(*), SUM(correct) FROM STUDENT_TEST WHERE ITEST_id = ? group by assignmentId", (user_id,))
		table = cur.fetchall()
		table = [i + (round(i[2]/float(i[1]), 2),) for i in table]
		cur.execute("SELECT assignmentId, problemId, skill, correct, attemptCount FROM STUDENT_TEST WHERE ITEST_id = ? ORDER BY assignmentId ASC", (user_id,))
		sub_table = cur.fetchall()
	else:
		cur.execute("SELECT ITEST_id, COUNT(assignmentId), SUM(correct) FROM STUDENT_TEST GROUP BY ITEST_id")
		table = cur.fetchall()
		table = [i + (round(i[2]/float(i[1]), 2),) for i in table]
		cur.execute("SELECT ITEST_id, assignmentId, COUNT(*), SUM(correct) FROM STUDENT_TEST GROUP BY ITEST_id, assignmentId ORDER BY ITEST_id ASC")
		sub_table = cur.fetchall()
		sub_table = [i + (round(i[3]/float(i[2]), 2),) for i in sub_table]

	d = dict()
	k = 0
	id_set = set([i[0] for i in sub_table])

	for i in sorted(id_set):
		for j in range(k, len(sub_table)):
			student_id = sub_table[j][0]
			if i != student_id:
				k = j
				break
			if student_id not in d:
				d[student_id] = {}#list(sub_table[i])
			d[i][j-k] = {}
			if user_type == "student":
				d[i][j-k]["problem_id"] = sub_table[j][1]
				d[i][j-k]["skill"] = sub_table[j][2]
				d[i][j-k]["correct"] = sub_table[j][3]
				d[i][j-k]["attemptCount"] = sub_table[j][4]
			else:
				d[i][j-k]["test_id"] = sub_table[j][1]
				d[i][j-k]["num_question"] = sub_table[j][2]
				d[i][j-k]["num_correct"] = sub_table[j][3]
				d[i][j-k]["percentage"] = sub_table[j][4]

	if user_type == "teacher":
		cur.execute("SELECT * FROM Questions")
		q = cur.fetchall()

	con.close()
	if user_type == "teacher":
		return user_type, table, d, q
	else:
		return user_type, table, d

blueprint = Blueprint('dashboard', __name__)

@blueprint.route('/', methods=['GET'])
@require_signin
def _index():
	data = get_data(session["username"])
	if len(data) == 3:
		user_type, table, sub_table = data
		question = None
		g = graph.create_graph_structure(session["username"])
	else:
		user_type, table, sub_table, question = data
		g = None

	return render_template('dashboard.html', username = session['username'], type = user_type, table = table, sub_table = sub_table, q = question, graph = g)

@blueprint.route('/', methods=['POST'])
@require_signin
def _add_test():
	con = sql.connect(config.dbname)
	cur = con.cursor()
	if "delete_problem_id" in request.form:
		cur.execute("DELETE FROM Questions WHERE problem_id = ?", (request.form['delete_problem_id'],))
	elif "problem_id" not in request.form:
		question = request.form['question']
		answer = request.form["answer"]
		skill = request.form["skill"]
		is_original = request.form["is_original"]
		cur.execute("SELECT MAX(problem_id) FROM Questions")
		problem_id = str(int(cur.fetchall()[0][0]) + 1)
		cur.execute("SELECT MAX(assistment_id) FROM Questions")
		assistment_id = str(int(cur.fetchall()[0][0]) + 1)
		cur.execute("INSERT INTO Questions(body,skill,is_original,answer, problem_id, assistment_id, answer) VALUES (?,?,?,?,?,?,?)", (question, skill, is_original, answer, problem_id, assistment_id, answer))
	else:
		problem_id = request.form["problem_id"]
		if request.form['question'] != "":
			cur.execute("UPDATE Questions SET body = ? WHERE problem_id = ?", (request.form['question'], problem_id))
		if request.form["answer"] != "":
			cur.execute("UPDATE Questions SET answer = ? WHERE problem_id = ?", (request.form['answer'], problem_id))
		if request.form['skill'] != "":
			cur.execute("UPDATE Questions SET skill = ? WHERE problem_id = ?", (request.form['skill'], problem_id))
		if request.form['is_original'] != "":
			cur.execute("UPDATE Questions SET is_original = ? WHERE problem_id = ?", (request.form['is_original'], problem_id))

	con.commit()
	con.close()
	user_type, table, sub_table, question = get_data(session["username"])

	return render_template('dashboard.html', username = session['username'], type = user_type, table = table, sub_table = sub_table, q = question)