# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 16:22:15 2024

@author: nliu
"""

# import geopandas as gpd
# import postbp
# import os

# os.chdir(r'E:\DATA\Banff_study_Ning\shp')

# # fireshp = postbp.read_fireshp('000testDataset_FF.shp')
# columns = ['fire', 'iteration']
# fireshp = gpd.read_file('0000testDataset_FF.shp', columns=columns, driver = 'ESRI Shapefile')

# hexagons, nodes = postbp.create_hexagons_nodes(area=0, boundaryShp=fireshp, side=1400)

# area = hexagons.at[0, 'geometry'].area/10000
# hexagons.rename(columns={'Node_ID':'GridID'}, inplace=True)
# nodes.rename(columns={'Node_ID':'GridID'}, inplace=True)

# burnp = postbp.generate_burn_prob(fireshp=fireshp, hexagons=hexagons, Node_ID='GridID')

# burnp.dropna(subset='fire', inplace=True)


