# Southeast Aquatic Barrier Inventory Data Processing

## Barriers Inventory

Final dams and small barriers data sent by Kat on 12/12/2018:

-   Dams_Webviewer_DraftOne_Final.gdb::SARP_Dam_Inventory_Prioritization_12132018_D1_ALL
-   Road_Related_Barriers_DraftOne_Final.gdb::Road_Barriers_WebViewer_DraftOne_ALL_12132018

#### Prior processing

The inventory datasets above were based in part on preprocessing to calculate network connectivity metrics and species information.
The results of the preprocessing were provided to Kat, and she combined into the authoritative inventory.

-   Network metrics: https://github.com/brendan-ward/nhdnet
-   Species information: `aggregate_spp_occurrences.py` followed by `extract_species_data.py`

#### SARP Boundary Fix

SARP_Bounds data (boundary and HUCs) sent by Kat on 7/11/2018.
There was a hole between Missouri and Kentucky. I selected the same states and Puerto Rico from Census TIGER 2015 state boundaries: SARP_states.shp
I then dissolved it: `SARP_boundary.shp` and reprojected to WGS84: `SARP_boundary_wgs84.shp`

#### Preprocessing

Dams and small barriers were prepared using:

-   `preprocess_dams.py`
-   `preprocess_small_barriers.py`

Followed by:

-   `summarize_by_unit.py`

## Other data sources

### Watersheds - updated

Downloaded the WBD dataset from: ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Hydrography/WBD/National/GDB/

1. selected units from HUC2 ... HUC12 that intersect SARP bounds
2. exported each to a new shapefile HUC\*.shp

### States and counties

Downloaded from US Census TIGER 2018: https://www.census.gov/cgi-bin/geo/shapefiles/index.php

1. Extracted states that fell within SARP boundary.
2. Extracted counties whose STATE_FP attribute was one of the states above.

## Vector Tiles

Assumes a working directory of `data/src`

Convert from shapefile to GeoJSON first, then cut tiles. Note the variation in max zoom; this was chosen by hand.

#### Dams

```
tippecanoe -f -Z10 -z12 -pg -pe --cluster-densest-as-needed -o ../tiles/dams_no_network.mbtiles -l no_network -T Name:string -T River:string dams_no_network.csv

tippecanoe -f -Z5 -z12 -B6 -pg -pe --cluster-densest-as-needed -o ../tiles/dams_with_network.mbtiles -l dams -T Name:string -T River:string dams_with_network.csv

tile-join -f -pg --no-tile-size-limit -o ../../tiles/sarp_dams.mbtiles dams_no_network.mbtiles dams_with_network.mbtiles
```

<!-- tippecanoe -f -Z4 -z12 -B4 -pg --cluster-densest-as-needed -o ../tiles/dams_topn.mbtiles -l dams_topn -T Name:string -T River:string dams_topn.csv -->

#### SARP Boundary:

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON boundary.json sarp_boundary.shp
tippecanoe -z 8 -l boundary -o ../tiles/boundary.mbtiles boundary.json
```

#### SARP Inverse Boundary (for masking):

Create a GeoJSON polygon for world bounds using GeoJSON.io. In ArcGIS, erase from this
using SARP boundary: SARP_mask.shp (already in wgs_84)

```
ogr2ogr -f GeoJSON mask.json sarp_mask.shp
tippecanoe -z 8 -l mask -o ../tiles/mask.mbtiles mask.json
```

#### Summary Units:

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON states.json states.shp -sql "SELECT NAME as id from states"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON counties.json counties.shp -sql "SELECT GEOID as id, NAME as name from counties"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC6.json HUC6.shp -sql "SELECT HUC6 as id, NAME as name from HUC6"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC8.json HUC8.shp -sql "SELECT HUC8 as id, NAME as name from HUC8"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC12.json HUC12.shp -sql "SELECT HUC12 as id, NAME as name from HUC12"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON ECO3.json sarp_ecoregion3.shp -sql "SELECT NA_L3CODE as id, US_L3NAME as name from sarp_ecoregion3"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON ECO4.json sarp_ecoregion4.shp -sql "SELECT US_L4CODE as id, US_L4NAME as name from sarp_ecoregion4"


tippecanoe -f -z 8 -l State -o ../tiles/states.mbtiles states.json
tippecanoe -f -Z 3 -z 12 -l County -o ../tiles/counties.mbtiles counties.json
tippecanoe -f -z 8 -l HUC6 -o ../tiles/HUC6.mbtiles  -T id:string HUC6.json
tippecanoe -f -z 10 -l HUC8 -o ../tiles/HUC8.mbtiles  -T id:string HUC8.json
tippecanoe -f -Z 6 -z 12 -l HUC12 -o ../tiles/HUC12.mbtiles  -T id:string HUC12.json
tippecanoe -f -z 10 -l ECO3 -o ../tiles/ECO3.mbtiles  -T id:string ECO3.json
tippecanoe -f -Z 3 -z 12 -l ECO4 -o ../tiles/ECO4.mbtiles  -T id:string ECO4.json
```

### Add summaries and join tiles together

Assumes a working directory of `data/tiles`.

Summaries are created using summarize_by_unit.py

```
tile-join -f -o states_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/State.csv states.mbtiles
tile-join -f -o counties_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/County.csv counties.mbtiles
tile-join -f -o HUC6_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc6.csv HUC6.mbtiles
tile-join -f -o HUC8_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc8.csv HUC8.mbtiles
tile-join -f -o HUC12_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc12.csv HUC12.mbtiles
tile-join -f -o ECO3_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/ECO3.csv ECO3.mbtiles
tile-join -f -o ECO4_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/ECO4.csv ECO4.mbtiles
```

Merge all tilesets together

```
tile-join -f --no-tile-size-limit -o ../../tiles/sarp_summary.mbtiles mask.mbtiles boundary.mbtiles states_summary.mbtiles counties_summary.mbtiles huc6_summary.mbtiles huc8_summary.mbtiles huc12_summary.mbtiles ECO3_summary.mbtiles ECO4_summary.mbtiles
```
