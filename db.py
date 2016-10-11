import sqlite3

def maintenance():
	conn = sqlite3.connect('db/TrainerRoadDatabase.db', check_same_thread=False)
	conn.execute("drop table tblworkoutdata")
	conn.execute("VACUUM")


def queryDBScalar(query):
	conn = sqlite3.connect('db/TrainerRoadDatabase.db', check_same_thread=False)
	cur = conn.execute(query)
	rv = cur.fetchall()
	cur.close()
	return rv[0][0]


def queryDB(query):
	conn = sqlite3.connect('db/TrainerRoadDatabase.db', check_same_thread=False)
	conn.row_factory = dict_factory
	cur = conn.execute(query)
	rv = cur.fetchall()
	cur.close()
	return rv

def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d
