'''Module to processing daily progression of fire
'''

import geopandas as gpd
import numpy as np
import pandas as pd
import itertools
from math import atan2, degrees
from .common import prj2hex
import warnings
warnings.filterwarnings("ignore")
from tqdm import tqdm

def angle(record):
    """Calculate angle from three points: ignition point and the points where fire spread from and to.  

    Args:
        record (dataframe): a row of the output from generate_daily_vectors function

    Returns:
        degree value: the value of beta angle, i.e. the angle between the line connecting ignition point and starting point of fire, and the line connecting the hexagon nodes that a fire spreading from and to. 
    """    
    x0, y0 = record['geometry_x'].x, record['geometry_x'].y
    x1, y1 = record['geometry'].x, record['geometry'].y
    x2, y2 = record['geometry_y'].x, record['geometry_y'].y
    xv1, yv1 = x1-x0, y1-y0
    xv2, yv2 = x2-x0, y2-y0
    deg1 = (360 + degrees(atan2(xv1, yv1))) % 360
    deg2 = (360 + degrees(atan2(xv2, yv2))) % 360
    return deg2 - deg1 if deg1 <= deg2 else 360 - (deg1 - deg2)



def generate_daily_vectors(fireshp, ignition, hexagons, bufferFactor=10, **kwargs):
    """Generate fire spreading vectors from the daily fire spread perimeters

    Args:
        fireshp (GeoDataFrame): the daily fire perimeter geometry with fire ID and day of spread as attributes
        ignition (GeoDataFrame): ignition point shapes with fire ID field in attributes
        hexagons (GeoDataFrame): geometry of hexagonal patches with ID field
        bufferFactor (int, optional): convert ignition point into a circle polygon of the diameter of bufferFactor
it shall be small enough so as not to have ignition point locates in more than one hexagons it also defines threshold for the minimum area of fire perimeter to be in a hexagon to be regarded as burned. Defaults to 10.

    Returns:
        DataFrame: a dataframe table containing fire starting hexagon ID (i), destination hexagon ID (j), 'day', fire ID, and ignition hexagon ID 
    """    
    hexagon = hexagons.copy()
    if 'Node_ID' in kwargs:
        hexagon = hexagon.rename(columns={kwargs["Node_ID"]: 'Node_ID'})
    
    threshold = 3.1415926*bufferFactor**2 - 1 
    SRID = fireshp.crs
    df = pd.DataFrame()
    dfMore = pd.DataFrame()
    
    for i in tqdm(np.unique(fireshp['fire'])):
        try: 
            fire_i = fireshp.loc[fireshp['fire'] == i]
            pts_i = ignition.loc[ignition['fire'] == i]
            pts_ni = gpd.sjoin(pts_i, hexagon, how = 'inner', op = 'within')
            ##### ignition point to all hexes
            dmax = max(fire_i['day'])
            fire_idmax = fire_i.loc[fire_i['day'] == dmax]
            dfDmax = prj2hex(fire_idmax, hexagon, threshold)
            dfMore = pd.DataFrame([e for e in itertools.product(pts_ni['Node_ID'], dfDmax['Node_ID'])], columns=['column_i', 'column_j'])
            # from ignition point to all other hexes in the fire perimeters (as regular fire vectors) are stored by day=999
            dfMore['day'] = 999       
            dfMore.drop(dfMore.loc[dfMore['column_i'] == dfMore['column_j']].index, inplace = True)
            #### leading edge
            leadEdge = list(pts_ni['Node_ID'])
            shpDB4 = gpd.GeoDataFrame(crs = SRID, geometry = pts_i.buffer(bufferFactor))
            for d in range(1, max(fire_i['day'])+1):
                fire_id = fire_i.loc[fire_i['day'] == d]
                fire_idn = prj2hex(fire_id, hexagon, threshold)
                ## hexagons in the fireshed of previous day
                lstDB4 = prj2hex(shpDB4, hexagon, threshold)
                lstDB4 = list(lstDB4['Node_ID'])
                ## hexagons to be spread
                listCur = list(fire_idn.loc[~fire_idn['Node_ID'].isin(lstDB4)]['Node_ID'])
                #### consider when two days spread overlap in hexagon projections, hence listCur is empty
                if listCur:
                    dfTemp = pd.DataFrame([e for e in itertools.product(leadEdge, listCur)], columns = ['column_i', 'column_j'])
                    dfTemp['day'] = d
                else:
                    dfTemp = pd.DataFrame()
                dfMore = pd.concat([dfMore, dfTemp])  #, sort = False
                dfMore.drop_duplicates(subset = ['column_i', 'column_j', 'day'], keep = 'first', inplace = True)
                #### update fireshed shape by merging fireshed of t with t-1
                shpDB4 = fire_id.copy()
                shpEx = gpd.GeoDataFrame(crs = SRID, geometry = shpDB4.exterior.buffer(1))
                shpExHex = prj2hex(shpEx, hexagon, threshold = 0)
                leadEdgeC = list(shpExHex['Node_ID'])
                leadEdgeN = [x for x in leadEdgeC if x not in lstDB4]
                if leadEdgeN:
                    leadEdge = leadEdgeN
                else:
                    pass
            dfMore = dfMore.reset_index(drop = True)
            dfMore.drop_duplicates(subset = ['column_i', 'column_j', 'day'], keep = 'first', inplace = True)
            dfMore['fire'] = i
            dfMore['ignPt'] = pts_ni['Node_ID'].item()
            df = pd.concat([df, dfMore], sort = True)
        except Exception as e:
            with open("errorlog_dailyfire.txt", "w+") as f:
                f.write(f'{e} occurs for fire ID # {i} \n')    
    return df

