# Southeast Aquatic Barrier Inventory Data Processing - Network Data Preparation

## Overall workflow:

1. Download NHDPlus High Resolution (HR) data for all applicable HUC4s that have dams.
2. Run any special pre-processing scripts in `special` (e.g., `region2.py`)
3. Run `extract_flowlines_waterbodies.py` to extract flowlines, flowline joins, waterbodies, and flowline / waterbody joins for each region group.
4. Run `extract_nhd_lines.py` and `extract_nhd_areas.py` to extract dam-related features and waterfalls from other NHD datasets.
5. Run `prepare_flowlines_waterbodies.py` to preprocess flowlines and waterbodies into data structures ready for analysis.
6. Run `merge_waterbodies.py` to merge waterbodies to the full SARP region and create files for large waterbodies.
7. Run `find_nhd_dams.py` to intersect NHD dam-related features with flowlines and extract intersection points.
8. Run `prep_floodplain_statistics.py` to extract pre-calculated statistics on natural landcover within floodplains for each flowline's catchment.

Now the underlying aquatic networks are ready for the network analysis.

Most of the data processing is performed by region group, which is one or more NHD HUC2s that flow into each other. This is done to reduce the number of networks connected across HUC2 boundaries that need to be merged after the analysis.

Feather files are used as a compact, fast I/O file format for these data.

### 1. Download NHDPlus HR data:

Run `download.py`. This will download NHDPlus HR data by HUC4 into `data/nhd/source/huc4`. For now, you need to unzip these files manually into that directory.

### 2. Run any special preprocessing scripts or hand-inspect NHD data

To get around issues with NHD HR+ Beta data, you likely need to inspect the NHD data first for errors. Two common problems are currently solved:

1. Some "loops" are miscoded; the main segment is mis-identified as a loop, whereas a pipeline may be identified as the main segment.
2. Chesapeake Bay contains many flowlines that cause networks to be joined together across the bay. These flowlines are excluded from the analysis.

The results of this analysis and preprocessing are stored in `analysis/constants.py` in `EXCLUDE_IDS` and `CONVERT_TO_NONLOOP` variables. These store lists of NHDPlusIDs that need to be acted upon.

### 3. Extract flowlines and waterbodies:

Run `extract_flowlines_waterbodies.py` to extract the flowlines, joins between flowlines, and waterbodies from the NHD FGDB files. This creates "raw" data extracted from NHD, with minimal processing, so that later processing steps can refine the extraction logic for network analysis without needing to go back to the raw NHD data.

This step should only need to be rerun if there are errors or additional HUC4s / regions are needed, or there are data updates from NHD.

It takes approximately 2 hours to run across all SARP regions (separate regions can be run in separate processes, to speed up overall execution time).

#### Flowlines:

These data are extracted from NHDFlowline, NHDPlusFlowlineVAA, NHDPlusFloW datasets.

-   aquatic networks that cross HUC4 boundaries within each region are joined together to create contiguous networks.
-   all coastlines (FType=566) and their joins are dropped
-   size classes are calculated (see `nhdnet::nhdnet/nhd/extract.py` for thresholds)
-   sinuosity and length are calculated
-   geometries are converted to XY LineStrings from XYZ MultiLineStrings
-   projected to SARP standard CRS

The output flowlines contain "loops" (secondary channels in addition to the main flow line). These may cause problems depending on network topology, but they are retained so that issues with NHD data can be identified and handled appropriately below. Loops are identified by the `loop` attribute.

#### Waterbodies:

These data are extracted from the NHDWaterbody dataset.

-   only waterbodies >= 0.02 sq km are retained. There are many below this threshold.
-   projected to SARP standard CRS

This script creates a rough first pass at all flowlines that intersect waterbodies. NOTE: this is for intersection only, it includes many flowlines that intersect with but do not actually fall within waterbodies.

#### Outputs:

This creates a directory (`data/nhd/raw/<region>`) for each region containing:

-   `flowlines.feather`: flowline geometries and attributes
-   `flowline_joins.feather`: joins between flowlines to represent network topology
-   `waterbodies.feather`: waterbody geometries and attributes
-   `waterbody_flowline_joins.feather`: joins between waterbodies and flowlines.

#### IMPORTANT:

-   flowlines are identified using `lineID` from this point forward; this is a unique ID assigned to this specific run of the data extraction. These ids are NOT durable from one extraction to the next. These are used because the flowlines are cut, yet we retain the original NHDPlusID of each original segment to be able to relate it back to NHD.
-   waterbodies are identified using `wbID`. These are also specific to this particular extraction.

### 4. Extract NHD lines and areas

