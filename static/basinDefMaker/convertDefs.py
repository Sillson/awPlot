# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 06:35:19 2018

@author: Beau.Uriona
"""

import pandas as pd
from os import path,walk,makedirs
import simplejson as json
import numpy as np

this_dir = path.dirname(path.abspath(__file__))
master_dir = path.dirname(this_dir)
hucs = list(reversed([4,6,8,10]))

basinFiles = []
for root, dirs, files in walk(this_dir):
    for file in files:
        if file.endswith('.xlsx'):
            basinFiles.append(file)

for basinFile in basinFiles:
    state = basinFile[:2] 
    print('Working on ' + state + ' basin def files...')
    df = pd.read_excel(path.join(this_dir,basinFile),dtype=np.dtype(str))
    
    basinNames = [n.replace('.1','').replace('.2','') for n in list(df)]
    
    transDict = {'BasinName':basinNames,'BasinSites':[],'HUCS':[]}
    
    for col in df:
        print('     ' + col.title())
        basinDef = [str(s) for s in df[col].tolist() if str(s) != 'nan']
        transDict['BasinSites'].append(';'.join(basinDef))
        hucID = ''
        for huc in hucs:
            hucFile = path.join(master_dir,'GIS','huc' + str(huc) + '.json')
            with open(hucFile) as f:
                jsonHUC = json.load(f)
                for h in jsonHUC['features']:
                    simpName = ' ' + col.replace('BASIN','').replace('RIVER','').strip().upper() + ' '
                    fromJsonName = ' ' + h['properties']['NAME'].upper() + ' '
                    huc2 = int(h['properties']['HUC' + str(huc)][:2])
                    if huc2 > 9 and fromJsonName and fromJsonName in simpName:
                        hucID = h['properties']['HUC' + str(huc)]
        transDict['HUCS'].append(hucID)
    
    dfTrans = pd.DataFrame.from_dict(transDict)
    makedirs(path.join(this_dir,'csvDefs'), exist_ok=True)
    exportName = path.join(this_dir,'csvDefs','basinDef_' + state + '.csv')
    dfTrans.to_csv(exportName,index=False)