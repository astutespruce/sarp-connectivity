# Southeast Aquatic Barrier Inventory Data Processing - Aquatic Barriers

This is the main data flow for updating barrier data, each time new barriers need to be processed for use in the tool.

Barriers are extracted from multiple sources for the network connectivity and barrier prioritization analyses.
These are processed in the following order.

1. dams
2. small barriers (inventoried road-related crossings)
3. road crossings (non-inventoried road-related crossings)
4. waterfalls

The output of the processing steps below are full barriers datasets in `data/barriers/master` and a subset of dams, small barriers, and waterfalls that were snapped to the aquatic network in `data/barriers/snapped`.

The full datasets include attributes that identify whether they were dropped (removed from all analyses and not shown on map), excluded (removed from all analyses but shown on map), snapped, or duplicates.

WARNING:
There are many duplicate dams within the inventory. Some occur very near each others, others are quite far away (>250m). The scripts try to identify likely duplicates and remove them from analysis.

## ArcGIS Online token

You must set `AGOL_TOKEN` in an `.env` file in the root of this project. It must be set to a current, valid ArcGIS Online token, and must have access to the SARP datasets. To get this token, go to one of the SARP web maps for the inventory, sign in, and get the token from the URL.

## Data sources:

- Dams: hosted on ArcGIS Online by state for SARP states, provided directly by Kat (SARP) for non-SARP states
- Small barriers: hosted on ArcGIS Online
- Waterfalls: obtained by Kat (SARP) from USGS in early 2019.
- Road crossings: downloaded from USGS in Feb 2022.
- NID: obtained by Kat and provided on 3/5/2021
- National Anthropogenic Barriers Database (NABD): obtained by Kat and provided on 1/22/2021

## Dams

### Prep: Dams in states outside SARP boundary

National Inventory of Dams (NID) dams are used to supplement the inventory for HUC4s outside the core states analyzed in this tool (see `analysis/constants.py::STATES` for the list).

NID dams for outer HUC4s (HUC4s that overlap states within the analysis region, but the portions of those HUC4s that are outside those states)
were provided by Kat @ SARP on 3/15/2022 (`OuterHUC4_Dams_2022.gdb`). These include dams from the NID (March 2022) Northeast aquatic connectivity project (TNC).

Kat took care of rectifying previous versions of NID and TNC data against the latest versions.

These were processed and joined with NABD, which provide updated (snapped) locations of many dams in NID using `special/prep_nid_dams_outer_huc4s.py`.

This step should only be necessary to run once each time the HUC4s outside the core states in the analysis are updated (i.e., by adding states to the analysis region).

### Prep: NABD dams

The National Anthropogenic Barrier Database is used to help snap dams derived from NID, unless otherwise manually reviewed.

NABD dams are prepared using `special/prep_nabd.py`.

### Processing

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

Downloaded from https://www.sciencebase.gov/catalog/item/6128fbf2d34e40dd9c061360 on 2/16/2022.

These are processed once for a given snapshot of the road crossings input
dataset ("stream_crossings_united_states_feb_2022.gpkg") using
`analysis/prep/barriers/special/prep_raw_road_crossings.py`.

Then, each time small barriers are processed above, run
`analysis/prep/barriers/prep_road_crossings.py`, which deduplicates road
crossings against small barriers, performs spatial joins, and prepares for use
in the analysis. These are ultimately merged in with final small barriers
dataset to create background barriers displayed on the map.

## Waterfalls

Waterfalls are processed using `analysis/prep/barriers/prep_waterfalls.py`.

Waterfalls are snapped to the aquatic network and duplicates are marked.
