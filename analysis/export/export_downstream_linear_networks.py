from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from pyarrow.dataset import dataset
from pyogrio import write_dataframe
import shapely

from analysis.constants import CRS
from analysis.lib.io import read_feathers
from analysis.lib.geometry.lines import merge_lines

src_dir = Path("data/networks")
out_dir = Path("/tmp/sarp")
out_dir.mkdir(exist_ok=True, parents=True)

# full network scenarios are: "dams", "combined_barriers", "largefish_barriers", "smallfish_barriers"
scenario = "dams"
# ext = "fgb"
# driver = "FlatGeobuf"
ext = "gdb"
driver = "OpenFileGDB"


groups_df = pd.read_feather(src_dir / "connected_huc2s.feather")

export_hucs = {
    # "01",
    # "02",
    "03"
    # "04",
    # "05",
    # "06",
    # "07",
    # "08",
    # "09",
    # "14",
    # "15",
    # "16",
    # "17",
    # "18",
    # "21"
}

for group in [{"03"}]:
    group = sorted(group)

    segments = (
        read_feathers(
            [src_dir / "clean" / huc2 / f"{scenario}_downstream_linear_segments.feather" for huc2 in group],
        )
        .set_index("lineID")
        .rename(columns={"id": "networkID"})
    )

    stats = (
        read_feathers(
            [src_dir / "clean" / huc2 / f"{scenario}_downstream_linear_network_stats.feather" for huc2 in group],
            columns=[
                "id",
                "total_linear_downstream_miles",
                "free_linear_downstream_miles",
                "free_perennial_linear_downstream_miles",
                "free_intermittent_linear_downstream_miles",
                "free_altered_linear_downstream_miles",
                "free_unaltered_linear_downstream_miles",
            ],
        )
        .rename(columns={"id": "networkID"})
        .set_index("networkID")
    )

    # select barriers with total mainstem miles
    barriers = read_feathers(
        [src_dir / "clean" / huc2 / "dams_network.feather" for huc2 in group],
        columns=["id", "TotalMainstemNetworkMiles"],
    )
    barriers = barriers.loc[barriers.TotalMainstemNetworkMiles > 0]
    export_barrier_ids = barriers.id.unique()
    segments = segments.loc[segments.networkID.isin(export_barrier_ids)]
    stats = stats.loc[stats.index.isin(export_barrier_ids)]

    # use smaller data types for smaller output files
    length_cols = [c for c in stats.columns if c.endswith("_miles")]
    for col in length_cols:
        stats[col] = stats[col].round(5).astype("float32")

    for kind in ["waterfalls", "dams", "small_barriers", "road_crossings"]:
        col = f"totd_{kind}"
        if col in stats.columns:
            stats[col] = stats[col].fillna(0).astype("uint32")

    for col in ["flows_to_ocean", "flows_to_great_lakes", "exits_region", "invasive_network"]:
        if col in stats.columns:
            stats[col] = stats[col].astype("uint8")

    # create output files by HUC2 based on where the segments occur
    for huc2 in group:
        if huc2 not in export_hucs:
            continue

        print(f"Dissolving networks in {huc2}...")

        # NOTE: the same flowline may belong to many networks

        # if export_barrier_ids:
        flowlines = (
            dataset(src_dir / "raw" / huc2 / "flowlines.feather", format="feather")
            .to_table(
                filter=pc.is_in(pc.field("lineID"), pa.array(np.unique(segments.index.unique()))),
                columns=[
                    "lineID",
                    "geometry",
                ],
            )
            .to_pandas()
        )
        flowlines = gp.GeoDataFrame(flowlines, geometry=shapely.from_wkb(flowlines.geometry.values), crs=CRS)

        flowlines = flowlines.set_index("lineID").join(segments, how="inner")

        networks = (
            merge_lines(flowlines, by=["networkID"])
            .set_index("networkID")
            .join(stats, how="inner")
            .reset_index()
            .sort_values(by="networkID")
        )

        print(f"Serializing {len(networks):,} dissolved networks...")
        write_dataframe(networks, out_dir / f"region{huc2}_{scenario}_linear_downstream_networks.{ext}", driver=driver)
