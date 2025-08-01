from pathlib import Path
import os
from time import time
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
import pyarrow as pa
from pyarrow.feather import write_feather
import pyarrow.compute as pc
import shapely

from analysis.constants import CRS, SIZECLASSES, BARRIER_KINDS, FLOWLINE_JOIN_TYPES
from analysis.lib.graph.speedups.directedgraph import DirectedGraph
from analysis.lib.flowlines import cut_flowlines_at_barriers
from analysis.lib.io import read_arrow_tables
from analysis.network.lib.networks import connect_huc2s

warnings.filterwarnings("ignore", message=".*invalid value encountered in line_locate_point.*")


data_dir = Path("data")
barriers_dir = data_dir / "barriers/snapped"
nhd_dir = data_dir / "nhd/clean"
waterbodies_dir = data_dir / "waterbodies"
wetlands_dir = data_dir / "wetlands"
out_dir = data_dir / "networks/raw"
out_dir.mkdir(exist_ok=True, parents=True)

huc2_df = pd.read_feather(data_dir / "boundaries/huc2.feather", columns=["HUC2"])
huc2s = sorted(huc2_df.HUC2.values)

# manually subset keys from above for processing
# huc2s = [
#     "01",
#     "02",
#     "03",
#     "04",
#     "05",
#     "06",
#     "07",
#     "08",
#     "09",
#     "10",
#     "11",
#     "12",
#     "13",
#     "14",
#     "15",
#     "16",
#     "17",
#     "18",
#     "19",
#     "20",
#     "21",
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
)

all_joins, groups = connect_huc2s(all_joins, huc2s)
print(f"Found {len(groups)} HUC2 groups in {time() - start:,.2f}s")

# recode type and HUC2 (we have to do this after reworking the joins)
join_type_values = pa.array(FLOWLINE_JOIN_TYPES)
huc2_values = pa.array(huc2s)
all_joins = pa.Table.from_pydict(
    {
        **{c: all_joins[c] for c in all_joins.column_names if c not in {"type", "HUC2"}},
        "type": pa.DictionaryArray.from_arrays(
            pc.cast(pc.index_in(all_joins["type"].combine_chunks(), join_type_values), pa.int8()), join_type_values
        ),
        "HUC2": pa.DictionaryArray.from_arrays(
            pc.cast(pc.index_in(all_joins["HUC2"].combine_chunks(), huc2_values), pa.int8()), huc2_values
        ),
    }
)


# remove any joins after joining regions that are marine but have an upstream of 0
# (likely due to joins with regions not included in analysis)
all_joins = all_joins.filter(pc.equal(pc.and_(all_joins["marine"], pc.equal(all_joins["upstream_id"], 0)), False))

# persist table of connected HUC2s
connected_huc2s = pd.DataFrame({"HUC2": groups}).explode(column="HUC2")
connected_huc2s["group"] = connected_huc2s.index.astype("uint8")
connected_huc2s.reset_index(drop=True).to_feather(data_dir / "networks/connected_huc2s.feather")


# find junctions (downstream_id with multiple upstream_id values)
num_upstreams = (
    all_joins.select(["downstream_id", "upstream_id"])
    .filter(pc.not_equal(all_joins["downstream_id"], 0))
    .group_by("downstream_id")
    .aggregate([("upstream_id", "count_distinct")])
    .rename_columns({"upstream_id_count_distinct": "num_upstream"})
)
multiple_upstreams = num_upstreams.filter(pc.greater(num_upstreams["num_upstream"], 1))[
    "downstream_id"
].combine_chunks()
all_joins = pa.Table.from_pydict(
    {
        **{c: all_joins[c] for c in all_joins.column_names},
        "junction": pc.is_in(all_joins["downstream_id"], multiple_upstreams),
    }
)


### Aggregate barriers
# NOTE: any barriers on loops or off-network flowlines have already been removed
# from the snapped barrier data.  All barriers in this dataset cut the raw
# networks, but subsets of them are used to create different network scenarios
print("Aggregating barriers")
all_barriers = read_arrow_tables(
    [barriers_dir / f"{kind}s.feather" for kind in BARRIER_KINDS],
    new_fields={"kind": BARRIER_KINDS},
    dict_fields={"kind"},
)
filled = {
    # removed is not applicable for road crossings or waterfalls, backfill with False
    "removed": pc.fill_null(all_barriers["removed"], False),
    "YearRemoved": pc.fill_null(all_barriers["YearRemoved"], 0),
    # invasive is not applicable for road crossings, backfill with False
    "invasive": pc.fill_null(all_barriers["invasive"], False),
}
all_barriers = pa.Table.from_pydict(
    {**{c: all_barriers[c] for c in all_barriers.column_names if c not in filled.keys()}, **filled},
    metadata=all_barriers.schema.metadata,
)
write_feather(all_barriers, out_dir / "all_barriers.feather")


