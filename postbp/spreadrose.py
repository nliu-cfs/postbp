from windrose import WindroseAxes
import matplotlib.cm as cm
import geopandas as gpd
from math import atan2, degrees
from shapely.geometry import LineString 
from matplotlib import pyplot as plt
import tqdm

def angle_from_pij(record):
    """_summary_

    Args:
        record (_type_): _description_

    Returns:
        _type_: _description_
    """    
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
    """_summary_

    Args:
        p1 (_type_): _description_
        p2 (_type_): _description_

    Returns:
        _type_: _description_
    """    
    x0, y0 = p1['geometry'].x,p1['geometry'].y
    x1, y1 = p2['geometry'].x, p2['geometry'].y
    dy = y0 - y1
    dx = x0 - x1
    theta = atan2(dx, dy)
    angle = degrees(theta)
    if angle < 0:
        angle = 360 + angle
    return angle

def generate_fire_rose(pijVectors, nodes, **kwargs):
    """_summary_

    Args:
        pijVectors (_type_): _description_
        nodes (_type_): _description_

    Returns:
        _type_: _description_
    """    
    node = nodes.copy()
    if 'Node_ID' in kwargs:
        node = node.rename(columns={kwargs["Node_ID"]: 'Node_ID'})
    pij = pijVectors.copy()  

    pij = node.merge(pij, left_on = 'Node_ID', right_on = 'column_i', how = 'right')
    pij = pij.merge(node, left_on = 'column_j', right_on = 'Node_ID', how = 'left')    
    pij.drop(labels = ['Node_ID_x', 'Node_ID_y'], axis = 1, inplace = True)
    for index, row in tqdm(pij.iterrows()):
        pij.at[index, 'angle'] = angle_from_pij(row)
    dffLine = [LineString(xy) for xy in zip(pij['geometry_x'], pij['geometry_y'])]
    pij = gpd.GeoDataFrame(pij, crs = node.crs, geometry = dffLine )
    pij.drop(labels = ['geometry_x', 'geometry_y'], axis = 1, inplace = True)
    pij['len'] = pij.geometry.length
    pij['pij'] = pij['pij'].astype(float)
    pij['pij_len'] = pij['pij']*pij['len']
    return pij

def plot_rose(pijRose, column='pij', save = False):
    if save:
        plt.rcParams.update({'font.size': 20})
        ax = WindroseAxes.from_ax()
        ax.bar(pijRose['angle'], pijRose[column], normed=True, blowto=False, cmap=cm.Set2, opening=0.8, edgecolor='white')
        ax.set_legend(fontsize="20",loc=(1.01, 0.01),frameon=False)
        plt.savefig(column + 'Rose.png', bbox_inches='tight', pad_inches=.1, transparent=False)
        plt.close()
    else:
        plt.rcParams.update({'font.size': 20})
        ax = WindroseAxes.from_ax()
        ax.bar(pijRose['angle'], pijRose[column], normed=True, blowto=False, cmap=cm.Set2, opening=0.8, edgecolor='white')
        ax.set_legend(fontsize="20",loc=(1.01, 0.01),frameon=False)
        plt.show()
