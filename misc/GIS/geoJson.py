# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 10:43:25 2017

@author: Beau.Uriona
"""

import json

geojson_path = r'HUC6_8.geojson'
geojsonbasin_path = r'utHUCs6_8.csv'

with open(geojson_path) as f:
    geoData = json.loads(f.read())
    geoData['features'][:] = [d for d in geoData['features'] if d['properties'].get('huc')[:2] == '16' or d['properties'].get('huc')[:2] =='14' or d['properties'].get('huc')[:2] =='15' or d['properties'].get('huc')[:2] =='17' or d['properties'].get('huc')[:2] =='18']
    
hucList = [(d['properties']['name'] + r',' + d['properties']['huc']) for d in geoData['features']]

with open(geojsonbasin_path,'w') as f:
    for x in hucList:
        f.write(str(x).replace("'",'').replace("[","").replace("]","")+'\n')
    



    
    