'''Module to project fire and ignition points to hexagon network.
1. user confirm whether there are multiple fires in each iteration:
    if yes, using spatialjoin_fire_iteration
    else, using spatialjoin_fire

2. user confirm whether is processing spreading by day data:
    if yes, using module dailyfirevectors
    else, current module suffices
'''
import geopandas as gpd
import pandas as pd
from .common import prj2hex
import warnings
warnings.filterwarnings("ignore")
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
from tqdm import tqdm

def _spatial_join(fireshp, ignition, hexagon, threshold=0, iteration=False):
    """Project fire perimeter and ignition points to the hexagonal network

    Args:
        fireshp (GeoDataFrame): fire perimeter dataset with fire ID (and iteration ID) and geometry
        ignition (GeoDataFrame): igntion points geodataframe
        hexagons (GeoDataFrame): geometry of hexagonal patches with ID field
        threshold (float, optional): Value between 0 and 1. The proportion for classifying hexagon as intersecting with shp0. Defaults to 0.
        iteration (bool, optional): Defaults to False. If multiple fires in each iteration, then set value to True

    Returns:
        GeoDataFrame: igntion point, starting point and destination point of each fire being identified with hexagon ID
    """    

    # make sure hexagons, fireShp and ignition point shapefile are in the same projection
    ignition = ignition.to_crs(fireshp.crs)
    hexagon = hexagon.to_crs(fireshp.crs)

    fire_vectors = pd.DataFrame()

    if not iteration:
        for i in tqdm(fireshp['fire']):
            try:
                fire_i = fireshp.loc[fireshp['fire'] == i]
                fire_ni = prj2hex(fire_i, hexagon, threshold)                        
                pts_i = ignition.loc[ignition['fire'] == i]
                #if newer version op is replace by predicate
                pts_ni = gpd.sjoin(pts_i, hexagon, how = 'inner', op = 'within')
                pts_ni = pts_ni[['fire', 'Node_ID']]
                
                dfTemp = fire_ni.merge(pts_ni, on = 'fire', how = 'left')
                dfTemp = dfTemp.drop(dfTemp[dfTemp['Node_ID_x'] == dfTemp['Node_ID_y']].index)
                dfTemp.drop(labels = ['geometry'], axis = 1, inplace = True)
                fire_vectors = pd.concat([fire_vectors, dfTemp], sort = True)
                
            except Exception as e:
                with open("errorlog_finalfire.txt", "w+") as f:
                    f.write(f'{e} occurs for fire ID # {i} \n')   
        return fire_vectors


    if iteration:
        for j in tqdm(set(fireshp['iteration'])):
            fire_j = fireshp.loc[fireshp['iteration'] == j]
            pts_j = ignition.loc[ignition['iteration'] == j]
            
            for i in fireshp['fire']:
                try:
                    fire_i = fire_j.loc[fire_j['fire'] == i]
                    fire_ni = prj2hex(fire_i, hexagon, threshold)                             
                    pts_i = pts_j.loc[pts_j['fire'] == i]
                    #if newer version op is replace by predicate
                    pts_ni = gpd.sjoin(pts_i, hexagon, how = 'inner', op = 'within') 
                    pts_ni = pts_ni[['fire', 'Node_ID']]
                    
                    dfTemp = fire_ni.merge(pts_ni, on = 'fire', how = 'left')
                    dfTemp = dfTemp.drop(dfTemp[dfTemp['Node_ID_x'] == dfTemp['Node_ID_y']].index)
                    dfTemp.drop(labels = ['geometry'], axis = 1, inplace = True)
                    fire_vectors = pd.concat([fire_vectors, dfTemp], sort = True)
                
                except Exception as e:
                    with open("errorlog_finalfire.txt", "w+") as f:
                        f.write(f'{e} occurs for fire ID # {i} \n')                         
        return fire_vectors
            
def generate_fire_vectors(fireshp, ignition, hexagons, threshold = 0, loopBy = "fire", **kwargs):
    """Generate fire spreading vectors from final fire spread perimeters

    Args:
        fireshp (GeoDataFrame): fire perimeter dataset with fire ID (and iteration ID) and geometry
        ignition (GeoDataFrame): ignition point shapes with fire ID field in attributes
        hexagons (GeoDataFrame): geometry of hexagonal patches with ID field
        threshold (float, optional): Value between 0 and 1. The proportion for classifying hexagon as intersecting with shp0. Defaults to 0.
        loopBy (str, optional): loop by 'fire' of 'iteration'. Defaults to "fire".

    Returns:
        DataFrame: a dataframe table containing fire starting hexagon ID (i), destination hexagon ID (j), fire ID, and ignition hexagon ID 
    """    
    hexagon = hexagons.copy()
    if 'Node_ID' in kwargs:
        hexagon = hexagon.rename(columns={kwargs["Node_ID"]: 'Node_ID'})
    
    if loopBy == "iteration":
        fire_vectors = _spatial_join(fireshp, ignition, hexagon, threshold, iteration=True)
    
    if loopBy == "fire":
        fire_vectors = _spatial_join(fireshp, ignition, hexagon, threshold, iteration=False)
     
    fire_vectors = fire_vectors.reset_index(drop = True)
    fire_vectors.drop(fire_vectors[fire_vectors['Node_ID_y'].isna()].index, inplace = True)                    
    
    fire_vectors['Node_ID_x'] = fire_vectors['Node_ID_x'].astype(int)
    fire_vectors['Node_ID_y'] = fire_vectors['Node_ID_y'].astype(int)
    
    fire_vectors.columns = ['Node_ID_x', 'Node_ID_y', 'fire', 'iteration']
    fire_vectors.rename(columns={'Node_ID_x':'column_j', 'Node_ID_y':'column_i'}, inplace=True)
    return fire_vectors

def pij_from_vectors(vectors, iterations):
    """Group vector pair by i, j and calculate probability by dividing number of occurrence by number of iterations

    Args:
        vectors (dataframe): outputs from generate_fire_vectors function
        iterations (int): number of iterations

    Returns:
        GeoDataFrame: return a geodataframe with probability values for pairs of i, j on the landscape
    """    

    fire_pij = vectors.groupby(['column_j', 'column_i'])[['fire']].count()
    fire_pij.reset_index(inplace = True)
    fire_pij = fire_pij.drop(fire_pij[fire_pij['column_j'] == fire_pij['column_i']].index)
    fire_pij['pij'] = fire_pij['fire'] / iterations
    fire_pij['pij'] = fire_pij['pij'].round(5)
    fire_pij['pij'] = fire_pij['pij'].apply(lambda x: '%.5f' % x)
    fire_pij.rename(columns={'fire':'firecounts'},inplace=True)
    fire_pij.sort_values(by = ['firecounts'], inplace = True)
    fire_pij.reset_index(drop=True, inplace=True)
    return fire_pij