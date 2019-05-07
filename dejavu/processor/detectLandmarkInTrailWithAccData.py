import sys
import __init__
from detection_util import peakdet, trailHasBreaker, gettimediff, std_dev
from numpy import var

limit = 3.0
ylimit = 5.0
zlimit = 10.5
tlimit = 20.0

def detect_stop(sensory, sensorz):
	if max(sensory) < ylimit:
		if len(filter(lambda z: z >= zlimit, sensorz)) < 3:
			return True

def detect_turns(comp_x):
	if abs(comp_x[-1] - comp_x[0]) > tlimit:
		return True

def detect_breaker(sensorz):
	peaks, dips = peakdet(sensorz)
	found = False
	pks = []
	loc = []
	dps = []
	dloc = []
	for pk in peaks:
		pks.append(pk[1])
		loc.append(pk[0])
	for dp in dips:
		dps.append(dp[1])
		dloc.append(dp[0])

	if len(pks) > 0 and len(dps) > 0:
		if min(loc) >= min(dloc):
			found = trailHasBreaker(loc, dloc, limit, sensorz)
		else:
			found = trailHasBreaker(dloc, loc, limit, sensorz)
	return (found)

def detect_landmark(sampledTrail, compsampledTrail, X, Y, Z):

	sensorx = []
	sensory = []
	sensorz = []

	comp_x = []

	for rd in compsampledTrail:
		l = rd.strip().split(',')
		comp_x.append(float(l[0]))

	for reading in sampledTrail:
		l1 = reading.strip().split(',')
		sensorx.append(float(l1[X]))
		sensory.append(float(l1[Y]))
		sensorz.append(float(l1[Z]))

	detected = ""

	#print X, Y, Z, len(sensory), len(sensorz)

	if detect_turns(comp_x):
		detected += "Turn"
	elif detect_stop(sensory, sensorz):
		detected += "Stop"
	elif detect_breaker(sensorz):
		detected += "Bumper"
	else:
		detected = "Normal"
	return detected
