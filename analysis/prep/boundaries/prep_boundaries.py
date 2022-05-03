"""
Create geofeather files for each of the input boundaries, in the same projection
as barriers (EPSG:102003 - CONUS Albers).

Note: output shapefiles for creating tilesets are limited to only those areas that overlap
the SARP states boundary.

"""
import json
from pathlib import Path
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
import pygeos as pg
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import (
    CRS,
    GEO_CRS,
    OWNERTYPE_TO_DOMAIN,
    OWNERTYPE_TO_PUBLIC_LAND,
)
from analysis.lib.geometry import explode, dissolve, to_multipolygon

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")


data_dir = Path("data")
out_dir = data_dir / "boundaries"
src_dir = out_dir / "source"
ui_dir = Path("ui/data")
county_filename = src_dir / "tl_2021_us_county.shp"

huc4_df = gp.read_feather(out_dir / "huc4.feather")

# state outer boundaries, NOT analysis boundaries
bnd_df = gp.read_feather(out_dir / "region_boundary.feather")
bnd = bnd_df.loc[bnd_df.id == "total"].geometry.values.data[0]

state_df = gp.read_feather(
    out_dir / "region_states.feather", columns=["STATEFIPS", "geometry"]
)
states = state_df.STATEFIPS.unique()

# Clip HUC4 areas outside state boundaries; these are remainder
state_merged = pg.coverage_union_all(state_df.geometry.values.data)

# find all that intersect but are not contained
tree = pg.STRtree(huc4_df.geometry.values.data)
intersects_ix = tree.query(state_merged, predicate="intersects")
contains_ix = tree.query(state_merged, predicate="contains")
ix = np.setdiff1d(intersects_ix, contains_ix)

outer_huc4 = huc4_df.iloc[ix].copy()
outer_huc4["km2"] = pg.area(outer_huc4.geometry.values.data) / 1e6

# calculate geometric difference, explode, and keep non-slivers
# outer HUC4s are used to clip NID dams for areas outside region states for which
# inventoried dams are available
outer_huc4["geometry"] = pg.difference(outer_huc4.geometry.values.data, state_merged)
outer_huc4 = explode(outer_huc4)
outer_huc4["clip_km2"] = pg.area(outer_huc4.geometry.values.data) / 1e6
outer_huc4["percent"] = 100 * outer_huc4.clip_km2 / outer_huc4.km2
keep_huc4 = outer_huc4.loc[outer_huc4.clip_km2 >= 100].HUC4.unique()
outer_huc4 = outer_huc4.loc[
    outer_huc4.HUC4.isin(keep_huc4) & (outer_huc4.clip_km2 >= 2.5)
].copy()
outer_huc4 = dissolve(outer_huc4, by="HUC4", agg={"HUC2": "first"}).reset_index(
    drop=True
)
outer_huc4.to_feather(out_dir / "outer_huc4.feather")
write_dataframe(outer_huc4, out_dir / "outer_huc4.fgb")

### Counties - within HUC4 bounds
print("Processing counties")
fips = sorted(state_df.STATEFIPS.unique())

county_df = (
    read_dataframe(county_filename, columns=["NAME", "GEOID", "STATEFP"],)
    .to_crs(CRS)
    .rename(columns={"NAME": "County", "GEOID": "COUNTYFIPS", "STATEFP": "STATEFIPS"})
)

# keep only those within the region HUC4 outer boundary
tree = pg.STRtree(county_df.geometry.values.data)
ix = np.unique(tree.query_bulk(huc4_df.geometry.values.data, predicate="intersects")[1])
ix.sort()
county_df = county_df.iloc[ix].reset_index(drop=True)
county_df.geometry = to_multipolygon(pg.make_valid(county_df.geometry.values.data))

# keep larger set for spatial joins
county_df.to_feather(out_dir / "counties.feather")
write_dataframe(county_df, out_dir / "counties.fgb")

# Subset these in the region for tiles and summary stats
county_df.loc[county_df.STATEFIPS.isin(states)].rename(
        columns={"COUNTYFIPS": "id", "County": "name"}
    ).to_feather(out_dir / "region_counties.feather")

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

# keep larger version for spatial joins
df.to_feather(out_dir / "eco3.feather")


# subset out those that intersect the region states
# not outer HUC4 boundary
# Drop ones only barely in region for mapping / summary stats

tree = pg.STRtree(df.geometry.values.data)
ix = np.unique(tree.query(bnd, predicate="intersects"))
ix.sort()

df = df.iloc[ix].reset_index(drop=True)

# calculate overlap and only keep those with > 25% overlap
in_region = pg.intersection(df.geometry.values.data, bnd)
pct_in_region = 100 * pg.area(in_region) / pg.area(df.geometry.values.data)
df = df.loc[pct_in_region >= 25].reset_index(drop=True)

