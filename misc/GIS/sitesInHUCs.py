# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 13:09:14 2017

@author: Beau.Uriona
"""

from suds.client import Client
import datetime
import csv

def isActive(x):
    if dt.strptime(x.endDate, "%Y-%m-%d %H:%M:%S").date() > today.date():
        return True

dt = datetime.datetime
date = datetime.date
today = dt.today()
wsdl = r"https://wcc.sc.egov.usda.gov/awdbWebService/services?WSDL"
svc_url = r"https://wcc.sc.egov.usda.gov/awdbWebService/services" 
awdb = Client(wsdl) #, location=svc_url, cache=None)
networks = [r'SNTL',r'SCAN',r'SNTLT']
sensor = r"WTEQ"
duration = r"DAILY"
states = [r"UT", r"NV", r"CA"]
normType = r'NORMAL'
siteList = []
for state in states:
    stations = awdb.service.getStations(
            "*", state, networks,"*","*",-1000,1000,-1000,1000,0,29000,
            "*",1,None,True)
    siteList.extend(stations)

meta = awdb.service.getStationMetadataMultiple(siteList)
meta[:] = [x for x in meta if isActive(x)]

hucList = list(set([x.huc[:8] for x in meta]))

hucDict = {}
for huc in hucList:
    sitesInHUC = []
    sitesInHUC = [x.stationTriplet for x in meta if x.huc[:8] == huc]
    hucDict[huc] = sitesInHUC
    
with open(r'utHUCs6_8.csv', 'r') as f:
    reader = csv.reader(f)
    hucNames = {rows[1]:rows[0] for rows in reader}

with open(r'basinDef_HUC.csv', 'w') as f:
    for key,item in hucDict.items():
        f.write(hucNames.get(str(key)) + ',' + ";".join(str(x) for x in item) + ',' + str(key) + "\n") 
