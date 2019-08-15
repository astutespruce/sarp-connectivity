# Southeast Aquatic Barrier Inventory Data preparation

## Overview

Data preparation includes:

1. Create summary units for analysis. These are joined to barriers and used for summary display on the map.
2. Extract summary units within SARP HUC4 boundary and create geofeather files for later processing.
3. Create vector tiles of all summary units that include name and ID in a standardized way. This only needs to be done again when summary units are modified or new ones are added.

Naming conventions:
`*_prj.shp` denotes a shapefile in the CONUS Albers projection of the inventory
`*_wgs84.shp` denotes a shapefile in WGS84 projection for use in `tippecanoe`

## Create summary units

All data are initially processed using an outer boundary defined by all HUC4s that intersect the SARP states boundary (below). This is so that spatial joins of these units to barriers always assign the correct value. Due to the large data volume for HUCs, these are extracted using queries in `ogr2ogr` (below) whereas others are extracted using python to evaluate the overlaps.

All tilesets created for use in the tool are limited to summary units that overlap the SARP states boundary.

All boundaries are projected using ogr2ogr in advance. Because `geopandas` doesn't recognize the EPSG code of the barrier inventory, we use a proj4 string throughout all processing:
"+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

Input files are stored in `/data/boundaries/source`.
Output files are stored in `/data/boundaries`
If needed (e.g., projected states but not yet extracted to SARP HUC4 boundary), intermediate files are stored in `/data/boundaries/intermediate`

### SARP States boundary

All states in the SARP region (defined by `/analysis/prep/prep_boundaries.py::SARP_STATES`) were extracted from the CENSUS tiger states dataset, and dissolved.

SARP inverse boundary (for masking):
Create a GeoJSON polygon for world bounds using GeoJSON.io. In ArcGIS, erase from this
using SARP boundary: SARP_mask.shp (already in wgs_84)

A list of HUC4s that intersect the SARP states boundary was generated and used for data extraction below. This can be queried later using the `HUC4_prj.shp` or `huc4.feather` files created below.

### Watersheds

HUCs were downloaded from: http://prd-tnm.s3-website-us-west-2.amazonaws.com/?prefix=StagedProducts/Hydrography/WBD/National/GDB/
and selected out for those within the SARP region (all HUC4s that overlap SARP region)

The following were processed in the `WBD_National_GDB` folder created by extracting above file, and final outputs copied to `/data/boundaries`. Intermediate files (`*_all_prj.shp`) can be deleted after creating the final shapefiles.

#### HUC4

Project HUC4:

```
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" -sql "SELECT HUC4, NAME from WBDHU4" HUC4_all_prj.shp WBD_National_GDB.gdb WBDHU4
```

Extract out HUC4s in SARP boundary:

```
ogr2ogr -sql "SELECT * from HUC4_all_prj WHERE HUC4 in ('0204', '0207', '0208', '0301', '0302', '0303', '0304', '0305', '0306', '0307', '0308', '0309', '0310', '0311', '0312', '0313', '0314', '0315', '0316', '0317', '0318', '0505', '0507', '0509', '0510', '0511', '0512', '0513', '0514', '0601', '0602', '0603', '0604', '0710', '0711', '0714', '0801', '0802', '0803', '0804', '0805', '0806', '0807', '0808', '0809', '1024', '1027', '1028', '1029', '1030', '1101', '1104', '1105', '1106', '1107', '1108', '1109', '1110', '1111', '1112', '1113', '1114', '1201', '1202', '1203', '1204', '1205', '1206', '1207', '1208', '1209', '1210', '1211', '1303', '1304', '1305', '1306', '1307', '1308', '1309', '1312', '2101', '2102')" HUC4_prj.shp HUC4_all_prj.shp
```

#### HUC6

Project HUC6:

```
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" -sql "SELECT HUC6, NAME, SUBSTR(HUC6, 0, 4) as HUC4 from WBDHU6" HUC6_all_prj.shp WBD_National_GDB.gdb WBDHU6
```

Extract out HUC6s in SARP boundary:

