"""Extract out species information

1. Read in USFWS ECOS listing of T & E species, Trout (obtained by SARP), Salmonid ESU / DPS (obtained by SARP)
2. Add in species names based on taxonomic synonyms
3. Read in aggregated species / HUC12 info
4. Fix species name issues for select species
5. Assign ECOS T & E in addition to those already present from states

Beware: Some species have incorrect spellings!  Some have many variants of common name!

"""

from pathlib import Path
from time import time

import geopandas as gp
import numpy as np
import pandas as pd
from pyogrio import read_dataframe, list_layers, write_dataframe
from pyarrow.csv import read_csv, ConvertOptions
import shapely

from analysis.constants import SARP_STATES, TROUT_SPECIES_TO_CODE, TROUT_CODE_TO_NAME
from analysis.lib.util import append


start = time()
data_dir = Path("data")
bnd_dir = data_dir / "boundaries"
src_dir = data_dir / "species/source"
out_dir = data_dir / "species/derived"


states = gp.read_feather(bnd_dir / "states.feather")
huc12 = gp.read_feather(bnd_dir / "huc12.feather", columns=["HUC12", "geometry"]).set_index("HUC12")

secas_huc12 = huc12.take(
    np.unique(
        shapely.STRtree(huc12.geometry.values).query(
            states.loc[states.id.isin(SARP_STATES)].geometry.values, predicate="intersects"
        )[1]
    )
)

salmonid_huc12 = pd.read_feather(
    src_dir / "salmonid_esu.feather",
    columns=["HUC12", "salmonid_esu", "salmonid_esu_count"],
).set_index("HUC12")

################################################################################
### Extract USFWS official listing information
################################################################################

print("Reading T&E species list")
listed_df = pd.read_csv(
    src_dir / "ECOS_listed_species_05_03_2024.csv",
    usecols=["Scientific Name", "Federal Listing Status", "Where Listed"],
    engine="pyarrow",
).rename(columns={"Scientific Name": "SNAME", "Federal Listing Status": "status", "Where Listed": "location"})

# only keep T&E species that are listed across their entire range
listed_df = listed_df.loc[
    listed_df.status.isin(["Endangered", "Threatened"])
    & (
        # typo is in source data
        listed_df.location.isin(["Wherever found", "U.S. Only", "U.S.A., coterminous, (lower 48 states)"])
        # ignore exemptions for experimental populations
        | (
            listed_df.location.str.lower().str.contains("except")
            & listed_df.location.str.lower().str.contains("experimental")
        )
    )
]
listed_df["official_status"] = listed_df.status.map({"Endangered": "E", "Threatened": "T"})


# Manually add in species that have had a taxanomic change (that we tripped over, NOT comprehensive)
# Ignoring experimental population exemption here
# Some are listed at the subspecies level by USFWS but the taxonomy at that level is not yet accepted
missing_spps = pd.DataFrame(
    [
        ### Endangered species
        # Acipenser oxyrinchus is listed as endangered or threatened across multiple populations / subspecies but all are listed in some way
        ["Acipenser oxyrinchus", "E"],
        ["Acipenser oxyrinchus oxyrinchus", "E"],
        ["Arcidens wheeleri", "E"],
        ["Arcidens wheeleri", "E"],
        ["Epioblasma curtisii", "E"],
        ["Epioblasma torulosa", "E"],
        # listed as Gila seminuda (=robusta), but as Gila seminuda in occurrence data
        ["Gila seminuda", "E"],
        ["Hamiota subangulata", "E"],
        ["Margaritifera monodonta", "E"],
        ["Marstonia pachyta", "E"],
        # Rhinichthys cobitis is listed as Tiaroga cobitis
        ["Rhinichthys cobitis", "E"],
        # Pristis pectinata has multiple population listings but all are endangered
        ["Pristis pectinata", "E"],
        # Venustaconcha trabalis is listed as Villosa trabalis (ignoring experimental populations)
        ["Venustaconcha trabalis", "E"],
        ### Threatened species
        ["Acipenser oxyrinchus desotoi", "T"],
        ["Hamiota altilis", "T"],
        ["Hamiota perovalis", "T"],
        ["Quadrula cylindrica", "T"],
        ["Troglichthys rosae", "T"],
        # listed at subspecies level at least at threatened level
        ["Theliderma cylindrica", "T"],
    ],
    columns=["SNAME", "official_status"],
)

