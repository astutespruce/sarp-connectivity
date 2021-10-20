""" Export summary stats of dams and barriers by HUC12 for SARP states, to send
exported data to SARP for further analysis.

This is a one-off script; not part of data processing chain.
"""

import os
from pathlib import Path


import pandas as pd
import numpy as np

from analysis.constants import SARP_STATE_NAMES

# Note: states are identified by name, whereas counties are uniquely identified by
# FIPS code.
# The values from these fields in the dams / small_barriers data must exactly match
# the IDs for those units set when the vector tiles of those units are created, otherwise
# they won't join properly in the frontend.

data_dir = Path("data")
src_dir = data_dir / "barriers/master"
bnd_dir = data_dir / "boundaries"
api_dir = data_dir / "api"

out_dir = Path("/tmp/sarp")
if not out_dir:
    os.makedirs(out_dir)


spp_df = (
    pd.read_feather(
        data_dir / "species/derived/spp_HUC12.feather",
        columns=["HUC12", "federal", "sgcn", "regional"],
    )
    .rename(
        columns={
            "federal": "TESpp",
            "sgcn": "StateSGCNSpp",
            "regional": "RegionalSGCNSpp",
        }
    )
    .set_index("HUC12")
)


### Read dams
dams = (
    pd.read_feather(
        api_dir / f"dams.feather",
        columns=["id", "HasNetwork", "Ranked", "Recon", "HUC12", "State"],
    )
    .set_index("id", drop=False)
    .rename(columns={"HasNetwork": "OnNetwork"})
)
dams["Recon"] = dams.Recon > 0

### Read road-related barriers
barriers = (
    pd.read_feather(
        api_dir / "small_barriers.feather",
        columns=["id", "HasNetwork", "Ranked", "HUC12", "State"],
    )
    .set_index("id", drop=False)
    .rename(columns={"HasNetwork": "OnNetwork"})
)
barriers_master = pd.read_feather(
    "data/barriers/master/small_barriers.feather", columns=["id", "dropped", "excluded"]
).set_index("id")

barriers = barriers.join(barriers_master)

# barriers that were not dropped or excluded are likely to have impacts
barriers["Included"] = ~(barriers.dropped | barriers.excluded)

### Read road / stream crossings
# NOTE: crossings are already de-duplicated against each other and against
# barriers
crossings = pd.read_feather(
    src_dir / "road_crossings.feather", columns=["id", "HUC12", "State"]
)


# Identify HUC12s that overlap with SARP states
huc12s = np.sort(
    np.unique(
        np.concatenate(
            [
                dams.loc[dams.State.isin(SARP_STATE_NAMES)].HUC12.unique(),
                barriers.loc[barriers.State.isin(SARP_STATE_NAMES)].HUC12.unique(),
                crossings.loc[crossings.State.isin(SARP_STATE_NAMES)].HUC12.unique(),
            ]
        )
    )
)

dams = dams.loc[dams.HUC12.isin(huc12s)]
barriers = barriers.loc[barriers.HUC12.isin(huc12s)]
crossings = crossings.loc[crossings.HUC12.isin(huc12s)]

huc12 = pd.read_feather(bnd_dir / "huc12.feather", columns=["HUC12", "name"]).set_index(
    "HUC12"
)
huc12 = huc12.loc[huc12.index.isin(huc12s)]


dam_stats = (
    dams[["HUC12", "id", "OnNetwork", "Ranked", "Recon"]]
    .groupby("HUC12")
    .agg({"id": "count", "OnNetwork": "sum", "Ranked": "sum", "Recon": "sum"})
    .rename(
        columns={
            "id": "inventory_dams",
            "OnNetwork": "on_network_dams",
            "Ranked": "ranked_dams",
            "Recon": "recon_dams",
        }
    )
)

barriers_stats = (
    barriers[["HUC12", "id", "Included", "OnNetwork", "Ranked"]]
    .groupby("HUC12")
    .agg({"id": "count", "Included": "sum", "Ranked": "sum", "OnNetwork": "sum",})
    .rename(
        columns={
            "id": "inventory_small_barriers",
            "Included": "small_barriers",
            "OnNetwork": "on_network_small_barriers",
            "Ranked": "ranked_small_barriers",
        }
    )
)

crossing_stats = crossings[["HUC12", "id"]].groupby("HUC12").size().rename("crossings")

df = (
    huc12.join(dam_stats, how="left")
    .join(barriers_stats, how="left")
    .join(crossing_stats, how="left")
    .join(spp_df)
    .fillna(0)
)

int_cols = [c for c in df.columns if not c in {"HUC12", "name"}]
df[int_cols] = df[int_cols].astype("uint32")

df = df.reset_index()


with pd.ExcelWriter(out_dir / "sarp_huc12_stats.xlsx") as xlsx:
    df.to_excel(xlsx, sheet_name="all HUC12", index=False)
    df.loc[df.TESpp > 0].to_excel(xlsx, sheet_name="HUC12 with TE spps", index=False)
