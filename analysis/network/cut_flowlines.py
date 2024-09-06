from pathlib import Path
import os
from time import time
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import shapely

from analysis.constants import CRS
from analysis.lib.graph.speedups.directedgraph import DirectedGraph
from analysis.lib.flowlines import cut_flowlines_at_barriers
from analysis.lib.io import read_feathers, read_arrow_tables
from analysis.network.lib.networks import connect_huc2s

warnings.filterwarnings("ignore", message=".*invalid value encountered in line_locate_point.*")


data_dir = Path("data")
barriers_dir = data_dir / "barriers/snapped"
nhd_dir = data_dir / "nhd/clean"
waterbodies_dir = data_dir / "waterbodies"
wetlands_dir = data_dir / "wetlands"
out_dir = data_dir / "networks/raw"

huc2_df = pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"])
huc2s = huc2_df.HUC2.sort_values().values

# manually subset keys from above for processing
# huc2s = [
# "01",
# "02",
# "03",
# "04",
# "05",
# "06",
# "07",
# "08",
# "09",
# "10",
# "11",
# "12",
# "13",
# "14",
# "15",
# "16",
# "17",
# "18",
# "19",
# "20",
# "21",
# ]


start = time()

### Find connected HUC2s and update joins at HUC2 boundaries
print("Finding connected HUC2s")
# NOTE: drop all loops from the analysis
all_joins = read_arrow_tables(
    [nhd_dir / huc2 / "flowline_joins.feather" for huc2 in huc2s],
    columns=[
        "upstream",
        "downstream",
        "upstream_id",
        "downstream_id",
        "type",
        "marine",
        "great_lakes",
    ],
    new_fields={"HUC2": huc2s},
    filter=pc.field("loop") == False,  # noqa
).to_pandas()

groups, all_joins = connect_huc2s(all_joins)
groups = sorted(groups)
print(f"Found {len(groups)} HUC2 groups in {time() - start:,.2f}s")

# remove any joins after joining regions that are marine but have an upstream of 0
# (likely due to joins with regions not included in analysis)
all_joins = all_joins.loc[~(all_joins.marine & (all_joins.upstream_id == 0))].copy()

# persist table of connected HUC2s
connected_huc2s = pd.DataFrame({"HUC2": groups}).explode(column="HUC2")
connected_huc2s["group"] = connected_huc2s.index.astype("uint8")
connected_huc2s.reset_index(drop=True).to_feather(data_dir / "networks/connected_huc2s.feather")


# find junctions (downstream_id with multiple upstream_id valeus)
num_upstreams = all_joins.loc[all_joins.downstream_id != 0].groupby("downstream_id").size()
multiple_upstreams = num_upstreams[num_upstreams > 1].index.values
all_joins["junction"] = all_joins.downstream_id.isin(multiple_upstreams)


### Aggregate barriers
# NOTE: any barriers on loops or off-network flowlines have already been removed
# from the snapped barrier data.  All barriers in this dataset cut the raw
# networks, but subsets of them are used to create different network scenarios
print("Aggregating barriers")
kinds = ["waterfall", "dam", "small_barrier", "road_crossing"]
all_barriers = read_feathers(
    [barriers_dir / f"{kind}s.feather" for kind in kinds],
    geo=True,
    new_fields={"kind": kinds},
).set_index("id", drop=False)

# removed is not applicable for road crossings or waterfalls, backfill with False
all_barriers["removed"] = all_barriers.removed.fillna(0).astype("bool")
all_barriers["YearRemoved"] = all_barriers.YearRemoved.fillna(0).astype("uint16")

# invasive is not applicable for road crossings, backfill with False
all_barriers["invasive"] = all_barriers.invasive.fillna(0).astype("bool")

print(f"Serializing {len(all_barriers):,} barriers")
all_barriers.to_feather(out_dir / "all_barriers.feather")