listed_df = pd.concat([listed_df[["SNAME", "official_status"]], missing_spps], ignore_index=True)

# Species with a T & E listing from states that are not updated
# because they are not listed by ECOS or NatureServe Explorer as being T & E:
# Crystallaria asprella, Etheostoma olmstedi, Fundulus jenkinsi, Notropis melanostomus, Pteronotropis welaka

# Others are under review and not listed yet according to USFWS:
# Pleurobema rubellum

federal_spp = listed_df.loc[listed_df.official_status.isin(["E", "T"])].SNAME.unique()


################################################################################
### Process trout data at species level for filtering
# NOTE: these are not necessarily T/E/SGCN
################################################################################

### TEMPORARY: use eastern brook trout habitat to backfill missing HUC12s in great lakes
ebt_habitat = read_dataframe(out_dir / "eastern_brook_trout_habitat.fgb", columns=["geometry"], use_arrow=True)
left, right = shapely.STRtree(ebt_habitat.geometry.values).query(huc12.geometry.values, predicate="intersects")
pairs = pd.DataFrame(
    {
        "HUC12": huc12.index.values.take(left),
        "HUC12_geom": huc12.geometry.values.take(left),
        "geometry": ebt_habitat.geometry.values.take(right),
    }
)

# exclude great lakes (also HUC12 fringe)
pairs = pairs.loc[
    ~pairs.HUC12.isin(
        [
            "041800000200",
            "042800020200",
            "042600000200",
            "042400020200",
            "041900000200",
            "041800000102",
            "042400020102",
            "042800020102",
            "042600000102",
        ]
    )
].copy()

# only keep HUC12s with at least 250m (arbitrary) of overlap
pairs = pairs.groupby("HUC12").agg({"HUC12_geom": "first", "geometry": shapely.multilinestrings}).reset_index()
pairs["geometry"] = shapely.intersection(pairs.HUC12_geom.values, pairs.geometry.values)
pairs = pairs.loc[shapely.length(pairs.geometry.values) >= 250].copy()
ebt_huc12 = pairs.HUC12.unique()

ebt_df = pd.DataFrame({"HUC12": ebt_huc12})
ebt_df["SNAME"] = "Salvelinus fontinalis"


################################################################################
### Extract occurrence table from SARP
################################################################################

status_cols = ["federal", "sgcn", "regional"]

merged = None
for filename in (src_dir / "Species HUC12 csvs").glob("*.csv"):
    print(f"Reading {filename}")
    df = (
        read_csv(filename, convert_options=ConvertOptions(column_types={"HUC12_Code": "str"}))
        .to_pandas()
        .rename(
            columns={
                "HUC12_Code": "HUC12",
                "Species_Name": "SNAME",
                "Common_Name": "CNAME",
                "Federal_Status": "federal",
                "SGCN_Listing": "sgcn",
                "Regional_SGCN": "regional",
                "Historical": "historical",
                "Trout": "is_trout",
            }
        )
    )

    if "CNAME" not in df.columns:
        df["CNAME"] = ""

    df = df[["HUC12", "SNAME", "CNAME", "historical", "federal", "sgcn", "regional", "is_trout"]]

    # fix data issues (have to do before merge or it has issues with blank columns)
    for col in df.columns:
        df[col] = df[col].fillna("").str.strip().str.replace("<Null>", "").str.replace("Unknown", "")

    # TEMPORARY: prefx huc12 codes that are not 0 prefixed to 12 chars
    ix = df.HUC12.apply(len) < 12
    df.loc[ix, "HUC12"] = df.loc[ix].HUC12.str.pad(12, side="left", fillchar="0")

    df = df.loc[(df.HUC12 != "") & (df.SNAME != "")].copy()

    if "Aquatic" in df.columns:
        df = df.loc[df.Aquatic != "No"].copy()

    # Convert status cols to bool
    df["historical"] = df.historical == "Yes"
    for col in status_cols:
        df[col] = ~df[col].isin(["No", ""])

    df["is_trout"] = ~df.is_trout.isin(["No", ""])
    # fix trout-perch (not a trout)
    df.loc[(df.SNAME == "Percopsis omiscomaycus") | (df.CNAME == "Trout-perch"), "is_trout"] = False

    merged = append(merged, df)

