# Usage

To use postbp in a project:

```
import postbp
```

To load FGM outputs:

```
fireshp = postbp.read_fireshp('testDataset_FF.shp')
SRID = fireshp.crs # record spatial reference of fire shapefile
ignition = postbp.read_pointcsv('testDataset_Statistics.csv', SRID, x_col='x_coord', y_col='y_coord')
fireshpDaily = postbp.read_fireshp('testDataset_DFF.shp', daily=True)
```

To generate hexagonal patches:

```
hexagons, nodes = postbp.create_hexagons_nodes(area=[your_choice_in_m2], boundaryShp=fireshp)
hexagons = postbp.create_hexagons(area=[your_choice_in_m2], boundaryShp=fireshp)
nodes = postbp.nodes_from_hexagons(hexagons)
```

To get ignition probability

```
ignProb = postbp.generate_ign_prob(ignition, hexagons, iterations=[number_of_iterations_in_your_model])
```

To get burn probability 

```
burnProb = postbp.generate_burn_prob(fireshp, hexagons, iterations=[number_of_iterations_in_your_model])
```

To generate fire vectors:

```
fire_vectors = postbp.generate_fire_vectors(fireshp, ignition, hexagons)
pij = postbp.pij_from_vectors(fire_vectors, iterations=16000)
pij_shp = postbp.pij_to_shp(pij, nodes)

```

To generate daily fire vectors:

```
fire_vectors_daily = postbp.generate_daily_vectors(fireshpDaily, ignition, hexagons)
fire_vectors_w_angles = postbp.calc_angles(fire_vectors_daily, nodes)
daily_vectors_150 = postbp.select_angle(fire_vectors_w_angles, alpha=150)
daily_vectors_60 = postbp.select_angle(fire_vectors_w_angles, alpha=60)
pij_daily_150 = postbp.pij_from_vectors(daily_vectors_150, iterations=16000)
pij_daily_60 = postbp.pij_from_vectors(daily_vectors_60, iterations=16000)
pij_daily_150_shp = postbp.pij_to_shp(pij_daily_150, nodes)
pij_daily_60_shp = postbp.pij_to_shp(pij_daily_60, nodes)
```

To generate SSR:

```
fireSSR = postbp.generate_ssr(fire_vectors, hexagons)
```

To plot fire rose:

```fireRose = postbp.generate_fire_rose(pij, nodes)
postbp.plot_rose(fireRose, column='len', save=False)
```

