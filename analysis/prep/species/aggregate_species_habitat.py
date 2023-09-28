from pathlib import Path

import pandas as pd


data_dir = Path("data")
working_dir = data_dir / "species/derived"

# datasets with species level columns
streamnet = pd.read_feather(working_dir / "streamnet_habitat.feather")

chesapeake_diadromous = pd.read_feather(
    working_dir / "chesapeake_diadromous_species_habitat.feather"
).rename(columns={"brook_trout_habitat": "chesapeake_brook_trout_habitat"})

eastern_brook_trout = pd.read_feather(
    working_dir / "eastern_brook_trout_habitat.feather",
    columns=["NHDPlusID", "HUC2", "eastern_brook_trout_habitat"],
)

# datasets with aggregated species
ca_baseline = pd.read_feather(
    working_dir / "ca_baseline_fish_habitat.feather",
    columns=["NHDPlusID", "HUC2", "ca_baseline_fish_habitat"],
)

south_atlantic_anadromous = pd.read_feather(
    working_dir / "south_atlantic_anadromous_habitat.feather",
    columns=["NHDPlusID", "HUC2", "south_atlantic_anadromous_habitat"],
)

### Join all datasets together
# aggregate NHDPlusIDs first; this gives us an outer join plus HUC2
df = pd.DataFrame(
    pd.concat(
        [
            streamnet[["NHDPlusID", "HUC2"]],
            chesapeake_diadromous[["NHDPlusID", "HUC2"]],
            eastern_brook_trout[["NHDPlusID", "HUC2"]],
            ca_baseline[["NHDPlusID", "HUC2"]],
            south_atlantic_anadromous[["NHDPlusID", "HUC2"]],
        ],
        ignore_index=True,
    )
    .groupby("NHDPlusID")
    .HUC2.first()
)

df = (
    df.join(streamnet.set_index("NHDPlusID").drop(columns=["HUC2"]))
    .join(chesapeake_diadromous.set_index("NHDPlusID").drop(columns=["HUC2"]))
    .join(eastern_brook_trout.set_index("NHDPlusID").drop(columns=["HUC2"]))
    .join(ca_baseline.set_index("NHDPlusID").drop(columns=["HUC2"]))
    .join(south_atlantic_anadromous.set_index("NHDPlusID").drop(columns=["HUC2"]))
)

cols = [c for c in df.columns if c != "HUC2"]
df[cols] = df[cols].fillna(False).astype("bool")

# combine Trout Unlimited and Chesapeake Bay data for brook trout
df["eastern_brook_trout_habitat"] = (
    df.eastern_brook_trout_habitat | df.chesapeake_brook_trout_habitat
)
df = df.drop(columns=["chesapeake_brook_trout_habitat"])


group_cols = [
    "ca_baseline_fish_habitat",
    "chesapeake_diadromous_habitat",
    "south_atlantic_anadromous_habitat",
    "streamnet_anadromous_habitat",
]

spp_cols = [
    "alewife_habitat",
    "american_eel_habitat",
    "american_shad_habitat",
    "atlantic_sturgeon_habitat",
    "blueback_herring_habitat",
    "bonneville_cutthroat_trout_habitat",
    "bull_trout_habitat",
    "chinook_salmon_habitat",
    "chum_salmon_habitat",
    "coastal_cutthroat_trout_habitat",
    "coho_salmon_habitat",
    "eastern_brook_trout_habitat",
    "green_sturgeon_habitat",
    "hickory_shad_habitat",
    "kokanee_habitat",
    "pacific_lamprey_habitat",
    "pink_salmon_habitat",
    "rainbow_trout_habitat",
    "redband_trout_habitat",
    "shortnose_sturgeon_habitat",
    "sockeye_salmon_habitat",
    "steelhead_habitat",
    "striped_bass_habitat",
    "westslope_cutthroat_trout_habitat",
    "white_sturgeon_habitat",
    "yellowstone_cutthroat_trout_habitat",
]

df = df[["HUC2"] + group_cols + spp_cols].reset_index()

df.to_feather(working_dir / "combined_species_habitat.feather")
