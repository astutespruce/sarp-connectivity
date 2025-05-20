from pathlib import Path

import geopandas as gp
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import shapely

from analysis.constants import CRS
from analysis.lib.io import read_arrow_tables
from pyogrio import write_dataframe

data_dir = Path("data")
nhd_dir = data_dir / "nhd/raw"
working_dir = data_dir / "species/derived"

datasets = {
    # single-species datasets
    "apache_trout": pd.read_feather(working_dir / "apache_trout_habitat.feather"),
    "ca_coastal_cutthroat_trout": pd.read_feather(working_dir / "ca_coastal_cutthroat_trout_habitat.feather").rename(
        columns={"ca_coastal_cutthroat_trout_habitat": "coastal_cutthroat_trout_habitat"}
    ),
    "colorado_river_cutthroat_trout": pd.read_feather(working_dir / "colorado_river_cutthroat_trout_habitat.feather"),
    "eastern_brook_trout": pd.read_feather(working_dir / "eastern_brook_trout_habitat.feather"),
    "gila_trout": pd.read_feather(working_dir / "gila_trout_habitat.feather"),
    "lahontan_cutthroat_trout": pd.read_feather(working_dir / "lahontan_cutthroat_trout_habitat.feather"),
    # multi-species datasets
    "chesapeake": pd.read_feather(working_dir / "chesapeake_diadromous_species_habitat.feather").rename(
        columns={"brook_trout_habitat": "eastern_brook_trout_habitat"}
    ),
    "southeast": pd.read_feather(working_dir / "southeast_diadromous_habitat.feather"),
    "streamnet": pd.read_feather(working_dir / "streamnet_habitat.feather"),
    # datasets with aggregated species; no individual species columns
    "ca_baseline": pd.read_feather(working_dir / "ca_baseline_fish_habitat.feather"),
}


### Join all datasets together
# aggregate NHDPlusIDs first; this gives us an outer join plus HUC2
cols = ["NHDPlusID", "HUC2"]

df = pd.DataFrame(
    pd.concat([df[cols] for df in datasets.values()], ignore_index=True).groupby("NHDPlusID").HUC2.first()
)

for key, right_df in datasets.items():
    right_df = right_df.set_index("NHDPlusID").drop(columns=["HUC2"])
    df = df.join(right_df.rename({c: c.lower() for c in right_df.columns}), rsuffix=f"_{key}")

cols = [c for c in df.columns if c != "HUC2"]
df[cols] = df[cols].fillna(0).astype("bool")

# merge species shared across multiple datasets
shared_cols = [c for c in df.columns if c.split("_")[-1] in datasets.keys()]
for col in shared_cols:
    key = col.split("_")[-1]
    root_col = col.replace(f"_{key}", "")
    df[root_col] = df[root_col] | df[col]

df = df.drop(columns=shared_cols)


group_cols = [
    "ca_baseline_fish_habitat",
    "chesapeake_diadromous_habitat",
    "southeast_diadromous_habitat",
    "streamnet_anadromous_habitat",
]

spp_cols = [
    "alabama_shad_habitat",
    "alewife_habitat",
    "american_eel_habitat",
    "american_shad_habitat",
    "apache_trout_habitat",
    "atlantic_sturgeon_habitat",
    "blueback_herring_habitat",
    "bonneville_cutthroat_trout_habitat",
    "bull_trout_habitat",
    "chinook_salmon_habitat",
    "chum_salmon_habitat",
    "colorado_river_cutthroat_trout_habitat",
    "coastal_cutthroat_trout_habitat",
    "coho_salmon_habitat",
    "eastern_brook_trout_habitat",
    "gila_trout_habitat",
    "green_sturgeon_habitat",
    "gulf_sturgeon_habitat",
    "hickory_shad_habitat",
    "kokanee_habitat",
    "lahontan_cutthroat_trout_habitat",
    "pacific_lamprey_habitat",
    "pink_salmon_habitat",
    "rainbow_trout_habitat",
    "redband_trout_habitat",
    "shortnose_sturgeon_habitat",
    "skipjack_herring_habitat",
    "sockeye_salmon_habitat",
    "steelhead_habitat",
    "striped_bass_habitat",
    "westslope_cutthroat_trout_habitat",
    "white_sturgeon_habitat",
    "yellowstone_cutthroat_trout_habitat",
]

df = df[["HUC2"] + group_cols + spp_cols].reset_index()

df.to_feather(working_dir / "combined_species_habitat.feather")


huc2s = sorted(df.HUC2.unique())


flowlines = (
    read_arrow_tables(
        [nhd_dir / huc2 / "flowlines.feather" for huc2 in huc2s],
        columns=["geometry", "NHDPlusID"],
        filter=pc.is_in(pc.field("NHDPlusID"), pa.array(df.NHDPlusID.unique())),
    )
    .to_pandas()
    .join(df.set_index("NHDPlusID"), on="NHDPlusID")
)

flowlines = gp.GeoDataFrame(
    flowlines[[c for c in flowlines.columns if not c == "geometry"]],
    geometry=shapely.from_wkb(flowlines.geometry),
    crs=CRS,
)

write_dataframe(flowlines, working_dir / "combined_species_habitat.fgb", use_arrow=True)
