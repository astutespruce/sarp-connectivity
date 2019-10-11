# Southeast Aquatic Barrier Inventory Data Processing - Aquatic Barriers

Barriers are extracted from multiple sources for the network connectivity and barrier prioritization analyses. These include:

-   waterfalls
-   dams
-   small barriers (inventoried road-related crossings)
-   road crossings (non-inventoried road-related crossings)

The output of the processing steps below are full barriers datasets in `data/barriers/master` and a subset of dams, small barriers, and waterfalls that were snapped to the aquatic network in `data/barriers/snapped`.

## ArcGIS Online token

You must set `AGOL_TOKEN` in an `.env` file in the root of this project. It must be set to a valid ArcGIS Online token, and must have access to the SARP datasets. To get this token, go to one of the SARP web maps for the inventory, sign in, and get the token from the URL.

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
