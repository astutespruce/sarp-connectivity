import warnings
from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
import shapely
from pyogrio import read_dataframe

from analysis.constants import CRS, GEO_CRS, REGION_STATES, SARP_STATES, STATES
from analysis.lib.geometry import dissolve, make_valid, to_multipolygon, unwrap_antimeridian

warnings.filterwarnings("ignore", message=".*more than 100 parts.*")


def encode_bbox(geometries):
    return np.apply_along_axis(
        lambda bbox: ",".join([str(v) for v in bbox]),
        arr=shapely.bounds(geometries).round(3).tolist(),
        axis=1,
    )


data_dir = Path("data")
out_dir = data_dir / "boundaries"
out_dir.mkdir(exist_ok=True)
src_dir = data_dir / "boundaries/source"

wbd_gdb = data_dir / "nhd/source/wbd/WBD_National_GDB_2026.gdb"

################################################################################
### Construct region boundary from states
################################################################################
# Note: STATEFIPS is needed to join to counties
print("Processing states...")
states = (
    read_dataframe(
        src_dir / "tl_2025_us_state.zip",
        columns=["STUSPS", "STATEFP", "NAME"],
        where=f"STUSPS in {tuple(STATES)}",
        use_arrow=True,
    )
    .to_crs(CRS)
    .rename(columns={"STUSPS": "id", "NAME": "name", "STATEFP": "STATEFIPS"})
    .sort_values(by="id")
    .reset_index(drop=True)
)
states["geometry"] = to_multipolygon(states.geometry.values)
states.to_feather(out_dir / "states.feather")

# unwrap the parts on the other side of the antimeridian
tmp = states.to_crs(GEO_CRS).explode(ignore_index=True)
tmp["geometry"] = unwrap_antimeridian(tmp.geometry.values)

# dissolve to create outer state boundary for total analysis area and regions
bnd_df = gp.GeoDataFrame(
    [
        {"geometry": shapely.union_all(tmp.geometry.values), "id": "total"},
    ]
    + [
        {
            "geometry": shapely.union_all(tmp.loc[tmp.id.isin(REGION_STATES[region])].geometry.values),
            "id": region,
        }
        for region in REGION_STATES
    ],
    crs=GEO_CRS,
)
bnd_df["geometry"] = to_multipolygon(bnd_df.geometry.values)
bnd_df.to_feather(out_dir / "region_boundary.feather")

bnd = bnd_df.loc[bnd_df.id == "total"].to_crs(CRS).geometry.values[0]
bnd_geo = bnd_df.loc[bnd_df.id == "total"].geometry.values[0]

################################################################################
### Extract HUC2 units that intersect boundaries
################################################################################
print("Extracting HUC2...")
huc2 = (
    read_dataframe(wbd_gdb, layer="WBDHU2", columns=["huc2", "name"], use_arrow=True)
    .to_crs(CRS)
    .rename(columns={"huc2": "HUC2"})
)

ix = np.unique(shapely.STRtree(huc2.geometry.values).query(states.geometry.values, predicate="intersects")[1])
huc2 = huc2.take(ix).sort_values(by="HUC2").reset_index(drop=True)

# drop holes within HUC2s (04, 19)
huc2 = huc2.explode(ignore_index=True)
huc2["geometry"] = shapely.polygons(shapely.get_exterior_ring(huc2.geometry.values))
huc2 = gp.GeoDataFrame(
    huc2.groupby("HUC2").agg({"name": "first", "geometry": shapely.multipolygons}),
    geometry="geometry",
    crs=huc2.crs,
).reset_index()

huc2.to_feather(out_dir / "huc2.feather")

################################################################################
### Use all HUC4s in these HUC2s except those only in Mexico
################################################################################
print("Extracting HUC4...")

# HUC4s in Mexico that are not available from NHD (HUC4s in Canada are available)
missing_huc4 = ["1310", "1311", "1312"]

huc4 = (
    read_dataframe(
        wbd_gdb,
        layer="WBDHU4",
        columns=["huc4"],
        where=f"SUBSTR(huc4, 0, 2) IN {tuple(huc2.HUC2)} AND huc4 not in {tuple(missing_huc4)}",
        use_arrow=True,
    )
    .rename(columns={"huc4": "HUC4"})
    .to_crs(CRS)
    .sort_values(by="HUC4")
    .reset_index(drop=True)
)
huc4["HUC2"] = huc4.HUC4.str[:2]

