from windrose import WindroseAxes
import matplotlib.cm as cm
import geopandas as gpd
from math import atan2, degrees
from shapely.geometry import LineString 
from matplotlib import pyplot as plt
from tqdm import tqdm

def angle_from_pij(record):
    """Calculate the clockwise angles between the fire vector and the North from postbp function generate_daily_vectors.

    Args:
        record (DataFrame): a row of outputs from pij_from_vectors function

    Returns:
        degree: return angle value
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
    """Calculate the clockwise angles between the fire vector and the North from start and end points of a vector.

    Args:
        p1 (GeoDataFrame): starting point of a vector with geometry.
        p2 (GeoDataFrame): end point of a vector with geometry.

    Returns:
        degree: return angle value
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
    """Prepare data for plotting fire rose.

    Args:
        pijVectors (DataFrame): outputs from pij_from_vectors function
        nodes (GeoDataFrame): centroid points of the hexagonal patch network

    Returns:
        DataFrame: return a dataframe containing angles, pij, and distance of spread. 
    """    
    node = nodes.copy()
    pij = pijVectors.copy() 
    if 'Node_ID' in kwargs:
        node = node.rename(columns={kwargs["Node_ID"]: 'Node_ID'})
    if 'column_i' in kwargs:
        pij.rename(columns={kwargs["column_i"]: 'column_i'}, inplace=True)    
    if 'column_j' in kwargs:
        pij.rename(columns={kwargs["column_j"]: 'column_j'}, inplace=True)     

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
    return pij

def plot_rose(pijRose, column='pij', save = False):
    """Plot fire rose.

    Args:
        pijRose (DataFrame): a dataframe containing angles, pij, and distance of spread. 
        column (str, optional): value can be 'pij' or 'len'. Defaults to 'pij'.
        save (bool, optional): whether save the plot to current repository or plot on screen. Defaults to False.
    """    
    
    plt.rcParams.update({'font.size': 20,"legend.frameon":False})
    ax = WindroseAxes.from_ax()
    ax.bar(pijRose['angle'], pijRose[column], normed=True, blowto=False, cmap=cm.Set2, opening=0.8, edgecolor='white')
    ax.set_legend(fontsize="20",loc=(1.1, 0.01))
    if save:
        plt.savefig(column + 'Rose.png', bbox_inches='tight', pad_inches=.1, transparent=False)
        plt.close()
    else:
        plt.show()

    plt.rcParams.update(plt.rcParamsDefault)

