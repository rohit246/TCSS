import os
from math import *


class Bunch:
     def __init__(self,**items):
        self.__dict__.update(items)

def geoDistance(lat1,long1,lat2,long2):
    
    lat1=float(lat1)
    lat2=float(lat2)
    long1=float(long1)
    long2=float(long2)

    if lat1==lat2 and long1==long2:
        return 0
        
    q=radians(lat2-lat1)
    r=radians(long2-long1)
    lat2r=radians(lat2)
    lat1r=radians(lat1)
    a=sin(q/2)*sin(q/2)+cos(lat1r)*cos(lat2r)*sin(r/2)*sin(r/2)
    c=2*atan2(sqrt(a),sqrt(1-a))
    R=6371*1000
    d=R*c
    return d
    
def zeroSpeed(dataList):

    output=[]
    count=1
    indexPoint=dataList[0]
    index=0
    previous=indexPoint
    #print dataList
    #print previous
    for i,each in enumerate(dataList[1:]):
        if geoDistance(previous[0],previous[1],each[0],each[1])==0:
            #print each
            count+=1
            previous=each
        else:
            if count>=2:
                indexPoint.extend([count,index])                
                output.append(indexPoint)
                #raw_input("wait")
            index=i-1
            count=1
            indexPoint=each
            previous=each
    #print len(output)
       
    return output

def readFile(filename,header,seperator=","):

    output=[]
    fopen=open(filename)
    
    if header:
        fopen.readline()
    while True:
        line=fopen.readline()
        if line and len(line)>1:    #len(line)>1 : to avoid empty last line
            output.append(line.strip().split(seperator))
        else:
            fopen.close()
            break

    return output

            
            
                
                
            
        
        
