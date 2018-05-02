#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 05:17:43 2017

@author: Beau.Uriona
"""
from os import path, makedirs
from zeep import Client
from zeep.transports import Transport
from zeep.cache import InMemoryCache
from zeep import helpers
import datetime
from queue import Queue
from threading import Thread
import simplejson as json
import time
import calendar as cal
this_dir = path.dirname(path.abspath(__file__))
master_dir = path.dirname(path.dirname(path.dirname(this_dir)))

wsdl = r"https://wcc.sc.egov.usda.gov/awdbWebService/services?WSDL"
transport = Transport(timeout=300,cache=InMemoryCache())
awdb = Client(wsdl=wsdl,transport=transport,strict=False)

dt = datetime.datetime
date = datetime.date
today = dt.utcnow() - datetime.timedelta(hours=8)
lastMonth = today - datetime.timedelta(days=30)
sDate = date(1900, 10, 1).strftime("%Y-%m-%d")
sDateHrly =  date(lastMonth.year, lastMonth.month, lastMonth.day).strftime("%Y-%m-%d")        
eDate = today.date().strftime("%Y-%m-%d 00:00:00")
duration = r"DAILY"

def isActive(x):
    if dt.strptime(x.endDate, "%Y-%m-%d %H:%M:%S").date() > today.date():
        return True
def isAbove(x,elev):
    if x.elevation >= elev:
        return True
def isBelow(x,elev):
    if x.elevation <= elev:
        return True
def isYearsOld(x,yrs):
    s = str(x.beginDate)
    c = dt.today().year - yrs
    if int(s[:4]) < c:
        return True
def nonLeapDaysBetween(_sDateLeap,_eDateLeap):
    nonLeapDays = 0    
    if _sDateLeap.month > 2:
        sYear = _sDateLeap.year + 1
    else:
        sYear = _sDateLeap.year
    if _eDateLeap.month < 3:
        eYear = _eDateLeap.year - 1
    else:
        eYear = _eDateLeap.year
    for t in range(sYear,eYear+1):
            if not cal.isleap(t): nonLeapDays += 1    
    return nonLeapDays

def getMetaData():
    networks = [r'SNTL',r'SCAN',r'SNTLT',r'USGS']
    sensors = [r"*",r"PREC",r"WTEQ",r"TAVG",r"SNWD",r"SMS",r"STO",r"BATT",
               r"SRDOO"]
    for sensor in sensors:
        bt = time.time()
        print("Working on station and metadata for sites with " + 
              sensor + "...")
        if sensor == r'SRDOO':
            forecasts = awdb.service.getForecastPoints('*','*',networks,
                                                       '*','*','*',True)
            stations = [x['stationTriplet'] for x in forecasts]
        else:
            stations = awdb.service.getStations(
                    "*", "*", networks,"*","*",-1000,1000,-1000,1000,0,29000,
                    sensor,1,None,True)
        if sensor == r"*": sensor = r"ALL"
        serialized_stations = helpers.serialize_object(stations)
        meta = awdb.service.getStationMetadataMultiple(stations)
        meta[:] = [x for x in meta if isActive(x) and isYearsOld(x,1)]
        validTrip = [x.stationTriplet for x in meta]
        serialized_stations[:] = [x for x in serialized_stations if
                           x in validTrip]
        serialized_meta = helpers.serialize_object(meta)
        makedirs(path.join(this_dir,'metaData',sensor), exist_ok=True)
        fileName = path.join(this_dir,'metaData', sensor, 'stations')
        with open(fileName + '.json',"w") as json_out:
            json_out.write(json.dumps(serialized_stations))       
        fileName = path.join(this_dir,'metaData', sensor, 'metaData')
        with open(fileName + '.json',"w") as json_out:
            json_out.write(json.dumps(serialized_meta)) 
        print(f'     {round(time.time()-bt,2)} seconds for {sensor} metadata call')
        
def getForecastEquations():
    bt = time.time()
    print("Working on forecast equations...")
    networks = [r'USGS']
    forecasts = helpers.serialize_object(awdb.service.getForecastPoints('*','*',networks,
                                                                '*','*','*',True))
    forecast_triplets = [x['stationTriplet'] for x in forecasts]
    chunks = [forecast_triplets[x:x+50] for x in range(0, len(forecast_triplets), 50)]
    
#    equations = awdb.service.getForecastEquationsMultiple(forecast_triplets[-3:])
#    serialized_equations = helpers.serialize_object(equations)
#    for trip in forecast_triplets[-3:]:
#        json_out = []
#        for eq in serialized_equations:
#            print(trip,eq['stationTriplet'])
#            if eq['stationTriplet'] == trip:
#                json_out.extend([eq])
#        return json_out
    
    num_threads=4
    q = Queue(maxsize=0) 
    for i in range(num_threads):
        t = Thread(target=getEquations, args=(q,))
        t.daemon = True
        t.start()
    for sites in chunks:
        q.put(sites)
    q.join()
    print(f'     {round(time.time()-bt,2)} seconds for forecast equation call')
    
def getEquations(q):
    while True:
        forecast_triplets = q.get()
        equations = awdb.service.getForecastEquationsMultiple(forecast_triplets)
        serialized_equations = helpers.serialize_object(equations)
        for trip in forecast_triplets:
            fcst_json = []
            for eq in serialized_equations:
                if eq and eq['stationTriplet'] == trip:
                    fcst_json.extend([eq])
            makedirs(path.join(this_dir,'frcstEq'), exist_ok=True)
            fileName = path.join(this_dir,'frcstEq',
                                trip.replace(':','_'))
            with open(fileName + '.json',"w") as json_out:
                json_out.write(json.dumps(fcst_json))
                    
#            for equation in serialized_equations:
#                makedirs(path.join(this_dir,'frcstEq'), exist_ok=True)
#                fileName = path.join(this_dir,'frcstEq',
#                                    equation['stationTriplet'].replace(':','_'))
#                with open(fileName + '.json',"w") as json_out:
#                    json_out.write(json.dumps(equation))
        q.task_done()
        
def getSiteData(q):
    while True:
        site = q.get()
        chunkData = awdb.service.getData(site,sensor, 1, None, duration, False,
                                        sDate, eDate, True)
        for siteData in chunkData:
            serialized_data = helpers.serialize_object(siteData)
            if serialized_data['values']:
                beginDate = dt.strptime(serialized_data['beginDate'], 
                                        "%Y-%m-%d %H:%M:%S")
                endDate = serialized_data['endDate']
                if beginDate.day != 1 or beginDate.month != 10:
                    offsetYear = 0
                    if beginDate.month > 9: offsetYear = 1
                    newBeginDate = dt(beginDate.year + offsetYear,10,1)
                    offsetNonLeap = nonLeapDaysBetween(beginDate,newBeginDate)
                    deltaDate = (newBeginDate - beginDate).days + offsetNonLeap
                    serialized_data['beginDate'] = newBeginDate.strftime("%Y-%m-%d 00:00:00")
                    serialized_data['values'] = serialized_data['values'][deltaDate:]
                if endDate != eDate:
                    jsonEndDate = dt.strptime(endDate, 
                                        "%Y-%m-%d %H:%M:%S")
                    dataCallEndDate = dt.strptime(eDate, 
                                        "%Y-%m-%d %H:%M:%S")
                    offsetNonLeap = nonLeapDaysBetween(jsonEndDate,dataCallEndDate)
                    deltaDate = abs((dataCallEndDate - jsonEndDate).days) + offsetNonLeap
                    serialized_data['values'].extend([None]*deltaDate)
                    serialized_data['endDate'] = eDate
            makedirs(path.join(this_dir,sensor), exist_ok=True)
            fileName = path.join(this_dir,sensor,
                                 siteData.stationTriplet.replace(':','_'))
            with open(fileName + '.json',"w") as json_out:
                json_out.write(json.dumps(serialized_data))
        q.task_done()

def getSiteHourlyData(q):
    while True:
        site = q.get()
        chunkData = awdb.service.getInstantaneousData(site,sensor, ordinal,None,
                                        sDateHrly, eDate, "ALL", "ENGLISH")
        for i,siteData in enumerate(chunkData):
            serialized_data = helpers.serialize_object(siteData)
            makedirs(path.join(this_dir,'HOURLY',sensor + str(ordinal)), exist_ok=True)
            fileName = path.join(this_dir,'HOURLY',sensor + str(ordinal),
                                 site[i].replace(':','_'))
            with open(fileName + '.json',"w") as json_out:
                json_out.write(json.dumps(serialized_data))
        q.task_done()
        
def getSiteSoilsData(q):
    while True:
        site = q.get()
        chunkData = awdb.service.getData(site[0],sensor, 1, site[1],
                                         duration, False,
                                        sDate, eDate, True)
        for siteData in chunkData:
            serialized_data = helpers.serialize_object(siteData)
            if serialized_data['values']:
                beginDate = dt.strptime(serialized_data['beginDate'], 
                                        "%Y-%m-%d %H:%M:%S")
                endDate = serialized_data['endDate']
                if beginDate.day != 1 or beginDate.month != 10:
                    offsetYear = 0
                    if beginDate.month > 9: offsetYear = 1
                    newBeginDate = dt(beginDate.year + offsetYear,10,1)
                    offsetNonLeap = nonLeapDaysBetween(beginDate,newBeginDate)
                    deltaDate = (newBeginDate - beginDate).days + offsetNonLeap
                    serialized_data['beginDate'] = newBeginDate.strftime("%Y-%m-%d 00:00:00")
                    serialized_data['values'] = serialized_data['values'][deltaDate:]
                if endDate != eDate:
                    jsonEndDate = dt.strptime(endDate, 
                                        "%Y-%m-%d %H:%M:%S")
                    dataCallEndDate = dt.strptime(eDate, 
                                        "%Y-%m-%d %H:%M:%S")
                    offsetNonLeap = nonLeapDaysBetween(jsonEndDate,dataCallEndDate)
                    deltaDate = abs((dataCallEndDate - jsonEndDate).days) + offsetNonLeap
                    serialized_data['values'].extend([None]*deltaDate)
                    serialized_data['endDate'] = eDate
            makedirs(path.join(this_dir,sensor,str(abs(depth))), exist_ok=True)
            fileName = path.join(this_dir,sensor,str(abs(depth)),
                                 siteData.stationTriplet.replace(':','_'))
            with open(fileName + '.json',"w") as json_out:
                json_out.write(json.dumps(serialized_data))
        q.task_done()

def getNormData(q):
    normType = r'NORMAL'
    while True:
        site = q.get()
        chunkData1 = awdb.service.getCentralTendencyData(
                site,sensor,None,duration,
                True,10,1,12,31,normType)
        chunkData2 = awdb.service.getCentralTendencyData(
                site,sensor,None,duration
                ,True,1,1,9,30,normType)
        
        for i,siteData in enumerate(chunkData1):  
            c1 = helpers.serialize_object(siteData)
            c2 = helpers.serialize_object(chunkData2[i])
            if hasattr(siteData,'values'):
                c1['endDay'] = c2['endDay']
                c1['endMonth'] = c2['endMonth']
                c1['values'].extend(c2['values'])
            makedirs(path.join(this_dir,r'norms',sensor), exist_ok=True)
            fileName = path.join(this_dir,r'norms',
                                 sensor,site[i].replace(':','_'))
            with open(fileName + '.json',"w") as json_out:
                json_out.write(json.dumps(c1))
        q.task_done()

def getStreamflowData(sensor):
    print("Working on " + sensor + " POR data...")
    networks = [r'USGS']
    forecasts = awdb.service.getForecastPoints('*','*',networks,'*',
                                               '*','*',True)
    stations = [x['stationTriplet'] for x in forecasts]
    if stations:
        meta = awdb.service.getStationMetadataMultiple(stations)
        meta[:] = [x for x in meta if isActive(x) and isAbove(x, 1) and
            isBelow(x,30000) and isYearsOld(x,1)]
        validTrip = [x.stationTriplet for x in meta]
        chunks = [validTrip[x:x+25] for x in range(0, len(validTrip), 25)]
        
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
        print(f'     {round(time.time()-bt,2)} seconds for {sensor} data call')

def getMetData(sensor):
    print("Working on " + sensor + " POR data...")
    networks = [r'SNTL',r'SCAN',r'SNTLT']
    stations = awdb.service.getStations(
            "*", "*", networks,"*","*",-1000,1000,-1000,1000,0,29000,
            sensor,1,None,True)
    if stations:
        meta = awdb.service.getStationMetadataMultiple(stations)
        meta[:] = [x for x in meta if isActive(x) and isAbove(x, 1) and
            isBelow(x,30000) and isYearsOld(x,1)]
        validTrip = [x.stationTriplet for x in meta]
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
        print(f'     {round(time.time()-bt,2)} seconds for {sensor} data call')

def getHourlyData(sensor):
    print("Working on " + sensor + str(ordinal) + " previous month hourly data...")
    networks = [r'SNTL',r'SCAN',r'SNTLT']
    stations = awdb.service.getStations(
            "*", "*", networks,"*","*",-1000,1000,-1000,1000,0,29000,
            sensor,1,None,True)
    if stations:
        meta = awdb.service.getStationMetadataMultiple(stations)
        meta[:] = [x for x in meta if isActive(x) and isAbove(x, 1) and
            isBelow(x,30000) and isYearsOld(x,1)]
        validTrip = [x.stationTriplet for x in meta]
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
        print(f'     {round(time.time()-bt,2)} seconds for {sensor} data call')
        
def getMetNormData(sensor):
    print("Working on " + sensor + " NORM data...")
    networks = [r'SNTL',r'SCAN',r'SNTLT']
    stations = awdb.service.getStations(
            "*", "*", networks,"*","*",-1000,1000,-1000,1000,0,29000,
            sensor,1,None,True)
    if stations:
        meta = awdb.service.getStationMetadataMultiple(stations)
        meta[:] = [x for x in meta if isActive(x) and isAbove(x, 1) and
            isBelow(x,30000) and isYearsOld(x,1)]
        validTrip = [x.stationTriplet for x in meta]
        chunks = [validTrip[x:x+50] for x in range(0, len(validTrip), 50)]
        
        bt = time.time()
        
        num_threads=4
        q = Queue(maxsize=0) 
        for i in range(num_threads):
            t = Thread(target=getNormData, args=(q,))
            t.daemon = True
            t.start()
        for sites in chunks:
            q.put(sites)
        q.join()
        print(f'     {round(time.time()-bt,2)} seconds for {sensor} norm data call')

def getSoilsData(sensor,depth):
    getSoilsDataAtDepth(sensor,depth)
    
def getSoilsDataAtDepth(sensor,depth):
    networks = [r'SNTL',r'SCAN',r'SNTLT']

    print("Working on " + sensor + " @ " + str(abs(depth)) + '" depth POR data...')
    heightDepths = awdb.service.getHeightDepths()
    heightDepth = [x for x in heightDepths if 
                   x.unitCd == 'in' and x.value == depth]
    stations = awdb.service.getStations("*", "*", networks,"*","*",
                                        -1000,1000,-1000,1000,0,29000,
                                        sensor,1,None,True)
    if stations:
        meta = awdb.service.getStationMetadataMultiple(stations)
        meta[:] = [x for x in meta if isActive(x) and isAbove(x, 1) and
                    isBelow(x,30000) and isYearsOld(x,1)] 
        validTrip = [x.stationTriplet for x in meta]
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
        print(f'     {round(time.time()-bt,2)} seconds for {sensor} @ {str(abs(depth))}" depth data call')
        
if __name__ == '__main__':

    if today.day == 1 or today.day == 15:
        getMetaData()
        getForecastEquations()
        sensors = [r"PREC",r"WTEQ"]
        for sensor in sensors:
            getMetNormData(sensor)
    else:
        print('Skipped meta-data and normal call, not the 1st or 15th...')
        
    if True:#today.weekday() == 3:
        sensors = [r"PREC",r"WTEQ",r"TAVG",r"SNWD"]
        for sensor in sensors:
            getMetData(sensor)
            
        sensors = [r"SMS",r"STO"]
        for sensor in sensors:
            depths = [-2,-4,-8,-20,-40]
            for depth in depths:
                getSoilsData(sensor,depth)
        
        sensors = [r"SRDOO"]
        for sensor in sensors:
            getStreamflowData(sensor)
        
        sensors = [r"BATT"]
        ordinals = [1]
        for ordinal in ordinals:
            for sensor in sensors:
                getHourlyData(sensor) 
           
        with open(path.join(this_dir,'lastCall.txt'), 'w') as f:
            f.write(eDate)
    else:
        print('Skipped POR data refresh call, not Sunday...')