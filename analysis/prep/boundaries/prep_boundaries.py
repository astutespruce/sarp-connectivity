"""
Create geofeather files for each of the input boundaries, in the same projection
as barriers (EPSG:102003 - CONUS Albers).

Note: output shapefiles for creating tilesets are limited to only those areas that overlap
the SARP states boundary.

"""


from pathlib import Path
import os

import geopandas as gp
from geofeather import to_geofeather
from nhdnet.io import to_shp

from analysis.constants import (
    CRS,
    OWNERTYPE_TO_DOMAIN,
    SARP_STATES_FIPS,
    OWNERTYPE_TO_PUBLIC_LAND,
)


data_dir = Path("./data")
boundaries_dir = data_dir / "boundaries"

# intermediate stores projected data that haven't been intersected to region
intermediate_dir = boundaries_dir / "intermediate"
out_dir = boundaries_dir

bnd = gp.read_file(boundaries_dir / "SARP_boundary_prj.shp")
bnd.sindex


### Process watershed boundaries
### HUC4s that overlap with SARP region is the outer boundary for analysis
huc4 = gp.read_file(boundaries_dir / "HUC4_prj.shp")
huc4.sindex


### Watersheds
### HUC6s - used for basin names
df = gp.read_file(intermediate_dir / "HUC6_prj.shp")[["geometry", "HUC6", "NAME"]]
df.sindex
to_geofeather(df, out_dir / "HUC6.feather")

# Select out within the SARP boundary
in_sarp = gp.sjoin(df, bnd)
df = df.loc[df.HUC6.isin(in_sarp.HUC6)]
to_shp(
    df.reset_index().rename(columns={"HUC6": "id", "NAME": "name"}),
    boundaries_dir / "HUC6_prj.shp",
)

### HUC8s - used for visualization; not needed for spatial joins
df = gp.read_file(intermediate_dir / "HUC8_prj.shp")[["geometry", "HUC8", "NAME"]]
df.sindex

# Select out within the SARP boundary
in_sarp = gp.sjoin(df, bnd)
df = df.loc[df.HUC8.isin(in_sarp.HUC8)]
to_shp(
    df.reset_index().rename(columns={"HUC8": "id", "NAME": "name"}),
    boundaries_dir / "HUC8_prj.shp",
)

### HUC12s - primary for all spatial joins (other codes can be derived from HUC12)
df = gp.read_file(intermediate_dir / "HUC12_prj.shp")[["geometry", "HUC12", "NAME"]]
df.sindex
to_geofeather(df, out_dir / "HUC12.feather")

# Select out within the SARP boundary
in_sarp = gp.sjoin(df, bnd)
df = df.loc[df.HUC12.isin(in_sarp.HUC12)]
to_shp(
    df.reset_index().rename(columns={"HUC12": "id", "NAME": "name"}),
    boundaries_dir / "HUC12_prj.shp",
)

### States - within HUC4 bounds
print("Processing states")
df = gp.read_file(intermediate_dir / "states_prj.shp")[
    ["geometry", "NAME", "STATEFP"]
].rename(columns={"NAME": "State", "STATEFP": "STATEFIPS"})
df.sindex
in_region = gp.sjoin(df, huc4)
df = df.loc[df.STATEFIPS.isin(in_region.STATEFIPS)]
to_geofeather(df.reset_index(drop=True), out_dir / "states.feather")

# select only those within the SARP states for tilesets
# since other states are only partially covered by data
df = df.loc[df.STATEFIPS.isin(SARP_STATES_FIPS)]
# Format field names for tilesets
to_shp(
    df.reset_index().rename(columns={"State": "id"}), boundaries_dir / "states_prj.shp"
)
# save as SARP boundary
df["sarp"] = 1
bnd = df.dissolve(by="sarp")
to_shp(
    bnd.reset_index()[["geometry", "sarp"]], boundaries_dir / "SARP_boundary_prj.shp"
)


# ### Counties - within HUC4 bounds
print("Processing counties")
df = gp.read_file(intermediate_dir / "counties_prj.shp")[
    ["geometry", "NAME", "GEOID", "STATEFP"]
].rename(columns={"NAME": "County", "GEOID": "COUNTYFIPS", "STATEFP": "STATEFIPS"})
df.sindex
in_region = gp.sjoin(df, huc4)
df = df.loc[df.COUNTYFIPS.isin(in_region.COUNTYFIPS)]
to_geofeather(df.reset_index(drop=True), out_dir / "counties.feather")

