import pandas
import math
import numpy as np
import sqlite3 as sql
import os.path as path

EWMA_SEED = 0.1
PROBABILITY_FIRST_PROBLEM_CORRECT = 0.894
PATH = path.dirname(path.abspath(path.join(__file__ ,"../..")))
BUFFER = {}

class AccuracyModel(object):
	def __init__(self, total_done, correct, correct_array):
		self.total_done = total_done
		self.correct = correct
		self.correct_array = correct_array

	def get_answer_at(self, i):
		return self.correct_array[i]

	def total_correct(self):
		return self.correct

	def exp_moving_avg(self, weight):
		ewma = EWMA_SEED

		for i in reversed(xrange(self.total_done)):
			ewma = weight * self.get_answer_at(i) + (1 - weight) * ewma

		return ewma

	def predict(self):
		if self.total_done == 0:
			return PROBABILITY_FIRST_PROBLEM_CORRECT

		ewma_3 = self.exp_moving_avg(0.333)
		ewma_10 = self.exp_moving_avg(0.1)

		log_num_done = math.log(self.total_done)
		log_num_missed = math.log(self.total_done - self.total_correct() + 1)
		percent_correct = float(self.total_correct()) / self.total_done

		# weighted_features = [
		# 	(ewma_3, params.EWMA_3),
		# 	(ewma_10, params.EWMA_10),
		# 	(log_num_done, params.LOG_NUM_DONE),
		# 	(log_num_missed, params.LOG_NUM_MISSED),
		# 	(percent_correct, params.PERCENT_CORRECT),
		# ]
		weighted_features = [
			(ewma_3, -1.5745),
			(ewma_10, 1.6535),
			(log_num_done, 0.4041),
			(log_num_missed, -0.8560),
			(percent_correct, 2.1508),
		]

		X, weight_vector = zip(*weighted_features)

		return AccuracyModel.logistic_regression_predict(0.7004, weight_vector, X)

	@staticmethod
	def logistic_regression_predict(intercept, weight_vector, X):
		dot_product = np.dot(weight_vector, X)
		#dot_product = sum(itertools.imap(operator.mul, weight_vector, X))
		z = dot_product + intercept

		return 1.0 / (1.0 + math.exp(-z))

def get_accuracy(student_id):
	con = sql.connect(PATH + "/mydb.db")
	cur = con.cursor()
	cur.execute("SELECT DISTINCT(SKILL) FROM STUDENT_TEST")
	rows = cur.fetchall()
	skills = [i[0] for i in rows]
	d = {}
	for skill in skills:
		if skill:
			cur.execute("SELECT correct FROM STUDENT_TEST where ITEST_id = ? AND SKILL = ? order by actionId", (student_id, skill))
			rows = cur.fetchall()
			array = [i[0] for i in rows]
			correct = sum(array)
			accuracy = AccuracyModel(len(array), correct, array)
			d[skill] = accuracy.predict()
	con.close()
	return d

def new_question(student_id, skill):
	con = sql.connect(PATH + "/mydb.db")
	cur = con.cursor()

	cur.execute("select * from Questions where problem_id in (select distinct(problemId) from STUDENT_TEST where skill= ? and ITEST_id = ? and problemId not in (select distinct(problemId) from STUDENT_TEST where skill= ? and ITEST_id = ? and correct =1))", (skill, student_id, skill, student_id))
	row = cur.fetchall()
	if len(row) == 0:
		cur.execute("SELECT * FROM Questions WHERE SKILL = ? AND is_original = 1 AND problem_id NOT IN (SELECT DISTINCT(problemId) FROM STUDENT_TEST WHERE ITEST_id = ? AND skill = ?)", (skill, student_id, skill))
		row = cur.fetchall()

	con.close()
	return row[0]

