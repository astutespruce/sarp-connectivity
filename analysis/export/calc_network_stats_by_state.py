from pathlib import Path

import geopandas as gp
import pandas as pd
import shapely

from analysis.constants import METERS_TO_MILES, NETWORK_TYPES
from analysis.lib.io import read_arrow_tables, read_feathers
from analysis.lib.util import append


data_dir = Path("data")
networks_dir = data_dir / "networks"
raw_dir = networks_dir / "raw"
clean_dir = networks_dir / "clean"


huc2_group_df = pd.read_feather(networks_dir / "connected_huc2s.feather").sort_values(by=["group", "HUC2"])
huc2s = huc2_group_df.HUC2.values
groups = huc2_group_df.groupby("group").HUC2.apply(list).tolist()

states = gp.read_feather(data_dir / "boundaries/states.feather", columns=["id", "geometry"]).explode(ignore_index=True)


# first, clip segments by state, but will have to aggregate to state across all segments
merged_lengths = None
for huc2 in sorted(huc2s):
    print(f"Clipping flowlines to states for {huc2}")
    flowlines = gp.read_feather(raw_dir / huc2 / "flowlines.feather", columns=["lineID", "geometry"])

    left, right = shapely.STRtree(flowlines.geometry.values).query(states.geometry.values, predicate="intersects")
    pairs = pd.DataFrame(
        {
            "lineID": flowlines.lineID.values.take(right),
            "geometry": flowlines.geometry.values.take(right),
            "state": states.id.values.take(left),
            "state_geom": states.geometry.values.take(left),
        }
    )
    shapely.prepare(pairs.state_geom.values)
    ix = ~shapely.contains_properly(pairs.state_geom.values, pairs.geometry.values)
    pairs.loc[ix, "geometry"] = shapely.intersection(pairs.loc[ix].geometry.values, pairs.loc[ix].state_geom.values)
    pairs["miles"] = shapely.length(pairs.geometry.values) * METERS_TO_MILES

    lengths = pairs[["state", "lineID", "miles"]]
    merged_lengths = append(merged_lengths, lengths)

network_types = ["full", "dams_only", "dams", "combined_barriers"]
segments = read_feathers(
    [clean_dir / huc2 / "network_segments.feather" for huc2 in huc2s],
    columns=["lineID"] + network_types,
).set_index("lineID")

networks = segments.join(merged_lengths.set_index("lineID")).dropna(subset=["state", "miles"])
networks = networks.loc[networks.miles > 0].copy()


stats = None
for col in network_types:
    avg_length = (
        networks.groupby(["state", col])
        .miles.sum()
        .reset_index()
        .groupby("state")
        .miles.median()
        # .mean()
        .rename(f"{col}_avg_network_miles")
    )

    if stats is None:
        stats = pd.DataFrame(avg_length)
    else:
        stats = stats.join(avg_length)

stats.reset_index().to_feather("/tmp/state_stats.feather")
stats.reset_index().to_excel("/tmp/sarp/state_avg_network_stats.xlsx", index=False)


# Dendritic connectivity index
# # TODO: do this by state too
# tmp = networks.groupby(["full", "dams_only"]).miles.sum().reset_index()
# full_lengths = tmp.groupby("full").miles.sum()
# tmp = tmp.join(full_lengths.rename("total_miles"), on="full")
# tmp["dci"] = (tmp.miles * tmp.miles) / (tmp.total_miles * tmp.total_miles)
# dci = tmp.groupby("full").dci.sum()

# dci.reset_index().to_feather("/tmp/dci.feather")
