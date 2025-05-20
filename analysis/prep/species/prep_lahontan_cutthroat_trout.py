from pathlib import Path
import warnings

import geopandas as gp
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from pyogrio import read_dataframe, write_dataframe
import shapely

from analysis.constants import CRS

from analysis.lib.io import read_arrow_tables

warnings.filterwarnings("ignore", category=UserWarning, message=".*Measured.*")

SELECTION_TOLERANCE = 10  # meters; used to select flowlines that are near habitat
# outer overlap used to check overlap of flowlines filled in gaps
OUTER_OVERLAP_TOLERANCE = 300  # meters;
ENDPOINT_TOLERANCE = 1  # meters; used to determine if endpoints are on habitat
MIN_LINE_LENGTH = 10  # meters
# required amount of overlap required beween flowline and buffer around habitat line
MIN_OVERLAP_RATIO = 0.5  # proportion
MIN_DOWNSTREAM_OVERLAP_RATIO = 0.25  # proportion
MAX_LENGTH_DIFF = 2000  # meters
MAX_ENDPOINT_DIFF = 1000  # meters


data_dir = Path("data")
src_dir = data_dir / "species/source"
# must use raw data to be able to join on NHDPlusID later
nhd_dir = data_dir / "nhd/raw"
out_dir = data_dir / "species/derived"

infilename = src_dir / "Trout_EPA_forBrendan.gdb"
layer = "Lines_Lahontan_Cutthroat_Trout_TU"

# manually-identified keep lines (NHDPlusIDs):
# NOTE: these are not necessarily perfect fits but represent reasonable compromise
# of selecting a flowline with enough overlap with habitat
keep_line_ids = np.array(
    [
        70000500058214,
        70000500058228,
        70000100128495,
        70000500050233,
        70000500108492,
        70000500101642,
        70000500038070,
        70000100158003,
        70000100199701,
        70000500029945,
        70000300009244,
        70000300003804,
        70000500050826,
        70000500143748,
        70000500051635,
        70000300011641,
    ]
)

# manually identified lines that are not habitat
disallowed_line_ids = np.array(
    [
        70000300058156,
        70000300058074,
        70000300058137,
        70000300053418,
        70000300058140,
        70000300069035,
        70000300070723,
        70000300068537,
        70000300068598,
        70000300068549,
        70000300001302,
        70000300037227,
        70000300037285,
        70000300037191,
        70000300037192,
        70000300037193,
        70000500067756,
        70000500046945,
        70000500046997,
        70000500046788,
        70000500051432,
        70000500058025,
        70000500058070,
        70000500058027,
        70000500058055,
        70000500139411,
        70000500142216,
        70000500140017,
    ]
)


df = read_dataframe(infilename, layer=layer, columns=["NHDPlusID"], use_arrow=True).to_crs(CRS)
df["geometry"] = shapely.force_2d(df.geometry.values)

################################################################################
### Load flowlines in HUC4s with species data
################################################################################
print("\n-------------------------------------------------------------------\n")
print("Loading flowlines and joins")
huc4_df = gp.read_feather(data_dir / "boundaries/huc4.feather", columns=["geometry", "HUC4", "HUC2"])
ix = shapely.STRtree(df.geometry.values).query(huc4_df.geometry.values, predicate="intersects")[0]
huc4s = sorted(huc4_df.HUC4.take(ix).unique())
huc2s = sorted(huc4_df.HUC2.take(ix).unique())
huc4_df = huc4_df.loc[huc4_df.HUC4.isin(huc4s)].copy()


flowlines = read_arrow_tables(
    [nhd_dir / huc2 / "flowlines.feather" for huc2 in huc2s],
    columns=[
        "geometry",
        "NHDPlusID",
        "GNIS_Name",
        "HUC4",
        "length",
        "loop",
        "offnetwork",
        "FType",
        "FCode",
    ],
    filter=pc.is_in(pc.field("HUC4"), pa.array(huc4s)),
    new_fields={"HUC2": huc2s},
).filter(pc.field("offnetwork") == False)

