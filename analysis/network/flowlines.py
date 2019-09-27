from pathlib import Path
from time import time

from nhdnet.nhd.cut import cut_flowlines
from nhdnet.io import (
    deserialize_df,
    deserialize_gdf,
    to_shp,
    serialize_df,
    serialize_gdf,
)
from analysis.constants import REGION_GROUPS

data_dir = Path("data")
nhd_dir = data_dir / "nhd/flowlines"


def cut_flowlines_at_barriers(region, barriers):
    """Read in flowlines and joins between segments, cut flowlines at barriers, and return updated
    flowlines, joins, and joins at each of the barriers
    
    Parameters
    ----------
    region : str
        ID of region group
    barriers : GeoDataFrame
        Barriers to cut the network
    
    Returns
    -------
    (GeoDataFrame, DataFrame, DataFrame)
        cut flowlines, updated joins, barrier joins
    """

    ### Read NHD flowlines and joins
    print("Reading flowlines...")
    flowline_start = time()
    flowlines = (
        deserialize_gdf(nhd_dir / region / "flowline.feather")
        .set_index("lineID", drop=False)
        .drop(columns=["HUC2"], errors="ignore")
    )
    joins = deserialize_df(nhd_dir / region / "flowline_joins.feather")
    print(
        "Read {:,} flowlines in {:.2f}s".format(len(flowlines), time() - flowline_start)
    )

    ### Cut flowlines at barriers
    cut_start = time()

    # since all other lineIDs use HUC4 prefixes, this should be unique
    # Use the first HUC2 for the region group
    next_segment_id = int(REGION_GROUPS[region][0]) * 1000000 + 1
    flowlines, joins, barrier_joins = cut_flowlines(
        flowlines, barriers, joins, next_segment_id=next_segment_id
    )

    print("Done cutting flowlines in {:.2f}".format(time() - cut_start))

    return flowlines, joins, barrier_joins


def save_cut_flowlines(out_dir, flowlines, joins, barrier_joins):
    """Save cut flowline data frames to disk for QA.
    
    Parameters
    ----------
    out_dir : str
    flowlines : GeoDataFrame
        cut flowlines
    joins : DataFrame
        updated joins
    barrier_joins : DataFrame
        barrier joins
    """

    print("serializing {:,} cut flowlines...".format(len(flowlines)))
    start = time()

    serialize_gdf(flowlines, out_dir / "split_flowlines.feather", index=False)
    serialize_df(joins, out_dir / "updated_joins.feather", index=False)
    serialize_df(barrier_joins, out_dir / "barrier_joins.feather", index=False)

    print("Done serializing cut flowlines in {:.2f}s".format(time() - start))
