"""The common module contains common functions and classes used by the other modules.
"""
import geopandas as gpd
from shapely.geometry import LineString #, Polygon, Point

def prj2hex(shp0, hexagons, threshold=0):
    '''
    Generate intersection shape by overlaying shapefile shp0 and the hexagon shapefile
    option to set threshold
    '''
    shp1 = gpd.overlay(shp0, hexagons, how='intersection') 
    shp1['areaFire'] = shp1.geometry.area
    shp1 = shp1.loc[shp1['areaFire'] > threshold]
    shp1.drop(labels='areaFire', axis=1, inplace=True)
    return shp1

def pij_to_shp(pij_input, nodes, **kwargs):
    '''
    Generate shapefile of lines connecting i and j, with column indicating probability of spread
    '''
    pij = pij_input.copy()

    if 'Node_ID' in kwargs:
        nodes.rename(columns={kwargs["Node_ID"]: 'Node_ID'}, inplace=True)
    if 'column_i' in kwargs:
        pij.rename(columns={kwargs["column_i"]: 'column_i'}, inplace=True)    
    if 'column_j' in kwargs:
        pij.rename(columns={kwargs["column_j"]: 'column_j'}, inplace=True)           

    SRID = nodes.crs
    pij = nodes.merge(pij, left_on='Node_ID', right_on='column_i', how='right')
    pij = pij.merge(nodes, left_on='column_j', right_on='Node_ID', how='left')
    pijLine = [LineString(xy) for xy in zip(pij['geometry_x'], pij['geometry_y'])]
    pijshp = gpd.GeoDataFrame(pij, crs = SRID, geometry = pijLine )
    pijshp.drop(labels = ['geometry_x', 'geometry_y'], axis = 1, inplace = True)
    return pijshp