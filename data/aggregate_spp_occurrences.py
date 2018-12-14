"""
1. Aggregates 12 GB worth of species polygon occurence information into unique HUC12, species, status combinations.
2. Aggregates the point data.
3. Merges both together and writes to a new CSV

Note: No fixes for status or species name issues are applied here.
"""


import pandas as pd

################# Aggregate polygon data ################
print("Reading polygon data...")
reader = pd.read_csv(
    "data/src/Species_polygons_HUC12_intersect.csv",
    chunksize=1e6,  # Read data 1 million records at a time
    usecols=[
        "SARP_Scientific_Name",
        "SARP_Federal_Status",
        # "SARP_Common_Name",
        "HUC12",
    ],
    dtype={
        "HUC12": str,
        "SARP_Scientific_Name": str,
        # "SARP_Common_Name": str,
        "SARP_Federal_Status": str,
    },
)

aggregated_df = None

for df in reader:
    print("Reading chunk...")
    df.rename(
        columns={"SARP_Scientific_Name": "SNAME", "SARP_Federal_Status": "status"},
        inplace=True,
    )

    df.fillna({"status": ""}, inplace=True)

    # standardize casing of scientific name
    df.SNAME = df.SNAME.str.capitalize()

    # Extract unique species records per HUC
    grouped_df = (
        df.groupby(["HUC12", "SNAME", "status"]).size().reset_index().drop(columns=[0])
    )

    if aggregated_df is None:
        aggregated_df = grouped_df
    else:
        aggregated_df = aggregated_df.append(grouped_df, ignore_index=True)


poly_df = (
    aggregated_df.groupby(["HUC12", "SNAME", "status"])
    .size()
    .reset_index()
    .drop(columns=[0])
)
poly_df.to_csv("data/src/Species_polygons_HUC12.csv", index=False)


################# Aggregate point data ################
print("Reading point data")
df = (
    pd.read_csv(
        "data/src/Species_points_HUC12.csv",
        usecols=[
            "SARP_Scientific_Name",
            # "SARP_Common_Name",
            "SARP_Federal_Status",
            "HUC12",
        ],
        dtype={"HUC12": str, "SARP_Scientific_Name": str, "SARP_Federal_Status": str},
    )
    .rename(
        columns={
            "SARP_Scientific_Name": "SNAME",
            # "SARP_Common_Name": "CNAME",
            "SARP_Federal_Status": "status",
        }
    )
    .fillna({"status": ""})
)

# Normalize casing on SNAME
df.SNAME = df.SNAME.str.capitalize()

point_df = (
    df.groupby(["HUC12", "SNAME", "status"]).size().reset_index().drop(columns=[0])
)

# merge the datasets together
merged_df = poly_df.append(point_df, ignore_index=True)
merged_df = (
    merged_df.groupby(["HUC12", "SNAME", "status"])
    .size()
    .reset_index()
    .drop(columns=[0])
)
merged_df.to_csv("data/src/species_HUC12.csv", index=False)
