"""
Create files for each of the input boundaries, in the same projection
as barriers (EPSG:102003 - CONUS Albers).

Note: output shapefiles for creating tilesets are limited to only those areas that overlap
the SARP states boundary.
"""

from pathlib import Path
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
import shapely
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import (
    CRS,
    GEO_CRS,
    OWNERTYPE_TO_DOMAIN,
    OWNERTYPE_TO_PUBLIC_LAND,
    STATES,
    FHP_LAYER_TO_CODE,
    SARP_STATES,
    TU_BROOK_TROUT_PORTFOLIO_TO_DOMAIN,
)
from analysis.lib.geometry import dissolve, to_multipolygon, make_valid
from analysis.lib.geometry.polygons import unwrap_antimeridian
from analysis.lib.util import append
from api.constants import FISH_HABITAT_PARTNERSHIPS

warnings.filterwarnings("ignore", message=".*more than 100 parts.*")

WSR_BUFFER_SIZE = 250  # meters, abitrary


def encode_bbox(geometries):
    return np.apply_along_axis(
        lambda bbox: ",".join([str(v) for v in bbox]),
        arr=shapely.bounds(geometries).round(3).tolist(),
        axis=1,
    )


data_dir = Path("data")
out_dir = data_dir / "boundaries"
src_dir = out_dir / "source"

county_filename = src_dir / "tl_2023_us_county.zip"
huc2s = sorted(pd.read_feather(out_dir / "huc2.feather", columns=["HUC2"]).HUC2.values)
huc4_df = gp.read_feather(out_dir / "huc4.feather")

# state outer boundaries, NOT analysis boundaries
# (region boundary is in WGS84)
bnd_df = gp.read_feather(out_dir / "region_boundary.feather").to_crs(CRS)
bnd = bnd_df.loc[bnd_df.id == "total"].geometry.values[0]
bnd_geo = bnd_df.loc[bnd_df.id == "total"].to_crs(GEO_CRS).geometry.values[0]

state_df = gp.read_feather(out_dir / "region_states.feather", columns=["STATEFIPS", "State", "geometry", "id"])

### Counties - within HUC4 bounds
print("Processing counties")
state_fips = sorted(state_df.STATEFIPS.unique())

county_df = (
    read_dataframe(county_filename, columns=["NAME", "GEOID", "STATEFP"], use_arrow=True)
    .to_crs(CRS)
    .rename(columns={"NAME": "County", "GEOID": "COUNTYFIPS", "STATEFP": "STATEFIPS"})
)

# keep only those within the region HUC4 outer boundary
tree = shapely.STRtree(county_df.geometry.values)
ix = np.unique(tree.query(huc4_df.geometry.values, predicate="intersects")[1])
ix.sort()
county_df = county_df.iloc[ix].reset_index(drop=True)
county_df.geometry = to_multipolygon(shapely.make_valid(county_df.geometry.values))

# keep larger set for spatial joins
county_df.to_feather(out_dir / "counties.feather")
write_dataframe(county_df, out_dir / "counties.fgb")

# Subset these in the region for tiles and summary stats
county_df.loc[county_df.STATEFIPS.isin(state_fips)].rename(columns={"COUNTYFIPS": "id", "County": "name"}).to_feather(
    out_dir / "region_counties.feather"
)

### Congressional districts for above states
print("Processing congressional districts")
district_df = gp.read_feather(src_dir / "congressional_districts.feather")

# keep only those within the region HUC4 outer boundary
tree = shapely.STRtree(district_df.geometry.values)
district_df = district_df.take(np.unique(tree.query(huc4_df.geometry.values, predicate="intersects")[1])).reset_index(
    drop=True
)
district_df.geometry = to_multipolygon(shapely.make_valid(district_df.geometry.values))

# keep larger set for spatial joins
district_df.to_feather(out_dir / "congressional_districts.feather")
write_dataframe(district_df, out_dir / "congressional_districts.fgb")

# Subset these to the states in the analysis
district_df.loc[district_df.STATEFIPS.isin(state_fips)].to_feather(out_dir / "region_congressional_districts.feather")

