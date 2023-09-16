from pathlib import Path
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
from pyogrio import read_dataframe, write_dataframe
import shapely

from analysis.constants import CRS
from analysis.lib.graph.speedups import DirectedGraph
from analysis.lib.geometry.lines import merge_lines, fill_endpoint_gaps
from analysis.lib.util import append

warnings.filterwarnings("ignore", category=UserWarning, message=".*Measured.*")


MIN_LENGTH = 1  # meters;
MAX_GAP = 5  # meters; maximum space between endpoints to bridge
# the maximum distance between lines in a group is primarily used to prevent
# tracing the downstream path from one to another causing those groups to be
# combined; however, there are large false gaps in StreamNet due to missing
# segments on mainstems that look like valid habitat
# NOTE: it is not a problem to join groups across ridgelines; there is no
# downstream path that will connect them
MAX_GROUP_DISTANCE = 1000  # meters

data_dir = Path("data")
src_dir = data_dir / "species/source"

infilename = (
    src_dir
    / "Generalized Fish Distribution - All Species Combined (StreamNet - January 2019)/StreamNet_20190131.gdb"
)
layer = "FishDist_AllSpeciesCombined_20190131"
keep_species = [
    "Bonneville cutthroat trout",
    "Bull trout",
    "Chinook salmon",
    "Chum salmon",
    "Coastal cutthroat trout",
    "Coho salmon",
    "Cutthroat trout",
    "Green sturgeon",
    "Kokanee",
    "Pacific lamprey",
    "Pink salmon",
    "Rainbow trout",
    "Redband trout",
    "Sockeye salmon",
    "Steelhead",
    "Westslope cutthroat trout",
    "White sturgeon",
    "Yellowstone cutthroat trout",
]


print("Reading StreamNet habitat data")
df = read_dataframe(
    infilename,
    layer=layer,
    use_arrow=True,
    columns=["Species", "Run", "LifeHistoryType"],
)

df = df.loc[
    df.Species.isin(keep_species) & (~shapely.is_empty(df.geometry.values))
].copy()
df["geometry"] = shapely.force_2d(df.geometry.values)
df = df.to_crs(CRS)

df["unit"] = df.Species
ix = df.Run != "N/A"
df.loc[ix, "unit"] += " (" + df.loc[ix].Run.str.lower() + ")"

df = df[["unit", "geometry"]].explode(ignore_index=True)

# first, drop any identical duplicates
print("Dropping duplicates")
df["hash"] = pd.util.hash_array(shapely.to_wkb(df.geometry.values))
df = gp.GeoDataFrame(
    df.groupby(by=["unit", "hash"]).first().reset_index()[["unit", "geometry"]],
    geometry="geometry",
    crs=CRS,
)

merged = None
for unit in sorted(df.unit.unique()):
    print(f"\n------------- Processing {unit}-------------")
    spp_df = df.loc[df.unit == unit].reset_index(drop=True)

    # Merge habitat linework for species
    # use unary union (not dissolve!) with a lower grid size followed by merge lines
    # in order to properly dissolve overlapping lines
    # use grid_size to coalesce very near parallel lines
    geometry = shapely.unary_union(spp_df.geometry.values, grid_size=0.01)
    spp_df = merge_lines(
        gp.GeoDataFrame({"unit": [unit]}, geometry=[geometry], crs=CRS).explode(
            ignore_index=True
        ),
        by="unit",
    ).explode(ignore_index=True)

    # fill short gaps in habitat linework; these cause issues later
    filled = fill_endpoint_gaps(spp_df, gap_size=MAX_GAP)
    filled_count = len(filled) - len(spp_df)
    if filled_count:
        print(f"Filled {filled_count:,} gaps between endoints <= {MAX_GAP}m")
        geometry = shapely.unary_union(filled.geometry.values)
        spp_df = merge_lines(
            gp.GeoDataFrame({"unit": [unit]}, geometry=[geometry], crs=CRS).explode(
                ignore_index=True
            ),
            by="unit",
        ).explode(ignore_index=True)

    # drop isolated slivers that are shorter than MIN_LENGTH
    spp_df = spp_df.loc[
        shapely.length(spp_df.geometry.values) >= MIN_LENGTH
    ].reset_index(drop=True)

    # assign group based on connected lines
    # due to topology / geometry issues in the data, there may still be some
    # small gaps; this attempts to bridge those using MAX_GROUP_DISTANCE
    tree = shapely.STRtree(spp_df.geometry.values)
    left, right = tree.query(
        spp_df.geometry.values, predicate="dwithin", distance=MAX_GROUP_DISTANCE
    )
    # add symmetric pairs
    groups = DirectedGraph(
        np.concatenate([left, right]), np.concatenate([right, left])
    ).components()
    groups = (
        pd.DataFrame(
            {i: list(g) for i, g in enumerate(groups)}.items(),
            columns=["group", "index"],
        )
        .explode("index")
        .set_index("index")
    )
    spp_df = spp_df.join(groups)

    merged = append(merged, spp_df)


df = merged.reset_index(drop=True)

df.to_feather(src_dir / "streamnet_habitat.feather")
write_dataframe(df, src_dir / "streamnet_habitat.fgb")
