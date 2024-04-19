"""Main module."""

import numpy as np
from .common import prj2hex
import geopandas as gpd

def generate_burn_prob(fireshp, hexagons, iterations, **kwargs):
    """Generate shapefile of hexagonal network with values of burn likelihood
    for each hexagon on the landscape

    Args:
        fireshp (GeoDataFrame): fire perimeter dataset with fire ID (and iteration ID) and geometry
        hexagons (GeoDataFrame): geometry of hexagonal patches with ID field
        iterations (int): number of iterations

    Returns:
        GeoDataFrame: return a GeoDataFrame containing burn probability value at each hexagonal patches
    """    
    if 'threshold' in kwargs:
        threshold = kwargs['threshold']
    else:
        threshold = 0
    hexagon = hexagons.copy()
    if 'Node_ID' in kwargs:
        hexagon = hexagon.rename(columns={kwargs["Node_ID"]: 'Node_ID'})

    fireOL = prj2hex(fireshp, hexagon, threshold=threshold)
    if 'fire_column' in kwargs:
        fireOL.rename(columns={kwargs["fire_column"]: 'fire'}, inplace=True) 
       
    burned = fireOL.groupby('Node_ID')[['fire']].count()
    burned.reset_index(inplace=True)
    burnP = hexagon.merge(burned, on='Node_ID', how='left')
    burnP.fillna(0, inplace=True)
    burnP['burnProb'] = burnP['fire']/iterations*100
    burnP = burnP[['Node_ID', 'burnProb', 'geometry']]
    return burnP

def generate_ign_prob(ignition, hexagons, iterations, **kwargs):
    """Generate shapefile of hexagonal network with values of ignition likelihood
    for each hexagon on the landscape

    Args:
        ignition (_type_): _description_
        hexagons (GeoDataFrame): geometry of hexagonal patches with ID field
        iterations (int): number of iterations
    Returns:
        GeoDataFrame: return a GeoDataFrame containing ignition probability value at each hexagonal patches

    """    

    ign = ignition.copy()
    hexagon = hexagons.copy()
    if 'Node_ID' in kwargs:
        hexagon = hexagon.rename(columns={kwargs["Node_ID"]: 'Node_ID'})
    if 'fire_column' in kwargs:
        ign.rename(columns={kwargs["fire_column"]: 'fire'}, inplace=True)    

    ignSJ = gpd.sjoin(ign, hexagon, how = 'inner', op = 'within')
    ignGr = ignSJ.groupby(['Node_ID'])[['fire']].count()
    ignGr = hexagon.merge(ignGr, on='Node_ID', how='right')
    ignGr.fillna(0, inplace=True)
    ignGr['ignProb'] = ignGr['fire']/iterations*100
    ignGr = ignGr[['Node_ID', 'ignProb', 'geometry']]
    return ignGr

def generate_fireshed(fire_vectors, AOCshp, fireshp, hexagons, **kwargs):
    """Generate the fireshed in regard to an area of concern (AOC) based on the fire vectors 

    Args:
        fire_vectors (DataFrame): outputs from generate_fire_vectors function
        AOCshp (GeoDataFrame): geometry of the area of concern
        fireshp (GeoDataFrame): fire perimeter dataset with fire ID (and iteration ID) and geometry
        hexagons (GeoDataFrame): geometry of hexagonal patches with ID field

    Returns:
        GeoDataFrame: return a geodataframe of dissolved geometry of the fireshed of fires that can burn into the area of concern.
    """    
    hexagon = hexagons.copy()
    if 'Node_ID' in kwargs:
        hexagon = hexagon.rename(columns={kwargs["Node_ID"]: 'Node_ID'})
    fv = fire_vectors.copy()
    if 'column_i' in kwargs:
        fv.rename(columns={kwargs["column_i"]: 'column_i'}, inplace=True)    
    if 'column_j' in kwargs:
        fv.rename(columns={kwargs["column_j"]: 'column_j'}, inplace=True)
    if 'fire_column' in kwargs:
        fv.renmae(columns={kwargs['fire_column']: 'fire'}, inplace=True)     

    aoc = prj2hex(AOCshp, hexagon, threshold=0)
    fireAOC = fv.loc[fv['column_j'].isin(aoc['Node_ID'])]
    fireAOCshp = fireshp.merge(fireAOC, on='fire', how='right')
    fireAOCshp['V'] = 1
    fireAOCshp = fireAOCshp.dissolve(by='V')
    fireAOCshp['area_ha'] = fireAOCshp.area/10000
    return fireAOCshp

