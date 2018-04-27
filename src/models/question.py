from regression import submit_answer, next_question, new_question
import sqlite3 as sql
import os.path as path

PATH = path.dirname(path.abspath(path.join(__file__ ,"../..")))

def getJSON(username, skill, is_new, flag = None, problem_id = None):

	con = sql.connect(PATH + "/mydb.db")
	cur = con.cursor()
	cur.execute("SELECT s_id FROM users2 WHERE username = ?", (username,))
	student_id = cur.fetchall()[0][0]
	json = {}
	json["info"] = {
		"name" : "Quiz about " + skill,
		"main":    "<p>Answer more questions to increase your mastry score!</p>",
		"result" : "u did well"
	}
	if is_new:
		question = new_question(student_id, skill)
	else:
		question = next_question(student_id, problem_id, flag, skill)

	if question != None:
		(problem_id, assistment_id, body, skill, is_original, answer) = question
	else:
		return None

	json["info"]["problem_id"] = problem_id
	json["info"]["assistment_id"] = assistment_id
	json["info"]["answer"] = answer
	json["info"]["skill"] = skill
	json["info"]["username"] = username
	json["info"]["student_id"] = student_id

	json["questions"] = [{
		"q": body,
		"a": answer,
		"correct": "<p><span>That's right!</span></p>"
	}]
	if is_original == 1:
		incorrect = "<p><span>Sorry, not correct.</span>This is a scaffolding question. Let's try to break this question to smaller piece</p>"
	else:
		incorrect = "<p><span>Sorry, not correct.</span>"
		
	json["questions"][0]["incorrect"] = incorrect
	#flag = submit_answer(student_id, problem_id, user_input, skill)
	#(problem_id, assistment_id, body, skill, is_original, answer) = next_question(student_id, problem_id, flag, skill)
	return json