huc4.to_feather(out_dir / "huc4.feather")

################################################################################
### Extract HUC6-HUC2 within these HUC4
################################################################################
for huc_level in range(6, 13, 2):
    print(f"Processing HUC{huc_level}...")
    hucs = (
        read_dataframe(
            wbd_gdb,
            layer=f"WBDHU{huc_level}",
            columns=[f"huc{huc_level}", "name"],
            where=f"SUBSTR(huc{huc_level}, 0, 4) IN {tuple(huc4.HUC4)}",
            use_arrow=True,
        )
        .rename(columns={f"huc{huc_level}": f"HUC{huc_level}"})
        .to_crs(CRS)
        .sort_values(f"HUC{huc_level}")
        .reset_index(drop=True)
    )
    hucs.to_feather(out_dir / f"huc{huc_level}.feather")

    del hucs

del huc4

################################################################################
### Extract counties
################################################################################
print("Processing counties...")
counties = (
    read_dataframe(
        src_dir / "tl_2025_us_county.zip",
        columns=["NAMELSAD", "GEOID", "STATEFP"],
        where=f"STATEFP in {tuple(states.STATEFIPS)}",
        use_arrow=True,
    )
    .to_crs(CRS)
    .rename(columns={"NAMELSAD": "name", "GEOID": "COUNTYFIPS", "STATEFP": "STATEFIPS"})
    .sort_values(by="COUNTYFIPS")
    .reset_index(drop=True)
)
# use COUNTYFIPS as id
counties["id"] = counties.COUNTYFIPS.values
counties = counties.join(
    states.set_index("STATEFIPS")[["id", "name"]].rename(columns={"id": "state", "name": "state_name"}), on="STATEFIPS"
)

counties["geometry"] = to_multipolygon(counties.geometry.values)
counties.to_feather(out_dir / "counties.feather")
del counties


################################################################################
### Extract congressional districts
################################################################################
print("Processing congressional districts...")
cd = (
    gp.read_feather(src_dir / "congressional_districts.feather", columns=["geometry", "STATEFP", "CD119FP", "NAMELSAD"])
    .to_crs(CRS)
    .rename(columns={"STATEFP": "STATEFIPS", "CD119FP": "District", "NAMELSAD": "name"})
)
cd = cd.join(
    states.set_index("STATEFIPS")[["id", "name"]].rename(columns={"id": "state", "name": "state_name"}),
    on="STATEFIPS",
    how="inner",
).reset_index(drop=True)

cd["id"] = cd.state + cd.District
cd["geometry"] = to_multipolygon(cd.geometry.values)
cd.to_feather(out_dir / "congressional_districts.feather")
del cd


################################################################################
### Process Fish Habitat Partnership boundaries
################################################################################
# NOTE: these include overlapping areas
print("Extracting FHP boundaries")

fhp = (
    read_dataframe(
        src_dir / "FHP_2026.gdb",
        columns=["FHP_Name", "fhp_ab"],
        # intentionally drop SARP; we use SARP states below instead
        where="fhp_ab != 'SARP'",
        use_arrow=True,
    )
    .rename(columns={"FHP_Name": "name", "fhp_ab": "id"})
    .to_crs(CRS)
    .explode(ignore_index=True)
)

# only keep overlapping parts
fhp = fhp.take(shapely.STRtree(fhp.geometry.values).query(bnd, predicate="intersects"))

# drop small parts (islands)
fhp = fhp.loc[shapely.area(fhp.geometry.values) / 1e6 >= 1].reset_index(drop=True)

fhp["geometry"] = make_valid(fhp.geometry.values)
fhp = fhp.explode(ignore_index=True).explode(ignore_index=True)
fhp = dissolve(fhp.loc[fhp.geometry.type == "Polygon"], by="id", agg={"name": "first"})

# merge SARP states to create SARP boundary
fhp = pd.concat(
    [
        fhp,
        gp.GeoDataFrame(
            [{"id": "SARP", "name": "Southeast Aquatic Resources Partnership"}],
            geometry=[shapely.union_all(states.loc[states.id.isin(SARP_STATES)].geometry.values)],
            crs=CRS,
        ),
    ],
    ignore_index=True,
)
fhp.to_feather(out_dir / "fhp_boundary.feather")
del fhp


