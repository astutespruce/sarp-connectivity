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

1. First convert to GeoJSON (use WGS84):

```
ogr2ogr -f GeoJSON -t_srs EPSG:4326 sarp_dams.json Dams_WebViewer.gdb Dam_Inventory_AllDams_Metrics_Draft_Two_08172018
```

TODO: investigate using CSV instead of GeoJSON so that we can manage attributes. Already contains x,y fields with long,lat

2. Then convert GeoJSON to MBTiles:
   TODO: tune tile creation / base zoom & reduce rate. Right now guesses base zoom of 5
   TODO: revisit clustering: https://github.com/mapbox/tippecanoe#clustered-points-world-cities-summing-the-clustered-population-visible-at-all-zoom-levels
   TODO: refine included attributes

Include select attributes that will be used to join to other info:
UniqueID,State,HUC12,Ecoregion4,Ecoregion3

Consider adding:
River,Height,PurposeCategory,<other domain fields>

```
tippecanoe -Bg -o ../../tiles/sarp_dams.mbtiles -n "SARP Dams" -A "SARP" -N "SARP Dams" -y UniqueID -y State -y HUC12 -y Ecoregion4 -y Ecoregion3 sarp_dams.json
```

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
ogr2ogr -t_srs EPSG:4326 -f GeoJSON SARP_boundary_wgs84.json sarp_boundary.shp
tippecanoe -z 8 -l boundary -o ../../tiles/sarp_boundary.mbtiles sarp_boundary_wgs84.json
```

SARP Inverse Boundary (for masking):
Create a GeoJSON polygon for world bounds using GeoJSON.io. In ArcGIS, erase from this
using SARP boundary: SARP_mask.shp (already in wgs_84)

```
ogr2ogr -f GeoJSON SARP_mask_wgs84.json sarp_mask.shp
tippecanoe -z 8 -l mask -o ../../tiles/sarp_mask.mbtiles sarp_mask_wgs84.json
```

States:

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON SARP_states_wgs84.json sarp_states.shp
tippecanoe -f -z 8 -l states -o ../../tiles/sarp_states.mbtiles -y NAME sarp_states_wgs84.json
```

HUC2 - 8:

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON SARP_HUC2_wgs84.json sarp_HUC2.shp
ogr2ogr -t_srs EPSG:4326 -f GeoJSON SARP_HUC4_wgs84.json sarp_HUC4.shp
ogr2ogr -t_srs EPSG:4326 -f GeoJSON SARP_HUC8_wgs84.json SARP_Bounds.gdb SARP_HUC8_Albers

tippecanoe -f -z 8 -l HUC2 -o ../../tiles/sarp_huc2.mbtiles  -T HUC2:string -y HUC2 sarp_huc2_wgs84.json
tippecanoe -f -z 8 -l HUC4 -o ../../tiles/sarp_huc4.mbtiles  -T HUC4:string -y HUC4 sarp_huc4_wgs84.json
tippecanoe -f -Z 5 -z 10 -l HUC8 -o ../../tiles/sarp_huc8.mbtiles  -T HUC8:string -y HUC8 sarp_huc8_wgs84.json
```

HUC12 - currently not being done:

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON SARP_HUC12_wgs84.json SARP_Bounds.gdb SARP_HUC12_Albers
tippecanoe -f -Z 7 -z 12 -l HUC12 -o ../../tiles/sarp_huc12.mbtiles  -T HUC12:string -y HUC12 sarp_huc12_wgs84.json
```

Ecoregions:

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON SARP_ecoregion1_wgs84.json sarp_ecoregion1.shp
ogr2ogr -t_srs EPSG:4326 -f GeoJSON SARP_ecoregion2_wgs84.json sarp_ecoregion2.shp
ogr2ogr -t_srs EPSG:4326 -f GeoJSON SARP_ecoregion3_wgs84.json sarp_ecoregion3.shp
ogr2ogr -t_srs EPSG:4326 -f GeoJSON SARP_ecoregion4_wgs84.json sarp_ecoregion4.shp

