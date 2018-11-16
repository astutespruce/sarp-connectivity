"""Extract out species information

1. filter out unique species / HUC combinations
2. filter out T & E species

TODO: make sure that T&E is used consistently for same species
Some species have incorrect spellings!  Some have many variants of common name!

"""

import pandas as pd

listed_df = pd.read_csv("data/src/ECOS_listed_aquatic_species_2018.csv").rename(
    columns={"ScientificName": "SNAME"}
)[["SNAME", "Status"]]

# Fix extra spaces in species name
listed_df.SNAME = listed_df.SNAME.str.replace("  ", " ")

# Assign consistent codes
listed_df.loc[listed_df.Status == "\xa0Endangered", "official_status"] = "E"
listed_df.loc[listed_df.Status == "\xa0Threatened", "official_status"] = "T"
listed_df = listed_df.loc[
    ~listed_df.official_status.isnull(), ["SNAME", "official_status"]
]

# Manually add in species that have had a taxomic change (that we tripped over, NOT comprehensive)
# Ignoring experimental population exemption here
# Some are listed at the subspecies level by USFWS but the taxonomy at that level is not yet accepted

missing_spps = pd.DataFrame(
    [
        # Endangered species
        ["Arkansia wheeleri", "E"],
        ["Epioblasma curtisii", "E"],
        ["Epioblasma torulosa", "E"],
        ["Hamiota subangulata", "E"],
        ["Margaritifera monodonta", "E"],
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


# Species with a T & E listing from states that are
# not updated because they are not listed by ECOS or NatureServe Explorer as being T & E:
# Crystallaria asprella, Etheostoma olmstedi, Fundulus jenkinsi, Notropis melanostomus, Pteronotropis welaka

# Others are under review and not listed yet
# Pleurobema rubellum


endangered_df = listed_df.loc[listed_df.official_status == "E"].SNAME.unique()
threatened_df = listed_df.loc[listed_df.official_status == "T"].SNAME.unique()
# listed_df.loc[listed_df.SNAME.isin(endangered_df), "official_status"] = "E"

# To simplify the join, apply the highest listing to all occurrences, this is the most conservative
# Flatten to single record for each species
# listed_df = (
#     listed_df.groupby(["SNAME", "official_status"])
#     .size()
#     .reset_index()
#     .drop(columns=[0])
#     .set_index(["SNAME"])
# )

# Extract species points, keep only the columns we care about, rename them to make them easier to use
# Need to fill empty values of status with empty strings to ensure that grouping works properly later
df = (
    pd.read_csv(
        "data/src/Species_points_HUC12.csv",
        dtype={"HUC12": str, "SARP_Scientific_Name": str, "SARP_Federal_Status": str},
    )
    .rename(
        columns={
            "SARP_Scientific_Name": "SNAME",
            "SARP_Common_Name": "CNAME",
            "SARP_Federal_Status": "status",
        }
    )[["SNAME", "CNAME", "STATUS", "HUC12"]]
    .fillna({"status": ""})
)

# Normalize casing on SNAME and CNAME
df.SNAME = df.SNAME.str.capitalize()
df.CNAME = df.CNAME.str.title()

# Fix Atlantic sturgeon (Acipenser ox*); it has multiple variants of the wrong spelling
# There are other species that have wrong spelling, but they aren't T&E, so we aren't fixing here
index = df.SNAME.str.startswith("Acipenser oxyrhynchus")
df.loc[index, "SNAME"] = df.loc[index].SNAME.str.replace("oxyrhynchus", "oxyrinchus")


# Apply T & E status from official listing info


# Some species are not consistently identified to the same T&E status
# For any species that has a status of E, appy that to all instances of it
# While there may be specific populations or areas where it is T&E versus others where it is not, it is probably more useful
# To know where all instances of that species occur.
# Also need to apply T & E status from species level to all subspecies
spp_status = df.groupby(["SNAME", "status"]).size().reset_index().drop(columns=[0])
# spp_status.to_csv("data/src/tmp/spp_status.csv")

# Before cleanup
# status
#      1177
#       123
# E      76
# S      19
# T      38


# For species that were inconsistently applied, assume the following:
# Acipenser oxyrinchus: all occurences: E
# Scaphirhynchus albus: all occurrences: E


# Group by the core columns to find unique combinations
# We don't really need the count, but we need it to get an aggregation
# So we drop it after running this
spphuc12_df = (
    df.groupby(["HUC12", "SNAME", "status"]).size().reset_index().drop(columns=[0])
)

# Extract out only those species that are T & E


# reader = pd.read_csv('')
