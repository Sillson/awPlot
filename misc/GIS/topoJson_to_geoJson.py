# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 10:43:25 2017

@author: Beau.Uriona
"""

import json
from itertools import chain
from shapely.geometry import asShape

def rel2abs(arc, scale=None, translate=None):
    """Yields absolute coordinate tuples from a delta-encoded arc.
    If either the scale or translate parameter evaluate to False, yield the
    arc coordinates with no transformation."""
    if scale and translate:
        a, b = 0, 0
        for ax, bx in arc:
            a += ax
            b += bx
            yield scale[0]*a + translate[0], scale[1]*b + translate[1]
    else:
        for x, y in arc:
            yield x, y
def coordinates(arcs, topology_arcs, scale=None, translate=None):
    """Return GeoJSON coordinates for the sequence(s) of arcs.
    
    The arcs parameter may be a sequence of ints, each the index of a
    coordinate sequence within topology_arcs
    within the entire topology -- describing a line string, a sequence of 
    such sequences -- describing a polygon, or a sequence of polygon arcs.
    
    The topology_arcs parameter is a list of the shared, absolute or
    delta-encoded arcs in the dataset.
    The scale and translate parameters are used to convert from delta-encoded
    to absolute coordinates. They are 2-tuples and are usually provided by
    a TopoJSON dataset. 
    """
    if isinstance(arcs[0], int):
        coords = [
            list(
                rel2abs(
                    topology_arcs[arc if arc >= 0 else ~arc],
                    scale, 
                    translate )
                 )[::arc >= 0 or -1][i > 0:] \
            for i, arc in enumerate(arcs) ]
        return list(chain.from_iterable(coords))
    elif isinstance(arcs[0], (list, tuple)):
        return list(
            coordinates(arc, topology_arcs, scale, translate) for arc in arcs)
    else:
        raise ValueError("Invalid input %s", arcs)
def geometry(obj, topology_arcs, scale=None, translate=None):
    """Converts a topology object to a geometry object.
    
    The topology object is a dict with 'type' and 'arcs' items, such as
    {'type': "LineString", 'arcs': [0, 1, 2]}.
    See the coordinates() function for a description of the other three
    parameters.
    """
    return {
        "type": obj['type'], 
        "coordinates": coordinates(
            obj['arcs'], topology_arcs, scale, translate )}
        

topojson_path = r'HUC.topojson'
topojson6_path = r'HUC6_8.topojson'
geojson_path = r'HUC6_8.geojson'

with open(topojson_path) as f:
    geoData = json.loads(f.read())
    geoData['objects']['layer1']['geometries'][:] = [d for d in geoData['objects']['layer1']['geometries'] if d['properties'].get('type') == 6 or d['properties'].get('type') == 8]

with open(topojson6_path,'w') as f:
    f.write(str(json.dumps(geoData)))
    
with open(topojson6_path, 'r') as fh:
    f = fh.read()
    topology = json.loads(f)

# file can be renamed, the first 'object' is more reliable
layername = list(topology['objects'].keys())[0]  

features = topology['objects'][layername]['geometries']
scale = topology['transform']['scale']
trans = topology['transform']['translate']

with open(geojson_path, 'w') as dest:
    fc = {'type': "FeatureCollection", 'features': []}

    for id, tf in enumerate(features):
        f = {'id': id, 'type': "Feature"}
        f['properties'] = tf['properties'].copy()

        geommap = geometry(tf, topology['arcs'], scale, trans)
        geom = asShape(geommap).buffer(0)
        assert geom.is_valid
        f['geometry'] = geom.__geo_interface__
        
        fc['features'].append(f) 

    dest.write(json.dumps(fc))
    
    


    
    