"""
1. Aggregates 12 GB worth of species polygon occurrence information into unique HUC12, species, status combinations.
2. Aggregates the point data.
3. Merges both together and writes to a new CSV

Note: No fixes for status or species name issues are applied here.
"""
from pathlib import Path
from time import time

import pandas as pd
from nhdnet.io import serialize_df


start = time()

data_dir = Path("data")
src_dir = data_dir / "species/source"
out_dir = data_dir / "species/derived"


################# Aggregate polygon data ################
print("Reading polygon data...")
reader = pd.read_csv(
    src_dir / "Species_polygons_HUC12_intersect.csv",
    chunksize=10e6,  # Read data 10 million records at a time
    usecols=["SARP_Scientific_Name", "SARP_Federal_Status", "HUC12"],
    dtype={"HUC12": str, "SARP_Scientific_Name": str, "SARP_Federal_Status": str},
)

merged = None

for df in reader:
    print("Reading chunk...")
    df = df.rename(
        columns={"SARP_Scientific_Name": "SNAME", "SARP_Federal_Status": "status"}
    ).fillna({"status": ""})

    # standardize casing of scientific name
    df.SNAME = df.SNAME.str.capitalize()

    # Extract unique species records per HUC
    # we don't actually use the groups, this is just to reduce data volume
    df = df.groupby(["HUC12", "SNAME", "status"]).first().reset_index()

    if merged is None:
        merged = df
    else:
        merged = merged.append(df, ignore_index=True, sort=False)

# Re-group to prevent any duplicates introduced above
poly_df = merged.groupby(["HUC12", "SNAME", "status"]).first().reset_index()


################# Aggregate point data ################
print("Reading point data")
df = (
    pd.read_csv(
        src_dir / "Species_points_HUC12.csv",
        usecols=["SARP_Scientific_Name", "SARP_Federal_Status", "HUC12"],
        dtype={"HUC12": str, "SARP_Scientific_Name": str, "SARP_Federal_Status": str},
    )
    .rename(columns={"SARP_Scientific_Name": "SNAME", "SARP_Federal_Status": "status"})
    .fillna({"status": ""})
)

# Normalize casing on SNAME
df.SNAME = df.SNAME.str.capitalize()

point_df = (
    df.groupby(["HUC12", "SNAME", "status"]).size().reset_index().drop(columns=[0])
)

# merge the datasets together and group to remove duplicates
merged = (
    poly_df.append(point_df, ignore_index=True, sort=False)
    .groupby(["HUC12", "SNAME", "status"])
    .first()
    .reset_index()
)
serialize_df(merged, out_dir / "spp_HUC12_occurrence.feather")

print("Extracted {:,} unique species occurrences in HUC12s".format(len(merged)))

print("All done extracting species in {:.2f}s".format(time() - start))