def generate_fireplain(fire_vectors, AOCshp, fireshp, hexagons, **kwargs):
    """Generate the fireplain in regard to an area of concern (AOC) based on the fire vectors

    Args:
        fire_vectors (DataFrame): outputs from generate_fire_vectors function
        AOCshp (GeoDataFrame): geometry of the area of concern
        fireshp (GeoDataFrame): fire perimeter dataset with fire ID (and iteration ID) and geometry
        hexagons (GeoDataFrame): geometry of hexagonal patches with ID field

    Returns:
        GeoDataFrame: return a geodataframe of dissolved geometry of the fireplain for fires ignited in the area of concern.
    """
    hexagon = hexagons.copy()
    if 'Node_ID' in kwargs:
        hexagon = hexagon.rename(columns={kwargs["Node_ID"]: 'Node_ID'})
    fv = fire_vectors.copy()
    if 'column_i' in kwargs:
        fv.rename(columns={kwargs["column_i"]: 'column_i'}, inplace=True)    
    if 'column_j' in kwargs:
        fv.rename(columns={kwargs["column_j"]: 'column_j'}, inplace=True)
    if 'fire_column' in kwargs:
        fv.renmae(columns={kwargs['fire_column']: 'fire'}, inplace=True) 
    
    aoc = prj2hex(AOCshp, hexagon, threshold=0)
    fireAOC = fire_vectors.loc[fire_vectors['i'].isin(aoc['Node_ID'])]
    fireAOCshp = fireshp.merge(fireAOC, on='fire', how='right')
    fireAOCshp['V'] = 1
    fireAOCshp = fireAOCshp.dissolve(by='V')
    fireAOCshp['area_ha'] = fireAOCshp.area/10000
    return fireAOCshp

def generate_ssr(fire_vectors, hexagons, **kwargs):
    """Generate a shapefile with values of Source-Sink-Ratio based on the fire vectors 

    Args:
        fire_vectors (DataFrame): outputs from generate_fire_vectors function
        hexagons (GeoDataFrame): geometry of hexagonal patches with ID field

    Returns:
        GeoDataFrame: return a GeoDataFrame containing the Source-Sink Ratio value at each hexagonal patches
    """    
    hexagon = hexagons.copy()
    if 'Node_ID' in kwargs:
        hexagon = hexagon.rename(columns={kwargs["Node_ID"]: 'Node_ID'})
    fv = fire_vectors.copy()
    if 'column_i' in kwargs:
        fv.rename(columns={kwargs["column_i"]: 'column_i'}, inplace=True)    
    if 'column_j' in kwargs:
        fv.rename(columns={kwargs["column_j"]: 'column_j'}, inplace=True)
    if 'fire_column' in kwargs:
        fv.renmae(columns={kwargs['fire_column']: 'fire'}, inplace=True) 
    
    fire_orig = fv.groupby('column_i')[['fire']].count()
    fire_orig.reset_index(inplace=True)
    fire_orig.rename(columns={'fire':'asSource'}, inplace=True)
    fire_dest = fire_vectors.groupby('column_j')[['fire']].count()
    fire_dest.reset_index(inplace=True)
    fire_dest.rename(columns={'fire':'asSink'}, inplace=True)
    fireSSR = hexagon.merge(fire_orig, left_on='Node_ID', right_on='column_i', how='left')
    fireSSR = fireSSR.merge(fire_dest, left_on='Node_ID', right_on='column_j', how='left')
    fireSSR['SSR'] = np.log10(fireSSR['asSource'] / fireSSR['asSink'])
    fireSSR.dropna(inplace=True)
    return fireSSR



