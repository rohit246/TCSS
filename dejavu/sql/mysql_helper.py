import mysql.connector
from random import uniform

def create_connection():
	cnx = mysql.connector.connect(user='root', password='landmark123', database='LandmarkDetection')
	cursor = cnx.cursor()

	return cnx, cursor

def destroy_connection(cnx, cursor):
	cursor.close()
	cnx.close()

def insert_into_landmarks(filename):
	cnx, cursor = create_connection()

	add_seedlandmarks = ("INSERT INTO Landmarks "
		           "(Landmark, Latitude, Longitude, SpecificSignature) "
		           "VALUES (%s, %s, %s, %s)")

	ip = open(filename)

	for eachline in ip:
		l1 = eachline.strip().split(' ')
		'''
		landmark = {
			'landmarkname' : l1[0],
			'timediff' : int(l1[1])
		}
		'''
		params = [l1[0], float(l1[1]), float(l1[2]), ""]

		cursor.execute(add_seedlandmarks, params)

		cnx.commit()

	destroy_connection(cnx, cursor)

def for_route(d, route, add_relation, cursor, cnx):

	for i in range(78,153):
		if i%d == 0:
			params = [i, route]

			cursor.execute(add_relation, params)

			cnx.commit()

def create_route_landmark_relation():
	cnx, cursor = create_connection()

	add_relation = ("INSERT INTO LandmarkToRoute "
		           "(LandmarkId, RouteId) "
		           "VALUES (%s, %s)")
	for_route(1, 1, add_relation, cursor, cnx)
	#for_route(4, 2, add_relation, cursor, cnx)
	#for_route(5, 3, add_relation, cursor, cnx)
	#for_route(7, 4, add_relation, cursor, cnx)

	destroy_connection(cnx, cursor)

def for_lmdetail(d, route, add_relation, cursor, cnx):

	f = 0
	for i in range(78,153):
		if i%d == 0:
			for j in range(1,5):
				t = uniform(5,300)
				params = [route, f, i, j, t, 1.0]

				cursor.execute(add_relation, params)

				cnx.commit()
			f = i

def create_landmark_details():
	cnx, cursor = create_connection()

	add_relation = ("INSERT INTO LandmarkDetails "
		           "(RouteId, FromLandmark, LandmarkId, TimeZone, TimeDiff, Confidence) "
		           "VALUES (%s, %s, %s, %s, %s, %s)")
	for_lmdetail(1, 1, add_relation, cursor, cnx)
	#for_lmdetail(4, 2, add_relation, cursor, cnx)
	#for_lmdetail(5, 3, add_relation, cursor, cnx)
	#for_lmdetail(7, 4, add_relation, cursor, cnx)

	destroy_connection(cnx, cursor)

def get_all_landmarks(T):
	cnx, cursor = create_connection()
	get_landmarks = ("SELECT * FROM `LandmarkDetails` AS LD, `Landmarks` AS L, `Routes` AS R WHERE L.`LandmarkId` = LD.`LandmarkId` AND R.`RouteId` = LD.`RouteId` AND LD.`TimeZone` = "+str(T))
	#print get_landmarks

	cursor.execute(get_landmarks)

	rows = cursor.fetchall()
	#print rows

	destroy_connection(cnx, cursor)

	return rows

def get_possible_routes(source, destination, lm):

	cnx, cursor = create_connection()
	 
	if 'Stop' in lm or 'All' in lm:
		lm = 'Stop'
	elif '+' in lm:
		lm = lm.split('+')[0]
	print lm
	s = source.split(',')
	d = destination.split(',')
	source_lat = float(s[0])
	source_long = float(s[1])
	destination_lat = float(d[0])
	destination_long = float(d[1])
	get_landmark = 'SELECT *, (6371 * acos (cos ( radians({0}) ) * cos( radians(`Latitude`) ) * cos(  radians(`Longitude`)  - radians({1}) ) + sin ( radians({2}) ) * sin( radians(`Latitude`)))) AS distance FROM Landmarks HAVING `Landmark` LIKE "%'+lm+'%" ORDER BY distance LIMIT 1'

	cursor.execute(get_landmark.format(source_lat, source_long, source_lat))

	l1 = cursor.fetchall()[0][0]

	cursor.execute(get_landmark.format(destination_lat, destination_long, destination_lat))

	l2 = cursor.fetchall()[0][0]

	get_routes = ('SELECT DISTINCT `RouteId` FROM `LandmarkDetails` WHERE `RouteId` in (SELECT `RouteId` FROM `LandmarkDetails` WHERE `LandmarkId` = %s) AND `LandmarkId` = %s')
	cursor.close()
	cursor = cnx.cursor()

	cursor.execute(get_routes, [l1, l2])

	routes = []
	for r in cursor.fetchall():
		routes.append(r[0])
	return routes, l1, l2
