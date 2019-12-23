# Southeast Aquatic Barrier Inventory Data Processing - Boundary Data Prep

This involves extracting boundary information within the SARP region that is used to attribute barriers, summarize barrier information, and identify barriers that are outside the region.

This should only need to run when new boundary data are available.

## Overall workflow

1. Create summary units for analysis. These are joined to barriers and used for summary display on the map.
2. Extract summary units within SARP HUC4 boundary and create geofeather files for later processing.
3. Create vector tiles of all summary units that include name and ID in a standardized way. This only needs to be done again when summary units are modified or new ones are added.

Naming conventions:
`*_prj.shp` denotes a shapefile in the CONUS Albers projection of the SARP inventory.
`*_wgs84.shp` denotes a shapefile in WGS84 projection for use in `tippecanoe`.

## 1. Create summary units

All data are initially processed using an outer boundary defined by all HUC4s that intersect the SARP states boundary (below). This is so that spatial joins of these units to barriers always assign the correct value. Due to the large data volume for HUCs, these are extracted using queries in `ogr2ogr` (below) whereas others are extracted using python to evaluate the overlaps.

All tilesets created for use in the tool are limited to summary units that overlap the SARP states boundary.

All boundaries are projected using ogr2ogr in advance. Because `geopandas` doesn't recognize the EPSG code of the barrier inventory, we use a proj4 string throughout all processing:
"+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

Input files are stored in `/data/boundaries/source`.
Output files are stored in `/data/boundaries`
If needed (e.g., projected states but not yet extracted to SARP HUC4 boundary), intermediate files are stored in `/data/boundaries/intermediate`

### SARP States boundary

All states in the SARP region (defined by `/analysis/prep/prep_boundaries.py::SARP_STATES`) were extracted from the CENSUS tiger states dataset and dissolved.

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

### Protected Areas

Kat Hoenke (SARP) extracted protected area data from CBI Protected Areas and TNC Secured Lands and merged them together. Kat later obtained a boundaries layer from USFS, and overlayed this over the top (11/4/2019). Because this causes multiple owner type polygons to occur in the same location, the `Preference` attribute is added, so that we can sort on ascending preference to assign the most appropriate ownership to a given barrier (nulls assigned arbitrary high value).

```
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" -sql "SELECT OwnerType as otype, OwnerName as owner, EasementHolderType as etype, Preference as sort from CBI_PADUS_NCED_TNC_USFS_Combine2019" ../intermediate/protected_areas.shp Protected_Areas_2019.gdb CBI_PADUS_NCED_TNC_USFS_Combine2019
```

## 2. Extract areas within SARP HUC4 boundary and processing

The above boundary data are processed into geofeather files using `/analysis/prep/boundaries/prep_boundaries.py`. This includes selecting out states, counties, and ecoregions that fall within the HUC4 outer boundary.

## 3. Create boundary vector tiles

Vector tiles are are created for each of the boundary layers.

Because `tippecanoe` uses GeoJSON in WGS84 projection as input, each vector tileset below includes a step to create this GeoJSON file first. These GeoJSON files can be deleted as soon as the vector tileset is created.

Run `analysis/prep/boundaries/generate_tiles.sh` from the root directory of the project.