flowlines = gp.GeoDataFrame(
    flowlines.select([c for c in flowlines.column_names if c not in {"geometry", "offnetwork"}]).to_pandas(),
    geometry=shapely.from_wkb(flowlines.column("geometry")),
    crs=CRS,
).set_index("NHDPlusID")


flowlines = flowlines.loc[~flowlines.index.isin(disallowed_line_ids)].copy()


# mark canals; these require higher confidence of overlap since they may spatially
# interact with habitat but not functionally
# include those with canal in the name since many are not marked via FType
flowlines["canal"] = (flowlines.FType == 336) | (flowlines.GNIS_Name.fillna("").str.lower().str.contains(" canal"))
canal_ids = flowlines.loc[flowlines.canal].index.values

joins = read_arrow_tables(
    [nhd_dir / huc2 / "flowline_joins.feather" for huc2 in huc2s],
    columns=["upstream", "downstream", "loop"],
).to_pandas()
joins = joins.loc[
    joins.upstream.isin(flowlines.index.values) | joins.downstream.isin(flowlines.index.values)
].reset_index(drop=True)


################################################################################
### Associate habitat linework with NHD flowlines by proximity
################################################################################
df["buf"] = shapely.buffer(df.geometry.values, SELECTION_TOLERANCE, cap_style="flat")

# DEBUG:
# write_dataframe(
#     gp.GeoDataFrame(geometry=df.buf, crs=CRS),
#     "/tmp/lahontan_cutthroat_trout_habitat_source_buffer.fgb",
# )

# add upstream / downstream points
flowlines["nhd_upstream_pt"] = shapely.get_point(flowlines.geometry.values, 0)
flowlines["nhd_downstream_pt"] = shapely.get_point(flowlines.geometry.values, -1)

# extract flowlines within SELECTION_TOLERANCE of habitat lines
# WARNING: this will include many flowlines that we should not keep
left, right = shapely.STRtree(flowlines.geometry.values).query(df.buf.values, predicate="intersects")
pairs = pd.DataFrame(
    {
        "NHDPlusID": flowlines.index.values.take(right),
        "spp_line": df.geometry.values.take(left),
        "spp_buf": df.buf.values.take(left),
    }
).join(
    flowlines[
        [
            "geometry",
            "length",
            "canal",
            "loop",
            "nhd_upstream_pt",
            "nhd_downstream_pt",
        ]
    ].rename(columns={"geometry": "nhd_line"}),
    on="NHDPlusID",
)

pairs["upstream_dist"] = shapely.distance(pairs.nhd_upstream_pt, pairs.spp_line.values)
pairs["downstream_dist"] = shapely.distance(pairs.nhd_downstream_pt, pairs.spp_line.values)

tmp = pairs.groupby("NHDPlusID").agg(
    {
        "upstream_dist": "min",
        "downstream_dist": "min",
        "canal": "first",
        "loop": "first",
    }
)


# keep any NHD flowlines where both endpoints are in habitat and discard from
# further processing
# exclude canals here because we need to analyze their overlap below
# exclude any flowlines that are loops; if there is much overlap they will be picked up below
keep_ids = tmp.loc[
    (tmp.upstream_dist < ENDPOINT_TOLERANCE) & (tmp.downstream_dist < ENDPOINT_TOLERANCE) & (~tmp.canal) & (~tmp.loop)
].index.unique()

# drop any that are too far away
drop_ids = tmp.loc[(tmp.upstream_dist > MAX_ENDPOINT_DIFF) | (tmp.downstream_dist > MAX_ENDPOINT_DIFF)].index.unique()

pairs = pairs.loc[~pairs.NHDPlusID.isin(np.unique(np.concatenate([keep_ids, drop_ids])))].copy()
print(f"keeping {len(keep_line_ids):,} NHD lines with endpoints that completely overlap habitat")

keep_line_ids = np.concatenate([keep_line_ids, keep_ids])


