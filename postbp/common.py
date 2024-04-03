"""The common module contains common functions and classes used by the other modules.
"""
import geopandas as gpd
from shapely.geometry import LineString #, Polygon, Point

def prj2hex(shp0, hexagons, threshold=0):
    """Generate intersection shape by overlaying shapefile shp0 and the hexagon shapefile
    option to set threshold

    Args:
        shp0 (type:GeoDataFrame): _description_
        hexagons (GeoDataFrame): hexagonal patches
        threshold (int, optional): _description_. Defaults to 0.

    Returns:
        GeoDataFrame: _description_
    """    
    
    shp1 = gpd.overlay(shp0, hexagons, how='intersection') 
    shp1['areaFire'] = shp1.geometry.area
    shp1 = shp1.loc[shp1['areaFire'] > threshold]
    shp1.drop(labels='areaFire', axis=1, inplace=True)
    return shp1

def pij_to_shp(pij_input, nodes, **kwargs):
    """Generate shapefile of lines connecting i and j, with column indicating probability of spread

    Args:
        pij_input (_type_): _description_
        nodes (_type_): _description_

    Returns:
        _type_: _description_
    """    
    
    pij = pij_input.copy()
    node = nodes.copy()
    if 'Node_ID' in kwargs:
        node = node.rename(columns={kwargs["Node_ID"]: 'Node_ID'})
    if 'column_i' in kwargs:
        pij.rename(columns={kwargs["column_i"]: 'column_i'}, inplace=True)    
    if 'column_j' in kwargs:
        pij.rename(columns={kwargs["column_j"]: 'column_j'}, inplace=True)           

    SRID = node.crs
    pij = node.merge(pij, left_on='Node_ID', right_on='column_i', how='right')
    pij = pij.merge(node, left_on='column_j', right_on='Node_ID', how='left')
    pijLine = [LineString(xy) for xy in zip(pij['geometry_x'], pij['geometry_y'])]
    pijshp = gpd.GeoDataFrame(pij, crs = SRID, geometry = pijLine )
    pijshp.drop(labels = ['geometry_x', 'geometry_y'], axis = 1, inplace = True)
    return pijshp