### Process Fish Habitat Partnership boundaries
# NOTE: these include overlapping areas
print("Extracting FHP boundaries")
merged = None
for layer, code in FHP_LAYER_TO_CODE.items():
    print(f"Extracting {layer}")

    columns = []
    if layer == "FHP_SEAK_Boundary_2013":
        columns = ["TYPE"]

    df = (
        read_dataframe(src_dir / "FHP_Official_Boundaries_2013.gdb", layer=layer, columns=columns, use_arrow=True)
        .to_crs(CRS)
        .explode(ignore_index=True)
    )

    ix = shapely.STRtree(df.geometry.values).query(bnd, predicate="intersects")
    df = df.take(ix)

    # drop small parts (islands)
    df = df.loc[shapely.area(df.geometry.values) / 1e6 >= 1].reset_index(drop=True)

    df["id"] = code

    if layer == "FHP_SEAK_Boundary_2013":
        # SE AK is crazy complex because of coastline and needs to be simplified to drop the small islands
        # only extract outer boundary, dissolve land and water parts, and then extract outer boundary again
        df["geometry"] = shapely.polygons(shapely.get_exterior_ring(df.geometry.values))
        df = dissolve(df, by="id").explode(ignore_index=True)
        df["geometry"] = shapely.polygons(shapely.get_exterior_ring(df.geometry.values))
        df = dissolve(df, by="id")

    else:
        df["geometry"] = make_valid(df.geometry.values)
        df = df.explode(ignore_index=True).explode(ignore_index=True)
        df = dissolve(df.loc[shapely.get_type_id(df.geometry.values) == 3], by="id")

    df["name"] = FISH_HABITAT_PARTNERSHIPS[code]

    merged = append(merged, df[["geometry", "id", "name"]])

fhp = merged

# merge SARP states to create SARP boundary
fhp = pd.concat(
    [
        fhp,
        gp.GeoDataFrame(
            [{"id": "SARP", "name": "Southeast Aquatic Resources Partnership"}],
            geometry=[shapely.union_all(state_df.loc[state_df.id.isin(SARP_STATES)].geometry.values)],
            crs=CRS,
        ),
    ],
    ignore_index=True,
)
fhp.to_feather(out_dir / "fhp_boundary.feather")
write_dataframe(fhp, out_dir / "fhp_boundary.fgb")


### State water resource areas
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
write_dataframe(state_wra, out_dir / "state_water_resource_areas.fgb")


################################################################################
### Extract bounds and names for unit search in user interface
################################################################################
print("Projecting geometries to geographic coordinates for search index")

print("Processing regions")
# NOTE: these already handle antimeridian correctly
region_geo_df = gp.read_feather(out_dir / "region_boundary.feather").to_crs(GEO_CRS)
region_geo_df = region_geo_df.loc[region_geo_df.id != "total"].copy()
region_geo_df["bbox"] = encode_bbox(region_geo_df.geometry.values)
region_geo_df["in_region"] = True
region_geo_df["state"] = ""
region_geo_df["layer"] = "Region"
region_geo_df["priority"] = np.uint8(99)  # not used in search
region_geo_df["name"] = ""  # not used
region_geo_df["key"] = region_geo_df.id

print("Processing state and county")
state_geo_df = (
    gp.read_feather(out_dir / "states.feather", columns=["geometry", "id", "State", "STATEFIPS"])
    .rename(columns={"State": "name"})
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
    crs=df.crs,
)
state_geo_df["bbox"] = encode_bbox(state_geo_df.geometry.values)
state_geo_df["in_region"] = state_geo_df.id.isin(STATES)
state_geo_df["state"] = ""  # state_geo_df.id
state_geo_df["layer"] = "State"
state_geo_df["priority"] = np.uint8(1)
state_geo_df["key"] = state_geo_df["name"]

# Unwrap Alaska counties around antimeridian
county_geo_df = (
    county_df.loc[county_df.STATEFIPS.isin(state_fips)]
    .rename(columns={"COUNTYFIPS": "id", "County": "name"})
    .join(state_df.set_index("STATEFIPS").id.rename("state"), on="STATEFIPS")
    .to_crs(GEO_CRS)
    .join(state_geo_df.set_index("STATEFIPS").name.rename("state_name"), on="STATEFIPS")
    .explode(ignore_index=True)
)
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
    crs=df.crs,
)
county_geo_df["name"] = county_geo_df["name"] + " County"
county_geo_df["bbox"] = encode_bbox(county_geo_df.geometry.values)
county_geo_df["layer"] = "County"
county_geo_df["priority"] = np.uint8(2)
county_geo_df["key"] = county_geo_df["name"] + " " + county_geo_df.state_name


print("Processing congressional districts")
# Unwrap Alaska congressional around antimeridian
district_geo_df = district_df.loc[district_df.STATEFIPS.isin(state_fips)].to_crs(GEO_CRS).explode(ignore_index=True)
district_geo_df["geometry"] = unwrap_antimeridian(district_geo_df.geometry.values)
district_geo_df = gp.GeoDataFrame(
    district_geo_df.groupby("id")
    .agg(
        {
            "geometry": shapely.multipolygons,
            **{c: "first" for c in district_geo_df.columns if c not in {"geometry", "id"}},
        }
    )
    .reset_index(),
    geometry="geometry",
    crs=df.crs,
)
district_geo_df["bbox"] = encode_bbox(district_geo_df.geometry.values)
district_geo_df["layer"] = "CongressionalDistrict"
district_geo_df["priority"] = np.uint8(5)
district_geo_df["key"] = district_geo_df.name + " " + district_geo_df.id

