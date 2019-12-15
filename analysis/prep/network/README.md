# Southeast Aquatic Barrier Inventory Data Processing - Network Data Preparation

## Overall workflow:

1. Download NHDPlus High Resolution (HR) data for all applicable HUC4s that have dams.
2. Run any special pre-processing scripts in `special` (e.g., `region2.py`)
3. Run `extract_flowlines_waterbodies.py` to extract flowlines, flowline joins, waterbodies, and flowline / waterbody joins for each region group.
4. Run `prepare_flowlines_waterbodies.py` to preprocess flowlines and waterbodies into data structures ready for analysis.
5. Run `merge_waterbodies.py` to merge waterbodies to the full SARP region and create files for large waterbodies.
6. Run `prep_floodplain_statistics.py` to extract pre-calculated statistics on natural landcover within floodplains for each flowline's catchment

Now the underlying aquatic networks are ready for the network analysis.

Most of the data processing is performed by region group, which is one or more NHD HUC2s that flow into each other. This is done to reduce the number of networks connected across HUC2 boundaries that need to be merged after the analysis.

Feather files are used as a compact, fast I/O file format for these data.

### Download NHDPlus HR data:

Run `download.py`. This will download NHDPlus HR data by HUC4 into `data/nhd/source/huc4`. For now, you need to unzip these files manually into that directory.

### Run any special preprocessing scripts or hand-inspect NHD data

To get around issues with NHD HR+ Beta data, you likely need to inspect the NHD data first for errors. Two common problems are currently solved:

1. Some "loops" are miscoded; the main segment is mis-identified as a loop, whereas a pipeline may be identified as the main segment.
2. Chesapeake Bay contains many flowlines that cause networks to be joined together across the bay. These flowlines are excluded from the analysis.

The results of this analysis and preprocessing are stored in `analysis/constants.py` in `EXCLUDE_IDS` and `CONVERT_TO_NONLOOP` variables. These store lists of NHDPlusIDs that need to be acted on.

### Extract flowlines and waterbodies, and other NHD data:

Run `extract_flowlines_waterbodies.py` to extract the flowlines and their joins tables from the NHD FGDB files. This creates feather files containing flowlines, their spatial index, and joins between flowlines for each region group. Aquatic networks that cross HUC4 boundaries are joined together to create contiguous networks. It takes approximately 2 hours to run.

This creates "raw" data extracted from NHD, with minimal processing. Data are output to `data/nhd/raw/<region>`.

The output flowlines contain "loops" (secondary channels in addition to the main flow line). These may cause problems depending on network topology, but they are retained so that issues with NHD data can be identified and handled appropriately below.

This script creates a first pass at all flowlines that intersect waterbodies. NOTE: this is for intersection only, it includes many flowlines that intersect with but do not actually fall within waterbodies.

Run `extract_nhd_lines.py` to extract features that NHD specifically mapped that may be important for breaking flowlines or waterbodies (Dam, Gate, Lock Chamber, Waterfall).
This creates `data/nhd/extra/nhd_lines.py`.

This step should only need to be rerun if there are errors or additional HUC4s / regions are needed.

### Prepare flowlines and waterbodies:

Run `prepare_flowlines_waterbodies.py` to preprocess flowlines and waterbodies into data structures ready for analysis.

This creates "clean" data for further analysis in `data/nhd/clean/<region>`

This performs several steps:

1. Drops any flowlines that are excluded (above)
2. Recodes "loops" as needed
3. Drops all "loops"
4. Dissolves waterbodies that are touching or overlapping each other; this also deduplicates waterbodies that may result from merging multiple regions together. If waterbodies touch NHD lines (dams, locks, etc), they are not dissolved, since these breaks between waterbodies are meaningful.
5. Flowlines are cut by waterbodies, and the waterbody / flowline joins are refined to only those flowlines that actually fall within waterbodies. Flowlines are attributed with `waterbody` to indicate if they fall within a waterbody.

NOTE: there are a number of geometry and related errors in NHD that confounds this analysis. The data output by this step are reasonably good, but not perfect.

This step may need to be run if the data above change, or there is need to change the processing logic.

### Prepare floodplain metrics

The amount of natural landcover in the floodplain of each aquatic network helps to measure the overall habitat quality of that network, and helps prioritize those barriers that if removed would contribute high quality upstream networks. In order to streamline processing for barrier inventories that grow over time, we approximated the natural landcover at the catchment level, so that floodplain statistics could be reused for many analyses rather than regenerated each time a new barrier is added to the inventory.

The floodplain statistics were generated in ArcGIS by:

1. developing a floodplain mask from existing data sources and 90m around all flowlines
2. developing a binary map of natural landcover / not natural landcover
3. clipping landcover by floodplain mask
4. running zonal stats to calculate the area in natural landcover and not natural landcover in the floodplain mask, for each catchment

Note: some catchments have no floodplain, and some have floodplains but no NHDPlusID (outside HUC4s we processed). These are filtered out.

These data were exported to a FGDB, and prepared for analysis here using `prepare_floodplain_stats.py`.
