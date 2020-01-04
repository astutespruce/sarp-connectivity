from pathlib import Path
import os
from time import time

import pandas as pd
import geopandas as gp
import numpy as np
import pygeos as pg
from shapely.geometry import MultiLineString

from pgpkg import to_gpkg
from geofeather import to_geofeather

from nhdnet.io import deserialize_df
from nhdnet.geometry.points import to2D

from analysis.pygeos_compat import to_pygeos, from_pygeos
from analysis.prep.network.lib.lines import calculate_sinuosity
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins
from analysis.constants import (
    CRS,
    DROP_MANUALREVIEW,
    EXCLUDE_MANUALREVIEW,
    DROP_RECON,
    DROP_FEASIBILITY,
    EXCLUDE_RECON,
    RECON_TO_FEASIBILITY,
)


NET_COLS = ["batNetID", "StreamOrde", "geometry"]

DAM_COLS = [
    "SARPUniqueID",
    "NIDID",
    "SourceDBID",
    "Barrier_Name",
    "Other_Barrier_Name",
    "River",
    "PurposeCategory",
    "Year_Completed",
    "Height",
    "StructureCondition",
    "ConstructionMaterial",
    "DB_Source",
    "Recon",
    "ManualReview",
    "PctNatFloodplain",
    "NumSizeClassGained",  # NOTE: our interpretation is different, we store total # size classes
    "USBatNetID",
    "DSBatNetID",
]


data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
nhd_dir = data_dir / "nhd"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
master_dir = barriers_dir / "master"
qa_dir = barriers_dir / "qa"
network_dir = data_dir / "networks/21/dams"
gdb = src_dir / "PR_Dec2019.gdb"

dams_layer = "Puerto_Inventory_Dec2019_Indicators"
network_layer = "PR_Functional_River_Network"


if not os.path.exists(network_dir):
    os.makedirs(network_dir)


start = time()
print("Reading Puerto Rico networks...")
networks = (
    gp.read_file(gdb, layer=network_layer)[NET_COLS]
    .rename(columns={"batNetID": "networkID", "StreamOrde": "streamorder"})
    .set_index("networkID")
)

# convert to LineStrings
ix = networks.loc[networks.geometry.type == "MultiLineString"].index
networks.loc[ix, "geometry"] = networks.loc[ix].geometry.apply(lambda g: g[0])

# project to crs
networks = networks.to_crs(CRS)

# convert to pygeos
networks = pd.DataFrame(networks.copy())
networks["geometry"] = to_pygeos(networks.geometry)

networks["length"] = pg.length(networks.geometry)
networks["miles"] = networks.length * 0.000621371
# sinuosity of each segment
networks["sinuosity"] = calculate_sinuosity(networks.geometry)

# aggregate up to the network
network_length = networks.groupby(level=0)[["length"]].sum()
temp_df = networks[["length", "sinuosity"]].join(network_length, rsuffix="_total")

# Calculate length-weighted sinuosity
wtd_sinuosity = (
    (temp_df.sinuosity * (temp_df.length / temp_df.length_total))
    .groupby(level=0)
    .sum()
    .rename("sinuosity")
)

# convert to miles
lengths = (network_length * 0.000621371).rename(columns={"length": "miles"})
# Per direction from SARP, assume all lengths are free-flowing
lengths["free_miles"] = lengths.miles

network_stats = lengths.join(wtd_sinuosity).join(
    networks.groupby(level=0).size().rename("segments")
).join(networks.groupby(level=0).streamorder.max())


