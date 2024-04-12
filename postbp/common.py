"""The common module contains common functions and classes used by the other modules.
"""
import geopandas as gpd
from shapely.geometry import LineString #, Polygon, Point
from tqdm import tqdm

def prj2hex(shp0, hexagons, threshold=0):
    """Generate a geometric intersection of shp0 and the hexagon shapefile.
    option to set threshold

    Args:
        shp0 (GeoDataFrame): GeoDataFrame to be identified by hexagon shape
        hexagons (GeoDataFrame): hexagonal patches
        threshold (float, optional): Value between 0 and 1. The proportion for classifying hexagon as intersecting with shp0. Defaults to 0.

    Returns:
        GeoDataFrame: Return a GeoDataFrame of the intersection with hexagon ID field as attributes
    """    
    thresholdArea = hexagons.at[1,'geometry'].area * threshold
    try:
        shp1 = gpd.overlay(shp0, hexagons, how='intersection') 
    except:
        pass    
    shp1['areaFire'] = shp1.geometry.area
    shp1 = shp1.loc[shp1['areaFire'] > thresholdArea]
    shp1.drop(labels='areaFire', axis=1, inplace=True)
    return shp1

def pij_to_shp(pij_input, nodes, **kwargs):
    """Adding geometry to pij vectors file

    Args:
        pij_input (DataFrame): pij dataframe
        nodes (GeoDataFrame): centroid of the hexagonal patches

    Returns:
        GeoDataFrame: pij value with geometry of lines connecting node-i and node-j
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
    pijshp.drop(labels = ['geometry_x', 'geometry_y', 'Node_ID_x', 'Node_ID_y'], axis = 1, inplace = True)
    return pijshp