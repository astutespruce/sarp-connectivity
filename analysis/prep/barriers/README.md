# Southeast Aquatic Barrier Inventory Data Processing - Aquatic Barriers

Barriers are extracted from multiple sources for the network connectivity and barrier prioritization analyses. These include:

-   waterfalls
-   dams
-   small barriers (inventoried road-related crossings)
-   road crossings (non-inventoried road-related crossings)

The output of the processing steps below are full barriers datasets in `data/barriers/master` and a subset of dams, small barriers, and waterfalls that were snapped to the aquatic network in `data/barriers/snapped`.

## Data sources:

-   Waterfalls: obtained by Kat (SARP) from USGS in early 2019.
-   Dams: hosted on ArcGIS Online by state for SARP states, provided directly by Kat (SARP) for non-SARP states
-   Small barriers: hosted on ArcGIS Online
-   Road crossings: obtained by Kat (SARP) from USGS in 2018.

## Waterfalls

Waterfalls are processed using `analysis/prep/barriers/prep_waterfalls.py`.

Waterfalls are snapped to the aquatic network and duplicates are marked.

## Dams

Dams for SARP states are downloaded from user-edited state-level datasets hosted on ArcGIS Online using `analysis/prep/barriers/download.py`. The individual states are standardized slightly and merged into a single dataset.

Dams for non-SARP states were provided by Kat on 9/5/2019. These include dams from National Inventory of Dams for HUC4s that overlap SARP states.

There is also a manually snapped dams dataset on ArcGIS Online. This is also downloaded as part of the above script. These locations are edited by users to correct snapping errors, or otherwise flag dams that should be excluded from processing. The locations of dams have been updated using corrected locations obtained from the National Anthropogenic Barrier database or snapped manually by SARP staff and aquatic connectivity team members. These corrected locations are joined to the master inventory after merging the SARP and non-SARP state datasets together.

Dams are processed using `analysis/prep/prep_dams.py`.

Dams are snapped automatically to the aquatic network if within 100 meters. Dams are excluded from analysis if they did not snap to the network or were otherwise identified by various attributes (e.g., Recon). After snapping, dams are de-duplicated to remove those that are very close to each other (within 30m).

## Small Barriers

Small barriers are hosted on ArcGIS Online and downloaded using `analysis/prep/barriers/download.py`.

Small barriers are processed using `analysis/prep/barriers/prep_small_barriers.py`.

Small barriers are automatically snapped to the aquatic network if within 50 meters. Barriers are excluded from analysis if they did not snap to the network or were otherwise identified by various attributes (e.g., Feasibility). After snapping, barriers are de-duplicated to remove those that are very close to each other (within 10m).

### Road crossings

These are processed using `analysis/prep/preprocess_road_crossings.py`. Run this before small barriers above so it can be merged in.

This creates a feather file that is joined in with final small barriers dataset to create background barriers displayed on the map.

<!--

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
