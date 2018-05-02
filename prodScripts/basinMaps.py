# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 13:55:01 2017

@author: Beau.Uriona
"""
from os import path, makedirs
import urllib.request as request
import simplejson as json
import plotly.graph_objs as go
import plotly.offline as py
#from zeep import Client
#from zeep.transports import Transport
#from zeep.cache import InMemoryCache
import datetime
import numpy as np
import warnings
import time
import csv
from lib.awdbToolsJson import dataUrl, getGeoData, getBasinSites

this_dir = path.dirname(path.abspath(__file__))
master_dir = path.dirname(this_dir)

mapBox_token = r'pk.eyJ1IjoiYmVhdXRhaCIsImEiOiJjajViNzZ5YngwaG9kMzZyeTRibDFrOGt4In0.6Ipwx1r4rm5I85yFo7gshg'
#wsdl = r"https://wcc.sc.egov.usda.gov/awdbWebService/services?WSDL"
#transport = Transport(timeout=300,cache=InMemoryCache())
#awdb = Client(wsdl=wsdl,transport=transport,strict=False)

dt = datetime.datetime
date = datetime.date
today = dt.utcnow() - datetime.timedelta(hours=8)

def updtChart(basinName, basinSites, basinTable):
    print('Working on ' + basinName + ' Map...')
    huc = basinTable.get(basinName).get('HUCS').replace(r';',r',')
    hucList = huc.split(r',')
    hucList[:] = [i for i in hucList if len(i) > 0]
    if hucList: 
        geoData = getGeoData(hucList)
    else:
        geoData = []
    networks = [r'SNTL',r'SCAN',r'SNTLT']
#    basinSites = getBasinSites(basin,basinTable)
    
    url = '/'.join([dataUrl,'metadata', 'ALL', 'metadata.json'])
    with request.urlopen(url) as data:
        meta = json.loads(data.read().decode())
    
    meta[:] = [x for x in meta if str.split(x['stationTriplet'],":")[2] in 
        networks and str.split(x['stationTriplet'],":")[0] in basinSites]
    
    validTrip = [x['stationTriplet'] for x in meta]
    validLong = [x['longitude'] for x in meta]
    validLat = [x['latitude'] for x in meta]
    validText = [str(x['name'] + r'<br>Lat - ' + str(x['latitude']) + r'<br>Long - ' +
                     str(x['longitude']) + r'<br>Elev - ' + str(x['elevation'])) for x in meta]
#    validAnno = [str(x.name) for x in meta]

    if validTrip:
        validLongSNTL = [x for index, x in enumerate(validLong) if
                 r'SNTL' in validTrip[index]]
        validLatSNTL = [x for index, x in enumerate(validLat) if
                 r'SNTL' in validTrip[index]]
        validLongSCAN = [x for index, x in enumerate(validLong) if
                 r'SCAN' in validTrip[index]]
        validLatSCAN = [x for index, x in enumerate(validLat) if
                 r'SCAN' in validTrip[index]]
        validLongSNTLT = [x for index, x in enumerate(validLong) if
                 r'SNTLT' in validTrip[index]]
        validLatSNTLT = [x for index, x in enumerate(validLat) if
                 r'SNTLT' in validTrip[index]]
        validTextSNTL = [x for index, x in enumerate(validText) if
                 r'SNTL' in validTrip[index]]
        validTextSCAN = [x for index, x in enumerate(validText) if
                 r'SCAN' in validTrip[index]]
        validTextSNTLT = [x for index, x in enumerate(validText) if
                 r'SNTLT' in validTrip[index]]
#            validAnno[:] = [x for index, x in enumerate(validAnno) if
#                     hasattr(normData[index], 'values')]
        
        zoomLat = abs(abs(np.max(validLat))-abs(np.min(validLat)))
        zoomLong = abs(abs(np.max(validLong))-abs(np.min(validLong)))
        if zoomLat > zoomLong: zoomLong = zoomLat
        with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                mapZoom = -1.35*np.log(float(zoomLat)) + 7
        if zoomLat == 0: mapZoom = 12
        trace = go.Data([
                go.Scattermapbox(
                        lat=validLatSNTL,
                        lon=validLongSNTL,
                        mode='markers',
                        marker=go.Marker(
                                symbol='circle',
                                size=9,
                                opacity=0.7),
                        text=validTextSNTL,
                        hoverinfo='text',
                        name='SNOTEL'
                        ),
                go.Scattermapbox(
                        lat=validLatSCAN,
                        lon=validLongSCAN,
                        mode='markers',
                        marker=go.Marker(
                                symbol='circle',
                                size=9,
                                opacity=0.7),
                        text=validTextSCAN,
                        hoverinfo='text',
                        name='SCAN'
                        ),
                go.Scattermapbox(
                        lat=validLatSNTLT,
                        lon=validLongSNTLT,
                        mode='markers',
                        marker=go.Marker(
                                symbol='circle',
                                size=9,
                                opacity=0.7),
                        text=validTextSNTLT,
                        hoverinfo='text',
                        name='SNOLITE'
                        )
                ],
        
        )
        annoText = ''
        if r'basin' in basinName: basinName = basinName.replace(r'basins',r'').replace(r'basin',r'')
        midLat = 0.5*float((max(validLat)+min(validLat)))
        midLong = 0.5*float((max(validLong)+min(validLong)))
        layout = go.Layout(images= [dict(
                    source= "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/US-NaturalResourcesConservationService-Logo.svg/2000px-US-NaturalResourcesConservationService-Logo.svg.png",
                    xref="paper",
                    yref="paper",
                    x= 0,
                    y= 0.975,
                    xanchor="left", yanchor="top",
                    sizex= 0.4,
                    sizey= 0.1,
                    opacity= 0.5,
                    layer= "above"
                )],
                annotations=[dict(
                    font=dict(size=10),
                    text=annoText,
                    x=1,y=1, 
                    yref='paper',xref='paper',
                    xanchor="left", yanchor="top",
                    align='left',
                    showarrow=False)],
                legend=dict(orientation="h",traceorder='reversed',tracegroupgap=1,
                        bordercolor='#E2E2E2',borderwidth=2,x=0,y=0.075),
                showlegend=True,
                title = r'Sites used in<br>'+ basinName + r'<br>Basin Calculations',
                height=622, width=700,
                autosize=True, 
                hovermode='closest',
                mapbox=dict(
                        accesstoken=mapBox_token,
                        style='outdoors',
                        layers=[dict(
                                sourcetype='geojson',
                                source=geoData,
                                type='fill',
                                color='#A9A9A9',
                                fill=dict(outlinecolor='#A9A9A9'),
                                opacity=0.4,
                                below='errythang')],
                        bearing=0,
                        center=dict(lat=midLat,lon=midLong),
                        pitch=0,
                        zoom=mapZoom                            
                    ),
        )
                                     
        return {'data': trace,
                'layout': layout}
        
if __name__ == '__main__':
    states = [r"UT",r"NV_CA",'AK','AZ','CA','CO','ID','MT','NM','OR','WA','WY']
    sensor = 'PREC'
    
    for state in states:
        delimiter = ','
        basinTable = {}
        basinDefDir = path.join(master_dir, r'static')
        basinDefFileName = path.join(basinDefDir,'basinDef_' + state + r'.csv')
        with open(basinDefFileName, 'r') as data_file:
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
                basinTable[name] = temp_dict
        
        for basinName in basinTable:
            bt = time.time()
            dirPath = path.join(master_dir, 'basinMaps', state)
            plotName = path.join(dirPath, basinName + r'.html')
            makedirs(dirPath, exist_ok=True)
            try:
                basinSites = getBasinSites(basinName, basinTable)
                fig = go.Figure(updtChart(basinName, basinSites, basinTable))
                py.plot(fig, filename=plotName, auto_open=False,
                        show_link=False, include_plotlyjs=False)
                bodyStr = r'<body style="background:url(https://www.wcc.nrcs.usda.gov/ftpref/states/ut/iCharts/misc/gears.gif) no-repeat 290px 250px;width:700px;height:622px;"><script src="https://www.wcc.nrcs.usda.gov/ftpref/states/ut/iCharts/misc/plotly.js"></script>'
                with open(plotName) as plotFile:
                    plotStr = plotFile.read().replace('<body>', bodyStr)
                with open(plotName, 'w') as newPlotFile:
                    newPlotFile.write(plotStr)
            except:
                print('     No sites with that sensor in that basin, no chart created')
            print(f'     in {round(time.time()-bt,2)} seconds')