print("Processing state water resource areas")
state_wra_geo_df = state_wra.to_crs(GEO_CRS).explode(ignore_index=True)
state_wra_geo_df["bbox"] = encode_bbox(state_wra_geo_df.geometry.values)
state_wra_geo_df["layer"] = "StateWRA"
state_wra_geo_df["priority"] = np.uint8(6)
# NOTE: trim state code from id
state_wra_geo_df["key"] = state_wra_geo_df.name + " " + state_wra_geo_df.id.str[2:]
state_wra_geo_df["name"] = state_wra_geo_df["name"] + " (" + state_wra_geo_df.id.str[2:] + ")"


print("Processing fish habitat partnerships")
fhp_geo_df = fhp.to_crs(GEO_CRS).explode(ignore_index=True)
fhp_geo_df["geometry"] = unwrap_antimeridian(fhp_geo_df.geometry.values)
fhp_geo_df = gp.GeoDataFrame(
    fhp_geo_df.groupby("id")
    .agg({"geometry": shapely.multipolygons, **{c: "first" for c in fhp_geo_df.columns if c not in {"geometry", "id"}}})
    .reset_index(),
    geometry="geometry",
    crs=df.crs,
)
fhp_geo_df["bbox"] = encode_bbox(fhp_geo_df.geometry.values)
fhp_geo_df["in_region"] = True
fhp_geo_df["state"] = ""  # not used
fhp_geo_df["layer"] = "FishHabitatPartnership"
fhp_geo_df["priority"] = np.uint8(99)  # not used in search
fhp_geo_df["key"] = fhp_geo_df["name"]


out = pd.concat(
    [
        state_geo_df.loc[state_geo_df.in_region][["layer", "priority", "id", "state", "name", "key", "bbox"]],
        county_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
        district_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
        fhp_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
        region_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
        state_wra_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
    ],
    sort=False,
    ignore_index=True,
)

for i, unit in enumerate(["HUC2", "HUC6", "HUC8", "HUC10", "HUC12"]):
    print(f"Processing {unit}")
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
        crs=df.crs,
    )

    df["bbox"] = encode_bbox(df.geometry.values)
    df["layer"] = unit
    df["priority"] = np.uint8(i + 2)

    # only keep those that overlap the boundary
    tree = shapely.STRtree(df.geometry.values)
    ix = tree.query(bnd_geo, predicate="intersects")
    df = df.loc[ix]

    # spatially join to states
    tree = shapely.STRtree(state_geo_df.geometry.values)
    left, right = tree.query(df.geometry.values, predicate="intersects")
    unit_states = (
        pd.DataFrame(
            {
                "id": df.id.values.take(left),
                "state": state_geo_df.id.values.take(right),
            }
        )
        .groupby("id")["state"]
        .unique()
        .apply(sorted)
    )

    df = df.join(unit_states, on="id")
    df["state"] = df.state.fillna("").apply(lambda x: ",".join(x))
    df["key"] = df.name + " " + df.id

    out = pd.concat(
        [out, df[["layer", "priority", "id", "state", "name", "key", "bbox"]]],
        sort=False,
        ignore_index=True,
    )

out.reset_index(drop=True).to_feather(out_dir / "unit_bounds.feather")

################################################################################
### Protected areas / land ownership
################################################################################
print("Extracting land ownership & protection information (will take a while)...")

# Extract USFS parcel ownership boundaries (highest priority)
usfs_ownership = read_dataframe(
    src_dir / "USFS_Ownership_Parcels/Surface_Ownership_Parcels%2C_detailed_(Feature_Layer).shp",
    columns=["OWNERCLASS"],
    where=""" "OWNERCLASS" = 'USDA FOREST SERVICE' """,
    use_arrow=True,
).to_crs(CRS)
usfs_ownership["geometry"] = make_valid(usfs_ownership.geometry.values)
usfs_ownership = (
    dissolve(usfs_ownership.explode(ignore_index=True), by="OWNERCLASS", grid_size=1e-3)
    .drop(columns=["OWNERCLASS"])
    .explode(ignore_index=True)
)
usfs_ownership["otype"] = "USDA Forest Service (ownership boundary)"
usfs_ownership["owner"] = usfs_ownership.otype.values
# assign highest priorioty
usfs_ownership["sort"] = 1

