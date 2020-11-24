"""
Create geofeather files for each of the input boundaries, in the same projection
as barriers (EPSG:102003 - CONUS Albers).

Note: output shapefiles for creating tilesets are limited to only those areas that overlap
the SARP states boundary.

"""
from pathlib import Path
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
import pygeos as pg
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import CRS, OWNERTYPE_TO_DOMAIN, OWNERTYPE_TO_PUBLIC_LAND

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
out_dir = data_dir / "boundaries"
src_dir = out_dir / "source"
county_filename = src_dir / "tl_2019_us_county/tl_2019_us_county.shp"

huc4_df = gp.read_feather(out_dir / "huc4.feather")
sarp_huc4_df = gp.read_feather(out_dir / "sarp_huc4.feather")

# state outer boundaries, NOT analysis boundaries
bnd = gp.read_feather(out_dir / "region_boundary.feather").geometry.values.data[0]
sarp_bnd = gp.read_feather(out_dir / "sarp_boundary.feather").geometry.values.data[0]

state_df = gp.read_feather(
    out_dir / "region_states.feather", columns=["STATEFIPS", "geometry"]
)
states = state_df.STATEFIPS.unique()

sarp_state_df = gp.read_feather(
    out_dir / "sarp_states.feather", columns=["STATEFIPS", "geometry"]
)
sarp_states = sarp_state_df.STATEFIPS.unique()


### Counties - within HUC4 bounds
print("Processing counties")
fips = sorted(state_df.STATEFIPS.unique())

df = (
    read_dataframe(
        county_filename,
        columns=["NAME", "GEOID", "STATEFP"],
        where=f"STATEFP IN {tuple(fips)}",
    )
    .to_crs(CRS)
    .rename(columns={"NAME": "County", "GEOID": "COUNTYFIPS", "STATEFP": "STATEFIPS"})
)

# keep only those within the region
tree = pg.STRtree(df.geometry.values.data)
ix = np.unique(tree.query_bulk(huc4_df.geometry.values.data, predicate="intersects")[1])
ix.sort()

df = df.iloc[ix].reset_index(drop=True)
df.geometry = pg.make_valid(df.geometry.values.data)
df.to_feather(out_dir / "counties.feather")

# Subset these in the region and SARP for tiles
write_dataframe(
    df.loc[df.STATEFIPS.isin(states)].rename(
        columns={"COUNTYFIPS": "id", "County": "name"}
    ),
    out_dir / "region_counties.gpkg",
)
write_dataframe(
    df.loc[df.STATEFIPS.isin(sarp_states)].rename(
        columns={"COUNTYFIPS": "id", "County": "name"}
    ),
    out_dir / "sarp_counties.gpkg",
)


### Process Level 3 Ecoregions
print("Processing level 3 ecoregions")
df = (
    read_dataframe(
        src_dir / "us_eco_l3/us_eco_l3.shp", columns=["NA_L3CODE", "US_L3NAME"]
    )
    .to_crs(CRS)
    .rename(columns={"NA_L3CODE": "ECO3", "US_L3NAME": "ECO3Name"})
)

tree = pg.STRtree(df.geometry.values.data)
ix = np.unique(tree.query_bulk(huc4_df.geometry.values.data, predicate="intersects")[1])
ix.sort()

df = df.iloc[ix].reset_index(drop=True)
df.geometry = pg.make_valid(df.geometry.values.data)
df.to_feather(out_dir / "eco3.feather")


# subset out those that intersect the region and SARP states
# not outer HUC4 boundary
# Drop ones only barely in region

tree = pg.STRtree(df.geometry.values.data)
ix = np.unique(tree.query(bnd, predicate="intersects"))
ix.sort()

df = df.iloc[ix].reset_index(drop=True)

# calculate overlap and only keep those with > 50% overlap
in_region = pg.intersection(df.geometry.values.data, bnd)
pct_in_region = 100 * pg.area(in_region) / pg.area(df.geometry.values.data)
df = df.loc[pct_in_region >= 25].reset_index(drop=True)

# write out for tiles
write_dataframe(
    df.rename(columns={"ECO3": "id", "ECO3Name": "name"}), out_dir / "region_eco3.gpkg"
)


tree = pg.STRtree(df.geometry.values.data)
ix = np.unique(tree.query(sarp_bnd, predicate="intersects"))
ix.sort()
df = df.iloc[ix].reset_index(drop=True)
in_sarp = pg.intersection(df.geometry.values.data, sarp_bnd)
pct_in_sarp = 100 * pg.area(in_sarp) / pg.area(df.geometry.values.data)
df = df.loc[pct_in_sarp >= 25].reset_index(drop=True)

# write out for tiles
write_dataframe(
    df.rename(columns={"ECO3": "id", "ECO3Name": "name"}), out_dir / "sarp_eco3.gpkg"
)

### Process Level 4 Ecoregions
print("Processing level 4 ecoregions")
df = (
    read_dataframe(
        src_dir / "us_eco_l4/us_eco_l4_no_st.shp",
        columns=["US_L4CODE", "US_L4NAME", "NA_L3CODE"],
    )
    .to_crs(CRS)
    .rename(columns={"US_L4CODE": "ECO4", "US_L4NAME": "ECO4Name", "NA_L3CODE": "ECO3"})
)

