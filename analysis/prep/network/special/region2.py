"""Generate list of NHDPlusIDs that intersect with Chesapeake Bay so that we can remove them"""


from pathlib import Path
import os

import numpy as np
import pandas as pd
import geopandas as gp
import pygeos as pg

from pyogrio import read_dataframe, write_dataframe

from analysis.lib.util import append
from analysis.lib.geometry import sjoin_geometry
from analysis.constants import CRS


REMOVE_WB_NAMES = ["Chesapeake Bay"]
REMOVE_WB_NHDPLUSID = [10000200354061]  # Delaware Bay


data_dir = Path("data/nhd/")
src_dir = data_dir / "source/huc4"

merged = None
for huc4 in ["0204", "0208"]:
    gdb = src_dir / huc4 / f"NHDPLUS_H_{huc4}_HU4_GDB.gdb"

    wb = read_dataframe(
        gdb, layer="NHDWaterbody", columns=["geometry", "NHDPlusID", "GNIS_Name"]
    )

    # Extract out Chesapeake Bay and Delaware Bay
    wb = wb.loc[
        wb.GNIS_Name.isin(REMOVE_WB_NAMES) | wb.NHDPlusID.isin(REMOVE_WB_NHDPLUSID)
    ].copy()

    merged = append(merged, wb)

wb = merged.to_crs(CRS).reset_index(drop=True)

flowlines = gp.read_feather(
    data_dir / "raw/02/flowlines.feather",
    columns=["geometry", "lineID", "NHDPlusID", "FType"],
)

# Filter out artificial paths only
flowlines = flowlines.loc[flowlines.FType == 558].reset_index(drop=True)


joined = sjoin_geometry(
    pd.Series(wb.geometry.values.data, index=wb.index),
    pd.Series(flowlines.geometry.values.data, index=flowlines.index),
)

joined = (
    wb[["geometry"]]
    .join(joined, how="inner")
    .join(flowlines.rename(columns={"geometry": "flowline"}), on="index_right")
)
joined["overlap"] = pg.length(
    pg.intersection(joined.geometry.values.data, joined.flowline.values.data)
)

ix = joined.overlap / pg.length(joined.flowline.values.data) > 0.9

# Hardcode this result in constants.py
remove_ids = np.sort(joined.loc[ix].NHDPlusID.unique())

# add in invalid loops
remove_ids = np.concatenate([remove_ids, [10000300073811, 10000300021333]])

# add in manually selected IDs
remove_ids = np.concatenate(
    [
        remove_ids,
        [
            10000300135353,
            10000300133504,
            10000300145587,
            10000300170313,
            10000300071775,
            10000300024437,
            10000300059454,
            10000300135352,
            10000300049075,
            10000300096526,
            10000300010493,
            10000300184385,
            10000300172151,
            10000300024439,
            10000300108656,
            10000300120911,
            10000300120953,
            10000300059411,
            10000300059410,
            10000300108656,
            10000300000015,
            10000300110635,
            10000300157938,
            10000300159825,
            10000300010334,
            10000300157939,
            10000300108720,
            10000300170276,
        ],
    ]
)


pd.DataFrame({"NHDPlusID": np.unique(remove_ids)}).to_feather(
    data_dir / "raw/02/remove_flowlines.feather"
)
