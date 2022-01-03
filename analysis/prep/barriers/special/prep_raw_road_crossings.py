"""
Preprocess road / stream crossings into data needed by tippecanoe for creating vector tiles.

Input:
* USGS Road / Stream crossings, projected to match SARP standard projection (Albers CONUS).
* pre-processed and snapped small barriers


Outputs:
`data/barriers/intermediate/road_crossings.feather`: road / stream crossing data for merging in with small barriers that do not have networks
"""

from pathlib import Path
from time import time
import warnings

from pyogrio import read_dataframe, write_dataframe
import pygeos as pg
import geopandas as gp


from analysis.constants import CRS
from analysis.prep.barriers.lib.duplicates import mark_duplicates
from analysis.prep.barriers.lib.spatial_joins import add_spatial_joins

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")

DUPLICATE_TOLERANCE = 10  # meters

start = time()

data_dir = Path("data")
boundaries_dir = data_dir / "boundaries"
barriers_dir = data_dir / "barriers"
src_dir = barriers_dir / "source"
qa_dir = barriers_dir / "qa"

gdb = src_dir / "NHDPlusV2_TIGERroads2014.gdb"

print("Reading road crossings")


huc4 = gp.read_feather(boundaries_dir / "huc4.feather", columns=["geometry"])

df = read_dataframe(
    gdb,
    layer="Rdx_Tiger2014_NHDPlusV2_NoAtt_wAdd",
    columns=["FULLNAME", "GNIS_NAME", "RDXID"],
    force_2d=True,
).to_crs(CRS)
print("Read {:,} road crossings".format(len(df)))

tree = pg.STRtree(df.geometry.values.data)
ix = tree.query_bulk(huc4.geometry.values.data, predicate="intersects")[1]

df = df.take(ix)
print("Selected {:,} road crossings in region".format(len(df)))

df["id"] = df.index.astype("uint32")
df = df.set_index("id", drop=False)

# There are a bunch of crossings with identical coordinates, remove them
# NOTE: they have different labels, but that seems like it is a result of
# them methods used to identify the crossings (e.g., named highways, roads, etc)
print("Removing duplicate crossings...")

# round to int
df["x"] = pg.get_x(df.geometry.values.data).astype("int")
df["y"] = pg.get_y(df.geometry.values.data).astype("int")

keep_ids = df[["x", "y", "id"]].groupby(["x", "y"]).first().reset_index().id
print(f"{len(df) - len(keep_ids):,} duplicate road crossings")

df = df.loc[keep_ids].copy()

### Remove crossings that are very close
print("Removing nearby road crossings...")
# consider 5 m nearby
df = mark_duplicates(df, 5)
print(f"{df.duplicate.sum():,} very close road crossings dropped")
df = df.loc[~df.duplicate].drop(columns=["duplicate", "dup_count", "dup_group"])


# Rename columns to standardize with small barriers dataset
df = df.rename(columns={"FULLNAME": "Road", "GNIS_NAME": "Stream", "RDXID": "SARPID"})
# Cleanup fields
df.Stream = df.Stream.str.strip().fillna("")
df.Road = df.Road.str.strip().fillna("")

df.loc[
    (df.Stream.str.strip().str.len() > 0) & (df.Road.str.strip().str.len() > 0), "Name"
] = (df.Stream + " / " + df.Road)

df.Name = df.Name.fillna("")

# match dtype of SARPID elsewhere
df.SARPID = "cr" + df.SARPID.round().astype(int).astype(str)

print("Adding lat / lon fields")
geo = df[["geometry"]].to_crs(epsg=4326)
geo["lat"] = pg.get_y(geo.geometry.values.data).astype("float32")
geo["lon"] = pg.get_x(geo.geometry.values.data).astype("float32")
df = df.join(geo[["lat", "lon"]])

df.reset_index(drop=True).to_feather(src_dir / "road_crossings.feather")

print("Done in {:.2f}".format(time() - start))