tree = pg.STRtree(df.geometry.values.data)
ix = np.unique(tree.query_bulk(huc4_df.geometry.values.data, predicate="intersects")[1])
ix.sort()

df = df.iloc[ix].reset_index(drop=True)
df.geometry = pg.make_valid(df.geometry.values.data)
df.to_feather(out_dir / "eco4.feather")


# subset out those that intersect the region and SARP states
# not outer HUC4 boundary
# Drop ones only barely in region

tree = pg.STRtree(df.geometry.values.data)
ix = np.unique(tree.query(bnd, predicate="intersects"))
ix.sort()

df = df.iloc[ix].reset_index(drop=True)

# of those that are at the edge, keep only those with substantial overlap
tree = pg.STRtree(df.geometry.values.data)
ix = np.unique(tree.query(bnd, predicate="contains"))
edge_df = df.loc[~df.index.isin(ix)].copy()
in_region = pg.intersection(edge_df.geometry.values.data, bnd)
pct_in_region = 100 * pg.area(in_region) / pg.area(edge_df.geometry.values.data)
ix = np.append(ix, edge_df.loc[pct_in_region >= 25].index)
df = df.iloc[ix].reset_index(drop=True)

# write out for tiles
write_dataframe(
    df.rename(columns={"ECO4": "id", "ECO4Name": "name"}), out_dir / "region_eco4.gpkg"
)

tree = pg.STRtree(df.geometry.values.data)
ix = np.unique(tree.query(sarp_bnd, predicate="intersects"))
ix.sort()
df = df.iloc[ix].reset_index(drop=True)
tree = pg.STRtree(df.geometry.values.data)
ix = np.unique(tree.query(sarp_bnd, predicate="contains"))
edge_df = df.loc[~df.index.isin(ix)].copy()
in_sarp = pg.intersection(edge_df.geometry.values.data, sarp_bnd)
pct_in_sarp = 100 * pg.area(in_sarp) / pg.area(edge_df.geometry.values.data)
ix = np.append(ix, edge_df.loc[pct_in_sarp >= 25].index)
df = df.iloc[ix].reset_index(drop=True)

# write out for tiles
write_dataframe(
    df.rename(columns={"ECO4": "id", "ECO4Name": "name"}), out_dir / "sarp_eco4.gpkg"
)


### Protected areas

# TODO: get protected areas for larger bounds from SARP
print("Extracting protected areas...")
df = (
    read_dataframe(
        src_dir / "Protected_Areas_2019.gdb",
        layer="CBI_PADUS_NCED_TNC_USFS_Combine2019",
    )
    .to_crs(CRS)
    .rename(
        columns={
            "OwnerType": "otype",
            "OwnerName": "owner",
            "EasementHolderType": "etype",
            "Preference": "sort",
        }
    )
)

# this takes a while...
print("Making geometries valid, this might take a while")
df.geometry = pg.make_valid(df.geometry.values.data)

# sort on 'sort' so that later when we do spatial joins and get multiple hits, we take the ones with
# the lowest sort value (1 = highest priority) first.
df.sort = df.sort.fillna(255).astype("uint8")  # missing values should sort to bottom
df = df.sort_values(by="sort").drop(columns=["sort"])

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
    "USDA Forest Service": [
        "USFS",
        "USDA FOREST SERVICE",
        "US Forest Service",
        "USDA Forest Service",
    ],
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
df.to_feather(out_dir / "protected_areas.feather")


### Priority layers
# These are joined on HUC8 codes

# USFS: 1=highest priority, 3=lowest priority
# based on USFS SE Region analysis May, 2010
usfs = (
    read_dataframe(src_dir / "Priority_Areas.gdb", layer="USFS_Priority")[
        ["HUC_8", "USFS_Priority"]
    ]
    .set_index("HUC_8")
    .rename(columns={"USFS_Priority": "usfs"})
)

# take the lowest value (highest priority) for duplicate watersheds
usfs = usfs.groupby(level=0).min()


# Conservation opportunity areas
# 1 = COA
coa = read_dataframe(src_dir / "Priority_Areas.gdb", layer="SARP_COA")[
    ["HUC_8"]
].set_index("HUC_8")
coa["coa"] = 1

# take the lowest value (highest priority) for duplicate watersheds
coa = coa.groupby(level=0).min()


# Top 10 HUC8s per state for count of SGCN
# TODO: get updated version from SARP
sgcn = read_dataframe(src_dir / "SGCN_Priorities.gdb")[["HUC_8"]].set_index("HUC_8")
sgcn["sgcn"] = 1


# 0 = not priority for a given priority dataset
priorities = (
    usfs.join(coa, how="outer").join(sgcn, how="outer").fillna(0).astype("uint8")
)

# drop duplicates
priorities = (
    priorities.reset_index()
    .drop_duplicates()
    .rename(columns={"index": "HUC8"})
    .reset_index(drop=True)
)

priorities.to_feather(out_dir / "priorities.feather")
