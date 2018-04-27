import os.path as path
import sqlite3 as sql
from regression import get_accuracy

PATH = path.dirname(path.abspath(path.join(__file__ ,"../..")))

def create_graph_structure(username):
	con = sql.connect(PATH + "/mydb.db")
	cur = con.cursor()
	cur.execute("SELECT Name, Learning_Sequence, level FROM Skills ORDER BY level, Learning_Sequence")
	row = cur.fetchall()
	row = [val + (i,) for i, val in enumerate(row)]

	cur.execute("SELECT s_id FROM users2 WHERE username = ?", (username,))
	user_id = cur.fetchall()[0][0]
	accuracy = get_accuracy(user_id)

	d = {
	"nodes": [],
	"edges": [],
	#"accuracy" : [accuracy]
	}
	for i in row:
		n = {}
		n["id"] = i[3]
		n["label"] = i[0]
		n["color"] = {}
		n["color"]["background"] = "#ff0f00" if accuracy[i[0]] < 0.5 else "#fb7116" if accuracy[i[0]] < 0.6 else "#f6d32b" if accuracy[i[0]] < 0.7 else "#f4fb16" if accuracy[i[0]] < 0.8 else "#b4dd1e" if accuracy[i[0]] < 0.9 else "#19d228"
		n["size"] = i[2] * 15
		n["accuracy"] = round(accuracy[i[0]], 2)
		d["nodes"].append(n)
	i = 0
	while i < len(row)-1: 
		v1 = row[i]
		v2 = row[i+1]
		e = {}
		if v1[1] == v2[1]:
			for j in range(i+1 ,len(row)):
				e = {}
				if row[j][1] != v1[1]:
					i = j
					break
				e["from"] = row[i-1][3]
				e["to"] = row[j][3]
				d["edges"].append(e)
			continue
		else:
			e["from"] = v1[3]
			e["to"] = v2[3]
			d["edges"].append(e)
		i += 1
	e = {}
	e["from"] = 8
	e["to"] = 11
	d["edges"].append(e)
	e = {}
	e["from"] = 8
	e["to"] = 12
	d["edges"].append(e)
	e = {}
	e["from"] = 9
	e["to"] = 11
	d["edges"].append(e)
	e = {}
	e["from"] = 9
	e["to"] = 12
	d["edges"].append(e)
	e = {}
	e["from"] = 10
	e["to"] = 11
	d["edges"].append(e)
	e = {}
	e["from"] = 11
	e["to"] = 13
	d["edges"].append(e)
	e = {}
	e["from"] = 12
	e["to"] = 13
	d["edges"].append(e)
	return d

# def create_graph(username):
# 	g = create_graph_structure()
# 	con = sql.connect(PATH + "/mydb.db")
# 	cur = con.cursor()
# 	cur.execute("SELECT s_id FROM users2 WHERE username = ?", (username,))
# 	user_id = cur.fetchall()[0][0]
# 	accuracy = get_accuracy(user_id)

# create_graph("francisng")