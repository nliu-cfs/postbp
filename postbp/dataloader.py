'''Module handling input files.
1. read in input fire shapefile.
2. read in input csv file of ignition points, and convert it to shapefile of the same projection as fire shp.
3. optionally parsing the big input files into chunks for parallel processing and saving time.

'''

import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
import pandas as pd
import warnings
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

def read_fireshp(path, *kwargs):
    """_summary_

    Args:
        path (_type_): _description_
    """    
     # check whether it is a daily progression shapefile
    if 'day' in kwargs:
        columns = ['fire', 'iteration', 'day']
    else:
        columns = ['fire', 'iteration']

    fire = gpd.read_file(path, columns=columns, driver = 'ESRI Shapefile')
    
    return fire
      
def read_pointcsv(path, SRID, **kwargs):
    """_summary_

    Args:
        path (_type_): _description_
        SRID (_type_): _description_

    Returns:
        _type_: _description_
    """    

    if "x_col" in kwargs:
        x_coord = kwargs['x_col']
    else:
        x_coord = 'x_coord'

    if "y_col" in kwargs:
        y_coord = kwargs['y_col']
    else:
        y_coord = 'y_coord'

    #### read in BurnP-3 output ignition point csv file
    points = pd.read_csv(path)
    points['geometry'] = [Point(xy) for xy in zip(points[x_coord], points[y_coord])]
    # note: make sure ignition points and fire shape are of the same projection, below it directly set by prj
    points = gpd.GeoDataFrame(points, crs = SRID, geometry = points['geometry'] )
    if 'day' in kwargs:
        points = points[['fire', 'iteration', 'day', 'geometry']]
    else:
        points = points[['fire', 'iteration', 'geometry']]
    return points

    
def read_pointshp(path, **kwargs):
    """_summary_

    Args:
        path (_type_): _description_

    Returns:
        _type_: _description_
    """ 
       
    if "x_col" in kwargs:
        x_coord = kwargs['x_col']
        
    else:
        x_coord = 'x_coord'

    if "y_col" in kwargs:
        y_coord = kwargs['y_col']
    else:
        y_coord = 'y_coord'
        
    #### read in BurnP-3 output ignition point csv file
    points = gpd.read_file(path, driver='ESRI Shapefile')
    ## check geometry to be point or polygon

    if points.geom_type.str.contains("Point").all():
        points = points[['fire', 'iteration', 'geometry']]
        
    else:
        SRID = points.crs
        points.drop(labels='geometry',axis=1,inplace=True)
        points = points[['fire', 'iteration']]
        points['geometry'] = [Point(xy) for xy in zip(points[x_coord], points[y_coord])]
        # note: make sure ignition points and fire shape are of the same projection, below it directly set by prj
        points = gpd.GeoDataFrame(points, crs = SRID, geometry = points['geometry'] )
        points = points[['fire', 'iteration', 'geometry']]

    return points

