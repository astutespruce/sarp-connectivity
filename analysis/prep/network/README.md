# National Aquatic Barrier Inventory & Prioritization Tool Data Processing - Network Data Preparation

This stage involves processing NHD data and related data into data structures that are ready to use for snapping and network analysis. These should only need to be rerun when you need more HUC4s than are currently included in the analysis, need to update NHD data, or need to resolve logic errors in the data extraction pipeline.

## Overall workflow:

1. Run `download_nhd.py` to download NHD High Resolution Plus data for all applicable HUC4s that have dams.
2. Run `download_nwi.py` to download National Wetlands Inventory data.
3. Manually download and extract state-level LIDAR waterbody datasets.
4. Run `extract_nhd.py` to extract flowlines, flowline joins, waterbodies, NHD barriers (points, lines, polygons) for each HUC2.
5. Run `merge_marine.py` to merge all marine areas.
6. Run any special pre-processing scripts in `special` (e.g. `find_loops.py`)
7. Run `extract_nwi.py` to extract NWI waterbodies and altered rivers that intersect the above flowlines.
8. Run `extract_lagos.py` to extract reservoirs from the LAGOS dataset.
9. Run `merge_waterbodies.py` to merge NHD and NWI waterbodies (and others, depending on region) and `merge_wetlands` to merge NHD and NWI wetlands.
10. Run `prepare_flowlines_waterbodies.py` to preprocess flowlines and waterbodies into data structures ready for analysis.
11. Run `find_nhd_dams.py` to intersect NHD dam-related features with flowlines and extract intersection points.
12. Run `prep_floodplain_stats.py` to extract pre-calculated statistics on natural landcover within floodplains for each flowline's catchment.

Now the underlying aquatic networks are ready for the network analysis.

Most of the data processing is performed by HUC2 region.

Feather files are used as a compact, fast I/O file format for these data.

### 1. Download NHDPlus HR data:

Run `download_nhd.py`. This will download NHDPlus HR data by HUC4 into `data/nhd/source/huc4`. For now, you need to unzip these files manually into that directory.

WARNING: NHD HR+ data are currently in beta. There are data issues, including, but not limited to miscoded flowlines / loops, spurious NHD areas, and fragmented adjacent waterbodies.

NHD data were last downloaded (NHD Regions 19 and 20) on 8/28/2024.

### 2. Download National Wetlands Inventory (NWI 2022) data:

NWI ponds and lakes are used to supplement the NHDWaterbody dataset downloaded above.

Run `download_nwi.py`. This will download data by HUC8 into `data/nwi/source/huc8`.

NWI were last updated (full nation) on 8/28/2024.

### 3. Download state-level LIDAR or imagery-based waterbody data

#### California

California data are available at:

- https://www.calfish.org/programsdata/referencelayershydrography/californiahydrography.aspx
- https://www.sfei.org/data/california-aquatic-resource-inventory-cari-version-03-gis-data
  These were downloaded on 2/19/2022 to `data/states/ca/CA_Lakes.shp` and `data/states/ca/CARIv0.3.gdb`.

#### Minnesota

Minnesota data were downloaded from https://gisdata.mn.gov/dataset/water-dnr-hydrography

These were downloaded on 4/14/2023 to `data/states/mn/water_dnr_hydrography.gpkg`.

Data were prepared using `analysis/prep/network/special/prepare_wi_waterbodies.py`.

#### Oregon

Oregon data are available at: https://spatialdata.oregonexplorer.info/geoportal/details;id=3439a3c43f9f4c4499802f55898b7dd8

These were downloaded on 2/19/2022 to `data/states/or/wb_oregon.shp`.

#### Rhode Island

Rhode Island data are available at: https://www.rigis.org/datasets/edc::lakes-and-ponds-15000/about

These were downloaded on 8/29/2024 to `data/states/ri/lakes_ponds.gdb`.

#### South Carolina

South Carolina data are available at: ftp://ftpdata.dnr.sc.gov/gisdata/elev/Hydrolines/SCHydroBreakline.zip
These were downloaded manually on 3/17/2021 to `data/states/sc/SCBreakline.gdb`.

#### South Dakota

South Dakota waterbody data are available at https://opendata2017-09-18t192802468z-sdbit.opendata.arcgis.com/datasets/052112ac4fce4489a55c7da9aa9a702c_0/about
These were downloaded manually on 3/8/2022 to `data/states/sd/State_Waterbodies.shp`.

#### Washington State

Washington State data are available at:

- https://geo.wa.gov/datasets/wdfw::visible-surface-water/explore (more metadata at: https://geodataservices.wdfw.wa.gov/arcgis/rest/services/HP_Projects/Visible_Surface_Water/MapServer)
- https://www.arcgis.com/sharing/rest/content/items/28a0f93c33454297b4a9d3faf3da552a/info/metadata/metadata.xml?format=default&output=html