df = merged


trout_df = pd.concat([ebt_df, df.loc[df.is_trout]]).groupby(["HUC12", "SNAME"])[[]].first().reset_index()

# drop duplicates, keeping the highest status per species per HUC12
df = (
    df.sort_values(by=["HUC12", "SNAME", "CNAME"], ascending=[True, True, False])
    .groupby(["HUC12", "SNAME"])
    .agg({"CNAME": "first", "historical": "min", **{c: "max" for c in status_cols}})
    .reset_index()
)

# DEBUG: use this to show the species that have mixed listing status and we don't (yet) override
# for entry in sorted(
#     df.loc[df.SNAME.isin(df.loc[df.federal].SNAME.unique()) & ~df.federal & ~df.SNAME.isin(federal_spp)].SNAME.unique()
# ):
#     print(entry)

# Update federal status based on T&E list above (helps get past some taxonomic issues)
df.loc[~df.federal & df.SNAME.isin(federal_spp), "federal"] = True


### Export species presence per HUC12 - Kat @ SARP often needs this
spp_presence = df.loc[df.federal | df.sgcn | df.regional].copy()

cols = ["historical", "federal", "sgcn", "regional"]
spp_presence[cols] = spp_presence[cols].astype("uint8")
write_dataframe(
    spp_presence, out_dir / "spp_HUC12_presence.gdb", layer="presence", driver="OpenFileGDB", use_arrow=True
)


### Extract counts for SECAS: exclude any entries that are historical
huc12_counts_secas = (
    secas_huc12[[]]
    .join(df.loc[~df.historical].groupby("HUC12")[["federal", "sgcn", "regional"]].sum())
    .fillna(0)
    .astype("uint8")
    .reset_index()
)
huc12_counts_secas.to_excel(out_dir / "SECAS_spp_HUC12_count_no_historical.xlsx", index=False)
write_dataframe(huc12_counts_secas, out_dir / "SECAS_spp_HUC12_count_no_historical.gdb", driver="OpenFileGDB")

### Extract summaries by HUC12 including salmonid ESUs
df = huc12[[]].join(df.groupby("HUC12")[status_cols].sum()).fillna(0).astype("uint8")


# aggregate trout to species level and then assign codes
trout_df["trout"] = (
    trout_df.SNAME.apply(lambda x: " ".join(x.split(" ")[:2])).str.strip(",").map(TROUT_SPECIES_TO_CODE).astype("uint8")
)
trout_df = pd.DataFrame(trout_df.groupby("HUC12").trout.unique())
trout_df["trout_spp_count"] = trout_df.trout.apply(len)
trout_df["trout_spp"] = trout_df.trout.apply(lambda x: ", ".join(sorted(TROUT_CODE_TO_NAME[v] for v in x)))
trout_df["trout"] = trout_df.trout.apply(lambda x: ",".join([str(v) for v in sorted(x)]))

# emit a message to manually update the hard-coded domain used for download
tmp = trout_df.groupby("trout").trout_spp.first().to_dict()
tmp.update({"": "not recorded"})

print("------------------------------------------------------------------------")
print("update TROUT_DOMAIN with the following entries:")
print(tmp)
print("------------------------------------------------------------------------")


df = df.join(trout_df)
df["trout"] = df.trout.fillna("")
df["trout_spp_count"] = df.trout_spp_count.fillna(0).astype("uint8")

df = df.join(salmonid_huc12)
df["salmonid_esu_count"] = df.salmonid_esu_count.fillna(0).astype("uint8")
df["salmonid_esu"] = df.salmonid_esu.fillna("")

# drop any huc12s that don't have useful data
df = df.loc[df[status_cols + ["trout_spp_count", "salmonid_esu_count"]].max(axis=1) > 0].reset_index()

df.to_feather(out_dir / "spp_HUC12.feather")

write_dataframe(df, out_dir / "spp_HUC12_count.gdb", layer="count", use_arrow=True, driver="OpenFileGDB")


print("All done in {:.2f}s".format(time() - start))