# Extract USFS admin boundaries (next highest priority)
usfs_admin = read_dataframe(
    src_dir / "USFS_Admin_Boundaries/Forest_Administrative_Boundaries_(Feature_Layer).shp", columns=[], use_arrow=True
).to_crs(CRS)
usfs_admin["otype"] = "USDA Forest Service (admin boundary)"
usfs_admin["geometry"] = make_valid(usfs_admin.geometry.values)
usfs_admin = dissolve(usfs_admin.explode(ignore_index=True), by="otype", grid_size=1e-3).explode(ignore_index=True)
usfs_admin["owner"] = usfs_admin.otype.values
usfs_admin["sort"] = 2


# Extract protected areas
df = read_dataframe(
    src_dir / "pad_us4.0.gpkg",
    layer="PADUS4_0Combined_Proclamation_Marine_Fee_Designation_Easement",
    columns=[
        "Category",
        "Own_Type",
        "Own_Name",
        "Des_Tp",
    ],
    # drop marine, unknown / private owner (not useful), UNK (not useful)
    where="Category != 'Marine' AND Own_Type NOT IN ('PVT', 'UNK') AND Own_Name NOT IN ('UNK')",
    use_arrow=True,
).to_crs(CRS)
df["sort"] = 3

# select those that are within the boundary
df = df.take(shapely.STRtree(df.geometry.values).query(bnd, predicate="intersects"))

# extract wilderness to a separate layer for filtering
# NOTE: these are dropped from protected areas because they are Own_Type == 'DESG'
wilderness = df.loc[df.Des_Tp == "WA"].copy()
wilderness["geometry"] = make_valid(wilderness.geometry.values)
wilderness = (
    dissolve(wilderness.explode(ignore_index=True), by="Des_Tp").explode(ignore_index=True).drop(columns=["Des_Tp"])
)
wilderness.to_feather(out_dir / "wilderness.feather")

# remove all USFS areas; they are handled above via specific USFS layers
df = df.loc[df.Own_Name != "USFS"].copy()

df["otype"] = df.Own_Name.map(
    {
        "BLM": "Bureau of Land Management",
        "CITY": "Local Land",
        "CNTY": "Local Land",
        "DOD": "Department of Defense",
        "DOE": "Federal Land",
        "FWS": "US Fish and Wildlife Service",
        "JNT": "Joint Ownership",
        "NGO": "NGO",
        "NPS": "National Park Service",
        "NRCS": "Federal Land",
        "OTHF": "Federal Land",
        "OTHS": "State Land",
        "PVT": "Private Conservation Land",
        "REG": "Regional Agency Special Distribution",
        "RWD": "Regional Agency Special Distribution",
        "SDC": "State Land",
        "SDNR": "State Land",
        "SDOL": "State Land",
        "SFW": "State Land",
        "SLB": "State Land",
        "SPR": "State Land",
        "TRIB": "Native American Land",
        "TVA": "Regional Agency Special Distribution",
        "UNKL": "Local Land",
        "USACE": "Department of Defense",
        "USBR": "Bureau of Reclamation",
        "USFS": "USDA Forest Service (admin boundary)",
        "VI": "State Land",
    }
)

# drop proclamation boundaries but retain military lands that only show up as
# proclamation
# NOTE: this specifically drops designation types (Own_Type=="DESG") that are used
# for things like wilderness and wild & scenic river corridors, because they are
# either contained in other boundaries (e.g., wilderness) or not necessarily indicative
# of ownership (e.g., wild & scenic river corridors)
# drop duplicates (there are some)
df = (
    df.loc[(df.Category != "Proclamation") | (df.Des_Tp == "MIL") & (df.Own_Type != "DESG")]
    .drop(columns=["Category", "Own_Type", "Own_Name", "Des_Tp"])
    .drop_duplicates()
)

# this takes a while...
print("Making geometries valid, this might take a while")
df["geometry"] = make_valid(df.geometry.values)


# Extract Hawaii reserves
hifr = read_dataframe(src_dir / "HI_Reserves", use_arrow=True).to_crs(CRS)
hifr = hifr.take(shapely.STRtree(hifr.geometry.values).query(bnd, predicate="intersects")).reset_index(drop=True)