```
ogr2ogr -sql "SELECT * from HUC6_all_prj WHERE HUC4 in ('0204', '0207', '0208', '0301', '0302', '0303', '0304', '0305', '0306', '0307', '0308', '0309', '0310', '0311', '0312', '0313', '0314', '0315', '0316', '0317', '0318', '0505', '0507', '0509', '0510', '0511', '0512', '0513', '0514', '0601', '0602', '0603', '0604', '0710', '0711', '0714', '0801', '0802', '0803', '0804', '0805', '0806', '0807', '0808', '0809', '1024', '1027', '1028', '1029', '1030', '1101', '1104', '1105', '1106', '1107', '1108', '1109', '1110', '1111', '1112', '1113', '1114', '1201', '1202', '1203', '1204', '1205', '1206', '1207', '1208', '1209', '1210', '1211', '1303', '1304', '1305', '1306', '1307', '1308', '1309', '1312', '2101', '2102')" HUC6_prj.shp HUC6_all_prj.shp
```

#### HUC8

Project HUC8:

```
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" -sql "SELECT HUC8, NAME, SUBSTR(HUC8, 0, 4) as HUC4 from WBDHU8" HUC8_all_prj.shp WBD_National_GDB.gdb WBDHU8
```

Extract out HUC6s in SARP boundary:

```
ogr2ogr -sql "SELECT * from HUC8_all_prj WHERE HUC4 in ('0204', '0207', '0208', '0301', '0302', '0303', '0304', '0305', '0306', '0307', '0308', '0309', '0310', '0311', '0312', '0313', '0314', '0315', '0316', '0317', '0318', '0505', '0507', '0509', '0510', '0511', '0512', '0513', '0514', '0601', '0602', '0603', '0604', '0710', '0711', '0714', '0801', '0802', '0803', '0804', '0805', '0806', '0807', '0808', '0809', '1024', '1027', '1028', '1029', '1030', '1101', '1104', '1105', '1106', '1107', '1108', '1109', '1110', '1111', '1112', '1113', '1114', '1201', '1202', '1203', '1204', '1205', '1206', '1207', '1208', '1209', '1210', '1211', '1303', '1304', '1305', '1306', '1307', '1308', '1309', '1312', '2101', '2102')" HUC8_prj.shp HUC8_all_prj.shp
```

#### HUC12

Project HUC12 and extract HUC2, HUC4 codes:

```
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" -sql "SELECT HUC12, NAME, SUBSTR(HUC12, 0, 4) as HUC4, SUBSTR(HUC12, 0, 2) as HUC2 from WBDHU12" HUC12_all_prj.shp WBD_National_GDB.gdb WBDHU12
```

Extract HUC12s for HUC4s in SARP boundary:

```
ogr2ogr -sql "SELECT * from HUC12_all_prj WHERE HUC4 in ('0204', '0207', '0208', '0301', '0302', '0303', '0304', '0305', '0306', '0307', '0308', '0309', '0310', '0311', '0312', '0313', '0314', '0315', '0316', '0317', '0318', '0505', '0507', '0509', '0510', '0511', '0512', '0513', '0514', '0601', '0602', '0603', '0604', '0710', '0711', '0714', '0801', '0802', '0803', '0804', '0805', '0806', '0807', '0808', '0809', '1024', '1027', '1028', '1029', '1030', '1101', '1104', '1105', '1106', '1107', '1108', '1109', '1110', '1111', '1112', '1113', '1114', '1201', '1202', '1203', '1204', '1205', '1206', '1207', '1208', '1209', '1210', '1211', '1303', '1304', '1305', '1306', '1307', '1308', '1309', '1312', '2101', '2102')" HUC12_prj.shp HUC12_all_prj.shp
```

### States and counties

States and counties were downloaded for 2018 from CENSUS TIGER: https://www.census.gov/cgi-bin/geo/shapefiles/index.php

Project states and counties:

```
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" states_prj.shp tl_2018_us_state.shp
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" counties_prj.shp tl_2018_us_county.shp
```

### Ecoregions

Ecoregions were downloaded from: https://www.epa.gov/eco-research/level-iii-and-iv-ecoregions-continental-united-states

Project ecoregions:

