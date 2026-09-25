"""
Create files for each of the input boundaries, in the same projection
as barriers (EPSG:102003 - CONUS Albers).

Note: output shapefiles for creating tilesets are limited to only those areas that overlap
the SARP states boundary.
"""

import warnings
from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
import shapely
from pyogrio import read_dataframe

from analysis.constants import (
    CRS,
    GEO_CRS,
    OWNERTYPE_TO_DOMAIN,
    OWNERTYPE_TO_PUBLIC_LAND,
    TU_BROOK_TROUT_PORTFOLIO_TO_DOMAIN,
)
from analysis.lib.geometry import dissolve, make_valid
from analysis.lib.util import append

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

huc2s = pd.read_feather(out_dir / "huc2.feather", columns=["HUC2"]).HUC2.tolist()
huc4_df = gp.read_feather(out_dir / "huc4.feather")
bnd_df = gp.read_feather(out_dir / "region_boundary.feather")
bnd_geo = bnd_df.loc[bnd_df.id == "total"].geometry.values[0]
bnd = bnd_df.loc[bnd_df.id == "total"].to_crs(CRS).geometry.values[0]


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
    src_dir / "pad_us4.1.gpkg",
    layer="PADUS4_1Combined_Proclamation_Marine_Fee_Designation_Easement",
    columns=["Category", "Own_Type", "Own_Name", "Des_Tp", "Mang_Type", "Mang_Name", "Loc_Ds"],
    use_arrow=True,
).to_crs(CRS)
df["sort"] = 3

# drop marine areas; we don't use them here
df = df.loc[df.Category != "Marine"].copy()

# correctly mark DOD proclamation lands
ix = (df.Category == "Proclamation") & (df.Des_Tp == "MIL")
df.loc[ix, "Own_Type"] = "FED"
df.loc[ix, "Own_Name"] = "DOD"

# mark easements to keep separate from other private conservation lands
ix = df.Category == "Easement"
df.loc[ix, "Own_Type"] = "Easement"
df.loc[ix, "Own_Name"] = "Easement"

### Try to fix other areas marked as DESG
# fix National Wildlife Refuges, National Historical Parks, USACE managed reservoirs,
# tribal lands (e.g., off-reservation trust lands, joint management areas, etc)
# excluding USFS and BLM because those are stacked designations (wilderness, RNAs, ACECs, etc)
ix = (
    (df.Category == "Designation")
    & (df.Own_Type == "DESG")
    & (df.Des_Tp != "WA")
    & (df.Loc_Ds.fillna("").str.upper() != "CLOSING ORDER BOUNDARY")
    & (df.Mang_Name.isin(["FWS", "NPS", "USACE", "TRIB"]))
)
df.loc[ix, "Own_Type"] = df.loc[ix].Mang_Type
df.loc[ix, "Own_Name"] = df.loc[ix].Mang_Name


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
        "Easement": "Easement",
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

# drop other proclamation boundaries and areas where owner type and name are unknown; these are not useful
# NOTE: this specifically drops designation types (Own_Type=="DESG") that are used
# for things like wilderness and wild & scenic river corridors, because they are
# either contained in other boundaries (e.g., wilderness) or not necessarily indicative
# of ownership (e.g., wild & scenic river corridors)
df = (
    df.loc[
        ((df.Category != "Proclamation") | (df.Des_Tp == "MIL"))
        & (df.Own_Type != "DESG")
        & (df.Own_Type != "UNK")
        & (df.Own_Name != "UNK")
    ]
    .drop(columns=["Category", "Own_Type", "Own_Name", "Des_Tp", "Mang_Type", "Mang_Name", "Loc_Ds"])
    .drop_duplicates()
)


# this takes a while...
print("Making geometries valid, this might take a while")
df["geometry"] = make_valid(df.geometry.values)


# Extract Hawaii reserves
hifr = read_dataframe(src_dir / "HI_Reserves/Reserves.shp", use_arrow=True).to_crs(CRS)
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
df = read_dataframe(src_dir / "tl_2022_us_aiannh.zip", columns=[], use_arrow=True).to_crs(CRS)
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

merged.to_feather(out_dir / "environmental_justice_flowlines.feather")


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
