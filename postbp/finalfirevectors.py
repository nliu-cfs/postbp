'''Module to project fire and ignition points to hexagon network.
1. user confirm whether there are multiple fires in each iteration:
    if yes, using spatialjoin_fire_iteration
    else, using spatialjoin_fire

2. user confirm whether is processing spreading by day data:
    if yes, using module daily_progression
    else, current module suffices
'''
import geopandas as gpd
import pandas as pd
from .common import prj2hex
import warnings
warnings.filterwarnings("ignore")
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
import tqdm

def spatial_join(fireshp, ignition, hexagon, threshold=0, iteration=False):
    """_summary_

    Args:
        fireshp (_type_): _description_
        ignition (_type_): _description_
        hexagon (_type_): _description_
        threshold (int, optional): _description_. Defaults to 0.
        iteration (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """    

    # make sure hexagons, fireShp and ignition point shapefile are in the same projection
    ignition = ignition.to_crs(fireshp.crs)
    hexagon = hexagon.to_crs(fireshp.crs)

    fire_vectors = pd.DataFrame()
    errorlog = []

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
                errorlog.append(f'{e} occurs for fire ID # {i} \n')
        # output errorlog to a txt
        with open("errorlog_finalfire.txt", "w+") as f:
            f.write(errorlog)
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
                    errorlog.append(f'{e} occurs for fire ID # {i} \n')
        # output errorlog to a txt
        with open("errorlog_finalfire.txt", "w+") as f:
            f.write(errorlog)                  
        return fire_vectors
            
def generate_fire_vectors(fireshp, ignition, hexagons, threshold = 0, loopBy = "fire", **kwargs):
    """_summary_

    Args:
        fireshp (_type_): _description_
        ignition (_type_): _description_
        hexagons (_type_): _description_
        threshold (int, optional): _description_. Defaults to 0.
        loopBy (str, optional): _description_. Defaults to "fire".

    Returns:
        _type_: _description_
    """    
    hexagon = hexagons.copy()
    if 'Node_ID' in kwargs:
        hexagon = hexagon.rename(columns={kwargs["Node_ID"]: 'Node_ID'})
    
    if loopBy == "iteration":
        fire_vectors = spatial_join(fireshp, ignition, hexagon, threshold, iteration=True)
    
    if loopBy == "fire":
        fire_vectors = spatial_join(fireshp, ignition, hexagon, threshold, iteration=False)
     
    fire_vectors = fire_vectors.reset_index(drop = True)
    fire_vectors.drop(fire_vectors[fire_vectors['Node_ID_y'].isna()].index, inplace = True)                    
    
    fire_vectors['Node_ID_x'] = fire_vectors['Node_ID_x'].astype(int)
    fire_vectors['Node_ID_y'] = fire_vectors['Node_ID_y'].astype(int)
    
    fire_vectors.columns = ['Node_ID_x', 'Node_ID_y', 'fire', 'iteration']
    fire_vectors.rename(columns={'Node_ID_x':'column_j', 'Node_ID_y':'column_i'}, inplace=True)
    return fire_vectors

def pij_from_vectors(vectors, iterations):
    """_summary_

    Args:
        vectors (_type_): _description_
        iterations (_type_): _description_

    Returns:
        _type_: _description_
    """    

    fire_pij = vectors.groupby(['column_j', 'column_i'])[['fire']].count()
    fire_pij.reset_index(inplace = True)
    fire_pij = fire_pij.drop(fire_pij[fire_pij['column_j'] == fire_pij['column_i']].index)
    fire_pij['pij'] = fire_pij['fire'] / iterations
    fire_pij['pij'] = fire_pij['pij'].round(5)
    fire_pij['pij'] = fire_pij['pij'].apply(lambda x: '%.5f' % x)
    
    return fire_pij