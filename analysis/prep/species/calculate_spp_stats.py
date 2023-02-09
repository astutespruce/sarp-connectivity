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

import pandas as pd
from pyogrio import read_dataframe

from analysis.lib.util import append


start = time()
data_dir = Path("data")
bnd_dir = data_dir / "boundaries"
src_dir = data_dir / "species/source"
out_dir = data_dir / "species/derived"
gdb = src_dir / "Species_Results_Tables_2022.gdb"
rare_spp_layers = ["Southeast_Table", "Western_Table"]
trout_layer = "Trout_Filter_2022"


############### Extract USFWS official listing information ######################

print("Reading T&E species list")
listed_df = pd.read_csv(
    src_dir / "ECOS_listed_aquatic_species_2018.csv",
    usecols=["ScientificName", "Status"],
).rename(columns={"ScientificName": "SNAME"})

# Fix extra spaces in species name
listed_df.SNAME = listed_df.SNAME.str.replace("  ", " ").str.strip()
listed_df.Status = listed_df.Status.str.replace("\xa0", "").str.strip()

# Assign consistent codes
listed_df.loc[listed_df.Status == "Endangered", "official_status"] = "E"
listed_df.loc[listed_df.Status == "Threatened", "official_status"] = "T"
listed_df = listed_df.loc[
    ~listed_df.official_status.isnull(), ["SNAME", "official_status"]
]

# Manually add in species that have had a taxanomic change (that we tripped over, NOT comprehensive)
# Ignoring experimental population exemption here
# Some are listed at the subspecies level by USFWS but the taxonomy at that level is not yet accepted

missing_spps = pd.DataFrame(
    [
        # Endangered species
        ["Arcidens wheeleri", "E"],
        ["Arkansia wheeleri", "E"],
        ["Epioblasma curtisii", "E"],
        ["Epioblasma torulosa", "E"],
        ["Hamiota subangulata", "E"],
        ["Margaritifera monodonta", "E"],
        ["Marstonia pachyta", "E"],
        # Threatened species
        ["Hamiota altilis", "T"],
        ["Hamiota perovalis", "T"],
        ["Quadrula cylindrica", "T"],
        ["Troglichthys rosae", "T"],
        # listed at subspecies level at least at threatened level
        ["Theliderma cylindrica", "T"],
    ],
    columns=["SNAME", "official_status"],
)

listed_df = pd.concat([listed_df, missing_spps], ignore_index=True)


# Species with a T & E listing from states that are not updated
# because they are not listed by ECOS or NatureServe Explorer as being T & E:
# Crystallaria asprella, Etheostoma olmstedi, Fundulus jenkinsi, Notropis melanostomus, Pteronotropis welaka

# Others are under review and not listed yet according to USFWS:
# Pleurobema rubellum

endangered_df = listed_df.loc[listed_df.official_status == "E"].SNAME.unique()
threatened_df = listed_df.loc[listed_df.official_status == "T"].SNAME.unique()


### Process trout data (not necessarily T/E/SGCN, just used for filtering)
trout = read_dataframe(
    gdb,
    layer=trout_layer,
    read_geometry=False,
    columns=[
        "HUC12_Code",
        "Species_Name",
        "Common_Name",
        "Historical",
        "Federal_Status",
        "State_Status",
        "SGCN_Listing",
    ],
).rename(
    columns={
        "HUC12_Code": "HUC12",
        "Species_Name": "SNAME",
        "Common_Name": "CNAME",
        "Federal_Status": "federal",
        "State_Status": "state",
        "SGCN_Listing": "sgcn",
    }
)

# drop Trout-perch
trout = trout.loc[trout.CNAME != "Trout-perch"].copy()

# Convert to bool
cols = ["federal", "state", "sgcn"]
for col in cols:
    trout.loc[trout[col] == "No", col] = ""
    trout[col] = trout[col] != ""

# drop any that are only historic
trout = trout.loc[trout.federal | trout.state | trout.sgcn].copy()

trout = trout.groupby(by=["HUC12", "SNAME"]).first().reset_index()


### Extract occurrence table from SARP
merged = None
for layer in rare_spp_layers:
    print(f"Reading species occurrence data: {layer}")

    cols = [
        "HUC12_Code",
        "Species_Name",
        "Common_Name",
        "Historical",
        "Federal_Status",
        "State_Status",
        "SGCN_Listing",
    ]
    if layer != "Western_Table":
        cols.append("Regional_SGCN")

    df = read_dataframe(gdb, layer=layer, read_geometry=False)[cols].rename(
        columns={
            "HUC12_Code": "HUC12",
            "Species_Name": "SNAME",
            "Common_Name": "CNAME",
            "Federal_Status": "federal",
            "State_Status": "state",
            "SGCN_Listing": "sgcn",
            "Regional_SGCN": "regional",
        }
    )

    if not "Regional_SGCN" in df.columns:
        df["Regional_SGCN"] = ""

    merged = append(merged, df)

df = merged

print("Processing species data")

# fix data issues
for col in df.columns[1:]:
    df[col] = df[col].fillna("").str.strip()

df = df.loc[df.SNAME.notnull() & (df.SNAME != "")].copy()
# drop duplicates
df = (
    df.sort_values(by=["HUC12", "SNAME", "CNAME"])
    .groupby(["HUC12", "SNAME"])
    .first()
    .reset_index()
)

# Update to overcome taxonomic issues
df.loc[(df.federal == "") & df.SNAME.isin(endangered_df), "federal"] = "LE"
df.loc[(df.federal == "") & df.SNAME.isin(threatened_df), "federal"] = "LT"

# Convert to bool
cols = ["federal", "state", "sgcn", "regional"]
for col in cols:
    df.loc[df[col] == "No", col] = ""
    df[col] = df[col] != ""

# drop any that are only historic
df = df.loc[df.federal | df.state | df.sgcn | df.regional].copy()


# Export intermediate - Kat @ SARP often needs this
summary = df.copy()
summary[cols] = summary[cols].astype("uint8")
summary.to_excel(out_dir / "spp_HUC12_summary.xlsx", index=False)


### Calculate TE/SGCN counts per HUC12 and join in trout and salmonids
huc12 = pd.read_feather(bnd_dir / "huc12.feather", columns=["HUC12"]).set_index("HUC12")
huc12 = (
    huc12.join(
        df[["HUC12", "federal", "state", "sgcn", "regional"]].groupby("HUC12").sum()
    )
    .fillna(0)
    .astype("uint8")
)

# NOTE: trout presence / absence converted to 0/1
huc12["trout"] = huc12.index.isin(trout.HUC12).astype("uint8")


salmonid_huc12 = pd.read_feather(
    src_dir / "salmonid_esu.feather",
    columns=["HUC12", "salmonid_esu", "salmonid_esu_count"],
).set_index("HUC12")


huc12 = huc12.join(salmonid_huc12)
huc12["salmonid_esu_count"] = huc12.salmonid_esu_count.fillna(0).astype("uint8")
huc12["salmonid_esu"] = huc12.salmonid_esu.fillna("")

# drop any huc12s that don't have useful data
huc12 = huc12.loc[
    huc12[["federal", "state", "sgcn", "regional", "trout", "salmonid_esu_count"]].max(
        axis=1
    )
    > 0
].reset_index()

huc12.to_feather(out_dir / "spp_HUC12.feather")
huc12.to_excel(out_dir / "spp_HUC12.xlsx", index=False)


print("All done in {:.2f}s".format(time() - start))
