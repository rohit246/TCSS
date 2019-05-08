import requests
import __init__
import processor.preprocess_db
from processor.node import node
from processor.edge import edge
from processor.nwgraph import nwgraph
import processor.dummy_processing
import processor.detectLandmarkInTrail
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
NON_VOLATILE_LANDMARKS = ['Turn']
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


def create_network_graph(edges, route, valid_lms):
	
	for n in graph.G.keys():
		for e in graph.G[n]:
			print e.l.Lm, e.d.Lm
	return graph

def get_new_route(uid, rlist, lastlm):

	tz = user_routes[uid]['timezone']
	g = create_network_graph(store.edge_dict[tz], rlist[0], user_routes[uid]['valid_landmarks'])
	user_routes[uid]['route_network'] = g
	for n in g.G.keys():
		if n.Lm != lastlm.Lm:
			continue
		else:
			return node, g
	return None, None
	

def search_nwgraph(uid, lm, lastlm):

	start = lastlm
	route_info = user_routes[uid]
	route_network = route_info['route_network']
	s_id = route_info['source_id']
	d_id = route_info['dest_id']
	timezone = route_info['timezone']
	op = open('serverlog.txt','a')
	op.write(lm+' ')
	if start == '':
		for n in route_network.G.keys():
			if n.Lm != store.node_dict[timezone][s_id].Lm:
				continue
			else:
				start = n
				break
	#op.write(lm+' '+start.Lm+' ')
	op.write(start.Lm+':')
	for e in route_network.G[start]:
		op.write(e.l.Lm+' '+ e.d.Lm + ' ' + str(e.g)+' '+ str(e.s) + ' '+ str(e.p)+' '+str((user_routes[uid]['current_time'] - user_routes[uid]['last_detection_time']).total_seconds())+'\n')
	new_ldl = ''
	for e in route_network.G[start]:
		success = False
		if lm in e.d.Lm:
			success = True
	if success:
		traverse_through = new_ldl
		op.write(' success '+e.d.Lm+'\n')
		op.write('___________________________________________________________________________________\n')
		return e.d
	op.write('\nfailure\n')
	op.write('___________________________________________________________________________________\n')
	return ''
	
def get_ttd(uid, curr_node):

	ttd = 0
	sd = 0
	count = 0
	
	route_info = user_routes[uid]
	route_network = route_info['route_network']
	s_id = route_info['source_id']
	d_id = route_info['dest_id']
	timezone = route_info['timezone']
	
	ttnlms = []
	for ed in route_network.G[curr_node]:
	    ttnlms.append(ed.g)
	
	while curr_node.Lm != store.node_dict[timezone][d_id].Lm:
		tl = defaultdict(float)
		pl = []
		for e in route_network.G[curr_node]:
			ttd += e.g
			pl.append(e.s)
		
	print ttd
	#user_routes[uid]['acc'] = 0
	mean_sd = np.mean(e.s)
	
	return ttd, mean_sd, max(ttnlms)

def getProcessedData(data,i):
	arr=[]
	for l in data:
		arr.append(float(l.split(",")[i]))
	rdata=[]
	l1 = preprocessor(arr)
	for l in l1:
		rdata.append(l)
	return rdata

def getLatLng(ldata,cdata,latlng):

	x=Symbol('x')
	lat1=latlng.split(",")[0]
	lon1=latlng.split(",")[1]
	xdata=getProcessedData(ldata,0)
	ydata=getProcessedData(ldata,1)
	zdata=getProcessedData(ldata,2)

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

