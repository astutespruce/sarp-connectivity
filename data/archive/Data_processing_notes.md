# ARCHIVE version of data processing notes

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

Save all dams for use in the heatmap but without attributes, save the full dams at zooms 6-14 (note: many dams still dropped at Z6, some at Z7), and the priority dams at all zooms:

```
tippecanoe -f -Z0 -z10 -B6 --cluster-densest-as-needed -o ../../tiles/dams_heatmap.mbtiles -l dams_heatmap --exclude-all dams_mbtiles.csv
tippecanoe -f -Z6 -z14 -B6 --cluster-densest-as-needed -o ../../tiles/dams_full.mbtiles -l dams dams_mbtiles.csv
tippecanoe -f -Z3 -z14 -B3 -o ../../tiles/dams_priority.mbtiles -l dams_priority dams_priority_mbtiles.csv

tile-join -f --no-tile-size-limit -o dams.mbtiles dams_heatmap.mbtiles dams_full.mbtiles dams_priority.mbtiles
```

TODO: consider creating another layer with just priorities > -1

TODO: consider --drop-densest-as-needed instead, or -r1 --cluster-distance=2\
TODO: tune tile creation / base zoom & reduce rate.
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

<!-- ## Watersheds - OLD

Obtained HUC12 - HUC8 levels from Kat

To HUC8 layer, added fields

-   HUC8 = HUC_8 (for consistency across the stack)
-   HUC6 = HUC8[:6]. Dissolved on this field: SARP_HUC6.shp
-   HUC4 = HUC8[:4]. Dissolved on this field: SARP_HUC4.shp
-   HUC2 = HUC8[:2]. Dissolved on this field: SARP_HUC2.shp

HUC8 has field issues that don't play nice with geopandas. Drop nonessential fields:
`ogr2ogr sarp_huc8.shp -select HUC8 sarp_bounds.gdb SARP_HUC8_Albers` -->

## Watersheds - updated

Downloaded the WBD dataset from: ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Hydrography/WBD/National/GDB/

1. selected units from HUC2 ... HUC12 that intersect SARP bounds
2. exported each to a new shapefile HUC\*.shp

## States and counties

Downloaded from US Census TIGER 2018: https://www.census.gov/cgi-bin/geo/shapefiles/index.php

1. Extracted states that fell within SARP boundary.
2. Extracted counties whose STATE_FP attribute was one of the states above.

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

states, HUC2 - 8 and ecoregions:

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON states.json states.shp -sql "SELECT NAME as id from states"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON counties.json counties.shp -sql "SELECT GEOID as id, NAME as name from counties"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC2.json HUC2.shp -sql "SELECT HUC2 as id, NAME as name from HUC2"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC4.json HUC4.shp -sql "SELECT HUC4 as id, NAME as name from HUC4"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC6.json HUC6.shp -sql "SELECT HUC6 as id, NAME as name from HUC6"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC8.json HUC8.shp -sql "SELECT HUC8 as id, NAME as name from HUC8"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC10.json HUC10.shp -sql "SELECT HUC10 as id, NAME as name from HUC10"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC12.json HUC12.shp -sql "SELECT HUC12 as id, NAME as name from HUC12"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON ECO3.json sarp_ecoregion3.shp -sql "SELECT NA_L3CODE as id, US_L3NAME as name from sarp_ecoregion3"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON ECO4.json sarp_ecoregion4.shp -sql "SELECT US_L4CODE as id, US_L4NAME as name from sarp_ecoregion4"