### Read data for Puerto Rico
# these were analyzed using NHD Med Res. data by SARP
print("Reading data for Puerto Rico...")
df = gp.read_file(gdb, layer=dams_layer)[["geometry"] + DAM_COLS].rename(
    columns={
        "SARPUniqueID": "SARPID",
        "PotentialFeasibility": "Feasibility",
        "Barrier_Name": "Name",
        "Other_Barrier_Name": "OtherName",
        "DB_Source": "Source",
        "Year_Completed": "Year",
        "ConstructionMaterial": "Construction",
        "PurposeCategory": "Purpose",
        "StructureCondition": "Condition",
        "PctNatFloodplain": "natfldpln",
        "NumSizeClassGained": "sizeclasses",
        "USBatNetID": "upNetID",
        "DSBatNetID": "downNetID",
    }
)

print("Read {:,} dams in Puerto Rico".format(len(df)))

### Standardize data
# SARPID is a string in other places
df["SARPID"] = df.SARPID.astype("str")
df['HasNetwork'] = df.upNetID.notnull()

# Calculate IDs so that they fall after existing dam IDs
dams = deserialize_df(master_dir / "dams.feather", columns=["id"])
next_id = (dams.id.max() + 1).astype("uint32")
df["id"] = df.index + next_id
df["id"] = df.id.astype("uint32")
df = df.set_index("id", drop=False)

# convert to 2D and project to CRS
df["geometry"] = df.geometry.apply(to2D)
df = df.to_crs(CRS)

# We store total # size classes, rather than gained
df["sizeclasses"] = (df.sizeclasses.fillna(0) + 1).astype("uint8")

### Join in network stats from above
upstream_networks = (
    df[["upNetID"]]
    .join(network_stats, on="upNetID")
    .rename(columns={"miles": "TotalUpstreamMiles", "free_miles": "FreeUpstreamMiles",})
).drop(columns=["upNetID"])

downstream_networks = (
    df[["downNetID"]]
    .join(
        network_stats[["free_miles", "miles"]].rename(
            columns={
                "free_miles": "FreeDownstreamMiles",
                "miles": "TotalDownstreamMiles",
            }
        ),
        on="downNetID",
    )
    .drop(columns=["downNetID"])
)

df = df.join(upstream_networks).join(downstream_networks)

for col in ["upNetID", "downNetID", "segments"]:
    df[col] = df[col].fillna(0).astype("uint32")

for col in [
    "TotalUpstreamMiles",
    "FreeUpstreamMiles",
    "TotalDownstreamMiles",
    "FreeDownstreamMiles",
    "sinuosity",
    "natfldpln",
]:
    df[col] = df[col].fillna(0).astype("float32")

### Set data types
for column in ("River", "NIDID", "Source", "Name", "OtherName"):
    df[column] = df[column].fillna("").str.strip()

for column in ("Construction", "Condition", "Purpose", "Recon"):
    df[column] = df[column].fillna(0).astype("uint8")

for column in ("Year", "ManualReview"):
    df[column] = df[column].fillna(0).astype("uint16")

# Recon is not available, so both Recon and Feasibility will 0 out
df["Feasibility"] = df.Recon.map(RECON_TO_FEASIBILITY).astype("uint8")


# Cleanup names
# Standardize the casing of the name
df.Name = df.Name.str.title()
df.OtherName = df.OtherName.str.title()
df.River = df.River.str.title()

# Round height to nearest foot.  There are no dams between 0 and 1 foot, so fill all
# na as 0
df.Height = df.Height.fillna(0).round().astype("uint16")

# Calculate height class
df["HeightClass"] = 0  # Unknown
df.loc[(df.Height > 0) & (df.Height < 5), "HeightClass"] = 1
df.loc[(df.Height >= 5) & (df.Height < 10), "HeightClass"] = 2
df.loc[(df.Height >= 10) & (df.Height < 25), "HeightClass"] = 3
df.loc[(df.Height >= 25) & (df.Height < 50), "HeightClass"] = 4
df.loc[(df.Height >= 50) & (df.Height < 100), "HeightClass"] = 5
df.loc[df.Height >= 100, "HeightClass"] = 6
df.HeightClass = df.HeightClass.astype("uint8")

### Spatial joins
# Note: there are no ecoregions mapped for Puerto Rico
df = add_spatial_joins(df)