### Cut flowlines in each HUC2
for huc2 in huc2s:
    region_start = time()
    print(f"----- {huc2} ------")

    huc2_dir = out_dir / huc2

    if not huc2_dir.exists():
        os.makedirs(huc2_dir)

    barriers = all_barriers.filter(pc.equal(all_barriers["HUC2"], huc2)).combine_chunks()
    barriers = gp.GeoDataFrame(
        barriers.drop(["HUC2", "geometry"]).to_pandas(),
        geometry=shapely.from_wkb(barriers["geometry"].to_numpy()),
        crs=CRS,
    ).set_index("id", drop=False)

    joins = all_joins.filter(pc.equal(all_joins["HUC2"], huc2)).drop(["HUC2"]).to_pandas()

    ##################### Cut flowlines at barriers #################
    ### Read NHD flowlines and joins
    print("Reading flowlines...")
    flowline_start = time()

    flowlines = pa.dataset.dataset(nhd_dir / huc2 / "flowlines.feather", format="feather").to_table(
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
            "sizeclass",
            "length",
            "intermittent",
            "altered",
            "waterbody",
        ],
        # exclude loops and off-network flowlines
        filter=(pc.field("loop") == False) & (pc.field("offnetwork") == False),  # noqa
    )

    sizeclass_values = pa.array(SIZECLASSES)
    flowlines = pa.Table.from_pydict(
        {
            **{c: flowlines[c] for c in flowlines.column_names if c != "sizeclass"},
            # NOTE: this converts blank size classes to nulls so they are excluded from stats
            "sizeclass": pa.DictionaryArray.from_arrays(
                pc.cast(pc.index_in(flowlines["sizeclass"].combine_chunks(), sizeclass_values), pa.int8()),
                sizeclass_values,
            ),
        }
    )

    flowlines = gp.GeoDataFrame(
        flowlines.drop(["geometry"]).to_pandas(), geometry=shapely.from_wkb(flowlines["geometry"].to_numpy()), crs=CRS
    ).set_index("lineID", drop=False)

    print(f"Read {len(flowlines):,} flowlines in {time() - flowline_start:.2f}s")

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

    # convert sizeclass to categorical for smaller data / memory footprint
    flowlines = flowlines.reset_index(drop=True)
    flowlines.to_feather(huc2_dir / "flowlines.feather")

    joins.reset_index(drop=True).to_feather(huc2_dir / "flowline_joins.feather")
    barrier_joins.reset_index(drop=True).to_feather(huc2_dir / "barrier_joins.feather")

    ### Build lookup table of flowlines to non-impounded / unaltered waterbodies (excluding Great Lakes)
    tree = shapely.STRtree(flowlines.geometry.values)

    print("Joining segments to waterbodies")
    waterbodies = (
        pa.dataset.dataset(waterbodies_dir / huc2 / "waterbodies.feather", format="feather")
        .to_table(
            filter=(~(pc.is_in(pc.field("wbID"), dam_wbid)))
            & (pc.field("altered") == False)  # noqa: E712
            & (pc.field("km2") < 8000),  # exclude Great Lakes
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
            "km2": waterbodies.km2.values.take(left).astype("float32"),
        }
    )

    # drop any waterbodies now marked as altered because of impoundments above
    drop_ids = pairs.loc[pairs.lineID.isin(flowlines.loc[flowlines.impoundment].lineID.unique())].wbID.unique()
    pairs = pairs.loc[~pairs.wbID.isin(drop_ids)].reset_index(drop=True)
    pairs.to_feather(huc2_dir / "flowline_waterbodies.feather")

    ### Build lookup table of flowlines to wetlands
    print("Joining cut segments to wetlands")
    wetlands = gp.read_feather(wetlands_dir / huc2 / "wetlands.feather", columns=["geometry", "id", "km2"])
    left, right = tree.query(wetlands.geometry.values, predicate="intersects")
    pairs = pd.DataFrame(
        {
            "lineID": flowlines.lineID.values.take(right),
            "wetlandID": wetlands.id.values.take(left),
            "km2": wetlands.km2.values.take(left).astype("float32"),
        }
    )
    pairs.to_feather(huc2_dir / "flowline_wetlands.feather")

    print(f"Region done in {time() - region_start:.2f}s\n\n")

print("All done in {:.2f}s".format(time() - start))
