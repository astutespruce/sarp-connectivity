"""Extract out species information

1. Read in USFWS ECOS listing of T & E species
2. Add in species names based on taxonomic synonyms
3. Read in aggregated species / HUC12 info
4. Fix species name issues for select species
5. Assign ECOS T & E in addition to those already present from states

Beware: Some species have incorrect spellings!  Some have many variants of common name!

"""

from pathlib import Path
from time import time
import csv

import pandas as pd
import geopandas as gp
from nhdnet.io import serialize_df

start = time()
data_dir = Path("data")
src_dir = data_dir / "species/source"
out_dir = data_dir / "species/derived"
gdb = src_dir / "Final_Species_Table_12302019.gdb"

############### Extract USFWS official listing information ######################
print("Reading T&E species list")
listed_df = pd.read_csv(
    src_dir / "ECOS_listed_aquatic_species_2018.csv",
    usecols=["ScientificName", "Status"],
).rename(columns={"ScientificName": "SNAME"})

# Fix extra spaces in species name
listed_df.SNAME = listed_df.SNAME.str.replace("  ", " ")

# Assign consistent codes
listed_df.loc[listed_df.Status == "\xa0Endangered", "official_status"] = "E"
listed_df.loc[listed_df.Status == "\xa0Threatened", "official_status"] = "T"
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

listed_df = listed_df.append(missing_spps, ignore_index=True)


# Species with a T & E listing from states that are not updated
# because they are not listed by ECOS or NatureServe Explorer as being T & E:
# Crystallaria asprella, Etheostoma olmstedi, Fundulus jenkinsi, Notropis melanostomus, Pteronotropis welaka

# Others are under review and not listed yet according to USFWS:
# Pleurobema rubellum


endangered_df = listed_df.loc[listed_df.official_status == "E"].SNAME.unique()
threatened_df = listed_df.loc[listed_df.official_status == "T"].SNAME.unique()


### Extract occurrence table from SARP

print("Reading species occurrence data...")
df = gp.read_file(gdb)[
    [
        "HUC12_Code",
        "Species_Name",
        "Common_Name",
        "Historical",
        "Federal_Status",
        "State_Status",
        "SGCN_Listing",
        "Regional_SGCN",
    ]
].rename(
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

# fix data issues
for col in ["SNAME", "CNAME"]:
    df[col] = df[col].fillna("").str.strip()


# Some species have a bunch of duplicates
df = df.drop_duplicates()

# Update to overcome taxonomic issues
df.loc[df.federal.isnull() & df.SNAME.isin(endangered_df), "federal"] = "LE"
df.loc[df.federal.isnull() & df.SNAME.isin(threatened_df), "federal"] = "LT"


# Convert to bool
for col in ["federal", "state", "sgcn", "regional"]:
    df[col] = df[col].notnull()


counts = df.groupby("HUC12").sum().astype("uint8").reset_index()

serialize_df(counts, out_dir / "spp_HUC12.feather")
counts.to_csv(out_dir / "spp_HUC12.csv", quoting=csv.QUOTE_NONNUMERIC, index=False)

print("All done in {:.2}s".format(time() - start))