### Add tracking fields
# master log field for status
df["log"] = ""
# dropped: records that should not be included in any later analysis
df["dropped"] = False

# excluded: records that should be retained in dataset but not used in analysis
df["excluded"] = False

# Not applicable to PR but needed to merge with other dams
df['duplicate'] = False

# Fill in other standard fields that are missing here
df['loop'] = False
df['sizeclass'] = None

# Drop any that didn't intersect HUCs or states
drop_idx = df.HUC12.isnull() | df.STATEFIPS.isnull()
print("{:,} dams are outside HUC12 / states".format(len(df.loc[drop_idx])))
# Mark dropped barriers
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: outside HUC12 / states"


### Drop any dams that should be completely dropped from analysis
# based on manual QA/QC and other reivew.

# Drop those where recon shows this as an error
drop_idx = df.Recon.isin(DROP_RECON) & ~df.dropped
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: Recon one of {}".format(DROP_RECON)

# Drop those where recon shows this as an error
drop_idx = df.Feasibility.isin(DROP_FEASIBILITY) & ~df.dropped
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: Feasibility one of {}".format(DROP_FEASIBILITY)

# Drop those that were manually reviewed off-network or errors
drop_idx = df.ManualReview.isin(DROP_MANUALREVIEW) & ~df.dropped
df.loc[drop_idx, "dropped"] = True
df.loc[drop_idx, "log"] = "dropped: ManualReview one of {}".format(DROP_MANUALREVIEW)

print("Dropped {:,} dams from all analysis and mapping".format(len(df.loc[df.dropped])))


### Exclude dams that should not be analyzed or prioritized based on manual QA
exclude_idx = df.Recon.isin(EXCLUDE_RECON) | df.ManualReview.isin(EXCLUDE_MANUALREVIEW)
df.loc[exclude_idx, "excluded"] = True
df.loc[exclude_idx, "log"] = "excluded: Recon one of {}".format(EXCLUDE_RECON)

exclude_idx = df.ManualReview.isin(EXCLUDE_MANUALREVIEW)
df.loc[exclude_idx, "excluded"] = True
df.loc[exclude_idx, "log"] = "excluded: ManualReview one of {}".format(
    EXCLUDE_MANUALREVIEW
)

print(
    "Excluded {:,} dams from analysis and prioritization".format(
        len(df.loc[df.excluded])
    )
)

df = df.reset_index(drop=True)


### Create final networks
# derive other stats from those already in network data
network_stats = (
    network_stats.join(df[["upNetID", "natfldpln", "sizeclasses"]].set_index("upNetID"))
    .join(df.groupby("downNetID").size().rename("up_ndams"))
    .fillna(0)
)


dissolved = (
    from_pygeos(networks.geometry).groupby(level=0).apply(list).apply(MultiLineString)
)


# approximate output data created by normal network analysis
networks = network_stats.join(dissolved.rename("geometry"))
networks["networkID"] = networks.index.copy()
networks["networkID"] = networks.networkID.astype("uint32")
networks["barrier"] = "dam"
networks["segments"] = networks.segments.astype("uint16")

for col in ["sizeclasses", "up_ndams"]:
    networks[col] = networks[col].astype("uint8")

for col in ["miles", "free_miles", "natfldpln"]:
    networks[col] = networks[col].astype("float32")

networks = gp.GeoDataFrame(networks, crs=CRS).reset_index(drop=True)


barriers = df[["geometry", "id", "upNetID", "downNetID"]].reset_index(drop=True)
barriers["kind"] = "dam"

print("Serializing data...")
to_geofeather(df, master_dir / "pr_dams.feather")
to_geofeather(networks, network_dir / "network.feather")
networks.to_file(network_dir / "network.shp")

to_geofeather(barriers, network_dir / "barriers.feather")
barriers.to_file(network_dir / "barriers.shp")


print("All done in {:.2f}s".format(time() - start))
