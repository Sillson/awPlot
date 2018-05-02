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
from scipy import stats
from itertools import chain
import warnings
import math
import time
from lib.awdbToolsJson import dataUrl, trimToOct1, padMissingData, ordinal, get_last_non_zero_index
py.init_notebook_mode(connected=True)

this_dir = path.dirname(path.abspath(__file__))
master_dir = path.dirname(this_dir)

#wsdl = r"https://wcc.sc.egov.usda.gov/awdbWebService/services?WSDL"
#transport = Transport(timeout=300,cache=InMemoryCache())
#awdb = Client(wsdl=wsdl,transport=transport,strict=False)

dt = datetime.datetime
date = datetime.date
today = dt.utcnow() - datetime.timedelta(hours=8)

def updtChart(site_triplet, siteName):
    print('Working on WTEQ POR Chart for ' + siteName)
    statsData = []
    minData = []
    maxData = []
    meanData = []
    lowestData = []
    highestData = []
    lowData = []
    highData = []
    sliderDates = []
    meanData = []
    trace = []
    sitePlotData = []
    PORplotData = []
    sitePlotNormData = []
    validTrip = [site_triplet]
    
    sensor = r"WTEQ"
    date_series = [date(2015,10,1) + datetime.timedelta(days=x)
                        for x in range(0, 366)] #could use any year with a leap day
    if validTrip:   
        normData = []
        for triplet in validTrip: 
            url = '/'.join([dataUrl,'normals', 'DAILY', sensor, 
                            triplet.replace(':','_') + '.json'])
            with request.urlopen(url) as d:
                jTemp = json.loads(d.read().decode())
            normData.append(jTemp)

        sitePlotNormData = np.array(normData[0]['values'], dtype=np.float)
    sitePlotNormData = sitePlotNormData.tolist()                     
    beginDateDict = {}
    for siteMeta in meta:
        beginDateDict.update(
                {str(siteMeta['stationTriplet']) : 
                    dt.strptime(str(siteMeta['beginDate']),
                                "%Y-%m-%d %H:%M:%S")}) 
    
    siteBeginDate = min(beginDateDict.values())

    sYear = siteBeginDate.year
    if siteBeginDate.year > sYear:
        if siteBeginDate.month < 10:
            sYear = siteBeginDate.year
        else:
            if siteBeginDate.month == 10 and siteBeginDate.day == 1:
                sYear = siteBeginDate.year
            else:
                sYear = siteBeginDate.year + 1
    
    sDate = date(sYear, 10, 1).strftime("%Y-%m-%d")             
    eDate = today.date().strftime("%Y-%m-%d")

    data = []
    for triplet in validTrip: 
        url = '/'.join([dataUrl,'DAILY', sensor, 
                        triplet.replace(':','_') + '.json'])
        with request.urlopen(url) as d:
            jTemp = json.loads(d.read().decode())
        data.append(trimToOct1(jTemp))

    for dataSite in data:
        if dataSite:
            padMissingData(dataSite,sDate,eDate)
            
    sitePlotData = np.array(data[0]['values'], dtype=np.float)

    PORplotData = list([sitePlotData[i:i+366] 
                    for i in range(0,len(sitePlotData),366)])

    allButCurrWY = list(PORplotData)
    del allButCurrWY[-1]
    statsData = list(map(list,zip(*allButCurrWY)))
    
    if len(statsData[0]) > 1:
        statsData[151] = statsData[150]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            minData = [np.nanmin(a) for a in statsData]
            maxData = [np.nanmax(a) for a in statsData]
            meanData = [np.nanpercentile(a,50) for a in statsData]        
            lowestData = [np.nanpercentile(a,10) for a in statsData]
            highestData = [np.nanpercentile(a,90) for a in statsData]
            lowData = [np.nanpercentile(a,30) for a in statsData]
            highData = [np.nanpercentile(a,70) for a in statsData]
        future_date_pad = 14
        if len(PORplotData[-1]) > 351: 
            future_date_pad = 366 - len(PORplotData[-1]) - 1
        sliderDates = list(chain([(date_series[0])] + 
                                  [date_series[get_last_non_zero_index(
                                          maxData[0:305]) + future_date_pad]]))
    else:
        sliderDates = list(chain([(date_series[0])] + 
                                  [date_series[-1]]))

    if len(PORplotData) > 0:
        for index, i in enumerate(PORplotData):
            if index == len(PORplotData)-1:
                trace.extend(
                        [go.Scatter(
                                x=date_series,y=i,
                                name=str(sYear + index + 1),
                                visible=True,connectgaps=True,
                                line=dict(color='rgb(0,0,0)'))])
            elif np.nansum(i) > 0:
                trace.extend(
                        [go.Scatter(x=date_series,y=i,
                                    name=str(sYear + index + 1),
                                    visible='legendonly',
                                    connectgaps=True)])
    if meanData:
        if lowestData:
            trace.extend(
                    [go.Scatter(x=date_series,y=minData
                                ,legendgroup='centiles',name=r'Min',
                                visible=True,mode='line',
                                line=dict(width=0),connectgaps=True,
                                fillcolor='rgba(237,0,1,0.15)',
                                fill='none',showlegend=False,
                                hoverinfo='none')])       
            trace.extend(
                    [go.Scatter(x=date_series,y=lowestData
                                ,legendgroup='centiles',name=r'10%',
                                visible=True,mode='line',
                                line=dict(width=0),connectgaps=True,
                                fillcolor='rgba(237,0,1,0.15)',
                                fill='tonexty',showlegend=False,
                                hoverinfo='none')])
        if lowData:
            trace.extend(
                    [go.Scatter(x=date_series,y=lowData,
                                legendgroup='centiles',name=r'30%',
                                visible=True,mode='line',
                                line=dict(width=0),connectgaps=True,
                                fillcolor='rgba(237,237,0,0.15)',
                                fill='tonexty',showlegend=False,
                                hoverinfo='none')])
        if highData:
            trace.extend(
                    [go.Scatter(x=date_series,y=highData,
                                legendgroup='centiles',
                                name=r'Stats. Shading',
                                visible=True,mode='line',
                                line=dict(width=0),connectgaps=True,
                                fillcolor='rgba(115,237,115,0.15)',
                                fill='tonexty',showlegend=True,
                                hoverinfo='none')])
        if highestData:
            trace.extend(
                    [go.Scatter(x=date_series,y=highestData,
                                legendgroup='centiles',connectgaps=True,
                                name=r'90%',visible=True
                                ,mode='line',line=dict(width=0),
                                fillcolor='rgba(0,237,237,0.15)',
                                fill='tonexty',showlegend=False,
                                hoverinfo='none')])
            trace.extend(
                    [go.Scatter(x=date_series,y=maxData
                                ,legendgroup='centiles',name=r'Max',
                                visible=True,mode='line',
                                line=dict(width=0),connectgaps=True,
                                fillcolor='rgba(1,0,237,0.15)',
                                fill='tonexty',showlegend=False,
                                hoverinfo='none')])

    if minData:
        trace.extend(
                [go.Scatter(x=date_series,y=minData,
                            name=r'Min',visible=True,
                            hoverinfo='none',connectgaps=True,
                            line=dict(color='rgba(237,0,0,0.5)'))])
    
    if len(sitePlotNormData) > 0:
        trace.extend(
                [go.Scatter(x=date_series,
                            y=sitePlotNormData,
                            name=r"Normal ('81-'10)",connectgaps=True,
                            visible=True,hoverinfo='none',
                            line=dict(color='rgba(0,237,0,0.4)'))])
    
    if meanData:
        if len(sitePlotNormData) > 0:
            trace.extend(
                    [go.Scatter(x=date_series,
                                y=meanData,name=r'Normal (POR)',
                                visible='legendonly',
                                hoverinfo='none',
                                connectgaps=True,
                                line=dict(color='rgba(0,237,0,0.4)',
                                          dash='dash'))])
        else:
            trace.extend(
                    [go.Scatter(x=date_series,y=meanData,
                                name=r'Normal (POR)',connectgaps=True,
                                visible=True,hoverinfo='none',
                                line=dict(color='rgba(0,237,0,0.4)'))])
    if maxData:
        trace.extend(
                [go.Scatter(x=date_series,y=maxData,
                            name=r'Max',visible=True,
                            hoverinfo='none',connectgaps=True,
                            line=dict(color='rgba(0,0,237,0.4)'))])
    
    annoText = str(r"Statistical shading breaks at 10th, 30th, 50th, 70th, and 90th Percentiles<br>Normal ('81-'10) - Official median calculated from 1981 thru 2010 data <br>Normal (POR) - Unofficial mean calculated from Period of Record data <br>For more information visit: <a href='https://www.wcc.nrcs.usda.gov/normals/30year_normals_data.htm'>30 year normals calcuation description</a>")
    asterisk = ''
    if len(sitePlotNormData) == 0: 
        sitePlotNormData = meanData
        annoText = annoText + '<br>*POR data used to calculate Normals since no published 30-year normals available for this site'
        asterisk = '*'
    jDay = len(PORplotData[-1])-1
    if len(sitePlotNormData) == 0: 
        perNorm = r'N/A'
    else:
        perNorm = str('{0:g}'.format(100*round(
                PORplotData[-1][jDay]/sitePlotNormData[jDay],2)))
    perPeak = str('{0:g}'.format(100*round(
            PORplotData[-1][jDay]/max(sitePlotNormData),2)))
    if not math.isnan(PORplotData[-1][jDay]):
        centile = ordinal(int(round(
                stats.percentileofscore(
                        statsData[jDay],PORplotData[-1][jDay]),0)))
    else:
        centile = 'N/A'
        
    dayOfPeak = sitePlotNormData.index(max(sitePlotNormData))
    if jDay > dayOfPeak:
        tense = r'Since'
    else:
        tense = r'Until'
    daysToPeak = str(abs(jDay-dayOfPeak))
    annoData = str(r"Current" + asterisk + ":<br>% of Normal - " + 
                   perNorm + r"%<br>" +
                   r"% Normal Peak - " + perPeak + r"%<br>" +
                   r"Days " + tense + 
                   r" Normal Peak - " + daysToPeak + r"<br>"                      
                   r"Percentile Rank- " + centile)
    
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
                opacity= 0.5,
                layer= "above"
            )],
            annotations=[dict(
                font=dict(size=10),
                text=annoText,
                x=0,y=-0.41, 
                yref='paper',xref='paper',
                align='left',
                showarrow=False),
                dict(font=dict(size=10),
                text=annoData,
                x=0,y=0.9, 
                yref='paper',xref='paper',
                align='left',
                xanchor="left", yanchor="top",
                showarrow=False)],    
        legend=dict(traceorder='reversed',tracegroupgap=1,
                    bordercolor='#E2E2E2',borderwidth=2),
        showlegend = True,
        title='Snow Water Equivalent at<br>' + siteName,
        height=622, width=700, autosize=False,
        yaxis=dict(title=r'Snow Water Equivalent (in.)',hoverformat='.1f',
                   tickformat="0f"),
        xaxis=dict(
            range=sliderDates,
            tickformat="%b %e",
            rangeselector=dict(
                buttons=list([
                    dict(count=9,
                         label='Jan',
                         step='month',
                         stepmode='todate'),
                    dict(count=6,
                         label='Apr',
                         step='month',
                         stepmode='todate'),
                    dict(count=3,
                         label='July',
                         step='month',
                         stepmode='todate'),
                    dict(label='WY', step='all')
                ])
            ),
            rangeslider=dict(thickness=0.1),
            type='date'
        )
        )                           
    return {'data': trace,
            'layout': layout}

if __name__ == '__main__':
    states = [r"UT",r"NV_CA",'AK','AZ','CA','CO','ID','MT','NM','OR','WA','WY']
    networks = ['SNTL','SCAN','SNTLT']
    for state in states:
        sensor = r"WTEQ"
        url = '/'.join([dataUrl,'metadata', sensor, 'metadata.json'])
        with request.urlopen(url) as data:
            meta = json.loads(data.read().decode())
        
        meta[:] = [x for x in meta if 
            x['stationTriplet'].split(':')[1] in state and 
            x['stationTriplet'].split(':')[2] in networks]
        
        for site in meta:
            
            bt = time.time()
            site_triplet = site['stationTriplet']
            siteName = site['name']
            dirPath = path.join(master_dir, 'siteCharts','POR', sensor, state)
            plotName = path.join(dirPath, siteName + r'.html')
            makedirs(dirPath, exist_ok=True)
            try:
                fig = go.Figure(updtChart(site_triplet,siteName))
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
        
