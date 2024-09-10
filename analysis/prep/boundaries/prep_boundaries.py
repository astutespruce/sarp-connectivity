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
)
from analysis.lib.geometry import dissolve, to_multipolygon, make_valid
from analysis.lib.geometry.polygons import unwrap_antimeridian
from analysis.lib.util import append
from api.constants import FISH_HABITAT_PARTNERSHIPS

warnings.filterwarnings("ignore", message=".*more than 100 parts.*")


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
huc4_df = gp.read_feather(out_dir / "huc4.feather")

# state outer boundaries, NOT analysis boundaries
# (region boundary is in WGS84)
bnd_df = gp.read_feather(out_dir / "region_boundary.feather").to_crs(CRS)
bnd = bnd_df.loc[bnd_df.id == "total"].geometry.values[0]
bnd_geo = bnd_df.loc[bnd_df.id == "total"].to_crs(GEO_CRS).geometry.values[0]

state_df = gp.read_feather(out_dir / "region_states.feather", columns=["STATEFIPS", "geometry", "id"])

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


### Extract bounds and names for unit search in user interface
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
        fhp_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
        region_geo_df[["layer", "priority", "id", "state", "name", "key", "bbox"]],
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

### Protected areas / land ownership
print("Extracting land ownership & protection information (will take a while)...")

# Extract USFS parcel ownership boundaries (highest priority)
gdb = src_dir / "Surface_Ownership_Parcels/Surface_Ownership_Parcels%2C_detailed_(Feature_Layer).shp"
usfs_ownership = read_dataframe(
    gdb, columns=["OWNERCLASS"], where=""" "OWNERCLASS" = 'USDA FOREST SERVICE' """, use_arrow=True
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

# NOTE: sometimes areas marked as designation are stacked within a protected area (e.g., wilderness area within NPS)
# but other times they are not, so we have to keep them all

# select those that are within the boundary
df = df.take(shapely.STRtree(df.geometry.values).query(bnd, predicate="intersects"))

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

# drop proclamation boundaries but retain military lands that only
# show up as proclamation
# drop duplicates (there are some)
df = (
    df.loc[(df.Category != "Proclamation") | (df.Des_Tp == "MIL")]
    .drop(columns=["Category", "Own_Type", "Own_Name", "Des_Tp"])
    .drop_duplicates()
)

df["sort"] = 2


# this takes a while...
print("Making geometries valid, this might take a while")
df["geometry"] = make_valid(df.geometry.values)


# Extract Hawaii reserves
hifr = read_dataframe(
    src_dir / "HI_Reserves",
    #   columns=["managedby"],
    use_arrow=True,
).to_crs(CRS)
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

hifr["sort"] = 3


# Merge all types
df = pd.concat([usfs_ownership, df, hifr[["geometry", "otype"]]], ignore_index=True).explode(ignore_index=True)

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


### Priority layers

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

df = append(sarp_coa, hi_gfa).explode(ignore_index=True)
df = dissolve(df.explode(ignore_index=True), by=["type", "name"])
df.to_feather(out_dir / "priority_areas.feather")

### Environmental justice disadvantaged communities
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


### Process native territories
df = (
    read_dataframe(src_dir / "indigenousTerritories.json", columns=["Name"], use_arrow=True)
    .rename(columns={"Name": "name"})
    .to_crs(CRS)
)
df["geometry"] = shapely.force_2d(df.geometry.values)
df["geometry"] = make_valid(df.geometry.values)
tree = shapely.STRtree(df.geometry.values)
df = df.take(tree.query(bnd, predicate="intersects")).explode(ignore_index=True)
df.to_feather(out_dir / "native_territories.feather")
