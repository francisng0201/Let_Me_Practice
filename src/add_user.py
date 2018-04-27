import sqlite3 as sql
import os.path as path
import hashlib

PATH = path.dirname(path.abspath(path.join(__file__ ,"../")))

con = sql.connect(PATH + "/mydb.db")
cur = con.cursor()
cur.execute("SELECT DISTINCT(ITEST_id) FROM STUDENT_TEST")

def _hash(password):
    return hashlib.sha224(password + "cs411").hexdigest().encode()


ids = cur.fetchall()
ids = [i[0] for i in ids]

for i in ids:
	if i == 6746 or i == 7501 or i == 7502:
		continue
	cur.execute("INSERT INTO users2(s_id, username, hash, type) VALUES (?,?,?,?)", (i, i, _hash(str(123456)), "student"))
	con.commit()
con.close()