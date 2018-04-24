import pandas
import math
import numpy as np
import sqlite3 as sql
import os.path as path

EWMA_SEED = 0.1
PROBABILITY_FIRST_PROBLEM_CORRECT = 0.894
PATH = path.dirname(path.abspath(path.join(__file__ ,"../..")))

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
			cur.execute("Select correct from STUDENT_TEST where ITEST_id = ? AND SKILL = ? order by actionId", (student_id, skill))
			rows = cur.fetchall()
			array = [i[0] for i in rows]
			correct = sum(array)
			accuracy = AccuracyModel(len(array), correct, array)
			d[skill] = accuracy.predict()
	con.close()
	return d

def next_question(d, student_id):
	#smaller_50 = {k: v for k, v in d.iteritems() if v < 0.5}
	con = sql.connect(PATH + "/mydb.db")
	cur = con.cursor()
	questions = {}
	#cur.execute("SELECT problemId FROM STUDENT_TEST WHERE ITEST_id = ?", (student_id,))
	#row = cur.fetchall()
	for k, v in d.iteritems():
		cur.execute("SELECT body from Problem_Text WHERE Problem_Text.problem_id IN (SELECT problemId from STUDENT_TEST WHERE ITEST_id = ? AND SKILL = ?)", (student_id, k))
		row = cur.fetchall()
		questions[k] = row
	#cur.execute("Select body from Problem_Text where ITEST_id = ? AND SKILL = ? order by actionId", (student_id, skill))
	return questions

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
	d = get_accuracy(student_id)
	ok = next_question(d, student_id)
	print ok

if __name__ == "__main__":
	main()