import numpy as np
# from common import prj2hex
import geopandas as gpd

def prj2hex(shp0, hexagons, threshold=0):
    shp1 = gpd.overlay(shp0, hexagons, how='intersection') 
    shp1['areaFire'] = shp1.geometry.area
    shp1 = shp1.loc[shp1['areaFire'] > threshold]
    shp1.drop(labels='areaFire', axis=1, inplace=True)
    return shp1

def generate_ignProb(ignition, hexagons):
    ign = gpd.sjoin(ignition, hexagons, how = 'inner', op = 'within')
    ignGr = ign.groupby(['Node_ID'])[['fire']].count()
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

def generate_burnProb(fireshp, hexagons, **kwargs):
    fireOL = prj2hex(fireshp, hexagons, threshold=0)
    burned = fireOL.groupby('Node_ID')[['fire']].count()
    burned.reset_index(inplace=True)
    burnP = hexagons.merge(burned, on='Node_ID', how='left')
    return burnP

def generate_fireshed(fire_vectors, AOCshp, fireshp, hexagons):
    if len(fire_vectors.columns)==3:
        fire_vectors.columns=['orig', 'dest', 'fire']
    elif len(fire_vectors.columns)==4:
        fire_vectors.columns=['orig', 'dest', 'fire', 'day']
    else:
        raise ValueError("please provide vector file in the format of columns: 'i', 'j', 'fire', ('day').")
    aoc = prj2hex(AOCshp, hexagons, threshold=0)
    fireAOC = fire_vectors.loc[fire_vectors['dest'].isin(aoc['Node_ID'])]
    fireAOCshp = fireshp.merge(fireAOC, on='fire', how='right')
    fireAOCshp['V'] = 1
    fireAOCshp = fireAOCshp.dissolve(by='V')
    fireAOCshp['area_ha'] = fireAOCshp.area/10000
    return fireAOCshp

def generate_SSR(fire_vectors, hexagons, **kwargs):
    fire_vectors.columns=['origi', 'desti','fire']
    fire_orig = fire_vectors.groupby('origi')[['fire']].count()
    fire_orig.reset_index(inplace=True)
    fire_orig.rename(columns={'fire':'asSource'}, inplace=True)
    fire_dest = fire_vectors.groupby('desti')[['fire']].count()
    fire_dest.reset_index(inplace=True)
    fire_dest.rename(columns={'fire':'asSink'}, inplace=True)
    fireSSR = hexagons.merge(fire_orig, left_on='Node_ID', right_on='origi', how='left')
    fireSSR = fireSSR.merge(fire_dest, left_on='Node_ID', right_on='desti', how='left')
    fireSSR['SSR'] = np.log10(fireSSR['asSource'] / fireSSR['asSink'])
    fireSSR.dropna(inplace=True)
    return fireSSR