# select only those within the SARP states for tilesets
df = df.loc[df.STATEFIPS.isin(SARP_STATES_FIPS)]
# Format field names for tilesets
to_shp(
    df.reset_index().rename(columns={"COUNTYFIPS": "id", "County": "name"}),
    boundaries_dir / "counties_prj.shp",
)


### Ecoregions - within HUC4 bounds
print("Processing ecoregions")
df = gp.read_file(intermediate_dir / "eco3_prj.shp")[
    ["geometry", "NA_L3CODE", "US_L3NAME"]
].rename(columns={"NA_L3CODE": "ECO3", "US_L3NAME": "ECO3Name"})
df.sindex
in_region = gp.sjoin(df, huc4)
df = df.loc[df.ECO3.isin(in_region.ECO3)]
to_geofeather(df.reset_index(drop=True), out_dir / "eco3.feather")

# Select out within the SARP boundary
df["tmp_id"] = df.index.astype("uint")
in_sarp = gp.sjoin(df, bnd)
df = df.loc[df.tmp_id.isin(in_sarp.tmp_id)].drop(columns=["tmp_id"])
to_shp(
    df.reset_index().rename(columns={"ECO3": "id", "ECO3Name": "name"}),
    boundaries_dir / "eco3_prj.shp",
)


df = gp.read_file(intermediate_dir / "eco4_prj.shp")[
    ["geometry", "US_L4CODE", "US_L4NAME", "NA_L3CODE"]
].rename(columns={"US_L4CODE": "ECO4", "US_L4NAME": "ECO4Name", "NA_L3CODE": "ECO3"})
df.sindex
in_region = gp.sjoin(df, huc4)
df = df.loc[df.ECO4.isin(in_region.ECO4)]
to_geofeather(df.reset_index(drop=True), out_dir / "eco4.feather")

# Select out within the SARP boundary (only the parts of multipart features in SARP)
df["tmp_id"] = df.index.astype("uint")
in_sarp = gp.sjoin(df, bnd)
df = df.loc[df.tmp_id.isin(in_sarp.tmp_id)].drop(columns=["tmp_id"])
to_shp(
    df.reset_index().rename(columns={"ECO4": "id", "ECO4Name": "name"}),
    boundaries_dir / "eco4_prj.shp",
)


### Protected areas
print("Extracting protected areas...")
df = gp.read_file(intermediate_dir / "protected_areas.shp").rename(
    columns={"type": "otype"}
)


# partner_federal = ["US Fish and Wildlife Service", "US Forest Service", "USDA Forest Service"]

# partner federal agencies to call out specifically
# map of substrings to search for specific owners
partner_federal = {
    "US Fish and Wildlife Service": [
        "USFWS",
        "USFW",
        "US FWS",
        "U.S. Fish and Wildlife Service",
        "U.S. Fish & Wildlife Service",
    ],
    "USDA Forest Service": ["USFS", "USDA FOREST SERVICE", "US Forest Service"],
}

has_owner = df.owner.notnull()
for partner, substrings in partner_federal.items():
    print("Finding specific federal partner {}".format(partner))
    # search on the primary name
    df.loc[has_owner & df.owner.str.contains(partner), "otype"] = partner

    for substring in substrings:
        df.loc[has_owner & df.owner.str.contains(substring), "otype"] = partner

    print("Found {:,} areas for that partner".format(len(df.loc[df.otype == partner])))


# convert to int groups
df["OwnerType"] = df.otype.map(OWNERTYPE_TO_DOMAIN)
# drop all that didn't get matched
# CAUTION: make sure the types we want are properly handled!
df = df.dropna(subset=["OwnerType"])
df.OwnerType = df.OwnerType.astype("uint8")

# Add in public status
df["ProtectedLand"] = (
    df.OwnerType.map(OWNERTYPE_TO_PUBLIC_LAND).fillna(False).astype("bool")
)

# only save owner type
df = df[["geometry", "OwnerType", "ProtectedLand"]].reset_index(drop=True)
to_geofeather(df, boundaries_dir / "protected_areas.feather")