```
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" eco3_prj.shp us_eco_l3.shp
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" eco4_prj.shp us_eco_l4_no_st.shp
```

## Extract areas within SARP HUC4 boundary and processing

The above boundary data are processed into geofeather files using `/analysis/prep/prep_boundaries.py`. This includes selecting out states, counties, and ecoregions that fall within the HUC4 outer boundary.

## Create boundary vector tiles

Vector tiles are are created for each of the boundary layers.

Because `tippecanoe` uses GeoJSON in WGS84 projection as input, each vector tileset below includes a step to create this GeoJSON file first. These GeoJSON files can be deleted as soon as the vector tileset is created.

All operations below are executed in the `/data/boundaries` directory.

### SARP boundary and inverse boundary:

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON boundary.json sarp_boundary.shp
tippecanoe -z 8 -l boundary -o tiles/boundary.mbtiles boundary.json

ogr2ogr -t_srs EPSG:4326 -f GeoJSON mask.json sarp_mask.shp
tippecanoe -z 8 -l mask -o tiles/mask.mbtiles mask.json
```

### Watersheds

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC6.json HUC6_prj.shp
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC8.json HUC8_prj.shp
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC12.json HUC12_prj.shp

tippecanoe -f -z 8 -l HUC6 -o tiles/HUC6.mbtiles  -T id:string HUC6.json
tippecanoe -f -z 10 -l HUC8 -o tiles/HUC8.mbtiles  -T id:string HUC8.json
tippecanoe -f -Z 6 -z 12 -l HUC12 -o tiles/HUC12.mbtiles  -T id:string HUC12.json
```

### States and counties

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON states.json states_prj.shp
ogr2ogr -t_srs EPSG:4326 -f GeoJSON counties.json counties_prj.shp

tippecanoe -f -z 8 -l State -o tiles/states.mbtiles states.json
tippecanoe -f -Z 3 -z 12 -l County -o tiles/counties.mbtiles counties.json
```

### Ecoregions

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON ECO3.json eco3_prj.shp
ogr2ogr -t_srs EPSG:4326 -f GeoJSON ECO4.json eco4_prj.shp

tippecanoe -f -z 10 -l ECO3 -o tiles/ECO3.mbtiles  -T id:string ECO3.json
tippecanoe -f -Z 3 -z 12 -l ECO4 -o tiles/ECO4.mbtiles  -T id:string ECO4.json
```

## Barriers pre-processing

### Road crossings

Road crossings were obtained by Kat from USGS in 2018.

These are processed using `analysis/prep/preprocess_road_crossings.py`.

This creates a feather file that is joined in with final small barriers dataset to create background barriers displayed on the map.

---

### Old Workflow BELOW

## General workflow

Processing is divided roughly into two parts:

-   preparation of summary unit vector tiles
-   preparation of dams and small barriers into vector tiles and data files for use in the API

The general sequence is roughly:

1. Create vector tiles of all summary units that include name and ID in a standardized way. This only needs to be done again when summary units are modified or new ones are added.
2. Process dams and small barriers into data files and vector tiles, and join summary statistics of dams and small barriers to the summary unit vector tiles. This needs to be done anytime the summary units change or the dams and small barriers are updated.

Unless otherwise noted, the python scripts are executed assuming the root of the repo as the working directory.

The tippecanoe commands are run from the `data/derived` directory.

## Prepare boundary and summary unit vector tiles

The boundaries are reprojected to geographic coordinates, exported to GeoJSON (required as input to `tippecanoe`), and converted to vector tiles using `tippecanoe`. Zoom levels were carefully chosen by hand based on tradeoffs in size of vector tiles vs the zoom levels where those data would be displayed.

This step only needs to be rerun when summary units are modified or new ones are added.

## Barriers Inventory

Final dams and small barriers data sent by Kat on 12/12/2018:

-   Dams_Webviewer_DraftOne_Final.gdb::SARP_Dam_Inventory_Prioritization_12132018_D1_ALL
-   Road_Related_Barriers_DraftOne_Final.gdb::Road_Barriers_WebViewer_DraftOne_ALL_12132018

#### Prior processing