Run `extract_nhd_lines.py` and `extract_nhd_areas.py' to extract extra spatial data from NHD data.

Note: there is also `extract_nhd_points.py` that could be used to extract data from the NHDPoint dataset. These data were not used elsewhere in the processing chain (nearly all features already present in SARP inventory).

This step should only need to be rerun if there are errors or additional HUC4s / regions are needed, or there are data updates from NHD.

Data are merged across all regions.

#### NHD lines:

These data are extracted from the NHDLine dataset.

We only extract linear features that interact with flowlines as barriers based on FType:

-   Dam (343)
-   Gate (369)
-   Lock Chamber (398)
-   Waterfall (487).

#### NHD areas:

These data are extracted from the NHDArea dataset.

We only extract linear features that interact with flowlines as barriers based on FType:

-   Dam (343)
-   Lock (398)
-   Spillway (455)

#### Outputs

This creates data in `nhd/data/extra`:
`nhd_lines.feather`
`nhd_areas.feather`

### 5. Prepare flowlines and waterbodies:

Run `prepare_flowlines_waterbodies.py` to preprocess flowlines and waterbodies into data structures ready for analysis. This implements the bulk of the logic to extract the appropriate flowline and waterbodies. This logic may need to be tuned to refine the network connectivity analysis.

This performs several steps:

1. Drops any flowlines that are excluded (from special processing above)
2. Recodes "loops" as needed
3. Drops all underground conduits (FType=420)
4. Drops pipelines (FType=428) that are isolated, at terminal ends of flowlines, or are long connectors between flowlines (>250m)
5. Dissolves waterbodies that are touching or overlapping each other; this also deduplicates waterbodies that may result from merging multiple regions together. Note: NHDPlusID ids of the original waterbodies are dropped when they are dissolved.
6. Flowlines are cut by waterbodies, and the waterbody / flowline joins are refined to only those flowlines that actually fall within waterbodies. Flowlines are attributed with `waterbody` to indicate if they fall within a waterbody.
7. Waterbody "drain points" are identified by taking the furthest downstream point of each flowline network that falls within a waterbody. Due to the way that waterbodies are connected to exiting flowlines, there may be several drain points for some waterbodies (most typically have just one). Note: some large riverways are mapped as NHD waterbodies; drain points are not as meaningful for these features.

Note:
short pipelines (<250m) between adjacent non-pipeline flowline are retained. From visual inspection, these occur at dam drain points, which means that removing them completely breaks the network and eliminates our ability to analyze the impact of those dams on network connectivity.

WARNING: there are a number of geometry and related errors in NHD that confounds this analysis. The data output by this step are reasonably good, but not perfect.

#### Outputs:

This creates "clean" data for further analysis in `data/nhd/clean/<region>`:

-   `flowlines.feather`: flowline geometries and attributes
-   `flowline_joins.feather`: joins between flowlines to represent network topology
-   `waterbodies.feather`: waterbody geometries and attributes
-   `waterbody_flowline_joins.feather`: joins between waterbodies and flowlines.
-   `waterbody_drain_points.feather`: drain points for each waterbody

The script outputs files with erroneous data, if errors are detected during processing. These are identified by `error_*` with a name that indicates the nature of the error.

### 6. Merge waterbodies

Run `merge_waterbodies.py` after the above script completes to merge waterbodies and their associated drain points across the entire region.

Large waterbodies are those that have >= 1km of intersected flowline length and are >= 0.25 sq km. From visual inspection, most appear to be impounded reservoirs.

#### Outputs:

This creates data in `data/nhd/merged`

-   `waterbodies.feather`
-   `waterbody_drains.feather`
-   `large_waterbodies.feather`
-   `large_waterbody_drains.feather`

### 7. Find NHD dams

Run `find_nhd_dams.py` to extract NHD dams from `nhd_lines.feather` and `nhd_areas.feather` above.

1. Dam-related feature are extracted from `nhd_lines.feather`.
2. Line are buffered by 5 meters.
3. Dam-related feature are extracted from `nhd_area.feather`.
4. Buffered lines and areas are combined and adjacent / overlapping feature are dissolved.
5. The GNIS_Name, if any, is retained for the dissolved features.
6. NHD dams are intersected with flowlines.
7. The lowest downstream segment of each flowline that overlaps these dams is identified.
8. A representative point is extracted for the lowest downstream segment; typically this is the furthest upstream or downstream point along that line or the portion of that line that intersects with the NHD dam feature.
9. Dams are attributed to the nearest waterbody or drain point (within 250m).

WARNING: there are data issues apparent in the NHD lines and areas. Some features are mis-coded (e.g. dikes parallel to flowlines rather than barriers), whereas others seem spurious and not validated by the satellite imagery for the same locatin.

#### Outputs:

This creates `data/nhd/merged/nhd_dams.feather`

### 8. Prepare floodplain metrics

Run `prepare_floodplain_stats.py` to prepare the floodplain data provided by SARP for later analysis.

The amount of natural landcover in the floodplain of each aquatic network helps to measure the overall habitat quality of that network, and helps prioritize those barriers that if removed would contribute high quality upstream networks. In order to streamline processing for barrier inventories that grow over time, we approximated the natural landcover at the catchment level, so that floodplain statistics could be reused for many analyses rather than regenerated each time a new barrier is added to the inventory.

The floodplain statistics were generated in ArcGIS by SARP:

1. developing a floodplain mask from existing data sources and 90m around all flowlines
2. developing a binary map of natural landcover / not natural landcover
3. clipping landcover by floodplain mask
4. running zonal stats to calculate the area in natural landcover and not natural landcover in the floodplain mask, for each catchment

Note:
some catchments have no floodplain, and some have floodplains but no NHDPlusID (outside HUC4s we processed). These are filtered out.

#### Outputs:

This creates `data/floodplains/floodplain_stats.feather` with the total area of floodplains and the area of those within natural landcover types.
