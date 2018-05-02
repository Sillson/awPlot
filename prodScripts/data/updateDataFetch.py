#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 10:23:43 2017

@author: Beau.Uriona
"""
from os import path
from zeep import Client
from zeep.transports import Transport
from zeep.cache import InMemoryCache
from zeep import helpers
import datetime
from queue import Queue
from threading import Thread
import simplejson as json
import time
import glob

this_dir = path.dirname(path.abspath(__file__))
master_dir = path.dirname(path.dirname(path.dirname(this_dir)))

wsdl = r"https://wcc.sc.egov.usda.gov/awdbWebService/services?WSDL"
transport = Transport(timeout=300,cache=InMemoryCache())
awdb = Client(wsdl=wsdl,transport=transport,strict=False)

dt = datetime.datetime
date = datetime.date
today = dt.utcnow() - datetime.timedelta(hours=8)
duration = r"DAILY"

with open(path.join(this_dir,'lastCall.txt')) as f:
    updt_since = f.read()

sDate = updt_since             
eDate = today.strftime("%Y-%m-%d %H:00:00")

def getSiteData(q):
    while True:
        site = q.get()
        getUpdt = awdb.service.getDataInsertedOrUpdatedSince
        chunkData = getUpdt(site, sensor, 1, None,duration, False, 
                            sDate,eDate, updt_since,True)
        
        for siteData in chunkData:
            serialized_data = helpers.serialize_object(siteData)
            if serialized_data['dataContentList']:
                fileName = path.join(this_dir,sensor,
                                     siteData.stationTriplet.replace(':','_'))
                with open(fileName + '.json',"r") as f:
                    json_in = json.load(f)
                    endDate = dt.strptime(json_in['endDate'], 
                                          "%Y-%m-%d %H:%M:%S")
                    for updt in serialized_data['dataContentList']:
                        time_stamp_str = updt['timestamp']
                        time_stamp = dt.strptime(time_stamp_str, 
                                                 "%Y-%m-%d %H:%M:%S")
                        endDateTemp = dt.strptime(json_in['endDate'], 
                                          "%Y-%m-%d %H:%M:%S")
                        value = float(updt['value'])
                        time_delta = (time_stamp - endDate).days
                        if time_delta <= 0:
                            json_in['values'][time_delta - 1] = value
                        elif abs(time_stamp - endDateTemp).days == 1:
                            json_in['endDate'] = time_stamp_str
                            json_in['values'].extend([value])
                        else:
                            nans = abs(time_stamp - endDateTemp).days - 1
                            json_in['endDate'] = time_stamp_str
                            json_in['values'].extend(nans*[None])
                            json_in['values'].extend([value]) 
                with open(fileName + '.json',"w") as f:
                    json.dump(json_in,f)
        q.task_done()

def getSiteHourlyData(q):
    while True:
        site = q.get()
        getUpdt = awdb.service.getInstantaneousDataInsertedOrUpdatedSince
        chunkData = getUpdt(site, sensor, ordinal, None, sDate,eDate, 
                            updt_since,'ALL','ENGLISH')
        
        for i,siteData in enumerate(chunkData):
            serialized_data = helpers.serialize_object(siteData)
            if serialized_data['values']:
                fileName = path.join(this_dir,'HOURLY',sensor + str(ordinal),
                                     site[i].replace(':','_'))
                with open(fileName + '.json',"r") as f:
                    json_in = json.load(f)
                    for val in serialized_data['values']:
                        val = dict(val)
                        val['value'] = float(val['value'])
                        for oldVal in json_in['values']:
                            if oldVal['time'] == val['time']:
                                oldVal['value'] = val['value']
                        json_in['values'].extend([val])
                    seen = set()
                    new_json = []
                    for d in json_in['values']:
                        t = tuple(sorted(d.items()))
                        if t not in seen:
                            seen.add(t)
                            new_json.append(d)
                    json_in['values'] = new_json
                with open(fileName + '.json',"w") as f:
                    json.dump(json_in,f)
        q.task_done()
        
def getSiteSoilsData(q):
    while True:
        site = q.get()
        getUpdt = awdb.service.getDataInsertedOrUpdatedSince
        chunkData = getUpdt(site[0], sensor, 1, site[1], duration, False, 
                            sDate,eDate, updt_since,True)
        
        for siteData in chunkData:
            serialized_data = helpers.serialize_object(siteData)
            if serialized_data['dataContentList']:
                fileName = path.join(this_dir,sensor,
                                     str(abs(depth)),
                                     siteData.stationTriplet.replace(':','_'))
                with open(fileName + '.json',"r") as f:
                    json_in = json.load(f)
                    endDate = dt.strptime(json_in['endDate'], 
                                          "%Y-%m-%d %H:%M:%S")
                    for updt in serialized_data['dataContentList']:
                        time_stamp_str = updt['timestamp']
                        time_stamp = dt.strptime(time_stamp_str, 
                                                 "%Y-%m-%d %H:%M:%S")
                        endDateTemp = dt.strptime(json_in['endDate'], 
                                          "%Y-%m-%d %H:%M:%S")
                        value = float(updt['value'])
                        time_delta = (time_stamp - endDate).days
                        if time_delta <= 0:
                            json_in['values'][time_delta - 1] = value
                        elif abs(time_stamp - endDateTemp).days == 1:
                            json_in['endDate'] = time_stamp_str
                            json_in['values'].extend([value])
                        else:
                            nans = abs(time_stamp - endDateTemp).days - 1
                            json_in['endDate'] = time_stamp_str
                            json_in['values'].extend(nans*[None])
                            json_in['values'].extend([value]) 
                with open(fileName + '.json',"w") as f:    
                    json.dump(json_in,f)    
        q.task_done()
        
def getMetData(sensor):
    print("Working on " + sensor + ' data updated since ' + updt_since + '...')
    updt_files = glob.glob(path.join(this_dir,sensor, r'*.json'))
    validTrip = [path.basename(x).replace('.json','').replace('_',':') for
                x in updt_files]
    chunks = [validTrip[x:x+50] for x in range(0, len(validTrip), 50)]
    
    bt = time.time()
        
    num_threads=4
    q = Queue(maxsize=0) 
    for i in range(num_threads):
        t = Thread(target=getSiteData, args=(q,))
        t.daemon = True
        t.start()
    for sites in chunks:
        q.put(sites)
    q.join()
    print(f'     {round(time.time()-bt,2)} seconds for {sensor} data')

def getHourlyData(sensor):
    print("Working on " + sensor + str(ordinal) + ' data updated since ' + updt_since + '...')
    updt_files = glob.glob(path.join(this_dir,'HOURLY',sensor + str(ordinal), r'*.json'))
    validTrip = [path.basename(x).replace('.json','').replace('_',':') for
                x in updt_files]
    chunks = [validTrip[x:x+50] for x in range(0, len(validTrip), 50)]
    
    bt = time.time()
        
    num_threads=4
    q = Queue(maxsize=0) 
    for i in range(num_threads):
        t = Thread(target=getSiteHourlyData, args=(q,))
        t.daemon = True
        t.start()
    for sites in chunks:
        q.put(sites)
    q.join()
    print(f'     {round(time.time()-bt,2)} seconds for {sensor} data')
    
def getSoilsData(sensor,depth):
    getSoilsDataAtDepth(sensor,depth)

def getSoilsDataAtDepth(sensor,depth):
    print("Working on " + sensor + " @ " + str(abs(depth)) + 
          '" depth POR updated since ' + updt_since + '...')
    heightDepths = awdb.service.getHeightDepths()
    heightDepth = [x for x in heightDepths if 
                   x.unitCd == 'in' and x.value == depth]
    updt_files = glob.glob(path.join(this_dir,sensor,str(abs(depth)), r'*.json'))
    validTrip = [path.basename(x).replace('.json','').replace('_',':') for
                x in updt_files]
    chunks = [validTrip[x:x+50] for x in range(0, len(validTrip), 50)]
    
    bt = time.time()
        
    num_threads=4
    q = Queue(maxsize=0) 
    for i in range(num_threads):
        t = Thread(target=getSiteSoilsData, args=(q,))
        t.daemon = True
        t.start()
    for sites in chunks:
        q.put([sites,heightDepth])
    q.join()
    print(f'     {round(time.time()-bt,2)} seconds for {sensor} data')
    
if __name__ == '__main__':
    
    if True:#today.hour % 2 == 0:
        sensors = [r"PREC",r"WTEQ",r"TAVG"]#,r"SNWD"]
        for sensor in sensors:
            getMetData(sensor)
        
        sensors = [r"SMS"]#,r"STO"]
        for sensor in sensors:
            depths = [-2,-4,-8,-20,-40]
            for depth in depths:
                getSoilsData(sensor,depth)
        
        sensors = [r"BATT"]
        ordinals = [1]#,2]
        for ordinal in ordinals:
            for sensor in sensors:
                getHourlyData(sensor) 
            
        with open(path.join(this_dir,'lastCall.txt'), 'w') as f:
            f.write(eDate)
    else:
        print("Skipped update/insert data call, the hour is odd...")