################################################################################
### State water resource areas (Washington State only)
################################################################################
wa_wria = (
    read_dataframe(src_dir / "WA_WRIA.gdb", columns=["WRIA_ID", "WRIA_NM", "geometry"], use_arrow=True)
    .to_crs(CRS)
    .rename(columns={"WRIA_ID": "id", "WRIA_NM": "name"})
)
wa_wria["id"] = "WA" + wa_wria.id.values.astype("str")
wa_wria["state"] = "WA"

# WA is only one for now
state_wra = wa_wria
state_wra.to_feather(out_dir / "state_water_resource_areas.feather")
del state_wra


################################################################################
### Compile all of analysis units above for use in the API
################################################################################
print("Compiling analysis units...")

### Regions
# NOTE: these are already in WGS84 and handle antimeridian correctly
region_geo_df = gp.read_feather(out_dir / "region_boundary.feather").to_crs(GEO_CRS)
region_geo_df = region_geo_df.loc[region_geo_df.id != "total"].copy()
region_geo_df["bbox"] = encode_bbox(region_geo_df.geometry.values)
region_geo_df["state"] = ""
region_geo_df["layer"] = "Region"
region_geo_df["priority"] = np.uint8(99)  # not used in search
region_geo_df["name"] = ""  # not used
region_geo_df["key"] = region_geo_df.id


### States
state_geo_df = (
    gp.read_feather(out_dir / "states.feather", columns=["geometry", "id", "name", "STATEFIPS"])
    .to_crs(GEO_CRS)
    .explode(ignore_index=True)
)
# unwrap Alaska around antimeridian
state_geo_df["geometry"] = unwrap_antimeridian(state_geo_df.geometry.values)
state_geo_df = gp.GeoDataFrame(
    state_geo_df.groupby("id")
    .agg(
        {"geometry": shapely.multipolygons, **{c: "first" for c in state_geo_df.columns if c not in {"geometry", "id"}}}
    )
    .reset_index(),
    geometry="geometry",
    crs=GEO_CRS,
)
state_geo_df["bbox"] = encode_bbox(state_geo_df.geometry.values)
state_geo_df["state"] = ""  # not used for these
state_geo_df["layer"] = "State"
state_geo_df["priority"] = np.uint8(1)
state_geo_df["key"] = state_geo_df["name"].str.lower()


### Counties
county_geo_df = (
    gp.read_feather(out_dir / "counties.feather", columns=["geometry", "state", "state_name", "id", "name"])
    .to_crs(GEO_CRS)
    .explode(ignore_index=True)
)
# Unwrap Alaska counties around antimeridian
county_geo_df["geometry"] = unwrap_antimeridian(county_geo_df.geometry.values)
county_geo_df = gp.GeoDataFrame(
    county_geo_df.groupby("id")
    .agg(
        {
            "geometry": shapely.multipolygons,
            **{c: "first" for c in county_geo_df.columns if c not in {"geometry", "id"}},
        }
    )
    .reset_index(),
    geometry="geometry",
    crs=GEO_CRS,
)
county_geo_df["name"] = county_geo_df["name"]
county_geo_df["bbox"] = encode_bbox(county_geo_df.geometry.values)
county_geo_df["layer"] = "County"
county_geo_df["priority"] = np.uint8(2)
county_geo_df["key"] = (county_geo_df["name"] + " " + county_geo_df.state_name).str.lower()


### Congressional districts
cd_geo_df = (
    gp.read_feather(out_dir / "congressional_districts.feather", columns=["geometry", "id", "name", "state"])
    .to_crs(GEO_CRS)
    .explode(ignore_index=True)
)
# Unwrap Alaska congressional around antimeridian
cd_geo_df["geometry"] = unwrap_antimeridian(cd_geo_df.geometry.values)
cd_geo_df = gp.GeoDataFrame(
    cd_geo_df.groupby("id")
    .agg(
        {
            "geometry": shapely.multipolygons,
            **{c: "first" for c in cd_geo_df.columns if c not in {"geometry", "id"}},
        }
    )
    .reset_index(),
    geometry="geometry",
    crs=GEO_CRS,
)
cd_geo_df["bbox"] = encode_bbox(cd_geo_df.geometry.values)
cd_geo_df["layer"] = "CongressionalDistrict"
cd_geo_df["priority"] = np.uint8(5)
cd_geo_df["key"] = (cd_geo_df.name + " " + cd_geo_df.id).str.lower()