These were downloaded on 2/19/2022 to `data/states/wa/SurfaceWaterUnified_forGeoWA.gdb` and `data/states/wa/hydro.gdb`.

### 4. Extract flowlines, waterbodies, and NHD barriers:

Run `extract_nhd.py` to extract the flowlines, joins between flowlines, waterbodies, and NHD barriers (points, lines, polygons) from the NHD FGDB files. This creates "raw" data extracted from NHD, with minimal processing, so that later processing steps can refine the extraction logic for network analysis without needing to go back to the raw NHD data.

This step should only need to be rerun if there are errors or additional HUC4s / regions are needed, or there are data updates from NHD.

#### Flowlines:

These data are extracted from NHDFlowline, NHDPlusFlowlineVAA, NHDPlusFlow datasets.

- aquatic networks that cross HUC4 boundaries within each region are joined together to create contiguous networks.
- all coastlines (FType=566) and their joins are dropped
- size classes are calculated (see `analysis/prep/network/lib/nhd/flowlines.py` for thresholds)
- length is calculated
- geometries are converted to XY LineStrings from XYZ MultiLineStrings
- projected to SARP standard CRS

The output flowlines contain "loops" (secondary channels in addition to the main flow line). These may cause problems depending on network topology, but they are retained so that issues with NHD data can be identified and handled appropriately below. Loops are identified by the `loop` attribute.

#### Waterbodies:

These data are extracted from the NHDWaterbody dataset. Only waterbodies that intersect flowlines are retained. These are reprojected to SARP standard CRS.

#### Barriers

These include points, lines, and polygons representing dams, dam-related features, and waterfalls with the following FTypes:

- Dam (343)
- Gate (369)
- Lock / Lock Chamber (398)
- Reservoir (436)
- Spillway (455)
- Waterfall (487)

#### Outputs:

This creates a directory (`data/nhd/raw/<region>`) for each region containing:

- `flowlines.feather`: flowline geometries and attributes
- `flowline_joins.feather`: joins between flowlines to represent network topology
- `waterbodies.feather`: waterbody geometries and attributes
- `nhd_points.feather`: NHD barrier points
- `nhd_lines.feather`: NHD barrier lines
- `nhd_poly.feather`: NHD barrier polygons
- `nhd_altered_rivers.feather`: altered river areas from NHDArea
- `nhd_marine.feather`: marine areas: ocean, inlets, bays, and estuaries

#### IMPORTANT:

- flowlines are identified using `lineID` from this point forward; this is a unique ID assigned to this specific run of the data extraction. These ids are NOT durable from one extraction to the next. These are used because the flowlines are cut, yet we retain the original NHDPlusID of each original segment to be able to relate it back to NHD.
- waterbodies are identified using `wbID`. These are also specific to this particular extraction.

### 5. Merge marine areas

Run `merge_marine.py` to merge all marine areas.

### 6. Run any special preprocessing scripts or hand-inspect NHD data

To get around issues with NHD HR+ Beta data, you likely need to inspect the NHD data first for errors:

1. Some "loops" are miscoded; the main segment is mis-identified as a loop, whereas a pipeline may be identified as the main segment. Other loops are simply not coded as such.

The results of this analysis and preprocessing are stored in `analysis/constants.py` in `REMOVE_IDS` and `CONVERT_TO_NONLOOP` variables. These store lists of NHDPlusIDs that need to be acted upon.

Use `special/find_loops.py` to help find the loops to add to `analysis/constants.py`.

NOTE: `find_loops.py` will find loops, but not necessarily the correct NHDPlusID for the actual
loop due to traversal order. Use this to manually search for the correct loop to exclude.

### California waterbodies

Run `special/prepare_ca_waterbodies.py` to extract waterbodies that intersect flowlines.

#### Oregon waterbodies

Run `special/prepare_or_waterbodies.py` to extract waterbodies that intersect flowlines.

#### South Carolina LIDAR-derived waterbodies

Run `special/prepare_sc_waterbodies.py` to extract waterbodies that intersect flowlines.

#### South Dakota waterbodies

Run `special/prepare_sd_waterbodies.py` to extract waterbodies that intersect flowlines.

#### Washington State imagery-derived waterbodies

Run `special/prepare_wa_waterbodies.py` to extract waterbodies that intersect flowlines.

#### TNC Freshwater resilience

TNC's Freshwater Resilience data for the contiguous US were provided by Kat on
1/30/2024 based on data contained in TNC's [Resilient River Explorer](https://www.maps.tnc.org/resilientrivers/#/explore).

TNC's temperature score data used for the above were provided by Kat on 2/4/2025
via email.

Resilient NHD flowlines were extracted where flowlines mostly overlap with areas
above average in the TNC resilience dataset.

Coldwater habitat flowlines were extracted where flowlines mostly overlap with areas at
least above average in the TNC cold water scores dataset.

