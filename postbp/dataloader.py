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
import numpy as np

def read_fireshp(path_n_file_name, daily=False):
    """Load the files with the final and daily fire perimeters and prepares the data

    Args:
        path_n_file_name (string): path and file name of fire perimeter shapefile

    Returns:
        GeoDataFrame: ignition point fire ID and geometry
    """    
     # check whether it is a daily progression shapefile

    fire = gpd.read_file(path_n_file_name,  driver = 'ESRI Shapefile') #columns=columns,

    # as geopands has malfunction in reading only the columns being specified, we manually redundantly do it again here
    if daily:
        fire = fire[['fire', 'iteration', 'day', 'geometry']]
    else:
        fire = fire[['fire', 'iteration', 'geometry']]
        
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


def _loadCSVdata(file_path):
        try:
            with open(file_path, 'r') as temp_f:
                # get No of columns in each line
                col_count = max([len(l.split(",")) for l in temp_f.readlines()])

            ### Generate column names  (names will be 0, 1, 2, ..., maximum columns - 1)
            column_names = [i for i in range(col_count)] 

            dataCSV = pd.read_csv(file_path, names=column_names,skiprows=1, header=None)
            dataCSV.rename(columns={0:'column', 1:'row'}, inplace=True)
            dataCSV.set_index(['column', 'row'], inplace=True)
            dataCSV.dropna(how='all',inplace=True)
            dataCSV.reset_index(inplace=True)
            reshapeCSV = dataCSV.melt(id_vars=['column','row'], var_name='round', value_name='iterationID')
            reshapeCSV.dropna(how='any',inplace=True)
            return reshapeCSV

        except Exception as e:
            print(
                "Error",
                f"An error occurred while reading the file:\n{str(e)}"
            )
            return None

def loadBI(file_path):
    dataBI = _loadCSVdata(file_path)
    return dataBI

def loadROS(file_path):
    dataROS = _loadCSVdata(file_path)
    return dataROS

def loadFI(file_path):
    dataFI = _loadCSVdata(file_path)
    return dataFI

def loadASC(file_path):
        def extract_header_info(file_path):
            ncols, nrows, xllcorner, yllcorner, cellsize = None, None, None, None, None 
            with open(file_path, 'r') as file:
                for i, line in enumerate(file):
                    if 'ncols' in line:
                        ncols = int(line.split()[1])
                    elif 'nrows' in line:
                        nrows = int(line.split()[1])
                    elif 'xllcorner' in line:
                        xllcorner = float(line.split()[1])
                    elif 'yllcorner' in line:
                        yllcorner = float(line.split()[1])
                    elif 'cellsize' in line:
                        cellsize = float(line.split()[1])
                        
                    if ncols and nrows and xllcorner and yllcorner and cellsize:
                        break
            
            return ncols, nrows, xllcorner, yllcorner, cellsize

        try:
            ncols, nrows, xllcorner, yllcorner, cellsize = extract_header_info(file_path)
            cols = np.arange(1, ncols + 1)
            rows = np.arange(1, nrows + 1)
            outlist = [(i, j) for i in cols for j in rows]
            grids = pd.DataFrame(data=outlist, columns=['column', 'row'])

            grids['y_coord'] = yllcorner + (grids['row'] - 1) * cellsize
            grids['x_coord'] = xllcorner + (grids['column'] - 1) * cellsize

            return grids

        except Exception as e:
            print(
                "Error",
                f"An error occurred while reading the file:\n{str(e)}"
            )
            return None