def submit_answer(student_id, question_id, answer, skill):
	con = sql.connect(PATH + "/mydb.db")
	cur = con.cursor()
	cur.execute("SELECT answer FROM Questions WHERE problem_id = ?", (question_id,))
	answer_from_db = cur.fetchall()[0][0]

	flag = 1 if answer_from_db == answer else 0
	cur.execute("SELECT actionId FROM STUDENT_TEST WHERE ITEST_id = ?", (student_id,))
	action_id = max([i[0] for i in cur.fetchall()]) + 1

	try:
		cur.execute("INSERT INTO STUDENT_TEST(ITEST_id,actionId,skill,problemId,correct) VALUES (?,?,?,?,?)", (student_id, action_id, skill, question_id, flag))
		con.commit()
		print "updated successfully"
	except:
		print "update failed"
	con.close()	
	return flag
	#cur.execute("INSERT INTO STUDENT_TEST WHERE ITEST_id = ?", (student_id,))

def next_question(student_id, previous_question_id, previous_answer_correctness, previous_question_skill):
	con = sql.connect(PATH + "/mydb.db")
	cur = con.cursor()
	cur.execute("SELECT is_original FROM Questions WHERE problem_id = ?", (previous_question_id,))
	is_original = cur.fetchall()[0][0]

	if previous_answer_correctness == 1:
		if is_original == 0:
			if len(BUFFER[student_id]) == 0:
				return new_question(student_id, previous_question_skill) 
			# from buffer
			question = BUFFER[student_id][0]
			BUFFER[student_id].pop(0)
			return question
		else:
			return new_question(student_id, previous_question_skill)
	else:
		if is_original == 1:
			# find scaffolding
			cur.execute("SELECT * FROM Questions WHERE assistment_id = ? AND is_original = 0 ORDER BY problem_id ASC", (previous_question_id,))
			row = cur.fetchall()
			BUFFER[student_id] = row[1:]
			return row[0]
		else:
			cur.execute("SELECT * FROM Questions WHERE problem_id = ?", (previous_question_id,))
			row = cur.fetchall()[0]
			return row

	con.close()
	return None

def main():
	# l = [
	# [0,1], 
	# [1,0],
	# [1,1],
	# [1,1,1],
	# [1,1,1,1],
	# [1,1,1,1,1],
	# [0,0,0,0,0],
	# [0,0,0,0],
	# [0,0,0],
	# [0,0],
	# [1,0,1,0],
	# [1,0,1,0,1,0],
	# [1,0,1,0,1,0,1,0],
	# [0,1,1,1,1,1,1],
	# [1,1,1,1,1,0,1,1,1],
	# [1,1,1,1,1,1,1,1,1,1],
	# [0,1,1,1,1,1,1,1,1,1,1],
	# [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1],
	# [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1]
	# ]
	# con = sql.connect("mydb.db")
	# cur = con.cursor()
	# cur.execute('''Select correct
	# 	from STUDENT_TEST
	# 	where ITEST_id = 7278 AND SKILL = "unit-conversion" 
	# 	order by actionId''')
	# rows = cur.fetchall()
	# array = [i[0] for i in rows]
	# correct = sum(array)
	# accuracy = AccuracyModel(len(array), correct, array)
	# print accuracy.predict()
	#for i in ['1821','1079','3601','954','1483','5347','8','7258','336','337','5638','6746','312','522','688']:
	student_id = 6746
	BUFFER[student_id] = []
	d = get_accuracy(student_id)

	(problem_id, assistment_id, body, skill, is_original, answer) = new_question(student_id, "percent-of")
	flag = submit_answer(student_id, problem_id, answer, skill)
	print body, flag
	(problem_id, assistment_id, body, skill, is_original, answer) = next_question(student_id, problem_id, flag, skill)

	flag = submit_answer(student_id, problem_id, "9", skill)
	print body, flag
	(problem_id, assistment_id, body, skill, is_original, answer) = next_question(student_id, problem_id, flag, skill)

	flag = submit_answer(student_id, problem_id, "10", skill)
	print body, flag
	(problem_id, assistment_id, body, skill, is_original, answer) = next_question(student_id, problem_id, flag, skill)

	flag = submit_answer(student_id, problem_id, "5", skill)
	print body, flag
	(problem_id, assistment_id, body, skill, is_original, answer) = next_question(student_id, problem_id, flag, skill)

	flag = submit_answer(student_id, problem_id, "5", skill)
	print body, flag
	(problem_id, assistment_id, body, skill, is_original, answer) = next_question(student_id, problem_id, flag, skill)

if __name__ == "__main__":
	main()