The inventory datasets above were based in part on preprocessing to calculate network connectivity metrics and species information.
The results of the preprocessing were provided to Kat, and she combined into the authoritative inventory.

-   Network metrics: https://github.com/brendan-ward/nhdnet
-   Species information: `aggregate_spp_occurrences.py` followed by `extract_species_data.py`

#### Preprocessing

Dams and small barriers were prepared using:

-   `preprocess_dams.py`
-   `preprocess_small_barriers.py`

Followed by:

-   `summarize_by_unit.py`

#### Dams

Preprocessed using `preprocess_dams.py`. This creates CSV files for dams with networks and dams without. Different zoom levels are used to display these, setup in such a way that dams without networks generally are not visible until you zoom further in. This was done in part to limit the total size of the tiles, and focus the available space on dams that have the highest value (those with networks).

In `data/derived` directory:

```
tippecanoe -f -Z5 -z12 -B6 -pk -pg -pe -ai -o ../tiles/dams_with_networks.mbtiles -l dams -T name:string -T river:string -T protectedland:bool -T County:string -T HUC6:string -T HUC8:string -T HUC12:string dams_with_networks.csv

tippecanoe -f -Z9 -z12 -B10 -pk -pg -pe -ai -o ../tiles/dams_without_networks.mbtiles -l background -T name:string -T river:string -T protectedland:bool dams_without_networks.csv
```

Merge the tilesets for dams with and without networks into a single tileset.

In `data/tiles` directory:

```
tile-join -f --no-tile-size-limit -o ../../tiles/sarp_dams.mbtiles dams_with_networks.mbtiles dams_without_networks.mbtiles
```

#### Small barriers

USGS Road / stream crossings: Preprocessed using `preprocess_road_crossings.py`.

Road-related barriers (that have been evaluated and snapped to network): preprocessed and off-network barriers merged with road / stream crossings using `preprocess_small_barriers.py`.

Note: because road / stream crossings are very large, these are only included in tiles and displayed in the map at higher zoom levels.

```
tippecanoe -f -Z5 -z12 -B6 -pk -pg -pe -ai -o ../tiles/barriers_with_networks.mbtiles -l barriers -T name:string -T stream:string -T road:string -T sarpid:string  -T protectedland:bool -T County:string -T HUC6:string -T HUC8:string -T HUC12:string barriers_with_networks.csv

tippecanoe -f -Z9 -z14 -B10 -pg -pe --drop-densest-as-needed -o ../tiles/barriers_background.mbtiles -l background -T name:string -T stream:string -T road:string -T sarpid:string -T protectedland:bool barriers_background.csv
```

Merge the small barriers with and without networks into a single tileset.

In `data/tiles` directory:

```
tile-join -f --no-tile-size-limit -o ../../tiles/sarp_barriers.mbtiles barriers_with_networks.mbtiles barriers_background.mbtiles
```

#### Create summary vector tiles

The summary unit boundary vector tiles are created above, and do not need to be recreated unless the summary units change. In contrast, the summary statistics of dams and small barriers are recalculated on each update to the barriers inventory, and these are joined into the final vector tiles below.

Assumes a working directory of `data/tiles`.

Summaries are created using `summarize_by_unit.py`

Join the summary statistics to the summary unit boundary vector tiles:

```
tile-join -f -o states_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/State.csv states.mbtiles
tile-join -f -o counties_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/County.csv counties.mbtiles
tile-join -f -o HUC6_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/huc6.csv HUC6.mbtiles
tile-join -f -o HUC8_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/huc8.csv HUC8.mbtiles
tile-join -f -o HUC12_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/huc12.csv HUC12.mbtiles
tile-join -f -o ECO3_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/ECO3.csv ECO3.mbtiles
tile-join -f -o ECO4_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/ECO4.csv ECO4.mbtiles
```

Merge all tilesets together to create a master vector tileset:

```
tile-join -f --no-tile-size-limit -o ../../tiles/sarp_summary.mbtiles mask.mbtiles boundary.mbtiles states_summary.mbtiles counties_summary.mbtiles huc6_summary.mbtiles huc8_summary.mbtiles huc12_summary.mbtiles ECO3_summary.mbtiles ECO4_summary.mbtiles
```