### Water resource areas
state_wra_geo_df = gp.read_feather(
    out_dir / "state_water_resource_areas.feather", columns=["geometry", "id", "name", "state"]
).to_crs(GEO_CRS)
state_wra_geo_df["bbox"] = encode_bbox(state_wra_geo_df.geometry.values)
state_wra_geo_df["layer"] = "StateWRA"
state_wra_geo_df["priority"] = np.uint8(6)
# NOTE: trim state code from id
state_wra_geo_df["key"] = (state_wra_geo_df.name + " " + state_wra_geo_df.id.str[2:]).str.lower()
state_wra_geo_df["name"] = state_wra_geo_df["name"] + " (" + state_wra_geo_df.id.str[2:] + ")"


### Fish habitat partnerships
fhp_geo_df = (
    gp.read_feather(out_dir / "fhp_boundary.feather", columns=["geometry", "id", "name"])
    .to_crs(GEO_CRS)
    .explode(ignore_index=True)
)
# unwrap SEAK around antimeridian
fhp_geo_df["geometry"] = unwrap_antimeridian(fhp_geo_df.geometry.values)
fhp_geo_df = gp.GeoDataFrame(
    fhp_geo_df.groupby("id")
    .agg({"geometry": shapely.multipolygons, **{c: "first" for c in fhp_geo_df.columns if c not in {"geometry", "id"}}})
    .reset_index(),
    geometry="geometry",
    crs=GEO_CRS,
)
fhp_geo_df["bbox"] = encode_bbox(fhp_geo_df.geometry.values)
fhp_geo_df["state"] = ""  # not used
fhp_geo_df["layer"] = "FishHabitatPartnership"
fhp_geo_df["priority"] = np.uint8(99)  # not used in search
fhp_geo_df["key"] = fhp_geo_df["name"].str.lower()

### Compile HUC levels (intentionally skipping HUC4)
huc_geo_df = None
for i, unit in enumerate(["HUC2", "HUC6", "HUC8", "HUC10", "HUC12"]):
    df = (
        gp.read_feather(out_dir / f"{unit.lower()}.feather")
        .rename(columns={unit: "id"})
        .to_crs(GEO_CRS)
        .explode(ignore_index=True)
    )
    # unwrap any of the Alaska units around the antimeridian
    df["geometry"] = unwrap_antimeridian(df.geometry.values)

    df = gp.GeoDataFrame(
        df.groupby("id")
        .agg(
            {
                "geometry": shapely.multipolygons,
                **{c: "first" for c in df.columns if c not in {"geometry", "id"}},
            }
        )
        .reset_index(),
        geometry="geometry",
        crs=GEO_CRS,
    )

    df["bbox"] = encode_bbox(df.geometry.values)
    df["layer"] = unit
    df["priority"] = np.uint8(i + 2)

    # only keep those that overlap the boundary
    df = df.take(shapely.STRtree(df.geometry.values).query(bnd_geo, predicate="intersects"))

    # spatially join to states
    left, right = shapely.STRtree(state_geo_df.geometry.values).query(df.geometry.values, predicate="intersects")
    unit_states = (
        pd.DataFrame(
            {
                "id": df.id.values.take(left),
                "state": state_geo_df.id.values.take(right),
                "state_name": state_geo_df.name.values.take(right),
            }
        )
        .groupby("id")
        .agg({"state": "unique", "state_name": "unique"})
    )
    unit_states["state"] = unit_states.state.apply(sorted).apply(",".join)
    unit_states["state_name"] = unit_states.state_name.apply(sorted).apply(",".join)

    df = df.join(unit_states, on="id")
    df["state"] = df.state.fillna("")
    df["state_name"] = df.state_name.fillna("")
    df["key"] = df.id.str.lower()
    ix = df.id != df.name
    df.loc[ix, "key"] += " " + df.loc[ix].name.str.lower()
    df["key"] += " " + df.state_name.str.lower()

    df = df[["layer", "priority", "id", "state", "name", "key", "bbox"]]

    if huc_geo_df is None:
        huc_geo_df = df
    else:
        huc_geo_df = pd.concat([huc_geo_df, df], sort=False, ignore_index=True)


### Combine all
out = pd.concat(
    [
        state_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
        county_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
        cd_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
        fhp_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
        region_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
        state_wra_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
        huc_geo_df,
    ],
    sort=False,
    ignore_index=True,
)

out.reset_index(drop=True).to_feather(out_dir / "map_units.feather")