def calc_angles(vectors, nodes, **kwargs):
    """Calculate beta angle for every pair of vectors of fire spread

    Args:
        vectors (dataframe): outputs from generate_daily_vectors function
        nodes (GeoDataFrame): centroid points of the hexagonal patch network

    Returns:
        dataframe: a dataframe containing geometry of i, j, ignition point and beta angle value of each vector
    """    
    node = nodes.copy()
    if 'Node_ID' in kwargs:
        node = node.rename(columns={kwargs["Node_ID"]: 'Node_ID'})

    vectorsW = vectors.copy()
    vectorsW = node.merge(vectors, left_on='Node_ID', right_on='column_i', how='right')
    vectorsW = vectorsW.merge(node, left_on='column_j', right_on='Node_ID', how='left')
    vectorsW = vectorsW.merge(node, left_on='ignPt', right_on='Node_ID', how='left')
    vectorsW.drop(labels = ['Node_ID_x', 'Node_ID_y', 'Node_ID'], axis = 1, inplace = True)

    #### note that 'geometry_x':origin; 'geometry_y':destination; 'geometry':ignition

    for index, row in tqdm(vectorsW.iterrows()):
        try: 
            vectorsW.at[index, 'angle'] = angle(row)
        except:
            vectorsW.at[index, 'angle'] = 181  # when origin is identical to ignition
    vectorsW.loc[vectorsW['day'] == 999, 'angle'] = 361  # from ignition to all hexes in perimeter
    vectorsW.loc[vectorsW['day'] == 1, 'angle'] = 181  # in day 1: origin is identical to ignition
    vectorsW.drop_duplicates(subset = ['day', 'column_j', 'fire', 'ignPt', 'column_i'], keep = 'first', inplace = True)
    return vectorsW

def select_angle(vectors_with_angle, alpha):
    """Select intended angle of fire spread sector

    Args:
        vectors_with_angle (dataframe): outputs from calc_angles function
        alpha (degree): fire spread sector angle (alpha angle), value from 0 to 360

    Returns:
        dataframe: a dataframe containing geometry of i, j, ignition point and beta angle value of each vector
    """    
    maxAngle = alpha/2+180
    minAngle = 180-alpha/2
    vectorsV = vectors_with_angle.copy()
    vectorsV.drop(vectorsV.loc[vectorsV['angle'] > maxAngle].index, inplace = True)
    vectorsV.drop(vectorsV.loc[vectorsV['angle'] < minAngle].index, inplace = True)
    vectorsV.sort_values(by = ['fire','day'], inplace = True)
    vectorsV.reset_index(drop = True, inplace = True)
    return vectorsV



