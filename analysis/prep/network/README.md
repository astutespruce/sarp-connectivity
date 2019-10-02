# Southeast Aquatic Barrier Inventory Data Processing - Network Data Preparation

## Overall workflow:

1. Download NHDPlus High Resolution (HR) data for all applicable HUC4s that have dams.
2. Run any special pre-processing scripts in `special` (e.g., `region2.py`)
3. Run `extract_flowlines.py` to extract flowlines and joins for each region group.
4. Run `prep_floodplain_statistics.py` to extract pre-calculated statistics on natural landcover within floodplains for each flowline's catchment

Now the underlying aquatic networks are ready for the network analysis.

Most of the data processing is performed by region group, which is one or more NHD HUC2s that flow into each other. This is done to reduce the number of networks connected across HUC2 boundaries that need to be merged after the analysis.

Feather files are used as a compact, fast I/O file format for these data.

### Download NHDPlus HR data:

Run `download.py`. This will download NHDPlus HR data by HUC4 into `data/nhd/source/huc4`. For now, you need to unzip these files manually into that directory.

### Extract flowlines:

Run `extract_flowlines` to extract the flowlines and their joins tables from the NHD FGDB files. This creates feather files containing flowlines, their spatial index, and joins between flowlines for each region group. Aquatic networks that cross HUC4 boundaries are joined together to create contiguous networks. It takes approximately 2 hours to run.

For QA/QC, a shapefile is also created from the flowlines.

The above steps should only need to be rerun if there are errors or additional HUC4s / regions are needed.

### Prepare floodplain metrics

The amount of natural landcover in the floodplain of each aquatic network helps to measure the overall habitat quality of that network, and helps prioritize those barriers that if removed would contribute high quality upstream networks. In order to streamline processing for barrier inventories that grow over time, we approximated the natural landcover at the catchment level, so that floodplain statistics could be reused for many analyses rather than regenerated each time a new barrier is added to the inventory.

The floodplain statistics were generated in ArcGIS by:

1. developing a floodplain mask from existing data sources and 90m around all flowlines
2. developing a binary map of natural landcover / not natural landcover
3. clipping landcover by floodplain mask
4. running zonal stats to calculate the area in natural landcover and not natural landcover in the floodplain mask, for each catchment

Note: some catchments have no floodplain, and some have floodplains but no NHDPlusID (outside HUC4s we processed). These are filtered out.

These data were exported to a FGDB, and prepared for analysis here using `prepare_floodplain_stats.py`.