# drop any already completely contained by others
ix = np.unique(shapely.STRtree(hifr.geometry.values).query(df.geometry.values, predicate="contains_properly")[1])
hifr = hifr.loc[~hifr.index.isin(ix)].reset_index(drop=True)
hifr["otype"] = hifr.managedby.map(
    {
        "(DOFAW)": "State Land",
        "City and County of Honolulu/Private": "Local Land",
        "DOAR": "State Land",
        "DOFAW": "State Land",
        "DOFAW/DOSP": "State Land",
        "DOFAW/Private": "State Land",
        "DOFAW/US Army": "Department of Defense",
        "DOFAW/US Military": "Department of Defense",
        "DOFAW/USNPS": "National Park Service",
        "DOSP": "State Land",
        "Daughters of Hawaii/DOSP": "State Land",
        "Hawaiian Islands Land Trust": "NGO",
        "Historic Preservation Division": "State Land",
        "KIRC": "State Land",
        "Keehi Memorial Org./DOSP": "State Land",
        "MOPEPP": "Local Land",
        "Maui County": "Local Land",
        "Maui Land and Pineapple Co.": "NGO",
        "Molokai Land Trust": "NGO",
        "National Audubon Society": "NGO",
        "OHA/DOFAW": "State Land",
        # "Private": "", # Hulu Islet Seabird Sanctuary, unclear ownership
        "TNC": "NGO",
        "US Army": "Department of Defense",
        "US Army/DOFAW": "Department of Defense",
        "USFWS": "US Fish and Wildlife Service",
        "USNPS": "National Park Service",
    }
)
hifr = hifr.dropna(subset="otype")

hifr["sort"] = 4


# Merge all types
df = pd.concat([usfs_ownership, usfs_admin, df, hifr[["geometry", "otype"]]], ignore_index=True).explode(
    ignore_index=True
)

t = shapely.get_type_id(df.geometry.values)
df = df.loc[(t == 3) | (t == 6)].reset_index(drop=True)

# sort on 'sort' so that later when we do spatial joins and get multiple hits, we take the ones with
# the lowest sort value (1 = highest priority) first.
df.sort = df.sort.fillna(255).astype("uint8")  # missing values should sort to bottom
df = df.sort_values(by="sort").drop(columns=["sort"])

# convert to int groups
df["OwnerType"] = df.otype.map(OWNERTYPE_TO_DOMAIN)
# drop all that didn't get matched
# CAUTION: make sure the types we want are properly handled!
df = df.dropna(subset=["OwnerType"])
df.OwnerType = df.OwnerType.astype("uint8")

# Add in public status
df["ProtectedLand"] = df.OwnerType.map(OWNERTYPE_TO_PUBLIC_LAND).fillna(0).astype("bool")

# only save owner type and protected land status
df = df[["geometry", "OwnerType", "ProtectedLand"]].explode(ignore_index=True)
df.to_feather(out_dir / "protected_areas.feather")

################################################################################
### Wild & scenic rivers - combine corridors and buffers
################################################################################

# Extract wild & scenic river corridors (designated and eligible / suitable)
# from PAD-US
wsr_corridors = read_dataframe(
    src_dir / "pad_us4.0.gpkg",
    layer="PADUS4_0Combined_Proclamation_Marine_Fee_Designation_Easement",
    columns=["Des_Tp", "Loc_Ds"],
    where="Des_Tp = 'WSR'",
    use_arrow=True,
).to_crs(CRS)

wsr_corridors["geometry"] = make_valid(wsr_corridors.geometry.values)
# keep only the polygons (making valid makes some other things)
wsr_corridors = wsr_corridors.explode(ignore_index=True)
wsr_corridors = wsr_corridors.loc[wsr_corridors.type == "Polygon"].reset_index(drop=True)

# split out designated from eligible / suitable
ix = wsr_corridors.Loc_Ds.str.contains("Eligible") | wsr_corridors.Loc_Ds.str.contains("Suitable")

# designated corridors
wsr_des_cor = shapely.union_all(wsr_corridors.loc[~ix].geometry.values)
# eligible / suitable corridors
wsr_es_cor = shapely.union_all(wsr_corridors.loc[ix].geometry.values)

# buffer the designated and eligible / suitable Wild & Scenic River lines by 250m (arbitrary)
wsr_des_lines = read_dataframe(
    src_dir / "S_USA.WildScenicRiver_LN/S_USA.WildScenicRiver_LN.shp", columns=[], use_arrow=True
).to_crs(CRS)
wsr_des_buffers = shapely.union_all(shapely.buffer(wsr_des_lines.geometry.values, WSR_BUFFER_SIZE))

wsr_es_lines = gp.read_feather(src_dir / "wsr_eligible_suitable.feather").explode(ignore_index=True)
wsr_es_lines = wsr_es_lines.loc[
    (wsr_es_lines.eligible == "Yes")
    | (wsr_es_lines.suitable == "Yes")
    # status seems to be set even if individual fields are not
    | (wsr_es_lines.status.isin(["Eligible", "Suitable"]))
]
wsr_es_buffers = shapely.union_all(shapely.buffer(wsr_es_lines.geometry.values, WSR_BUFFER_SIZE))

# only keep eligible / suitable corridors outside designated corridors
# NOTE: BLM has several eligible / suitable that overlap with and extend beyond
# USFS designated corridors
wsr_es_cor = shapely.get_parts(shapely.difference(wsr_es_cor, wsr_des_cor))
# this yields several fragments, drop those
wsr_es_cor = shapely.multipolygons(wsr_es_cor[shapely.area(wsr_es_cor) > 100000])