### Cut flowlines in each HUC2
for huc2 in huc2s:
    region_start = time()
    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2

    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    barriers = all_barriers.loc[(all_barriers.HUC2 == huc2)].drop(columns=["HUC2"])
    joins = all_joins.loc[all_joins.HUC2 == huc2].drop(columns=["HUC2"])

    ##################### Cut flowlines at barriers #################
    ### Read NHD flowlines and joins
    print("Reading flowlines...")
    flowline_start = time()

    flowlines = (
        pa.dataset.dataset(nhd_dir / huc2 / "flowlines.feather", format="feather")
        .to_table(
            columns=[
                "lineID",
                "NHDPlusID",
                "FCode",
                "FType",
                "GNIS_Name",
                "geometry",
                "StreamOrder",
                "StreamLevel",  # used to create network tiles
                "AreaSqKm",
                "TotDASqKm",
                "AnnualFlow",
                "AnnualVelocity",
                "loop",
                "sizeclass",
                "length",
                "intermittent",
                "altered",
                "waterbody",
            ],
            # exclude loops and off-network flowlines
            filter=(pc.field("loop") == False) & (pc.field("offnetwork") == False),  # noqa
        )
        .to_pandas()
        .set_index("lineID", drop=False)
    )
    flowlines["geometry"] = shapely.from_wkb(flowlines.geometry.values)
    flowlines = gp.GeoDataFrame(flowlines, geometry="geometry", crs=CRS)
    print(f"Read {len(flowlines):,} flowlines in {time() - flowline_start:.2f}s")

    # increment lineIDs before dropping loops
    next_segment_id = flowlines.lineID.max() + np.uint32(1)

    flowlines, joins, barrier_joins = cut_flowlines_at_barriers(
        flowlines, joins, barriers, next_segment_id=next_segment_id
    )

    barrier_joins = barrier_joins.join(barriers.kind)

    ### mark likely impoundments (waterbody flowlines upstream of dam joins)
    dam_joins = barrier_joins.loc[barrier_joins.kind == "dam"].copy()
    wb_flowline_ids = flowlines.loc[flowlines.waterbody].lineID.values
    wb_joins = joins.loc[
        # only include waterbody flowlines in network
        joins.upstream_id.isin(wb_flowline_ids)
        # break at any dams
        & ~joins.upstream_id.isin(dam_joins.upstream_id.unique())
        & (joins.upstream_id != 0)
        & (joins.downstream_id != 0),
        ["upstream_id", "downstream_id"],
    ]
    graph = DirectedGraph(wb_joins.downstream_id.values.astype("int64"), wb_joins.upstream_id.values.astype("int64"))

    start_ids = dam_joins.loc[dam_joins.upstream_id.isin(wb_flowline_ids)].upstream_id.unique()

    ### also bring in drains of any waterbodies associated with dams, so that we
    # can mark all flowlines in these waterbodies as impoundments
    dam_wbid = (
        pa.dataset.dataset(data_dir / "barriers/master/dams.feather", format="feather")
        .to_table(
            filter=(pc.field("HUC2") == huc2)
            & (pc.field("primary_network") == True)  # noqa
            & (~pc.is_null(pc.field("wbID"))),
            columns=["wbID"],
        )["wbID"]
        .combine_chunks()
    )

    if len(dam_wbid):
        drain_line_ids = (
            pa.dataset.dataset(nhd_dir / huc2 / "waterbody_drain_points.feather", format="feather")
            .to_table(filter=pc.is_in(pc.field("wbID"), dam_wbid), columns=["lineID"])["lineID"]
            .to_numpy()
            .astype("uint32")
        )

        start_ids = np.unique(np.concatenate([start_ids, drain_line_ids]))

    impoundment_ids = graph.network_pairs(start_ids.astype("int64")).T[1]
    impoundment_ids = np.unique(impoundment_ids[impoundment_ids != 0])
    flowlines["impoundment"] = flowlines.lineID.isin(impoundment_ids)
    flowlines["altered"] = flowlines.altered | flowlines.impoundment

    print(f"Serializing {len(flowlines):,} cut flowlines...")
    flowlines = flowlines.reset_index(drop=True)
    flowlines.to_feather(huc2_dir / "flowlines.feather")

    joins.reset_index(drop=True).to_feather(huc2_dir / "flowline_joins.feather")
    barrier_joins.reset_index(drop=True).to_feather(
        huc2_dir / "barrier_joins.feather",
    )

    ### Build lookup table of flowlines to non-impounded / unaltered waterbodies
    tree = shapely.STRtree(flowlines.geometry.values)

    print("Joining segments to waterbodies")
    waterbodies = (
        pa.dataset.dataset(waterbodies_dir / huc2 / "waterbodies.feather", format="feather")
        .to_table(
            filter=(~(pc.is_in(pc.field("wbID"), dam_wbid))) & (pc.field("altered") == False),  # noqa: E712
            columns=["geometry", "wbID", "km2", "altered"],
        )
        .to_pandas()
    )
    waterbodies = gp.GeoDataFrame(waterbodies, geometry=shapely.from_wkb(waterbodies.geometry.values), crs=CRS)
    left, right = tree.query(waterbodies.geometry.values, predicate="intersects")
    pairs = pd.DataFrame(
        {
            "lineID": flowlines.lineID.values.take(right),
            "wbID": waterbodies.wbID.values.take(left),
            "km2": waterbodies.km2.values.take(left),
        }
    )
    pairs.to_feather(huc2_dir / "flowline_waterbodies.feather")

    ### Build lookup table of flowlines to wetlands
    print("Joining cut segments to wetlands")
    wetlands = gp.read_feather(wetlands_dir / huc2 / "wetlands.feather", columns=["geometry", "id", "km2"])
    left, right = tree.query(wetlands.geometry.values, predicate="intersects")
    pairs = pd.DataFrame(
        {
            "lineID": flowlines.lineID.values.take(right),
            "wetlandID": wetlands.id.values.take(left),
            "km2": wetlands.km2.values.take(left),
        }
    )
    pairs.to_feather(huc2_dir / "flowline_wetlands.feather")

    print(f"Region done in {time() - region_start:.2f}s\n\n")

print("All done in {:.2f}s".format(time() - start))
