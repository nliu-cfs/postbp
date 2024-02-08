from windrose import WindroseAxes
import matplotlib.cm as cm
import pandas as pd
import geopandas as gpd
from math import atan2, degrees
from shapely.geometry import LineString  #Polygon, Point, 
from matplotlib import pyplot as plt

def angle_from_pij(record):
    x0, y0 = record['geometry_x'].x, record['geometry_x'].y
    x1, y1 = record['geometry_y'].x, record['geometry_y'].y
    dy = y0 - y1
    dx = x0 - x1
    theta = atan2(dx, dy)
    angle = degrees(theta)
    if angle < 0:
        angle = 360 + angle
    return angle

def angle_from_2pts(p1, p2):
    x0, y0 = p1['geometry'].x,p1['geometry'].y
    x1, y1 = p2['geometry'].x, p2['geometry'].y
    dy = y0 - y1
    dx = x0 - x1
    theta = atan2(dx, dy)
    angle = degrees(theta)
    if angle < 0:
        angle = 360 + angle
    return angle

def generate_fireRose(pijVectors, nodes, **kwargs):
    pij = pijVectors.copy()
    pij = pij.merge(nodes, left_on = 'desti', right_on = 'Node_ID', how = 'left')
    pij.drop(labels = ['Node_ID_x', 'Node_ID_y'], axis = 1, inplace = True)
    for index, row in pij.iterrows():
        pij.at[index, 'angle'] = angle_from_pij(row)
    dffLine = [LineString(xy) for xy in zip(pij['geometry_x'], pij['geometry_y'])]
    pij = gpd.GeoDataFrame(pij, crs = nodes.crs, geometry = dffLine )
    pij.drop(labels = ['geometry_x', 'geometry_y'], axis = 1, inplace = True)
    pij['len'] = pij.geometry.length
    pij['pij'] = pij['pij'].astype(float)
    pij['pij_len'] = pij['pij']*pij['len']
    return pij

def plotRose(pijRose, column='pij', save = False):
    if save:
        ax = WindroseAxes.from_ax()
        ax.bar(pijRose['angle'], pijRose[column], normed=True, blowto=False, cmap=cm.Set2, opening=0.8, edgecolor='white')
        ax.set_legend()
        plt.savefig(column + 'Rose.png', bbox_inches='tight', pad_inches=.1, transparent=False)
        plt.close()
    else:
        ax = WindroseAxes.from_ax()
        ax.bar(pijRose['angle'], pijRose[column], normed=True, blowto=False, cmap=cm.Set2, opening=0.8, edgecolor='white')
        ax.set_legend()
        plt.show()