# only keep the parts of the designated buffers outside all types of corridors
tmp = shapely.union(wsr_des_cor, wsr_es_cor)
wsr_des_buffers = shapely.difference(wsr_des_buffers, tmp)

# only keep the parts of the eligible / suitable buffers outside of all the above
tmp = shapely.union(tmp, wsr_des_buffers)
wsr_es_buffers = shapely.difference(wsr_es_buffers, tmp)

# combine corridors and buffers
wsr = gp.GeoDataFrame(
    {
        "geometry": [wsr_des_cor, wsr_es_cor, wsr_des_buffers, wsr_es_buffers],
        "wsr": np.array([1, 2, 3, 4], dtype="uint8"),
        "name": [
            "Designated Wild & Scenic River corridor",
            "Eligible / suitable Wild & Scenic River corridor",
            "Near designated Wild & Scenic River",
            "Near eligible / suitable Wild & Scenic River",
        ],
        "type": [
            "wsr_designated_corridor",
            "wsr_eligible_suitable_corridor",
            "wsr_designated_buffer",
            "wsr_eligible_suitable_buffer",
        ],
    },
    crs=CRS,
).explode(ignore_index=True)


# export for spatial joins
wsr.to_feather(out_dir / "wild_scenic_rivers.feather")


################################################################################
### Priority layers (OVERLAYS)
### NOTE: these are used only for overlay in the map and not for spatial joins
################################################################################

# Conservation opportunity areas (for now the only priority type) joined to HUC8
# 1 = COA
sarp_coa = (
    read_dataframe(
        src_dir / "Priority_Areas.gdb",
        layer="SARP_COA",
        where="""COA = 'Yes'""",
        columns=["HUC8_Name", "COA"],
        use_arrow=True,
    )
    .to_crs(CRS)
    .rename(columns={"HUC8_Name": "name"})
    .drop(columns=["COA"])
)
sarp_coa["type"] = "sarp_coa"

# bring in Hawaii FHP geographic focus areas and merge
merged = None
for filename in src_dir.glob("Hawaii FHP Focus Areas/*.shp"):
    name = (
        filename.stem.lower()
        .replace("_wgs84", "")
        .replace("_outline", "")
        .replace("_fixed", "")
        .replace("025mile", "")
        .replace("_", " ")
        .title()
        .strip()
    )

    if name == "Kahaluu To Hakipuu":
        # this is completely contained within Heeia To Hakipuu
        continue

    df = read_dataframe(filename, columns=[], use_arrow=True).to_crs(CRS)
    df["name"] = name
    merged = append(merged, df)

hi_gfa = merged.reset_index(drop=True)
hi_gfa["type"] = "hifhp_gfa"


# combine all 3 priority area types for display in maps
df = pd.concat([sarp_coa, hi_gfa, wsr[["geometry", "name", "type"]]], ignore_index=True).explode(ignore_index=True)
df = dissolve(df.explode(ignore_index=True), by=["type", "name"]).explode(ignore_index=True)
df.to_feather(out_dir / "priority_areas.feather")


################################################################################
### Environmental justice disadvantaged communities
################################################################################
print("Processing environmental justice areas")

# Process Census tracts for disadvantaged communities
df = read_dataframe(src_dir / "environmental_justice_tracts/usa.shp", columns=["SN_C"], use_arrow=True)
df = df.loc[df.geometry.notnull() & (df.SN_C == 1)].reset_index(drop=True)

# select areas that overlap HUC4s
tree = shapely.STRtree(df.geometry.values)
huc4_geo = huc4_df.to_crs(GEO_CRS)
ix = np.unique(tree.query(huc4_geo.geometry.values, predicate="intersects")[1])
df = df.take(ix).to_crs(CRS)

df = (
    dissolve(df.explode(ignore_index=True), by="SN_C")
    .drop(columns=["SN_C"])
    .explode(ignore_index=True)
    .reset_index(drop=True)
)
df.to_feather(out_dir / "environmental_justice_tracts.feather")
ej_tract = df

# process Tribal lands (all are considered disadvantaged)
df = read_dataframe(src_dir / "tl_2023_us_aiannh.zip", columns=[], use_arrow=True).to_crs(CRS)
tree = shapely.STRtree(df.geometry.values)
ix = np.unique(tree.query(huc4_df.geometry.values, predicate="intersects")[1])
df = df.take(ix)

df["group"] = 1
df = (
    dissolve(df.explode(ignore_index=True), by="group")
    .drop(columns=["group"])
    .explode(ignore_index=True)
    .reset_index(drop=True)
)
df.to_feather(out_dir / "tribal_lands.feather")
ej_tribal = df

