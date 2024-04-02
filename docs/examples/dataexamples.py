# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 16:22:15 2024

@author: nliu
"""

import geopandas as gpd
import postbp
import os
import tqdm
import time

os.chdir(r'E:\DATA\Banff_study_Ning\shp')

fireshp = postbp.read_fireshp('000testDataset_FF.shp')
ignition = postbp.read_pointshp('0000testDataset_ign.shp')
fireshpdaily = postbp.read_fireshp('000testDataset_DFF.shp', 'day')

hexagons, nodes = postbp.create_hexagons_nodes(boundaryShp=fireshp, diameter=2700)
hexagons = postbp.create_hexagons(boundaryShp=fireshp, side=1395)
nodes = postbp.nodes_from_hexagons(hexagons)
# hexarea = hexagons.at[0,'geometry'].area

hexagons.rename(columns={'Node_ID':'GridID'}, inplace=True)
nodes.rename(columns={'Node_ID':'GridID'}, inplace=True)


#### test progress bar
with tqdm(total=100) as pbar:
    for i in range(10):
        time.sleep(0.1)
        pbar.update(10)

print('done')
def prj2hex(shp0, hexagons, threshold=0):
    shp1 = gpd.overlay(shp0, hexagons, how='intersection') 
    shp1['areaFire'] = shp1.geometry.area
    shp1 = shp1.loc[shp1['areaFire'] > threshold]
    shp1.drop(labels='areaFire', axis=1, inplace=True)
    return shp1

burnp = postbp.generate_burn_prob(fireshp=fireshp, hexagons=hexagons, iterations=16000, Node_ID='GridID')

burnp.dropna(subset='fire', inplace=True)


