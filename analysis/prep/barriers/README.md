# National Aquatic Barrier Inventory & Prioritization Tool Data Processing - Aquatic Barriers

This is the main data flow for updating barrier data, each time new barriers need to be processed for use in the tool.

Barriers are extracted from multiple sources for the network connectivity and barrier prioritization analyses.
These are processed in the following order.

1. dams
2. waterfalls
3. road-related barriers (assessed) and road crossings (unassessed)

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
- OpenStreetMap

## One-time data preparation

### Prep: Download and extract OpenStreetMap dams

OpenStreetMap (OSM) data for the U.S. was downloaded from https://download.geofabrik.de/north-america.html on 9/6/2023.

OSM data are very slow to process. Features of interest are first extracted to a GPKG file using the following command-line commands:

```bash
export OSM_CONFIG_FILE="analysis/prep/barriers/special/osmconf.ini"
ogr2ogr data/barriers/source/us_osm.gpkg -nln points data/barriers/source/us-latest.osm.pbf -sql "SELECT * from points WHERE \"waterway\" in ('waterfall', 'dam', 'weir', 'fish_pass')"
ogr2ogr data/barriers/source/us_osm.gpkg -nln lines -update data/barriers/source/us-latest.osm.pbf -sql "SELECT * from lines WHERE \"waterway\" in ('dam', 'weir', 'fish_pass')"
ogr2ogr data/barriers/source/us_osm.gpkg -nln multipolygons -update data/barriers/source/us-latest.osm.pbf -sql "SELECT * from multipolygons WHERE \"waterway\" in ('dam', 'weir', 'fish_pass')"
```

Dams and waterfalls are extracted from OSM data using `special/extract_osm_barriers.py`.

### Prep: NABD dams

The National Anthropogenic Barrier Database is used to help snap dams derived
from NID, unless otherwise manually reviewed.

NABD dams are prepared using `special/prep_nabd.py`.

## Dams

### Dam removal costs

Estimated dam costs were modeled by Suman Jumani (TNC) and provided to Kat Hoenke on 1/16/2024,
saved to `data/barriers/source/sarp_dam_costpred_V2.xlsx`.

We extracted Mean and 95% upper / lower prediction intervals and saved to a Feather file for faster joins later.
These were post-processed using `analysis/prep/barriers/special/extract_cost_estimates.py`.

### Processing

Dams are downloaded from the user-edited national dataset hosted
on ArcGIS Online using `analysis/prep/barriers/download.py`.

There is also a manually snapped dams dataset on ArcGIS Online. This is also
downloaded as part of the above script. These locations are edited by users to
correct snapping errors, or otherwise flag dams that should be excluded from
processing. The locations of dams have been updated using corrected locations
obtained from the National Anthropogenic Barrier database or snapped manually by
SARP staff and aquatic connectivity team members. These corrected locations are
joined to the master inventory.

Dams are processed using `analysis/prep/prep_dams.py`.

Dams are snapped automatically to the aquatic network if within 100 meters. Dams
are excluded from analysis if they did not snap to the network or were otherwise
identified by various attributes (e.g., Recon). After snapping, dams are
de-duplicated to remove those that are very close to each other (within 30m).

## Waterfalls

Waterfalls are processed using `analysis/prep/barriers/prep_waterfalls.py`.

Waterfalls are snapped to the aquatic network and duplicates are marked.

## Road-related barriers and crossings

Road-related barriers are hosted on ArcGIS Online and downloaded using `analysis/prep/barriers/download.py`.

Road-related barriers are processed using `analysis/prep/barriers/prep_road_barriers.py`.

Road-related barriers are automatically snapped to the aquatic network if within 50
meters. Barriers are excluded from analysis if they did not snap to the network
or were otherwise identified by various attributes (e.g., Feasibility). After
snapping, barriers are de-duplicated to remove those that are very close to each
other (within 10m).

Barriers are deduplicated against dams and waterfalls.

Road crossings were downloaded from https://www.sciencebase.gov/catalog/item/6128fbf2d34e40dd9c061360 on 2/16/2022.

Road crossings are based on TIGER 2020 roads data. The roads data were downloaded
from https://www2.census.gov/geo/tiger/TGRGDB20/ on 5/17/2024 and used to link
in road ownership type used to derive BarrierOwnerType.

TODO: NBI linking

These are processed in advance for a given snapshot of the road crossings input
dataset ("stream_crossings_united_states_feb_2022.gpkg") using
`analysis/prep/barriers/special/prep_raw_road_crossings.py`. These go through
multiple steps of deduplication against each other and are snapped to flowlines.

Road crossings are deduplicated against dams, waterfalls, and assessed road-
related barriers. The nearest duplicate crossing to each assessed road-related
barrier is assigned to the road-related barrier it duplicates.
