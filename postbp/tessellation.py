'''Module for setting up hexagon network.

1. grabs the spatial bounds of fire shapefile.
2. using user-defined area value to build hexagon network on the bounded area. 
3. projection of the hexagon network to be the same as that of the fire shapefile.
4. generate the centroid of the hexes as nodes shapefile
5. generate arcs connecting neighbouring nodes

'''

import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
import warnings
warnings.filterwarnings("ignore")
import math
import tqdm

def create_hexnodes(area, xmin, ymin, xmax, ymax):
    nodes = []
    
    side = 3**0.25 * math.sqrt(2 * area / 9)
    v_step = math.sqrt(3) * side
    h_step = 1.5 * side


    h_skip = math.ceil(xmin / h_step) - 1
    h_start = h_skip * h_step

    v_skip = math.ceil(ymin / v_step) - 1
    v_start = v_skip * v_step

    h_end = xmax + h_step
    v_end = ymax + v_step

    if v_start - (v_step / 2.0) < ymin:
        v_start_array = [v_start + (v_step / 2.0), v_start]
    else:
        v_start_array = [v_start - (v_step / 2.0), v_start]

    v_start_idx = int(abs(h_skip) % 2)

    c_x = h_start
    c_y = v_start_array[v_start_idx]
    v_start_idx = (v_start_idx + 1) % 2
    while c_x < h_end:
        while c_y < v_end:
            nodes.append((c_x, c_y))
            c_y += v_step
        c_x += h_step
        c_y = v_start_array[v_start_idx]
        v_start_idx = (v_start_idx + 1) % 2
        
    return nodes

def create_hexgrids(area, x, y):
    """
    Create a hexagon centered on (x, y)
    :param x: x-coordinate of the hexagon's center
    :param y: y-coordinate of the hexagon's center
    :return: The polygon containing the hexagon's coordinates
    """
    # l: length of the hexagon's side
    l = 3**0.25 * math.sqrt(2 * area / 9)
    c = [[x + math.cos(math.radians(angle)) * l, y + math.sin(math.radians(angle)) * l] for angle in range(0, 360, 60)]
    return Polygon(c)

def create_hexagons_nodes(boundaryShp, **kwargs):
    """_summary_

    Args:
        boundaryShp (_type_): _description_

    Returns:
        _type_: _description_
    """    
    if 'area' in kwargs:
        area = kwargs['area']

    if "side" in kwargs:
        area = kwargs["side"]**2*3/2*math.sqrt(3)

    if "diameter" in kwargs:
        area = kwargs["diameter"]**2*3/8*math.sqrt(3)
    
    myCRS = boundaryShp.crs
    xmin,ymin,xmax,ymax =  boundaryShp.total_bounds
    nodes = create_hexnodes(area, xmin, ymin, xmax, ymax)
    hexagons = [create_hexgrids(area, node[0], node[1]) for node in nodes]
    
    nodes = [Point(node) for node in nodes]
    nodes = gpd.GeoDataFrame({'geometry': nodes})
    nodes['Node_ID'] = nodes.index + 1
    nodes.crs = myCRS
    hexagons = gpd.GeoDataFrame({'geometry':hexagons})
    hexagons['Node_ID'] = hexagons.index + 1
    hexagons.crs = myCRS

    return hexagons, nodes

def create_hexagons(boundaryShp, **kwargs):
    """_summary_

    Args:
        boundaryShp (_type_): _description_

    Returns:
        _type_: _description_
    """    
    if 'area' in kwargs:
        area = kwargs['area']

    if "side" in kwargs:
        area = kwargs["side"]**2*3/2*math.sqrt(3)

    if "diameter" in kwargs:
        area = kwargs["diameter"]**2*3/8*math.sqrt(3)
    
    myCRS = boundaryShp.crs
    xmin,ymin,xmax,ymax =  boundaryShp.total_bounds
    nodes = create_hexnodes(area, xmin, ymin, xmax, ymax)
    hexagons = [create_hexgrids(area, node[0], node[1]) for node in nodes]
    
    nodes = [Point(node) for node in nodes]
    nodes = gpd.GeoDataFrame({'geometry': nodes})
    nodes['Node_ID'] = nodes.index + 1
    nodes.crs = myCRS
    hexagons = gpd.GeoDataFrame({'geometry':hexagons})
    hexagons['Node_ID'] = hexagons.index + 1
    hexagons.crs = myCRS

    return hexagons

def nodes_from_hexagons(hexagons):
    """_summary_

    Args:
        hexagons (_type_): _description_

    Returns:
        _type_: _description_
    """    
    nodes = hexagons.copy()
    nodes['centroid'] = nodes.geometry.centroid
    nodes.drop(labels='geometry', axis=1, inplace=True)
    nodes.rename(columns={'centroid':'geometry'}, inplace=True)
    nodes = nodes.set_geometry('geometry')
    return nodes

def create_arcs(hexagons, **kwargs):
    """_summary_

    Args:
        hexagons (_type_): _description_

    Returns:
        _type_: _description_
    """    
    hexagon = hexagons.copy()
    if 'Node_ID' in kwargs:
        hexagon = hexagon.rename(columns={kwargs["Node_ID"]: 'Node_ID'})
        
    nodes = nodes_from_hexagons(hexagon)
    nodes = nodes.set_index('Node_ID')
    SRID = hexagon.crs
    hexagon = hexagon.set_index('Node_ID')

    arcs = gpd.GeoDataFrame()
    df=gpd.GeoDataFrame()
    for index, _ in tqdm(hexagon.iterrows()):
        nnnn = hexagon[~hexagon.geometry.disjoint(hexagon.at[index,'geometry'])].index.tolist()
        nnnn = [i for i in nnnn if index != i]
        mmmm = [index] * len(nnnn)
        mmnn = [LineString(xy) for xy in zip(nodes.loc[mmmm].geometry, nodes.loc[nnnn].geometry)]
        mmnn = gpd.GeoDataFrame(df, crs = SRID, geometry = mmnn )
        mmnn['Node_1'] = mmmm
        mmnn['Node_2'] = nnnn
        arcs = arcs.append(mmnn)
    arcs['Node_1'] = arcs['Node_1'].astype(int)
    arcs['Node_2'] = arcs['Node_2'].astype(int)

    return arcs