# write out for tiles
df.rename(columns={"ECO3": "id", "ECO3Name": "name"}).to_feather(out_dir / "region_eco3.feather")


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


# subset out those that intersect the region
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
df.rename(columns={"ECO4": "id", "ECO4Name": "name"}).to_feather(out_dir / "region_eco4.feather")


### Extract bounds and names for unit search in user interface
print("Projecting geometries to geographic coordinates for search index")
print("Processing state and county")
state_geo_df = (
    gp.read_feather(
        out_dir / "region_states.feather", columns=["geometry", "STATEFIPS"]
    )
    .rename(columns={"STATEFIPS": "id"})
    .to_crs(GEO_CRS)
)
state_geo_df["bbox"] = pg.bounds(state_geo_df.geometry.values.data).round(1).tolist()

states_geo = (
    gp.read_feather(out_dir / "states.feather", columns=["geometry", "STATEFIPS"])
    .rename(columns={"STATEFIPS": "id"})
    .to_crs(GEO_CRS)
)

county_geo_df = (
    county_df.loc[county_df.STATEFIPS.isin(states)]
    .rename(columns={"COUNTYFIPS": "id", "County": "name", "STATEFIPS": "state"})
    .to_crs(GEO_CRS)
)
county_geo_df["bbox"] = pg.bounds(county_geo_df.geometry.values.data).round(2).tolist()


out = {
    "State": state_geo_df[["id", "bbox"]]
    .sort_values(by="id")
    .to_dict(orient="records"),
    "County": county_geo_df[["id", "name", "state", "bbox"]]
    .sort_values(by="id")
    .to_dict(orient="records"),
}


for unit in ["HUC6", "HUC8", "HUC10", "HUC12", "ECO3", "ECO4"]:
    print(f"Processing {unit}")
    df = (
        gp.read_feather(out_dir / f"{unit.lower()}.feather")
        .rename(columns={unit: "id", "ECO3Name": "name", "ECO4Name": "name"})
        .to_crs(GEO_CRS)
    )

    if unit in ["ECO3", "ECO4"]:
        df = dissolve(df, by="id", agg={"name": "first"})

    df["bbox"] = pg.bounds(df.geometry.values.data).round(2).tolist()

    # spatially join to states
    tree = pg.STRtree(states_geo.geometry.values.data)
    left, right = tree.query_bulk(df.geometry.values.data, predicate="intersects")
    unit_states = (
        pd.DataFrame(
            {"id": df.id.values.take(left), "state": states_geo.id.values.take(right),}
        )
        .groupby("id")["state"]
        .unique()
        .apply(list)
    )

    df = df.join(unit_states, on="id")
    df["state"] = df.state.fillna("").apply(lambda x: ",".join(x))
    out[unit] = (
        df[["id", "name", "state", "bbox"]]
        .sort_values(by="id")
        .to_dict(orient="records")
    )

with open(ui_dir / "unit_bounds.json", "w") as outfile:
    outfile.write(json.dumps(out))


### Protected areas

print("Extracting protected areas (will take a while)...")
df = (
    read_dataframe(
        src_dir / "SARP_ProtectedAreas_2021.gdb",
        layer="SARP_ProtectedArea_National_2021",
        columns=["OwnerType", "OwnerName", "EasementHolderType", "Preference"],
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

# select those that are within the boundary
tree = pg.STRtree(df.geometry.values.data)
ix = tree.query(bnd, predicate="intersects")

df = df.take(ix)

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
        "FWS",
        "USFWS",
        "USFW",
        "US FWS",
        "U.S. Fish and Wildlife Service",
        "U. S. Fish & Wildlife Service",
        "U.S. Fish & Wildlife Service",
        "U.S. Fish and Wildlife Service (FWS)",
        "US Fish & Wildlife Service",
        "US Fish and Wildlife Service",
        "USDI FISH AND WILDLIFE SERVICE",
    ],
    "USDA Forest Service": [
        "Forest Service",
        "USFS",
        "USDA FOREST SERVICE",
        "USDA Forest Service",
        "US Forest Service",
        "USDA Forest Service",
        "U.S. Forest Service",
        "U.S. Forest Service (USFS)",
        "United States Forest Service",
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

# join to HUC8 dataset for tiles
huc8_df = gp.read_feather(out_dir / "huc8.feather")
df = huc8_df.join(priorities.set_index("HUC_8"), on="HUC8")

for col in ["usfs", "coa", "sgcn"]:
    df[col] = df[col].fillna(0).astype("uint8")

df.rename(columns={"HUC8": "id"}).to_feather(out_dir / "huc8_priorities.feather")

