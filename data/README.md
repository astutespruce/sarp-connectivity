DRAFT dams data obtained from Kat on 8/17/2018
SARP_Bounds data (boundary and HUCs) sent by Kat on 7/11/2018.
Level 3 & 4 ecoregions downloaded from EPA

## SARP Boundary

There was a hole between Missouri and Kentucky. I selected the same states and Puerto Rico from Census TIGER 2015 state boundaries: SARP_states.shp
I then dissolved it: SARP_boundary.shp
Reprojected to WGS84: SARP_boundary_wgs84.shp

## Dams vector tiles

To convert dams to CSV:

```
ogr2ogr -f CSV sarp_dams.csv Dams_WebViewer.gdb Dam_Inventory_AllDams_Metrics_Draft_Two_08172018 -overwrite
```

To convert dams to mbtiles:

1. First convert to CSV and preprocess
   Using `preprocess_data.py`

2. Then convert CSV to MBTiles:
   TODO: only include the attributes actually needed for the mbtiles file.

```
tippecanoe -f -Z0 -z14 -B6 --cluster-densest-as-needed -o ../../tiles/dams_full.mbtiles -l dams dams_mbtiles.csv
```

-r1 --cluster-distance=2

TODO: consider --drop-densest-as-needed instead

TODO: tune tile creation / base zoom & reduce rate. Right now guesses base zoom of 5
TODO: revisit clustering: https://github.com/mapbox/tippecanoe#clustered-points-world-cities-summing-the-clustered-population-visible-at-all-zoom-levels

## Ecoregions

Downloaded L3 and L4 ecoregions from EPA.

Selected by location in ArcMap against SARP_boundary:

-   SARP_ecoregion4.shp
-   SARP_ecoregion3.shp

Dissolved on L2_CODE:

-   SARP_ecoregion2.shp

Dissolved on L1_CODE:

-   SARP_ecoregion1.shp

## Watersheds

Obtained HUC12 - HUC8 levels from Kat

To HUC8 layer, added fields

-   HUC8 = HUC_8 (for consistency across the stack)
-   HUC6 = HUC8[:6]. Dissolved on this field: SARP_HUC6.shp
-   HUC4 = HUC8[:4]. Dissolved on this field: SARP_HUC4.shp
-   HUC2 = HUC8[:2]. Dissolved on this field: SARP_HUC2.shp

HUC8 has field issues that don't play nice with geopandas. Drop nonessential fields:
`ogr2ogr sarp_huc8.shp -select HUC8 sarp_bounds.gdb SARP_HUC8_Albers`

## Create Other layers vector tiles

Convert from shapefile to GeoJSON first, then cut tiles. Note the variation in max zoom; this was chosen by hand.

SARP Boundary:

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON boundary.json sarp_boundary.shp
tippecanoe -z 8 -l boundary -o ../../tiles/boundary.mbtiles boundary.json
```

SARP Inverse Boundary (for masking):
Create a GeoJSON polygon for world bounds using GeoJSON.io. In ArcGIS, erase from this
using SARP boundary: SARP_mask.shp (already in wgs_84)

```
ogr2ogr -f GeoJSON mask.json sarp_mask.shp
tippecanoe -z 8 -l mask -o ../../tiles/mask.mbtiles mask.json
```

States:

states, HUC2 - 8 and ecoregions:

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON states.json sarp_states.shp -sql "SELECT NAME as id from sarp_states"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC2.json sarp_HUC2.shp -sql "SELECT HUC2 as id from sarp_HUC2"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC4.json sarp_HUC4.shp -sql "SELECT HUC4 as id from sarp_HUC4"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC8.json SARP_Bounds.gdb SARP_HUC8_Albers -sql "SELECT HUC8 as id, HU_8_NAME as name from SARP_HUC8_Albers"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON ECO3.json sarp_ecoregion3.shp -sql "SELECT NA_L3CODE as id, US_L3NAME as name from sarp_ecoregion3"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON ECO4.json sarp_ecoregion4.shp -sql "SELECT US_L4CODE as id, US_L4NAME as name from sarp_ecoregion4"


tippecanoe -f -z 8 -l states -o ../../tiles/states.mbtiles -y id states.json
tippecanoe -f -z 8 -l HUC2 -o ../../tiles/HUC2.mbtiles  -T id:string -y id HUC2.json
tippecanoe -f -z 8 -l HUC4 -o ../../tiles/HUC4.mbtiles  -T id:string -y id HUC4.json
tippecanoe -f -z 10 -l HUC8 -o ../../tiles/HUC8.mbtiles  -T id:string -y id -y name HUC8.json
tippecanoe -f -z 10 -l ECO3 -o ../../tiles/ECO3.mbtiles  -T id:string -y id -y name ECO3.json
tippecanoe -f -z 12 -l ECO4 -o ../../tiles/ECO4.mbtiles  -T id:string -y id -y name ECO4.json
```

<!-- HUC12 - currently not being done:

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON SARP_HUC12_wgs84.json SARP_Bounds.gdb SARP_HUC12_Albers
tippecanoe -f -Z 7 -z 12 -l HUC12 -o ../../tiles/sarp_huc12.mbtiles  -T HUC12:string -y HUC12 sarp_huc12_wgs84.json
``` -->

<!-- ## Create centroids vector tiles (for labeling) - OUTDATED, not needed anymore:

Centroids are extracted using `extract_centroids.py`.

```
tippecanoe -f -B 0 -z 4 -l states_centroids -o ../../tiles/sarp_states_centroids.mbtiles sarp_states_centroids.csv
tippecanoe -f -B 0 -z 4 -l HUC2_centroids -o ../../tiles/sarp_HUC2_centroids.mbtiles  -T HUC2:string sarp_HUC2_centroids.csv
tippecanoe -f -B 0 -z 6 -l HUC4_centroids -o ../../tiles/sarp_HUC4_centroids.mbtiles  -T HUC4:string sarp_HUC4_centroids.csv
tippecanoe -f -B 4 -Z 4 -z 8 -l HUC8_centroids -o ../../tiles/sarp_HUC8_centroids.mbtiles  -T HUC8:string sarp_HUC8_centroids.csv

tippecanoe -f -B 0 -z 6 -l ecoregion3_centroids -o ../../tiles/sarp_ecoregion3_centroids.mbtiles  -T NA_L3CODE:string sarp_ecoregion3_centroids.csv
tippecanoe -f -B 4 -Z 4 -z 10 -l ecoregion4_centroids -o ../../tiles/sarp_ecoregion4_centroids.mbtiles  -T US_L4CODE:string sarp_ecoregion4_centroids.csv
``` -->

### Add summaries and join tiles together

Summaries are created using summarize_by_unit.py

```
tile-join -f -o states_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/state.csv states.mbtiles
tile-join -f -o HUC2_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc2.csv HUC2.mbtiles
tile-join -f -o HUC4_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc4.csv HUC4.mbtiles
tile-join -f -o HUC8_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc8.csv HUC8.mbtiles
tile-join -f -o ECO3_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/ECO3.csv ECO3.mbtiles
tile-join -f -o ECO4_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/ECO4.csv ECO4.mbtiles
```

Merge all tilesets together

```
tile-join -f -o sarp_summary.mbtiles mask.mbtiles boundary.mbtiles states_summary.mbtiles huc2_summary.mbtiles huc4_summary.mbtiles huc8_summary.mbtiles ECO3_summary.mbtiles ECO4_summary.mbtiles
```