### join to flowlines
print("Joining environmental justice areas to flowlines")
merged = None
for huc2 in huc2s:
    print(f"Processing {huc2}...")
    flowlines = gp.read_feather(
        data_dir / "nhd/raw/" / huc2 / "flowlines.feather", columns=["geometry", "HUC4", "NHDPlusID"]
    )
    flowlines["HUC2"] = flowlines.HUC4.str[:2]
    tree = shapely.STRtree(flowlines.geometry.values)
    # for speed and simplicity just use simple intersection and not check overlap
    # full intersection and overlap calculation takes a LONG time
    left, right = tree.query(ej_tract.geometry.values, predicate="intersects")
    ids = flowlines.NHDPlusID.values.take(np.unique(right))
    flowlines["EJTract"] = flowlines.NHDPlusID.isin(ids)

    left, right = tree.query(ej_tribal.geometry.values, predicate="intersects")
    ids = flowlines.NHDPlusID.values.take(np.unique(right))
    flowlines["EJTribal"] = flowlines.NHDPlusID.isin(ids)

    flowlines = flowlines.loc[flowlines.EJTract | flowlines.EJTribal, ["NHDPlusID", "HUC2", "EJTract", "EJTribal"]]

    if merged is None:
        merged = flowlines
    else:
        merged = pd.concat([merged, flowlines], ignore_index=True)

merged.to_feather(out_dir / "derived/environmental_justice_flowlines.feather")


################################################################################
### Process native territories
################################################################################
df = (
    read_dataframe(src_dir / "indigenousTerritories.json", columns=["Name"], use_arrow=True)
    .rename(columns={"Name": "name"})
    .to_crs(CRS)
)
df["geometry"] = shapely.force_2d(df.geometry.values)
df["geometry"] = make_valid(df.geometry.values)
tree = shapely.STRtree(df.geometry.values)
df = df.take(tree.query(bnd, predicate="intersects")).explode(ignore_index=True)

# Fix names that can't be rendered properly in react-pdf; stripping the unrenderable
# names is the lesser evil that rendering them totally wrong.

# To find those with non-Ascii characters:
# names = [n for n in sorted(df.name.unique()) if re.search("[^a-zA-Z -\'’()]", n)]