tippecanoe -f -z 8 -l ecoregion1 -o ../../tiles/sarp_ecoregion1.mbtiles  -T NA_L1CODE:string -y HUC4 sarp_ecoregion1_wgs84.json
tippecanoe -f -z 8 -l ecoregion2 -o ../../tiles/sarp_ecoregion2.mbtiles  -T NA_L2CODE:string -y HUC4 sarp_ecoregion2_wgs84.json
tippecanoe -f -Z 3 -z 10 -l ecoregion3 -o ../../tiles/sarp_ecoregion3.mbtiles  -T NA_L3CODE:string -y HUC4 sarp_ecoregion3_wgs84.json
tippecanoe -f -Z 4 -z 12 -l ecoregion4 -o ../../tiles/sarp_ecoregion4.mbtiles  -T L4_KEY:string -y HUC4 sarp_ecoregion4_wgs84.json
```

## Create centroids vector tiles (for labeling) - OUTDATED, not needed anymore:

Centroids are extracted using `extract_centroids.py`.

```
tippecanoe -f -B 0 -z 4 -l states_centroids -o ../../tiles/sarp_states_centroids.mbtiles sarp_states_centroids.csv
tippecanoe -f -B 0 -z 4 -l HUC2_centroids -o ../../tiles/sarp_HUC2_centroids.mbtiles  -T HUC2:string sarp_HUC2_centroids.csv
tippecanoe -f -B 0 -z 6 -l HUC4_centroids -o ../../tiles/sarp_HUC4_centroids.mbtiles  -T HUC4:string sarp_HUC4_centroids.csv
tippecanoe -f -B 4 -Z 4 -z 8 -l HUC8_centroids -o ../../tiles/sarp_HUC8_centroids.mbtiles  -T HUC8:string sarp_HUC8_centroids.csv

tippecanoe -f -B 0 -z 4 -l ecoregion1_centroids -o ../../tiles/sarp_ecoregion1_centroids.mbtiles  -T NA_L1CODE:string sarp_ecoregion1_centroids.csv
tippecanoe -f -B 0 -z 4 -l ecoregion2_centroids -o ../../tiles/sarp_ecoregion2_centroids.mbtiles  -T NA_L2CODE:string sarp_ecoregion2_centroids.csv
tippecanoe -f -B 0 -z 6 -l ecoregion3_centroids -o ../../tiles/sarp_ecoregion3_centroids.mbtiles  -T NA_L3CODE:string sarp_ecoregion3_centroids.csv
tippecanoe -f -B 4 -Z 4 -z 10 -l ecoregion4_centroids -o ../../tiles/sarp_ecoregion4_centroids.mbtiles  -T L4_KEY:string sarp_ecoregion4_centroids.csv
```

### Add summaries and join tiles together

Summaries are created using summarize_by_unit.py

```
tile-join -f -o sarp_states_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/state.csv sarp_states.mbtiles
tile-join -f -o sarp_huc2_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc2.csv sarp_huc2.mbtiles
tile-join -f -o sarp_huc4_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc4.csv sarp_huc4.mbtiles
tile-join -f -o sarp_huc8_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc8.csv sarp_huc8.mbtiles

tile-join -f -o sarp_ecoregion1_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/ecoregion1.csv sarp_ecoregion1.mbtiles
tile-join -f -o sarp_ecoregion2_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/ecoregion2.csv sarp_ecoregion2.mbtiles
tile-join -f -o sarp_ecoregion3_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/ecoregion3.csv sarp_ecoregion3.mbtiles
tile-join -f -o sarp_ecoregion4_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/ecoregion4.csv sarp_ecoregion4.mbtiles
```

Merge all tilesets together

```
tile-join -f -o sarp_summary.mbtiles sarp_mask.mbtiles sarp_boundary.mbtiles sarp_states_summary.mbtiles sarp_huc2_summary.mbtiles sarp_huc4_summary.mbtiles sarp_huc8_summary.mbtiles sarp_ecoregion1_summary.mbtiles sarp_ecoregion2_summary.mbtiles sarp_ecoregion3_summary.mbtiles sarp_ecoregion4_summary.mbtiles
```
