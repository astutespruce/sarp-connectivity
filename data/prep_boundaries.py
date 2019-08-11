"""
Create geofeather files for each of the input boundaries, in the same projection
as barriers (EPSG:102003 - CONUS Albers).
Note: geopandas doesn't recognize that EPSG code, so we use proj4 string throughout:
"+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

HUCs downloaded from: http://prd-tnm.s3-website-us-west-2.amazonaws.com/?prefix=StagedProducts/Hydrography/WBD/National/GDB/
and selected out for those within the SARP region (all HUC4s that overlap SARP region)

States and counties were downloaded for 2018 from CENSUS TIGER: https://www.census.gov/cgi-bin/geo/shapefiles/index.php

Ecoregions were downloaded from: https://www.epa.gov/eco-research/level-iii-and-iv-ecoregions-continental-united-states


All boundaries are projected using ogr2ogr in advance:

```
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" SARP_boundary_prj.shp SARP_boundary.shp

# Project HUC4 
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" -sql "SELECT HUC4 from WBDHU4" HUC4_all_prj.shp WBD_National_GDB.gdb WBDHU4

# Extract out HUC4s in SARP boundary
ogr2ogr -sql "SELECT * from HUC4_all_prj WHERE HUC4 in ('0204', '0207', '0208', '0301', '0302', '0303', '0304', '0305', '0306', '0307', '0308', '0309', '0310', '0311', '0312', '0313', '0314', '0315', '0316', '0317', '0318', '0505', '0507', '0509', '0510', '0511', '0512', '0513', '0514', '0601', '0602', '0603', '0604', '0710', '0711', '0714', '0801', '0802', '0803', '0804', '0805', '0806', '0807', '0808', '0809', '1024', '1027', '1028', '1029', '1030', '1101', '1104', '1105', '1106', '1107', '1108', '1109', '1110', '1111', '1112', '1113', '1114', '1201', '1202', '1203', '1204', '1205', '1206', '1207', '1208', '1209', '1210', '1211', '1303', '1304', '1305', '1306', '1307', '1308', '1309', '1312', '2101', '2102')" HUC4_sarp.shp HUC4_all_prj.shp


# Project HUC6
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" -sql "SELECT HUC6, NAME, SUBSTR(HUC6, 0, 4) as HUC4 from WBDHU6" HUC6_all_prj.shp WBD_National_GDB.gdb WBDHU6

# Extract out HUC6s in SARP boundary
ogr2ogr -sql "SELECT * from HUC6_all_prj WHERE HUC4 in ('0204', '0207', '0208', '0301', '0302', '0303', '0304', '0305', '0306', '0307', '0308', '0309', '0310', '0311', '0312', '0313', '0314', '0315', '0316', '0317', '0318', '0505', '0507', '0509', '0510', '0511', '0512', '0513', '0514', '0601', '0602', '0603', '0604', '0710', '0711', '0714', '0801', '0802', '0803', '0804', '0805', '0806', '0807', '0808', '0809', '1024', '1027', '1028', '1029', '1030', '1101', '1104', '1105', '1106', '1107', '1108', '1109', '1110', '1111', '1112', '1113', '1114', '1201', '1202', '1203', '1204', '1205', '1206', '1207', '1208', '1209', '1210', '1211', '1303', '1304', '1305', '1306', '1307', '1308', '1309', '1312', '2101', '2102')" HUC6_sarp.shp HUC6_all_prj.shp



# Project HUC12 and extract HUC2, HUC4 codes
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" -sql "SELECT HUC12, SUBSTR(HUC12, 0, 4) as HUC4, SUBSTR(HUC12, 0, 2) as HUC2 from WBDHU12" HUC12_all_prj.shp WBD_National_GDB.gdb WBDHU12

# Extract HUC12s for HUC4s in SARP boundary
ogr2ogr -sql "SELECT * from HUC12_all_prj WHERE HUC4 in ('0204', '0207', '0208', '0301', '0302', '0303', '0304', '0305', '0306', '0307', '0308', '0309', '0310', '0311', '0312', '0313', '0314', '0315', '0316', '0317', '0318', '0505', '0507', '0509', '0510', '0511', '0512', '0513', '0514', '0601', '0602', '0603', '0604', '0710', '0711', '0714', '0801', '0802', '0803', '0804', '0805', '0806', '0807', '0808', '0809', '1024', '1027', '1028', '1029', '1030', '1101', '1104', '1105', '1106', '1107', '1108', '1109', '1110', '1111', '1112', '1113', '1114', '1201', '1202', '1203', '1204', '1205', '1206', '1207', '1208', '1209', '1210', '1211', '1303', '1304', '1305', '1306', '1307', '1308', '1309', '1312', '2101', '2102')" HUC12_sarp.shp HUC12_all_prj.shp

# Project states and counties
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" states_prj.shp tl_2018_us_state.shp
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" counties_prj.shp tl_2018_us_county.shp

# Project ecoregions
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" eco3_prj.shp us_eco_l3.shp
ogr2ogr -t_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" eco4_prj.shp us_eco_l4_no_st.shp
```

"""


