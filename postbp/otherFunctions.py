import numpy as np
from postbp.common import prj2hex
import geopandas as gpd


def generate_ign_prob(ignition, hexagons, **kwargs):

    '''
    Generate shapefile of hexagonal network with values of ignition likelihood
    for each hexagon on the landscape
    '''

    ign = ignition.copy()
    if 'Node_ID' in kwargs:
        hexagons.rename(columns={kwargs["Node_ID"]: 'Node_ID'}, inplace=True)
    if 'fire_column' in kwargs:
        ign.rename(columns={kwargs["fire_column"]: 'fire'}, inplace=True)    

    ignSJ = gpd.sjoin(ign, hexagons, how = 'inner', op = 'within')
    ignGr = ignSJ.groupby(['Node_ID'])[['fire']].count()
    ignGr.rename(column={'fire':'ignCount'})
    ignGr = hexagons.merge(ignGr, on='Node_ID', how='right')
    ignGr = ignGr[['Node_ID', 'ignCount', 'geometry']]
    return ignGr

def generate_ESA(fire_vectors, AOCshp, fireshp, hexagons, pij):
    if len(fire_vectors.columns)==3:
        fire_vectors.columns=['i', 'j', 'fireCount']
    elif len(fire_vectors.columns)==4:
        fire_vectors.columns=['i', 'j', 'fireCount', 'day']
    else:
        raise ValueError("please provide vector file in the format of columns: 'i', 'j', 'fire', ('day').")
    aoc = prj2hex(AOCshp, hexagons, threshold=0)
    fireAOC = fire_vectors.loc[fire_vectors['i'].isin(aoc['Node_ID'])]
    fireAOCgr = fireAOC.groupby(['i', 'j'])[['fireCount']].count()
    fireAOCgr = fireAOCgr.merge(pij, on = ['i', 'j'], how='left')
    fireAOCshp = fireshp.merge(fireAOC, on='fire', how='right')
    fireAOCshp['V'] = 1
    fireAOCshp = fireAOCshp.dissolve(by='V')
    fireAOCshp['area_ha'] = fireAOCshp.area/10000
    return fireAOCshp

def generate_burn_prob(fireshp, hexagons, **kwargs):

    '''
    Generate shapefile of hexagonal network with values of burn likelihood
    for each hexagon on the landscape
    '''

    if 'Node_ID' in kwargs:
        hexagons.rename(columns={kwargs["Node_ID"]: 'Node_ID'}, inplace=True)

    fireOL = prj2hex(fireshp, hexagons, threshold=0)
    if 'fire_column' in kwargs:
        fireOL.rename(columns={kwargs["fire_column"]: 'fire'}, inplace=True) 
       
    burned = fireOL.groupby('Node_ID')[['fire']].count()
    burned.reset_index(inplace=True)
    burnP = hexagons.merge(burned, on='Node_ID', how='left')
    return burnP

def generate_fireshed(fire_vectors, AOCshp, fireshp, hexagons, **kwargs):

    '''
    Generate fire shed to an area of concern (AOC) based on the fire vectors 
    '''
    if 'Node_ID' in kwargs:
        hexagons.rename(columns={kwargs["Node_ID"]: 'Node_ID'}, inplace=True)
    fv = fire_vectors.copy()
    if 'column_i' in kwargs:
        fv.rename(columns={kwargs["column_i"]: 'column_i'}, inplace=True)    
    if 'column_j' in kwargs:
        fv.rename(columns={kwargs["column_j"]: 'column_j'}, inplace=True)
    if 'fire_column' in kwargs:
        fv.renmae(columns={kwargs['fire_column']: 'fire'}, inplace=True)     

    aoc = prj2hex(AOCshp, hexagons, threshold=0)
    fireAOC = fv.loc[fv['column_j'].isin(aoc['Node_ID'])]
    fireAOCshp = fireshp.merge(fireAOC, on='fire', how='right')
    fireAOCshp['V'] = 1
    fireAOCshp = fireAOCshp.dissolve(by='V')
    fireAOCshp['area_ha'] = fireAOCshp.area/10000
    return fireAOCshp

def generate_SSR(fire_vectors, hexagons, **kwargs):
    '''
    Generate a shapefile with values of Source-Sink-Ratio based on the fire vectors 
    '''
    if 'Node_ID' in kwargs:
        hexagons.rename(columns={kwargs["Node_ID"]: 'Node_ID'}, inplace=True)
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
    fireSSR = hexagons.merge(fire_orig, left_on='Node_ID', right_on='column_i', how='left')
    fireSSR = fireSSR.merge(fire_dest, left_on='Node_ID', right_on='column_j', how='left')
    fireSSR['SSR'] = np.log10(fireSSR['asSource'] / fireSSR['asSink'])
    fireSSR.dropna(inplace=True)
    return fireSSR



