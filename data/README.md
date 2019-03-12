# Southeast Aquatic Barrier Inventory Data Processing

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

### SARP Boundary:

SARP_Bounds data (boundary and HUCs) sent by Kat on 7/11/2018.
There was a hole between Missouri and Kentucky. I selected the same states and Puerto Rico from Census TIGER 2015 state boundaries: SARP_states.shp
I then dissolved it: `SARP_boundary.shp` and reprojected to WGS84: `SARP_boundary_wgs84.shp`

** boundary: **

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON boundary.json sarp_boundary.shp
tippecanoe -z 8 -l boundary -o ../tiles/boundary.mbtiles boundary.json
```

** inverse boundary: ** (for masking)

Create a GeoJSON polygon for world bounds using GeoJSON.io. In ArcGIS, erase from this
using SARP boundary: SARP_mask.shp (already in wgs_84)

```
ogr2ogr -f GeoJSON mask.json sarp_mask.shp
tippecanoe -z 8 -l mask -o ../tiles/mask.mbtiles mask.json
```

### Summary Units:

#### States and counties

Downloaded from US Census TIGER 2018: https://www.census.gov/cgi-bin/geo/shapefiles/index.php

1. Extracted states that fell within SARP boundary.
2. Extracted counties whose STATE_FP attribute was one of the states above.

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON states.json states.shp -sql "SELECT NAME as id from states"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON counties.json counties.shp -sql "SELECT GEOID as id, NAME as name from counties"

tippecanoe -f -z 8 -l State -o ../tiles/states.mbtiles states.json
tippecanoe -f -Z 3 -z 12 -l County -o ../tiles/counties.mbtiles counties.json
```

#### Watersheds

Downloaded the WBD dataset from: ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Hydrography/WBD/National/GDB/

1. selected units from HUC2 ... HUC12 that intersect SARP bounds
2. exported each to a new shapefile HUC\*.shp

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC6.json HUC6.shp -sql "SELECT HUC6 as id, NAME as name from HUC6"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC8.json HUC8.shp -sql "SELECT HUC8 as id, NAME as name from HUC8"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON HUC12.json HUC12.shp -sql "SELECT HUC12 as id, NAME as name from HUC12"

tippecanoe -f -z 8 -l HUC6 -o ../tiles/HUC6.mbtiles  -T id:string HUC6.json
tippecanoe -f -z 10 -l HUC8 -o ../tiles/HUC8.mbtiles  -T id:string HUC8.json
tippecanoe -f -Z 6 -z 12 -l HUC12 -o ../tiles/HUC12.mbtiles  -T id:string HUC12.json

```

#### Ecoregions

Downloaded from the EPA Ecoregions website, and extracted within the SARP boundary.

```
ogr2ogr -t_srs EPSG:4326 -f GeoJSON ECO3.json sarp_ecoregion3.shp -sql "SELECT NA_L3CODE as id, US_L3NAME as name from sarp_ecoregion3"
ogr2ogr -t_srs EPSG:4326 -f GeoJSON ECO4.json sarp_ecoregion4.shp -sql "SELECT US_L4CODE as id, US_L4NAME as name from sarp_ecoregion4"

tippecanoe -f -z 10 -l ECO3 -o ../tiles/ECO3.mbtiles  -T id:string ECO3.json
tippecanoe -f -Z 3 -z 12 -l ECO4 -o ../tiles/ECO4.mbtiles  -T id:string ECO4.json
```

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