from pathlib import Path
import os

import geopandas as gp
from nhdnet.io import serialize_gdf, to_shp


data_dir = Path("../data/sarp/")
wbd_dir = data_dir / "nhd/wbd"
boundaries_dir = data_dir / "boundaries"
out_dir = data_dir / "derived/boundaries"

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

### Process watershed boundaries
### HUC4s that overlap with SARP region is the outer boundary for analysis
huc4 = gp.read_file(wbd_dir / "HUC4_sarp.shp")
huc4.sindex


### Watersheds - already have shapefiles
# ### HUC12s
# df = gp.read_file(wbd_dir / "HUC12_sarp.shp")[["geometry", "HUC12"]]
# serialize_gdf(df, out_dir / "HUC12.feather")

### HUC6s - used for basin names
df = gp.read_file(wbd_dir / "HUC6_sarp.shp")[["geometry", "HUC6", "NAME"]]
serialize_gdf(df, out_dir / "HUC6.feather")


# ### States - within HUC4 bounds
print("Processing states")
df = gp.read_file(boundaries_dir / "states_prj.shp")[
    ["geometry", "NAME", "STATEFP"]
].rename(columns={"NAME": "State", "STATEFP": "STATEFIPS"})
df.sindex
in_region = gp.sjoin(df, huc4)
df = df.loc[df.STATEFIPS.isin(in_region.STATEFIPS)]
serialize_gdf(df, out_dir / "states.feather", index=False)
to_shp(df.reset_index(), out_dir / "states.shp")

# # ### Counties - within HUC4 bounds
print("Processing counties")
df = gp.read_file(boundaries_dir / "counties_prj.shp")[
    ["geometry", "NAME", "GEOID"]
].rename(columns={"NAME": "County", "GEOID": "COUNTYFIPS"})
df.sindex
in_region = gp.sjoin(df, huc4)
df = df.loc[df.COUNTYFIPS.isin(in_region.COUNTYFIPS)]
serialize_gdf(df, out_dir / "counties.feather", index=False)
to_shp(df.reset_index(), out_dir / "counties.shp")

### Ecoregions - within HUC4 bounds
print("Processing ecoregions")
df = gp.read_file(boundaries_dir / "eco3_prj.shp")[
    ["geometry", "NA_L3CODE", "US_L3NAME"]
].rename(columns={"NA_L3CODE": "ECO3", "US_L3NAME": "ECO3Name"})
df.sindex
in_region = gp.sjoin(df, huc4)
df = df.loc[df.ECO3.isin(in_region.ECO3)]
serialize_gdf(df, out_dir / "eco3.feather", index=False)
to_shp(df.reset_index(), out_dir / "eco3.shp")


df = gp.read_file(boundaries_dir / "eco4_prj.shp")[
    ["geometry", "US_L4CODE", "US_L4NAME", "NA_L3CODE"]
].rename(columns={"US_L4CODE": "ECO4", "US_L4NAME": "ECO4Name", "NA_L3CODE": "ECO3"})
df.sindex
in_region = gp.sjoin(df, huc4)
df = df.loc[df.ECO4.isin(in_region.ECO4)]
serialize_gdf(df, out_dir / "eco4.feather", index=False)
to_shp(df.reset_index(), out_dir / "eco4.shp")