tippecanoe -f -z 8 -l State -o ../../tiles/states.mbtiles states.json
tippecanoe -f -Z 3 -z 12 -l counties -o ../../tiles/counties.mbtiles counties.json
tippecanoe -f -z 8 -l HUC2 -o ../../tiles/HUC2.mbtiles  -T id:string HUC2.json
tippecanoe -f -z 8 -l HUC4 -o ../../tiles/HUC4.mbtiles  -T id:string HUC4.json
tippecanoe -f -z 8 -l HUC6 -o ../../tiles/HUC6.mbtiles  -T id:string HUC6.json
tippecanoe -f -z 10 -l HUC8 -o ../../tiles/HUC8.mbtiles  -T id:string HUC8.json
tippecanoe -f -Z 4 -z 12 -l HUC10 -o ../../tiles/HUC10.mbtiles  -T id:string HUC10.json
tippecanoe -f -Z 4 -z 12 -l HUC12 -o ../../tiles/HUC12.mbtiles  -T id:string HUC12.json
tippecanoe -f -z 10 -l ECO3 -o ../../tiles/ECO3.mbtiles  -T id:string ECO3.json
tippecanoe -f -Z 3 -z 12 -l ECO4 -o ../../tiles/ECO4.mbtiles  -T id:string ECO4.json
```

### Add summaries and join tiles together

Summaries are created using summarize_by_unit.py

```
tile-join -f -o states_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/state.csv states.mbtiles
tile-join -f -o HUC2_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc2.csv HUC2.mbtiles
tile-join -f -o HUC4_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc4.csv HUC4.mbtiles
tile-join -f -o HUC6_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc6.csv HUC6.mbtiles
tile-join -f -o HUC8_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc8.csv HUC8.mbtiles
tile-join -f -o HUC10_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc10.csv HUC10.mbtiles
tile-join -f -o HUC12_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/huc12.csv HUC12.mbtiles
tile-join -f -o ECO3_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/ECO3.csv ECO3.mbtiles
tile-join -f -o ECO4_summary.mbtiles -c /Users/bcward/projects/sarp/data/summary/ECO4.csv ECO4.mbtiles
```

Merge all tilesets together

```
tile-join -f --no-tile-size-limit -o sarp_summary.mbtiles mask.mbtiles boundary.mbtiles states_summary.mbtiles huc2_summary.mbtiles huc4_summary.mbtiles huc6_summary.mbtiles huc8_summary.mbtiles huc10_summary.mbtiles huc12_summary.mbtiles ECO3_summary.mbtiles ECO4_summary.mbtiles
```

## Rare species occurrences

Kat collated information on rare species from multiple states into 2 datasets and sent these on 11/15-11/15/2018:

-   Species_points_HUC12.csv
-   Species_polygons_HUC12_intersect.csv (HUGE!)

These are first aggregated to unique HUC12, species, status records using `aggregate_spp_occurrences.py`

Several species had variants of species name (some incorrect spellings) and status.

Kat obtained a species list from ECOS and extracted aquatic species. She removed the parenthentical parts of species names.

-   ECOS_listed_aquatic_species_2018.csv

Based on that information and Google searching based on different taxonomies, we were able to derive an updated list of T & E species
to apply to the point and polygon level data.

After applying T & E status, we extracted all T & E records, then counted unique species by HUC12.

# NHD Network processing

Data obtained by HUC4 from: https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Hydrography/NHDPlus/HU4/HighResolution/GDB/
Note: Region 08 data are not available as high resolution and need to be handled using Medium Resolution

# ARCHIVE / UNUSED

## River network - NOT USED

Obtained from Kat as DataSnapshot.gdb SARP_NHD_Dendrite.

Note: there are lots of issues here - selecting out StreamOrde does not produce consistent results (e.g., Ohio river at confluence of Mississipi).
One possible way would be to select by GNIS_ID, based on the max StreamOrde for a given name.
Can take a first cut by filtering out the major ones by order, then find the GNIS_IDs of those, then re-filter on those.

Pull out different levels to use for different tilesets

```
ogr2ogr -f "ESRI Shapefile" rivers8.shp DataSnapshots.gdb SARP_NHD_Dendrite -dim 2 -sql "SELECT BATID as id, GNIS_NAME as name from SARP_NHD_Dendrite where StreamOrde >= 8"
ogr2ogr -f "ESRI Shapefile" rivers6.shp DataSnapshots.gdb SARP_NHD_Dendrite -dim 2 -sql "SELECT BATID as id, GNIS_NAME as name from SARP_NHD_Dendrite where StreamOrde >= 6"
ogr2ogr -f "ESRI Shapefile" rivers4.shp DataSnapshots.gdb SARP_NHD_Dendrite -dim 2 -sql "SELECT BATID as id, GNIS_NAME as name from SARP_NHD_Dendrite where StreamOrde >= 4"
ogr2ogr -f "ESRI Shapefile" rivers2.shp DataSnapshots.gdb SARP_NHD_Dendrite -dim 2 -sql "SELECT BATID as id, GNIS_NAME as name from SARP_NHD_Dendrite where StreamOrde >= 2"
ogr2ogr -f "ESRI Shapefile" rivers.shp DataSnapshots.gdb SARP_NHD_Dendrite -dim 2 -sql "SELECT BATID as id, GNIS_NAME as name from SARP_NHD_Dendrite"

ogr2ogr -t_srs EPSG:4326 -f "GeoJSON" rivers8.json rivers8.shp
ogr2ogr -t_srs EPSG:4326 -f "GeoJSON" rivers6.json rivers6.shp
ogr2ogr -t_srs EPSG:4326 -f "GeoJSON" rivers4.json rivers4.shp


tippecanoe -f -z 6 -l rivers8 -o ../../tiles/rivers8.mbtiles -y id -y name rivers8.json
tippecanoe -f -Z 4 -z 8 -l rivers6 -o ../../tiles/rivers6.mbtiles -y id -y name rivers6.json
tippecanoe -f -Z 7 -z 10 -l rivers4 -o ../../tiles/rivers4.mbtiles -y id -y name rivers4.json
```

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
