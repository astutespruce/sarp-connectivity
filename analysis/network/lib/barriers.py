from pathlib import Path
from time import time

import geopandas as gp
from pyogrio.geopandas import write_dataframe


# ID ranges for each type
WATERFALLS_ID = 1e6
DAMS_ID = 2 * 1e6
SB_ID = 3 * 1e6


barriers_dir = Path("data/barriers/snapped")


def read_barriers(huc2, mode):
    """Read files created by prep_dams.py, prep_waterfalls.py, prep_small_barriers.py
    Merge together and assign uniqueID for internal use in network analysis

    NOTE: barriers on loops are dropped

    Parameters
    ----------
    huc2 : str
    mode : str
        One of "natural", "dams", "small_barriers"

    Returns
    -------
    GeoDataFrame
        Merged barriers file
    """

    start = time()

    wf = gp.read_feather(barriers_dir / "waterfalls.feather")
    wf = wf.loc[wf.HUC2 == huc2].copy()

    wf["barrierID"] = WATERFALLS_ID + wf.id
    wf["kind"] = "waterfall"

    barriers = wf

    if mode != "natural":
        dams = gp.read_feather(barriers_dir / "dams.feather")
        dams = dams.loc[dams.HUC2 == huc2].copy()

        dams["barrierID"] = DAMS_ID + dams.id
        dams["kind"] = "dam"

        if len(dams):
            barriers = barriers.append(dams, ignore_index=True, sort=False)

    if mode == "small_barriers":
        sb = gp.read_feather(barriers_dir / "small_barriers.feather")
        sb = sb.loc[sb.HUC2 == huc2].copy()

        sb["barrierID"] = SB_ID + sb.id
        sb["kind"] = "small_barrier"

        if len(sb):
            barriers = barriers.append(sb, ignore_index=True, sort=False)

    barriers.barrierID = barriers.barrierID.astype("uint64")

    ix = barriers.loop == True
    print(f"Found {ix.sum():,} barriers on loops, dropping")
    barriers = barriers.loc[~ix].copy()

    print(f"Extracted {len(barriers):,} barriers in {time() - start:.2f}s")
    print(barriers.groupby("kind").size())

    return barriers[
        ["geometry", "id", "lineID", "NHDPlusID", "barrierID", "kind", "intermittent"]
    ].set_index("barrierID", drop=False)


def save_barriers(out_dir, barriers):
    """Save consolidated barriers to disk for QA.

    Parameters
    ----------
    out_dir : str
    barriers : GeoDataFrame
    """

    print("Serializing {:,} barriers...".format(len(barriers)))

    tmp = barriers.reset_index(drop=True)
    tmp.to_feather(out_dir / "barriers.feather")
    write_dataframe(tmp, out_dir / "barriers.fgb")
