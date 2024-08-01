'''Module handling input files.
1. read in input fire shapefile.
2. read in input csv file of ignition points, and convert it to shapefile of the same projection as fire shp.
3. optionally parsing the big input files into chunks for parallel processing and saving time.

'''

import geopandas as gpd
from shapely.geometry import  Point #, LineString, Polygon,
import pandas as pd
import warnings
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

def read_fireshp(path_n_file_name, daily=False):
    """Load the files with the final and daily fire perimeters and prepares the data

    Args:
        path_n_file_name (string): path and file name of fire perimeter shapefile

    Returns:
        GeoDataFrame: ignition point fire ID and geometry
    """    
     # check whether it is a daily progression shapefile
    if daily:
        columns = ['fire', 'iteration', 'day']
    else:
        columns = ['fire', 'iteration']

    fire = gpd.read_file(path_n_file_name, columns=columns, driver = 'ESRI Shapefile')

    # as geopands has malfunction in reading only the columns being specified, we manually redundantly do it again here
    fire = fire[[columns]]

    # some BP3 fireshp data does not have valid prj, it needs to have a warning to the users
    if not fire.crs:
        print('The fire perimeter shapefile does not have a valid projection, please set a valid SRID.')
    
    return fire
      
def read_pointcsv(path_n_file_name, SRID, **kwargs):
    """Load the fire ignition points if this information is provided as a comma-delimited .csv file

    Args:
        path_n_file_name (string): path and file name of fire ignition points shapefile
        SRID (CRS): spatial reference identifiers (SRID) 
        x_col (str): column name of x coordinates, default to be 'x_coord'
        y_col (str): column name of x coordinates, default to be 'y_coord'
    Returns:
        GeoDataFrame: ignition point fire ID and geometry
    """    

    if "x_col" in kwargs:
        x_col = kwargs['x_col']
    else:
        x_col = 'x_coord'

    if "y_col" in kwargs:
        y_col = kwargs['y_col']
    else:
        y_col = 'y_coord'

    #### read in BurnP-3 output ignition point csv file
    points = pd.read_csv(path_n_file_name)
    # points.columns=points.columns.str.strip()
    points['geometry'] = [Point(xy) for xy in zip(points[x_col], points[y_col])]
    # note: make sure ignition points and fire shape are of the same projection, below it directly set by prj
    points = gpd.GeoDataFrame(points, crs = SRID, geometry = points['geometry'] )
    points = points[['fire', 'iteration', 'geometry']]
    return points

    
def read_pointshp(path_n_file_name, **kwargs):
    """Load the ignition points if the data is provided as X-Y coordinates in separate columns in the attribute table of the ESRI shapefile with fire perimeters (or in a separate ESRI point shapefile)

    Args:
        path_n_file_name (str): path and file name of fire ignition points shapefile
        x_col (str): column name of x coordinates, default to be 'x_coord'
        y_col (str): column name of x coordinates, default to be 'y_coord'
    Returns:
        GeoDataFrame: ignition point fire ID and geometry
    """ 
       
    if "x_col" in kwargs:
        x_col = kwargs['x_col']
        
    else:
        x_col = 'x_coord'

    if "y_col" in kwargs:
        y_col = kwargs['y_col']
    else:
        y_col = 'y_coord'
        
    #### read in BurnP-3 output ignition point csv file
    points = gpd.read_file(path_n_file_name, driver='ESRI Shapefile')
    ## check geometry to be point or polygon

    if points.geom_type.str.contains("Point").all():
        points = points[['fire', 'iteration', 'geometry']]
        
    else:
        SRID = points.crs
        points.drop(labels='geometry',axis=1,inplace=True)
        points = points[['fire', 'iteration']]
        points['geometry'] = [Point(xy) for xy in zip(points[x_col], points[y_col])]
        # note: make sure ignition points and fire shape are of the same projection, below it directly set by prj
        points = gpd.GeoDataFrame(points, crs = SRID, geometry = points['geometry'] )
        points = points[['fire', 'iteration', 'geometry']]

    return points

def validify_fireshp(fireshp):
    """if encounter error message of invalid geometry, use this function to convert invalid geometry to valid ones

    Args:
        fireshp (GeoDataFrame): fire perimeter dataset with fire ID (and iteration ID) and geometry

    Returns:
        GeoDataFrame: return validified geodataframe
    """    
    from shapely.validation import make_valid
    fireshp.geometry = fireshp.apply(lambda row: make_valid(row.geometry) if not row.geometry.is_valid else row.geometry, axis=1)
    return fireshp