replacements = {
    "Anishinabewaki ᐊᓂᔑᓈᐯᐗᑭ": "Anishinabewaki",
    "Báxoje Máyaⁿ (Ioway)": "Ioway",
    "Chikashsha I̠yaakni’ (Chickasaw)": "Chickasaw",
    "Dena’ina Ełnena": "Dena’ina",
    "Hoocąk (Ho-Chunk)": "Ho-Chunk",
    "Inuit Nunangat ᐃᓄᐃᑦ ᓄᓇᖓᑦ": "Inuit Nunangat",
    "Jíwere–Ñút’achi Máyaⁿ (Otoe-Missouria [Oklahoma])": "Otoe-Missouria (Oklahoma)",
    "Kanienʼkehá꞉ka (Mohawk)": "Mohawk",
    "Ktunaxa ɁamakɁis": "Ktunaxa",
    "La̱xyuubm Ts’msyen (Tsimshian)": "Tsimshian",
    "Meškwahki·aša·hina (Fox)": "Fox",
    "Mánu: Yį Įsuwą (Catawba)": "Catawba",
    "Ndee/Nnēē: (Western Apache)": "Western Apache",
    "Ndé Kónitsąąíí Gokíyaa (Lipan Apache)": "Lipan Apache",
    "Niitsítpiis-stahkoii ᖹᐟᒧᐧᐨᑯᐧ ᓴᐦᖾᐟ (Blackfoot / Niitsítapi ᖹᐟᒧᐧᒣᑯ)": "Blackfoot",
    "Nisg̱a’a": "Nisga’a",
    "Núu-agha-tʉvʉ-pʉ̱ (Ute)": "Ute",
    "Nā moku ʻehā": "Na moku eha",
    "Nłeʔkepmx Tmíxʷ (Nlaka’pamux)": "Nlaka’pamux",
    "Nʉmʉnʉʉ Sookobitʉ (Comanche)": "Comanche",
    "O-ga-xpa Ma-zhoⁿ (O-ga-xpa) (Quapaw)": "O-ga-xpa (Quapaw)",
    "Odǫhwęja:deˀ (Cayuga)": "Cayuga",
    "Oma͞eqnomenew-ahkew (Menominee)": "Menominee",
    "Onʌyote’a•ka (Oneida)": "Oneida",
    "Očhéthi Šakówiŋ": "Oceti Sakowin",
    "O’odham Jeweḍ": "O’odham",
    "Páⁿka tóⁿde ukʰéthiⁿ (Ponca)": "Ponca",
    "Qʷidiččaʔa•tx̌ (Makah)": "Makah",
    "Sq’ʷayáiɬaqtmš (Chehalis)": "Chehalis",
    "S’ólh Téméxw (Stó:lō)": "S'olh Temexw",
    "Tāłtān Konelīne (Tahltan)": "Talhtan",
    "Umoⁿhoⁿ (Omaha)": "Omaha",
    "Washtáge Moⁿzháⁿ (Kaw / Kansa)": "Kaw / Kansa",
    "Wašišiw Ɂítdeʔ (Washoe)": "Washoe",
    "Wintʰu• Po•m (Northern Wintu)": "Northern Wintu",
    "Xawiƚƚ kwñchawaay (Cocopah)": "Cocopah",
    "bəqəlšuɬ (Muckleshoot)": "Muckleshoot",
    "dxʷdəwʔabš (Duwamish)": "Duwamish",
    "dxʷlilap (Tulalip)": "Tulalip",
    "dxʷsqʷaliʔabš (Nisqually)": "Nisqually",
    "dxʷsəq̓ʷəbš (Suquamish)": "Suquamish",
    "np̓əšqʷáw̓səxʷ (Wenatchi)": "Wenatchi",
    "nspiləm (Nespelem)": "Nespelem",
    "oθaakiiwaki‧hina‧ki (Sauk)": "Sauk",
    "oθaakiiwaki‧hina‧ki (Sauk) & Meškwahki·aša·hina (Fox)": "Sauk & Fox",
    "saʔqʷəbixʷ-suyaƛ̕bixʷ (Sauk Suiattle)": "Sauk Suiattle",
    "sc̓əwaθenaɁɬ təməxʷ (Tsawwassen)": "Tsawwassen",
    "sduhubš (Snohomish)": "Snohomish",
    "sdukʷalbixʷ (Snoqualmie)": "Snoqualmie",
    "snʕickstx tmxʷúlaʔxʷ (Sinixt)": "Sinixt",
    "spuyaləpabš (Puyallup)": "Puyallup",
    "sp̓aƛ̓mul̓əxʷəxʷ (Methow)": "Methow",
    "sqaǰətabš (Upper Skagit)": "Upper Skagit",
    "sqʷax̌sədabš (Squaxin)": "Squaxin",
    "stuləgʷábš (Stillaguamish)": "Stillaguamish",
    "swədəbš (Swinomish)": "Swinomish",
    "sx̌ʷyʔiɬp (Colville)": "Colville",
    "sńpʕawílx (Sanpoil)": "Sanpoil",
    "ščəl’ámxəxʷ (Chelan)": "Chelan",
    "škwáxčənəxʷ (Moses-Columbia)": "Moses-Columbia",
    "šntiyátkʷəxʷ (Entiat)": "Entiat",
    "Á,LEṈENEȻ ȽTE (W̱SÁNEĆ)": "Saanich",
    "Ĩyãħé Nakón mąkóce (Stoney)": "Stoney",
    "Ɂívil̃uwenetem Meytémak (Cahuilla)": "Cahuilla",
    "ᏣᎳᎫᏪᏘᏱ Tsalaguwetiyi (Cherokee, East)": "Eastern Cherokee",
    "ᓀᐦᐃᔭᐤ ᐊᐢᑭᕀ Nêhiyaw-Askiy (Plains Cree)": "Plains Cree",
    "𐓏𐒰𐓓𐒰𐓓𐒷  𐒼𐓂𐓊𐒻  𐓆𐒻𐒿𐒷  𐓀𐒰^𐓓𐒰^(Osage)": "Osage",
}

ix = df.name.isin(replacements.keys())
df.loc[ix, "name"] = df.loc[ix].name.map(replacements)

df.to_feather(out_dir / "native_territories.feather")


################################################################################
### Process Trout Unlimited Eastern Brook Trout Conservation Portfolio
################################################################################
print("Processing Trout Unlimited Eastern Brook Trout Conservation Portfolio")
df = (
    read_dataframe(src_dir / "TU_MostRecentBrookTroutPortfolio.gdb", use_arrow=True, columns=["Portfolio_category"])
    .to_crs(CRS)
    .rename(columns={"Portfolio_category": "category"})
)
df = df.loc[~df.category.isin(["Not a brook trout population", "No brook trout"])].copy()
df["geometry"] = make_valid(shapely.force_2d(df.geometry.values))
df["category"] = df.category.map(TU_BROOK_TROUT_PORTFOLIO_TO_DOMAIN).astype("uint8")
df = dissolve(df.explode(ignore_index=True), by="category", grid_size=1e-3).explode(ignore_index=True)

df.to_feather(out_dir / "brook_trout_portfolio.feather")
