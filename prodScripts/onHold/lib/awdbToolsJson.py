# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 14:00:27 2017

@author: Beau.Uriona
"""
import datetime
import math
import pandas as pd
import calendar as cal
import numpy as np
import csv
import warnings
import json
import os

this_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(os.path.dirname(this_dir), r'static')

dt = datetime.datetime
date = datetime.date
today = dt.utcnow() - datetime.timedelta(hours=8)

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
def get_last_non_zero_index(d, default=366):
    rev = (len(d) - idx for idx, item in enumerate(reversed(d), 1) if item)
    return next(rev, default)
def ordinal(n):
    return "%d%s" % (n,"tsnrhtdd"[(math.floor(n//10)%10!=1)*(n%10<4)*n%10::4])
def fillMissingData(x,daysBack):
    daysBack = -1*daysBack
    if math.isnan(sum(x[daysBack:])) or not x:
        return x
    else:
        if len(x) < daysBack:
            daysBack = len(x)
        if math.isnan(x[-1]):
            x[-1] = [i for i in x if not math.isnan(i)][-1]
        y = x[daysBack:]
        x[:] = (x[:daysBack] + 
         pd.DataFrame(y).interpolate().values.ravel().tolist())
        return x
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
def padMissingData(x,_sDate,_eDate):
#    if not hasattr(x, r'values'): return x                                        
    eDateChkSite = dt.strptime(x['endDate'],"%Y-%m-%d %H:%M:%S").date()
    eDateChkBasin = dt.strptime(_eDate,"%Y-%m-%d").date()
    if eDateChkBasin > eDateChkSite:
        eDiff = ((eDateChkBasin - eDateChkSite).days + 
                 nonLeapDaysBetween(eDateChkSite, eDateChkBasin))
        x['values'] = list(x['values'] + [np.nan]*eDiff)
    sDateChkSite = dt.strptime(
            x['beginDate'],"%Y-%m-%d %H:%M:%S").date()
    sDateChkBasin =dt.strptime(_sDate,"%Y-%m-%d").date()
    if sDateChkBasin < sDateChkSite:
        sDiff = ((sDateChkSite - sDateChkBasin).days + 
                 nonLeapDaysBetween(sDateChkBasin, sDateChkSite))
        x['values'] = list([np.nan]*sDiff + x['values'])
    if sDateChkBasin > sDateChkSite: 
        sDiff = ((sDateChkBasin - sDateChkSite).days + 
                 nonLeapDaysBetween(sDateChkSite,sDateChkBasin))
        x['values'] = list(x['values'][sDiff:])
    return x
def createPRECProjTrace(i,jDay,lastValue,nanList):
    dailyData = list(i)
    if jDay < 151 and np.isnan(dailyData[151]):
            dailyData[151] = dailyData[150]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        if dailyData:
            projection = list(np.nancumsum(np.diff(dailyData[jDay:])))
            projTrace = nanList + [lastValue] + [lastValue + x for x in projection]
        else:
            projTrace = [np.nan]*366
    return projTrace
def createSWEProjTrace(i,jDay,lastValue,nanList):
    dailyData = list(i)
    if jDay < 151 and np.isnan(dailyData[151]):
            dailyData[151] = dailyData[150]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        peakSWEday = np.array(dailyData).argmax()
        meltOut = 0
        for index,day in enumerate(dailyData[peakSWEday:]):
            if day < 0.1:
                meltOut = index + peakSWEday
                break
        if meltOut > jDay:
            projection = list(np.nancumsum(np.diff(dailyData[jDay:meltOut])))
            projTrace = nanList + [lastValue] + [lastValue + x if abs(x) < 
                          lastValue or jDay < peakSWEday else np.nan for x in projection]
            projTrace[:] = [x if x >= 0 else np.nan for x in projTrace]
            meltList = [projTrace[-1]]
            for t in range(0,366-len(projTrace)):
                meltRate = 0.00008*(len(projTrace) + t)**2 - 0.0159*(len(projTrace) + t) + 0.7903
                if meltRate < meltList[-1]:
                    meltList.extend([meltList[-1] - meltRate])
                else:
                    meltList.extend([0])
            projTrace.extend(meltList)
        else:
            projTrace = [np.nan]*366
    return projTrace   
def getBasinSites(basinName,basinTable):
    siteListStr = basinTable.get(basinName).get(r'BasinSites')
    siteList = []
    if siteListStr:
        siteList = siteListStr.split(r';')
    if siteList:
        return siteList
def calcSMSAvg(dataSMS):
    smsAllAvg = {}
    allSites = list(dataSMS[-2].keys())
    for smsSite in allSites:
        sms40 = []
        sms20 = []
        sms8 = []
        sms4 = []
        sms2 = []
        if dataSMS[-40]: sms40 = list(dataSMS[-40][smsSite])
        if dataSMS[-20]: sms20 = list(dataSMS[-20][smsSite])
        if dataSMS[-8]: sms8 = list(dataSMS[-8][smsSite])
        if dataSMS[-4]: sms4 = list(dataSMS[-4][smsSite])
        if dataSMS[-2]: sms2 = list(dataSMS[-2][smsSite])
        if sms2 and sms4 and sms8 and sms20 and sms40:
            sms40[:] = [np.asarray(x)*(15/50) if not math.isnan(x) else
                 np.nan for x in sms40]
            sms20[:] = [np.asarray(x)*(15/50) if not math.isnan(x) else
                 np.nan for x in sms20]
            sms8[:] = [np.asarray(x)*(10/50) if not math.isnan(x) else
                np.nan for x in sms8]
            sms4[:] = [np.asarray(x)*(5/50) if not math.isnan(x) else
                np.nan for x in sms4]
            sms2[:] = [np.asarray(x)*(5/50) if not math.isnan(x) else
                np.nan for x in sms2]
            smsAll = list([sms40,sms20,sms8,sms4,sms2])
            smsAvg = [sum(x) for x in zip(*smsAll)]
        elif sms2 and sms8 and sms20:
            sms20[:] = [np.asarray(x)*(12/26) if not math.isnan(x) else
                 np.nan for x in sms20]
            sms8[:] = [np.asarray(x)*(9/26) if not math.isnan(x) else
                np.nan for x in sms8]
            sms2[:] = [np.asarray(x)*(5/26) if not math.isnan(x) else
                np.nan for x in sms2]
            smsAll = list([sms20,sms8,sms2])
            smsAvg = [sum(x) for x in zip(*smsAll)]
        elif sms2 and sms8:
            sms8[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms8]
            sms2[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms2]
            smsAll = list([sms8,sms2])
            smsAvg = [sum(x) for x in zip(*smsAll)]
        elif sms20 and sms8:
            sms8[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms8]
            sms20[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms20]
            smsAll = list([sms8,sms20])
            smsAvg = [sum(x) for x in zip(*smsAll)]
        elif sms20 and sms2:
            sms2[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms2]
            sms20[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms20]
            smsAll = list([sms2,sms20])
            smsAvg = [sum(x) for x in zip(*smsAll)]
        else:
            smsAvg = []
        smsAllAvg.update({str(smsSite) : list(smsAvg)})
    return smsAllAvg
def integrateSMS(dataSMS):
    smsAllAvg = {}
    allSites = list(dataSMS[-8].keys())
#    allSites20 = list(dataSMS[-20].keys())
#    allSites = allSites8 + list(set(allSites20) - set(allSites8)) 
    for smsSite in allSites:
        sms20 = []
        sms8 = []
        if dataSMS[-20]: sms20 = list(dataSMS[-20][smsSite])
        if dataSMS[-8]: sms8 = list(dataSMS[-8][smsSite])
        if sms20 and sms8:
            sms8[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms8]
            sms20[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms20]
            smsAll = list([sms8,sms20])
            smsAvg = [sum(x) for x in zip(*smsAll)]
        elif sms8:
            sms8[:] = [np.asarray(x) if not math.isnan(x) else
                np.nan for x in sms8]
            smsAvg = list(sms8)
        elif sms20:
            sms20[:] = [np.asarray(x) if not math.isnan(x) else
                np.nan for x in sms20]
            smsAvg = list(sms20)
        else:
            smsAvg = []
        smsAllAvg.update({str(smsSite) : list(smsAvg)})
    return smsAllAvg
def calcSTOAvg(dataSMS):
    smsAllAvg = {}
    allSites = list(dataSMS[-2].keys())
    for smsSite in allSites:
        sms8 = []
        sms4 = []
        sms2 = []
        if dataSMS[-8]: sms8 = list(dataSMS[-8][smsSite])
        if dataSMS[-4]: sms4 = list(dataSMS[-4][smsSite])
        if dataSMS[-2]: sms2 = list(dataSMS[-2][smsSite])
        if sms2 and sms4 and sms8:
            sms8[:] = [np.asarray(x)*(1/3) if not math.isnan(x) else
                np.nan for x in sms8]
            sms4[:] = [np.asarray(x)*(1/3) if not math.isnan(x) else
                np.nan for x in sms4]
            sms2[:] = [np.asarray(x)*(1/3) if not math.isnan(x) else
                np.nan for x in sms2]
            smsAll = list([sms8,sms4,sms2])
            smsAvg = [sum(x) for x in zip(*smsAll)]
        elif sms2 and sms8:
            sms8[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms8]
            sms2[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms2]
            smsAll = list([sms8,sms2])
            smsAvg = [sum(x) for x in zip(*smsAll)]
        elif sms2 and sms4:
            sms4[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms4]
            sms2[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms2]
            smsAll = list([sms4,sms2])
            smsAvg = [sum(x) for x in zip(*smsAll)]
        elif sms4 and sms8:
            sms8[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms8]
            sms4[:] = [np.asarray(x)*(1/2) if not math.isnan(x) else
                np.nan for x in sms4]
            smsAll = list([sms8,sms4])
            smsAvg = [sum(x) for x in zip(*smsAll)]
        elif sms2:
            sms2[:] = [np.asarray(x) if not math.isnan(x) else
                np.nan for x in sms2]
            smsAvg = list(sms2)
        elif sms4:
            sms4[:] = [np.asarray(x) if not math.isnan(x) else
                np.nan for x in sms4]
            smsAvg = list(sms4)
        elif sms8:
            sms8[:] = [np.asarray(x) if not math.isnan(x) else
                np.nan for x in sms8]
            smsAvg = list(sms8)
        else:
            smsAvg = []
        smsAllAvg.update({str(smsSite) : list(smsAvg)})
    return smsAllAvg
def getSaturation(depth,triplet,default=40):
    delimiter = ','
    satTable = {}
    with open(os.path.join(static_dir,'soilsSat.csv'), 'r') as data_file:
        data = csv.reader(data_file, delimiter=delimiter)
        headers = next(data)[1:]
        for row in data:
            temp_dict = {}
            name = row[0]
            values = []
            for x in row[1:]:
                values.append(x)
            for i in range(len(values)):
                temp_dict[headers[i]] = values[i]
            satTable[name] = temp_dict 
    siteTrip = triplet.split(':')
    site = satTable.get(siteTrip[0])
    sat = None
    if site:
        sat = site.get(str(depth))
    if sat:
        return sat
    else:
        return default
def getBasinTable():
    delimiter = ','
    basinTable = {}
    with open(os.path.join(static_dir,'basinDef.csv'), 'r') as data_file:
        data = csv.reader(data_file, delimiter=delimiter)
        headers = next(data)[1:]
        for row in data:
            temp_dict = {}
            name = row[0]
            while name in basinTable:
                name = name + '\u0080'
            values = []
            for x in row[1:]:
                values.append(x)
            for i in range(len(values)):
                temp_dict[headers[i]] = values[i]
            basinTable[name] = temp_dict
    return basinTable
def getGeoData(hucList):
    geoData = {'type' : 'FeatureCollection', 'features' : []}
    equalLength = False
    if all(len(i) == len(hucList[0]) for i in hucList):
        equalLength = True
        hucLength = str(len(hucList[0]))
        geojson_path = (os.path.join(static_dir,'GIS/huc' + hucLength + r'.json'))
        with open(geojson_path) as f:
            geoDataJson = json.loads(f.read())
    for huc in hucList:
        if not equalLength:
            hucLength = str(len(huc))
            geojson_path = (os.path.join(static_dir,'GIS/huc' + hucLength + r'.json'))
            with open(geojson_path) as f:
                geoDataJson = json.loads(f.read())
        geoDataTemp = [d for d in geoDataJson['features'] if
                    d['properties'].get('HUC' + hucLength) == huc]
        geoData['features'].extend(geoDataTemp)
    return geoData
statesLong = {
        'AK': 'AstatesLonglaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'Eastern Sierra',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}
if __name__ == '__main__':
    import os
    print('why are you running this?')
    dirpath = os.getcwd()
    print(os.path.basename(dirpath))