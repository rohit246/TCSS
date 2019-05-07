import sys
import math
from numpy import NaN, Inf, arange, isscalar, asarray, array
from datetime import datetime

def peakdet(v, delta=0.01, x = None):
    maxtab = []
    mintab = []
       
    if x is None:
        x = arange(len(v))
    
    v = asarray(v)
    
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    
    if not isscalar(delta):
        sys.exit('Input argument delta must be a scalar')
    
    if delta <= 0:
        sys.exit('Input argument delta must be positive')
    
    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN
    
    lookformax = True
    
    for i in arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]
        
        if lookformax:
            if this < mx-delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn+delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True
 
    return maxtab, mintab
    
def hasbreaker(l1, l2, limit, sampledlist, sensorz):
	i = 0
	p = l1[i]
	j = 0
	found = False
	bindex = -1
	for j in range(len(l2)):					
		while abs(p - l2[j]) > 1 and l2[j] < p:
			j+=1
			if j >= len(l2):
				break
		if j >= len(l2):
			break
		while l2[j] < p:
			if abs(sampledlist[l2[j]]-sampledlist[p]) > limit:
				found = True
				bindex = sensorz.index(sampledlist[p])
				break
			j+=1
			if j >= len(l2):
				break
		if found:
			break
		i+=1
		if i >= len(l1):
			break
		p = l1[i]
	return bindex, found
	
def trailHasBreaker(l1, l2, limit, sampledlist):
	i = 0
	p = l1[i]
	j = 0
	found = False
	for j in range(len(l2)):					
		while abs(p - l2[j]) > 1 and l2[j] < p:
			j+=1
			if j >= len(l2):
				break
		if j >= len(l2):
			break
		while l2[j] < p:
			if abs(sampledlist[l2[j]]-sampledlist[p]) > limit:
				found = True
				break
			j+=1
			if j >= len(l2):
				break
		if found:
			break
		i+=1
		if i >= len(l1):
			break
		p = l1[i]
	return found

def gettimediff(t1, t2):
	l1 = t1.split(':')
	l2 = t2.split(':')
	
	h1, m1, s1 = int(l1[0]), int(l1[1]), int(l1[2])
	h2, m2, s2 = int(l2[0]), int(l2[1]), int(l2[2])
	
	time1 = datetime(2015,4,15,h1,m1,s1)
	time2 = datetime(2015,4,15,h2,m2,s2)
	
	if time1 > time2:
		return (time1-time2).seconds
	else:
		return (time2-time1).seconds
		
def std_dev(x):
	mean=sum(x)/len(x)
	total=0
	for i in x:
		total+=(i-mean)**2
	var=total/len(x)
	std=math.sqrt(var)
	return std