Run `special/prepare_tnc_resilience.py` to extract TNC resilience and cold water
areas to NHD flowlines.

### 7. Extract NWI waterbodies and altered rivers

Run `extract_nwi.py` to extract NWI waterbodies and altered rivers that intersect
the above flowlines. Altered rivers are those that have been marked in NWI as
diked, ditched, excavated, or have altered substrate.

This creates a directory (`data/nwi/raw/<region>`) for each region containing:

- waterbodies.feather
- altered_rivers.feather

### 8. Extract LAGOS reservoirs

LAGOS reservoirs were downloaded from https://portal.edirepository.org/nis/mapbrowse?scope=edi&identifier=1016
on 12/12/2024.

These are preprocessed to extract representative points that can be used to
attribute merged waterbodies using `extract_lagos.py`.

### 9. Merge waterbodies

Run `merge_waterbodies.py` to merge NHD, NWI, and other waterbodies. This first
dissolves any overlapping waterbodies. It then uses the NHD data to determine
valid breaks between adjacent waterbodies (e.g., large reservoir system with
internal dams), based on break points that are near NHD dam lines. NHD dams are
buffered slightly and merged with these break points, and they are used to cut the
waterbodies back apart.

Note: this may produce slight artifacts in the waterbody edges where dams are cut in
to separate adjacent waterbodies.

This creates `data/waterbodies/<region>/waterbodies.feather`.

Run `merge_wetlands.py` to merge NHD and NWI wetlands. This only retains wetlands
not marked as altered in NWI (NHD has no altered modifier for these) and only
keeps NHD wetlands that don't intersect with NWI wetlands.

This creates `data/wetlands/<region>/wetlands.feather`.

### 10. Prepare flowlines and waterbodies:

Run `prepare_flowlines_waterbodies.py` to preprocess flowlines and waterbodies into data structures ready for analysis. This implements the bulk of the logic to extract the appropriate flowline and waterbodies. This logic may need to be tuned to refine the network connectivity analysis.

This performs several steps:

1. Drops any flowlines that are excluded (from special processing above)
2. Recodes "loops" as needed
3. Drops all underground conduits (FType=420)
4. Drops underground connectorspipelines (FType=420 or 428) that are isolated, at terminal ends of flowlines, or are long connectors between flowlines (>250m)
5. Flowlines are cut by waterbodies, and flowlines are attributed with `waterbody` to indicate if they fall entirely or mostly (>50%) within a waterbody.
6. Waterbody "drain points" are identified by taking the furthest downstream point of each flowline network that falls within a waterbody. Due to the way that waterbodies are connected to exiting flowlines, there may be multiple drain points for some waterbodies (most typically have just one). Note: some large riverways are mapped as NHD waterbodies; drain points are not as meaningful for these features.

Note:
short pipelines (<250m) between adjacent non-pipeline flowline are retained. From visual inspection, these occur at dam drain points, which means that removing them completely breaks the network and eliminates our ability to analyze the impact of those dams on network connectivity.

WARNING: there are a number of geometry and related errors in NHD that confounds this analysis. The data output by this step are reasonably good, but not perfect.

#### Outputs:

This creates "clean" data for further analysis in `data/nhd/clean/<region>`:

- `flowlines.feather`: flowline geometries and attributes
- `flowline_joins.feather`: joins between flowlines to represent network topology
- `waterbodies.feather`: waterbody geometries and attributes
- `waterbody_flowline_joins.feather`: joins between waterbodies and flowlines.
- `waterbody_drain_points.feather`: drain points for each waterbody

The script outputs files with erroneous data, if errors are detected during processing. These are identified by `error_*` with a name that indicates the nature of the error.

### 11. Find NHD dams

Run `find_nhd_dams.py` to extract NHD dams from `nhd_lines.feather` and `nhd_areas.feather` above.

1. Dam-related feature are extracted from `nhd_lines.feather`.
2. Line are buffered by 5 meters.
3. Dam-related feature are extracted from `nhd_area.feather`.
4. Buffered lines and areas are combined and adjacent / overlapping feature are dissolved.
5. The GNIS_Name, if any, is retained for the dissolved features.
6. NHD dams are intersected with flowlines.
7. The lowest downstream segment of each flowline that overlaps these dams is identified.
8. A representative point is extracted for the lowest downstream segment; typically this is the furthest upstream or downstream point along that line or the portion of that line that intersects with the NHD dam feature.
9. Dams are attributed to the nearest waterbody (within 50m).

WARNING: there are data issues apparent in the NHD lines and areas. Some features are mis-coded (e.g. dikes parallel to flowlines rather than barriers), whereas others seem spurious and not validated by the satellite imagery for the same location.

#### Outputs:

This creates `data/nhd/merged/nhd_dams_pt.feather`

### 12. Prepare floodplain metrics

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