# keep any flowlines that are sufficiently covered by buffer of habitat line and drop
# them from further analysis and drop any where the overlap is too short
pairs["overlap"] = shapely.length(shapely.intersection(pairs.nhd_line.values, pairs.spp_buf.values))
pairs["overlap_ratio"] = pairs.overlap / pairs["length"]

# keep any where there is a high degree of overlap across all habitat lines
# unless they overlap multiple species groups
total_overlap = pairs.groupby("NHDPlusID").agg(
    {
        "overlap": "sum",
        "length": "first",
        "canal": "first",
    }
)
total_overlap["overlap_ratio"] = total_overlap.overlap / total_overlap.length

drop_ids = total_overlap.loc[total_overlap.overlap < MIN_LINE_LENGTH].index.unique().values
print(f"dropping {len(drop_ids):,} NHD lines that barely overlap habitat")

upstream_in_habitat = pairs.loc[pairs.upstream_dist < ENDPOINT_TOLERANCE].NHDPlusID.unique()

keep_ids = np.setdiff1d(
    total_overlap.loc[
        (
            (total_overlap.length - total_overlap.overlap < MAX_LENGTH_DIFF)
            & (
                (total_overlap.overlap_ratio >= MIN_OVERLAP_RATIO)
                # allow less overlap if the upstream end is in habitat since the
                # downstream end of habitat seems to be cut by barriers
                | (
                    (total_overlap.overlap_ratio >= MIN_DOWNSTREAM_OVERLAP_RATIO)
                    & total_overlap.index.isin(upstream_in_habitat)
                )
            )
        )
    ].index.unique(),
    drop_ids,
)

# filter out short segments with upstreams that are not in keep_ids; these
# are short root points of incoming tribs that are not themselves included
potential_fragments = pd.Series(
    total_overlap.loc[
        (total_overlap.overlap_ratio >= MIN_OVERLAP_RATIO) & (total_overlap.length < 3 * SELECTION_TOLERANCE)
    ].index.unique()
)

# do this iteratively in case we leave fragments after removing ones upstream of them
# this gets small enough after 10 iterations
for i in range(10):
    potential_keep = np.unique(np.concatenate([keep_line_ids, keep_ids]))
    keep_fragments = joins.loc[
        joins.downstream.isin(potential_fragments.values) & joins.upstream.isin(potential_keep)
    ].downstream.unique()
    drop_fragments = potential_fragments.loc[~potential_fragments.isin(keep_fragments)].values

    if len(drop_fragments) == 0:
        break

    keep_ids = np.setdiff1d(keep_ids, drop_fragments)
    potential_fragments = pd.Series(np.setdiff1d(potential_fragments, drop_fragments))


keep_line_ids = np.unique(np.concatenate([keep_line_ids, keep_ids]))
pairs = pairs.loc[~(pairs.NHDPlusID.isin(np.unique(np.concatenate([keep_line_ids, drop_ids]))))].reset_index()
print(f"keeping {len(keep_ids):,} NHD lines that mostly overlap habitat")


# DEBUG:
# write_dataframe(
#     flowlines.loc[flowlines.index.isin(keep_line_ids)].join(total_overlap[["overlap", "overlap_ratio"]]).reset_index(),
#     "/tmp/lahontan_cutthroat_trout_high_overlap_keep_lines.fgb",
# )


flowlines["lahontan_cutthroat_trout_habitat"] = flowlines.index.isin(keep_line_ids)

print(
    f"species habitat: {shapely.length(df.geometry.values).sum() / 1000:,.1f} km; "
    f"extracted {flowlines.loc[flowlines.lahontan_cutthroat_trout_habitat, ['length']].values.sum() / 1000:,.1f} km from NHD"
)

out = flowlines.loc[flowlines.lahontan_cutthroat_trout_habitat].reset_index()
write_dataframe(out, out_dir / "lahontan_cutthroat_trout_habitat.fgb")
out[["NHDPlusID", "HUC2", "lahontan_cutthroat_trout_habitat"]].to_feather(
    out_dir / "lahontan_cutthroat_trout_habitat.feather"
)
