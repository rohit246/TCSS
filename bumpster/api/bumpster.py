from flask import request, Flask, url_for, json, jsonify
import requests
import __init__
import processor.preprocess_db
from processor.node import node
from processor.edge import edge
from processor.pta import pta
import processor.dummy_processing
import processor.detectLandmarkInTrail
import processor.detectLandmarkInTrailWithAccData
import sql.mysql_helper
from datetime import datetime
from collections import defaultdict
import numpy as np
import scipy
import scipy.stats
from scipy import signal
import numpy.fft as fft
import matplotlib
from processor.preprocessing import preprocessor
from numpy.linalg import inv
import sys
from sympy import *
import geopy
from geopy.distance import VincentyDistance
import processor.lib
from math import sqrt,pow

'''
CONSTANTS
'''
NOTIFY_DESTINATION = 180
FAILURE_ACCEPTABLE = 1
FAILURE_SWITCH_ROUTE = 3
NON_VOLATILE_LANDMARKS = ['Turn', 'Bumper']
SPEED_HISTORY_THRESHOLD = 0.5
SWITCH_LANDMARK_THRESHOLD = 15
EPSILON = 0.3
'''
Storage class used to store the nodes and edges in the network
'''
class storage:

	def __init__(self):
		self.node_dict = {}
		self.edge_dict = {}

'''
Global variables:
store - stores the nodes and edges in the network
user_routes - all user routes in the network
'''
store = storage()
user_routes = defaultdict(lambda : defaultdict())
date = '2015-01-01'
'''
Create a flask application
'''
app = Flask(__name__)

## HELPER FUNCTIONS
'''
Function to convert from seconds to HH:MM:SS format
'''
def sec_to_hms(ttd):
	h = int(ttd/3600)
	m = int(ttd/60) - (h*60)
	s = int(ttd) - (m*60) - (h*3600)

	return str(ttd)
	
def getProcessedData(data,i):
	arr=[]
	for l in data:
		arr.append(float(l.split(",")[i]))
	rdata=[]
	l1 = preprocessor(arr)
	for l in l1:
		rdata.append(l)
	return rdata

def getLatLng(ldata,cdata, axes, lat1, lon1):

	x=Symbol('x')
	X = axes[0]
	Y = axes[1]
	Z = axes[2]
	xdata=getProcessedData(ldata,X)
	ydata=getProcessedData(ldata,Y)
	zdata=getProcessedData(ldata,Z)

	t=0.0
	dist=0.0
	u=0.0
	v=0.0
	s=0.0
	d_arr=[]

	for a in xdata:
		v=u+a[0]*t
		exp=integrate(u+a[0]*x,x)
		#print exp
		f=lambdify(x,exp,"numpy")
		s=f(t)
		dist=dist+s
		t=t+0.2
		u=v

	d_arr.append(dist)

	t=0.0
	dist=0.0
	u=0.0
	v=0.0
	s=0.0

	for a in ydata:
		v=u+a[0]*t
		exp=integrate(u+a[0]*x,x)
		#print exp
		f=lambdify(x,exp,"numpy")
		s=f(t)
		dist=dist+s
		t=t+0.2
		u=v

	d_arr.append(dist)

	t=0.0
	dist=0.0
	u=0.0
	v=0.0
	s=0.0

	for a in zdata:
		v=u+a[0]*t
		exp=integrate(u+a[0]*x,x)
		#print exp
		f=lambdify(x,exp,"numpy")
		s=f(t)
		dist=dist+s
		t=t+0.2
		u=v

	d_arr.append(dist)

	d=sqrt(pow(d_arr[0],2)+pow(d_arr[1],2)+pow(d_arr[2],2))/3
	b=float(cdata[7].split(",")[0])-270
	if b<0:
		b=b+360
	origin = geopy.Point(lat1, lon1)
	destination = VincentyDistance(meters=-d).destination(origin, b)

	lat2, lon2 = destination.latitude, destination.longitude
	rep=str(lat2)+","+str(lon2)
	return rep
	
def checkbump(ldata, cdata, uid, X, Y, Z):

	lm = processor.detectLandmarkInTrail.detect_landmark(ldata, cdata, X, Y, Z)
	if 'Bump' in lm:
		return 1
	return 0

'''
App route which is called when a sample is sent from the client.
Gets the sample trail, processes it and returns the time to destination to the client
'''
def api_ttd(uid, acc, lacc, comp):
	user_routes[uid]['current_time'] = datetime.strptime(date+' '+request.json['time'], "%Y-%m-%d %H:%M:%S")
	X,Y,Z = get_orientations(acc)
	c = checkbump(lacc, comp, uid, X, Y, Z)
	return c
	
@app.route('/initializing', methods = ['POST'])
def api_intializing():
	if 'application/json' in request.headers['Content-Type']:

		s_lat = request.json['locations'][0]['lat']
		s_long = request.json['locations'][0]['long']
		d_lat = request.json['locations'][1]['lat']
		d_long = request.json['locations'][1]['long']

		uid = request.json['uid']

		print 'request',s_lat, s_long, d_lat, d_long

		route_list, s_id, d_id = sql.mysql_helper.get_possible_routes(s_lat+','+s_long, d_lat+','+d_long, "All")

		print s_id, d_id,">>>"

		timezone = int(request.json['timezone'])
		
		route_network = create_network_graph(store.edge_dict[timezone], route_list[0], "All")

		ttd, mean_sd = initial_time_to_destination(route_network, s_id, d_id, timezone)
		
		print ttd, mean_sd

		timetodest = sec_to_hms(ttd)

		lastlm = store.node_dict[timezone][s_id]
		
		user_routes[uid]['route_network'] = route_network_to_string(route_network)
		user_routes[uid]['source_id'] = store.node_dict[timezone][s_id].Lm
		user_routes[uid]['dest_id'] = store.node_dict[timezone][d_id].Lm
		user_routes[uid]['route_list'] = ','.join(route_list[1:])

		return json.dumps(user_routes[uid])
	else:
		return "415 Unsupported Media Type!!"+request.headers['Content-Type']

'''
Pre-process the database to create a directed graph of the complete network
'''
@app.route('/preprocessing', methods = ['GET'])
def api_preprocess():
	for i in range(1,5):
		store.node_dict.update({i:{}})
		store.edge_dict.update({i:{}})
		rows = sql.mysql_helper.get_all_landmarks(i)
		store.node_dict[i], store.edge_dict[i] = processor.preprocess_db.get_nodes_and_edges(rows)
	print len(store.node_dict.keys()), len(store.edge_dict.keys())
	return 'AllCompleted'

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5984)