def get_ttd_from_trail(ldata, cdata, uid, X, Y, Z):

	lm = processor.detectLandmarkInTrail.detect_landmark(ldata, cdata, X, Y, Z)
	
	if 'Normal' in lm or lm == user_routes[uid]['last_detected']:
		user_routes[uid]['last_landmark'].Pos = getLatLng(ldata,cdata,user_routes[uid]['last_landmark'].Pos)
		#user_routes[uid]['last_landmark'].Pos = snaptoroad(user_routes[uid]['last_landmark'].Pos)	
		res_string = sec_to_hms(user_routes[uid]['prev_ttd'])+'_sd_'+str(user_routes[uid]['prev_sd'])+'_latlng_'+user_routes[uid]['last_landmark'].Pos+'\n'
		#user_routes[uid]['prev_ttd'] -= 3.0
		
		return res_string

	user_routes[uid]['last_detected'] = lm
	
	searched_lm = search_nwgraph(uid, lm.strip(), user_routes[uid]['last_landmark'])
	if searched_lm == '':
		user_routes[uid]['last_landmark'].Pos = getLatLng(ldata,cdata,user_routes[uid]['last_landmark'].Pos)
		#user_routes[uid]['last_landmark'].Pos = snaptoroad(user_routes[uid]['last_landmark'].Pos)
		res_string = sec_to_hms(user_routes[uid]['prev_ttd'])+'_sd_'+str(user_routes[uid]['prev_sd'])+'_latlng_'+user_routes[uid]['last_landmark'].Pos+'$$$$'+lm+'\n'
		user_routes[uid]['failure'] += 1
		#user_routes[uid]['prev_ttd'] -= 3.0
	else:
		user_routes[uid]['acc'] = 0
		user_routes[uid]['last_landmark'] = searched_lm
		ttd, mean_sd, timetonextlm = get_ttd(uid, user_routes[uid]['last_landmark'])
		
		res_string = sec_to_hms(ttd)+'_sd_'+str(mean_sd)+'_latlng_'+user_routes[uid]['last_landmark'].Pos+'$$'+lm+'\n'
		
		user_routes[uid]['prev_ttd'] = ttd
		user_routes[uid]['prev_sd'] = mean_sd
		user_routes[uid]['ttnlm'] = timetonextlm
		user_routes[uid]['failure'] = 0
		user_routes[uid]['last_detection_time'] = user_routes[uid]['current_time']
	
	if user_routes[uid]['failure'] != 0:
		g = user_routes[uid]['route_network']
		if user_routes[uid]['failure'] > FAILURE_SWITCH_ROUTE:
			rlist = user_routes[uid]['route_list']
			g = user_routes[uid]['route_network']
			if len(rlist) > 0:
				okroute = False
				while len(rlist) > 0 and okroute == False:
					llm, g = get_new_route()
					if llm:
						user_routes[uid]['last_landmark'] = llm
						for mlm in user_routes[uid]['missed_lms']:
							for e in g.G[user_routes[uid]['last_landmark']]:
								if lm in e.d.Lm:
									okroute = True
									break
							if okroute:
								break
				if okroute:
					user_routes[uid]['route_network'] = g
	return res_string

def get_orientations(acc):

	accx = []
	accy = []
	accz = []
	X,Y,Z = 0,1,2
	for a in acc:
		l1 = a.split(',')
		accx.append(float(l1[0]))
		accy.append(float(l1[1]))
		accz.append(float(l1[2]))
	avgs = [sum(accx)/len(accx),sum(accy)/len(accy),sum(accz)/len(accz)]
	Z = avgs.index(max(avgs))
	if Z == 1:
		X = 0
		Y = 2
	elif Z == 0:
		X = 1
		Y = 2
	return X,Y,Z


## Route Methods
'''
App route which is called when a sample is sent from the client.
Gets the sample trail, processes it and returns the time to destination to the client
'''
def api_ttd(uid, acc, lacc, comp):
	user_routes[uid]['current_time'] = datetime.strptime(date+' '+request.json['time'], "%Y-%m-%d %H:%M:%S")
	X,Y,Z = get_orientations(acc)
	ttd = get_ttd_from_trail(lacc, comp, uid, X, Y, Z)
	return ttd



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
	app.run(debug=True)
