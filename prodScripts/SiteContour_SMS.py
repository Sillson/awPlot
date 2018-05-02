# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 10:41:31 2017

@author: Beau.Uriona
"""
from os import path, makedirs
import urllib.request as request
#from zeep import Client
#from zeep.transports import Transport
#from zeep.cache import InMemoryCache
import datetime
import plotly.graph_objs as go
import plotly.offline as py
import numpy as np
import simplejson as json
from itertools import chain
import time
from lib.awdbToolsJson import dataUrl, trimToOct1, getSaturation
py.init_notebook_mode(connected=True)

this_dir = path.dirname(path.abspath(__file__))
master_dir = path.dirname(this_dir)

#wsdl = r"https://wcc.sc.egov.usda.gov/awdbWebService/services?WSDL"
#transport = Transport(timeout=300,cache=InMemoryCache())
#awdb = Client(wsdl=wsdl,transport=transport,strict=False)

dt = datetime.datetime
date = datetime.date
today = dt.utcnow() - datetime.timedelta(hours=8)

def updtChart(site_meta):
    siteName = site_meta['name']
    site_triplet = site_meta['stationTriplet']
    meta = [site_meta]
    siteTriplet = site_triplet.split(':')
    state = siteTriplet[1]
    sensor = r"SMS"
    date_series = []
    print('Working on SMS Contour Chart for ' + siteName)
    
    date_series = [date(2015,10,1) + datetime.timedelta(days=x) for
                   x in range(0, 366)] # could use any year with a leap day  

    cscale=[[0.0, 'rgb(165,0,38)'], [0.1111111111111111, 'rgb(215,48,39)'],
             [0.2222222222222222, 'rgb(244,109,67)'],
             [0.3333333333333333, 'rgb(253,174,97)'],
             [0.4444444444444444, 'rgb(254,224,144)'],
             [0.5555555555555556, 'rgb(224,243,248)'],
             [0.6666666666666666, 'rgb(171,217,233)'],
             [0.7777777777777778, 'rgb(116,173,209)'],
             [0.8888888888888888, 'rgb(69,117,180)'], [1.0, 'rgb(49,54,149)']]
    eDate = today.date().strftime("%Y-%m-%d")
    if today.month > 9:
        sDateWY = date(today.year, 10, 1).strftime("%Y-%m-%d")    
    else:
        sDateWY = date(today.year-1, 10, 1).strftime("%Y-%m-%d")
          
    depths = {}
    for site in meta:
        elements = awdb.service.getStationElements(site['stationTriplet'],sDateWY,eDate)
        siteDepths = []
        for element in elements:
            if element.elementCd == sensor and element.ordinal == 1 and element.duration == "DAILY":
                siteDepths.append(element.heightDepth)
        depths[site['stationTriplet']] = siteDepths
    SMSPlotData = []        
    
    if meta:
        for validSite in meta:
            trace = []
            barPrec = []
            barSWE = []
            depthVals = []
            plotData = []
            SMSPlotData = []
            date_series = []
            y = []
            for depth in depths[validSite['stationTriplet']]:
                y.extend([depth.value])
            if len(y) > 1:
                smsDepth = [float(min(y))+(0.5*float((y[-1]-y[-2]))),0]
            else:
                smsDepth = [float(min(y))*1.5,0]                
            for i in y:
                triplet = validSite['stationTriplet']
                for depth in depths[triplet]:
                    data = []
                    if depth.value == i and depth.unitCd == r'in':
                        sDate = date(dt.strptime(validSite['beginDate'],"%Y-%m-%d %H:%M:%S").year,
                                     10, 1).strftime("%Y-%m-%d")                                                   
                        url = '/'.join([dataUrl,'DAILY', sensor, 
                                        triplet.replace(':','_') + '.json'])
                        with request.urlopen(url) as d:
                            jTemp = json.loads(d.read().decode())
                        data.append(trimToOct1(jTemp))
                        
                        if data[0]['beginDate']:
                            sDate = date(dt.strptime(data[0]['beginDate'],"%Y-%m-%d %H:%M:%S").year,
                                         10, 1).strftime("%Y-%m-%d")
                            date_series = [dt.strptime(sDate,"%Y-%m-%d") + 
                                           datetime.timedelta(days=x) for 
                                           x in range(0, (dt.strptime(eDate,"%Y-%m-%d")-
                                                          dt.strptime(sDate,"%Y-%m-%d")).days+1)]
                            sliderDates= list(chain([(date_series[0])] + [date_series[-1]]))
                            if len(date_series) > 365:
                                currDates= list(chain([date_series[-365]] + [date_series[-1]]))
                            else:
                                currDates= list(chain([date_series[0]] + [date_series[-1]]))
                            if hasattr(data[0],r'values'):
                                sat = getSaturation(i,validSite['stationTriplet'])
                                siteDepthData = np.array(data[0]['values'], dtype=np.float)
                                plotData = [100*(c/int(sat)) if 
                                            c else np.nan for c in siteDepthData]
                                plotData[:] = [100 if c and c > 100 else c for c
                                        in plotData]
                                if i == max(y):
                                    SMSPlotData.extend([plotData])
                                    depthVals.extend([0])
                                SMSPlotData.extend([plotData])
                                depthVals.extend([i])
            dataPrec = []
            url = '/'.join([dataUrl,'DAILY', 'PREC', 
                            triplet.replace(':','_') + '.json'])
            try:
                with request.urlopen(url) as d:
                    jTemp = json.loads(d.read().decode())
                dataPrec.append(trimToOct1(jTemp))
            except:
                dataPrec = [{"values": []}]
#might need to deal with mismatched start date between SMS and PREC
            dataSWE = []
            url = '/'.join([dataUrl,'DAILY', 'WTEQ', 
                            triplet.replace(':','_') + '.json'])
            try:
                with request.urlopen(url) as d:
                    jTemp = json.loads(d.read().decode())
                dataSWE.append(trimToOct1(jTemp))
            except:
                dataSWE = [{"values": []}]
            maxPrecRng = 5
            if dataPrec[0]['values']:
                precValues = np.array(dataPrec[0]['values'], dtype=np.float)
                precDelta = list(np.diff(precValues))
                if precDelta:
                    maxPrecRng = list(chain([0], [3 * np.nanmax(precDelta)]))
                    precDelta.extend([0])
                    barPrec = go.Bar(x=date_series,y=precDelta,yaxis='y2',
                                     showlegend=True,
                                     marker=dict(color='rgba(0,0,0,0.60)'),
                                     name='Daily Precip.')
            if dataSWE[0]['values']:
                sweValues = np.array(dataSWE[0]['values'], dtype=np.float)
                sweDelta = list(np.diff(sweValues))
                sweDeltaNeg = [round(-1*c,1) if 
                               c < 0 else np.nan for c in sweDelta]
                sweDeltaNeg.extend([0])
                barSWE = go.Bar(x=date_series,y=sweDeltaNeg,yaxis='y2',
                                showlegend=True,
                                marker=dict(color='rgba(0,0,0,0.35)'),
                                name='SWE melt')    
            if data[0]['values']:
                trace = go.Heatmap(z=SMSPlotData,x=date_series,y=depthVals,
                                   connectgaps=True,zsmooth='best',
                                   colorbar=dict(title='% Saturation',
                                                 titleside='right',x=1.125),
                                                 colorscale=cscale,
                                                 hoverinfo='none')
            annoText = str(validSite['countyName'] + r' County, ' + state +
                           r'. Elev = ' + 
                           str(int(round(validSite['elevation'],0))) +
                           r', Lat = ' + str(round(validSite['latitude'],3)) +
                           r', Long = ' + str(round(validSite['longitude'],3)))
            
            layout = go.Layout(
                    images= [dict(
                        source= "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/US-NaturalResourcesConservationService-Logo.svg/2000px-US-NaturalResourcesConservationService-Logo.svg.png",
                        xref="paper",
                        yref="paper",
                        x= 0,
                        y= 0.9,
                        xanchor="left", yanchor="bottom",
                        sizex= 0.4,
                        sizey= 0.1,
                        opacity= 0.75,
                        layer= "above"
                    )],
                    annotations=[dict(
                        font=dict(size=10),
                        text=annoText,
                        x=0,y=-0.31, 
                        yref='paper',xref='paper',
                        align='left',
                        showarrow=False
                    )],    
                showlegend = True,
                legend=dict(orientation="h",x=0.5,y=1.1),
                barmode='stack',
                title='Soil Moisture at ' + siteName,
                height=622, width=700, autosize=False,
                yaxis=dict(title=r'Soil Depth (in.)',range=smsDepth,
                           tickformat="0f", hoverformat='.1f',),
                yaxis2=dict(
                        title=r'Daily Incremental Precip./Snow Melt (in.)',
                        overlaying='y',
                        side='right',
                        anchor='free',
                        position=1,
                        range=maxPrecRng,
                        tickformat="0f",
                        hoverformat='.1f',),
                xaxis=dict(
                    range=currDates,
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1,
                                 label='1m',
                                 step='month',
                                 stepmode='backward'),
                            dict(count=6,
                                 label='6m',
                                 step='month',
                                 stepmode='backward'),
                            dict(count=1,
                                 label='1y',
                                 step='year',
                                 stepmode='backward'),
                            dict(count=3,
                                 label='3y',
                                 step='year',
                                 stepmode='backward'),
                            dict(label='POR', step='all')
                        ])
                    ),
                    rangeslider=dict(thickness=0.1,range=sliderDates),
                    type='date'
                )
                )
        plots = [trace, barPrec, barSWE]
        figPlots = []
        for plot in plots:
            if plot:
                figPlots.extend([plot])
        return {'data': figPlots,
                'layout': layout}

if __name__ == '__main__':
    states = [r"UT",r"NV_CA",'AK','AZ','CA','CO','ID','MT','NM','OR','WA','WY']
    networks = ['SNTL','SCAN','SNTLT']
    for state in states:
        sensor = r"SMS"
        url = '/'.join([dataUrl,'metadata', sensor, 'metadata.json'])
        with request.urlopen(url) as data:
            meta = json.loads(data.read().decode())
        
        meta[:] = [x for x in meta if 
            x['stationTriplet'].split(':')[1] in state and 
            x['stationTriplet'].split(':')[2] in networks]
        
        for site in meta:
            
            bt = time.time()
            siteName = site['name']
            dirPath = path.join(master_dir, 'siteCharts','Contour', sensor, state)
            plotName = path.join(dirPath, siteName + r'.html')
            makedirs(dirPath, exist_ok=True)
            try:
                fig = go.Figure(updtChart(site))
                py.plot(fig, filename=plotName, auto_open=False,
                        show_link=False, include_plotlyjs=False)
                bodyStr = r'<body style="background:url(https://www.wcc.nrcs.usda.gov/ftpref/states/ut/iCharts/misc/gears.gif) no-repeat 290px 250px;width:700px;height:622px;"><script src="https://www.wcc.nrcs.usda.gov/ftpref/states/ut/iCharts/misc/plotly.js"></script>'
                with open(plotName) as plotFile:
                    plotStr = plotFile.read().replace('<body>', bodyStr)
                with open(plotName, 'w') as newPlotFile:
                    newPlotFile.write(plotStr)
            except:
                print('     Something went wrong, no chart created')
            print(f'     in {round(time.time()-bt,2)} seconds')