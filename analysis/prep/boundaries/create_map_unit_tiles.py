import subprocess
from pathlib import Path

import geopandas as gp
import numpy as np
import pandas as pd
import shapely
from pyogrio import write_dataframe

from analysis.constants import GEO_CRS
from analysis.post.lib.tiles import get_col_types

MAX_ZOOM = "12"

tippecanoe = "tippecanoe"
tile_join = "tile-join"
tippecanoe_args = [tippecanoe, "-f", "-pg", "--visvalingam", "--no-simplification-of-shared-nodes"]

src_dir = Path("data/boundaries")
out_dir = Path("data/tiles")
tmp_dir = Path("/tmp")


################################################################################
### Create tiles for full analysis area and regions
################################################################################
print("Creating region tiles")
regions = gp.read_feather(src_dir / "region_boundary.feather")
bnd = regions.loc[regions.id == "total"].geometry.values[0]
outfilename = tmp_dir / "region_boundary.fgb"
write_dataframe(regions, outfilename)
pmtiles_filename = out_dir / "region_boundary.pmtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", MAX_ZOOM]
    + ["-l", "boundary"]
    + get_col_types(regions)
    + ["-o", str(pmtiles_filename), outfilename],
    check=True,
)
ret.check_returncode()
outfilename.unlink()


################################################################################
### Create tiles for Fish Habitat Partnership boundaries
################################################################################
print("\nCreating fish habitat partnership tiles")
fhp = gp.read_feather(src_dir / "fhp_boundary.feather").to_crs(GEO_CRS)
outfilename = out_dir / "fhp_boundary.fgb"
write_dataframe(fhp, outfilename)
pmtiles_filename = out_dir / "fhp_boundary.pmtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", MAX_ZOOM]
    + ["-l", "fhp_boundary"]
    + get_col_types(fhp)
    + ["-o", str(pmtiles_filename), outfilename],
    check=True,
)
ret.check_returncode()
outfilename.unlink()


################################################################################
### Create state tiles
################################################################################
print("\nCreating state tiles")
states = gp.read_feather(src_dir / "states.feather", columns=["geometry", "id"]).to_crs(GEO_CRS)
outfilename = tmp_dir / "states.fgb"
write_dataframe(states, outfilename)
pmtiles_filename = out_dir / "State.pmtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", MAX_ZOOM]
    + ["-l", "State"]
    + get_col_types(states)
    + ["-o", f"{pmtiles_filename!s}", str(outfilename)],
    check=True,
)
ret.check_returncode()
outfilename.unlink()


################################################################################
### Create tiles of masks outside regions, FHPs, and states
################################################################################
print("\nCreating mask tiles")
world = shapely.box(-180, -85, 180, 85)
mask = pd.concat([regions[["id", "geometry"]], fhp[["id", "geometry"]], states[["id", "geometry"]]], ignore_index=True)
mask["id"] = mask.id.values + "_mask"

# create a 5 degree grid then intersect with all masks; this defines the break between the coarse and fine mask
xmin, ymin = np.meshgrid(np.arange(-180, 180, 5), np.arange(-85, 85, 5))
xmax, ymax = np.meshgrid(np.arange(-175, 181, 5), np.arange(-80, 86, 5))
grid = gp.GeoDataFrame(geometry=shapely.box(xmin, ymin, xmax, ymax).flatten(), crs=GEO_CRS)


# find all cells within 5 degrees of each mask (to avoid seamlines close to their borders)
left, right = shapely.STRtree(grid.geometry.values).query(mask.geometry.values, predicate="dwithin", distance=5)
overlaps = pd.DataFrame(
    {
        "id": mask.id.values.take(left),
        "mask": mask.geometry.values.take(left),
        "cell_ix": right,
        "cell": grid.geometry.take(right),
    }
)

# find all cells not intersected for each mask
mask_lowres = []
for _, row in mask.iterrows():
    ix = sorted(overlaps.loc[overlaps.id == row.id].cell_ix.unique())
    mask_lowres.append(
        {"id": row.id, "geometry": shapely.coverage_union_all(grid.loc[~grid.index.isin(ix)].geometry.values)}
    )
mask_lowres = gp.GeoDataFrame(mask_lowres, geometry="geometry", crs=GEO_CRS)
outfilename = tmp_dir / "mask_lowres.fgb"
write_dataframe(mask_lowres, outfilename)
pmtiles_filename = out_dir / "mask_lowres.pmtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", "6"]
    + ["-l", "mask_lowres"]
    + get_col_types(mask_lowres)
    + ["-o", str(pmtiles_filename), str(outfilename)],
    check=True,
)
ret.check_returncode()
outfilename.unlink()


mask_highres = (
    overlaps.groupby(by="id").agg({"mask": "first", "cell": lambda g: shapely.coverage_union_all(g)}).reset_index()
)
mask_highres["geometry"] = shapely.difference(mask_highres.cell.values, mask_highres["mask"].values)
mask_highres = gp.GeoDataFrame(mask_highres[["id", "geometry"]], geometry="geometry", crs=GEO_CRS)
outfilename = tmp_dir / "mask_highres.fgb"
write_dataframe(mask_highres, outfilename)
pmtiles_filename = out_dir / "mask_highres.pmtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", MAX_ZOOM]
    + ["-l", "mask_highres"]
    + get_col_types(mask_highres)
    + ["-o", str(pmtiles_filename), str(outfilename)],
    check=True,
)
ret.check_returncode()
outfilename.unlink()


del regions
del fhp
del states
del mask_lowres
del mask_highres


################################################################################
### Counties
################################################################################
print("\nCreating county tiles")
df = gp.read_feather(src_dir / "counties.feather", columns=["geometry", "id", "name"]).to_crs(GEO_CRS)
outfilename = tmp_dir / "counties.fgb"
write_dataframe(df, outfilename)
pmtiles_filename = out_dir / "County.pmtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "3", "-z", MAX_ZOOM]
    + ["-l", "County"]
    + get_col_types(df)
    + ["-o", f"{pmtiles_filename!s}", str(outfilename)],
    check=True,
)
ret.check_returncode()
outfilename.unlink()


################################################################################
### Congressional districts
################################################################################
print("\nCreating congressional district tiles")
df = gp.read_feather(src_dir / "congressional_districts.feather", columns=["geometry", "id", "name"]).to_crs(GEO_CRS)
outfilename = tmp_dir / "congressional_districts.fgb"
write_dataframe(df, outfilename)
pmtiles_filename = out_dir / "CongressionalDistrict.pmtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "1", "-z", MAX_ZOOM]
    + ["-l", "CongressionalDistrict"]
    + get_col_types(df)
    + ["-o", f"{pmtiles_filename!s}", str(outfilename)],
    check=True,
)
ret.check_returncode()
outfilename.unlink()


################################################################################
### State water resource areas
################################################################################
print("\nCreating state water resource area tiles")
df = gp.read_feather(src_dir / "state_water_resource_areas.feather", columns=["geometry", "id", "name"]).to_crs(GEO_CRS)
outfilename = tmp_dir / "state_water_resource_areas.fgb"
write_dataframe(df, outfilename)
pmtiles_filename = out_dir / "StateWRA.pmtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "1", "-z", MAX_ZOOM]
    + ["-l", "StateWRA"]
    + get_col_types(df)
    + ["-o", f"{pmtiles_filename!s}", str(outfilename)],
    check=True,
)
ret.check_returncode()
outfilename.unlink()
del df


################################################################################
## HUC2
################################################################################
print("\nCreating HUC2 tiles")
df = gp.read_feather(src_dir / "HUC2.feather").rename(columns={"HUC2": "id"}).to_crs(GEO_CRS)
outfilename = tmp_dir / "HUC2.fgb"
write_dataframe(df, outfilename)
pmtiles_filename = out_dir / "HUC2.pmtiles"
ret = subprocess.run(
    tippecanoe_args
    + ["-Z", "0", "-z", MAX_ZOOM]
    + ["-l", "HUC2"]
    + get_col_types(df)
    + ["-o", f"{pmtiles_filename!s}", str(outfilename)],
    check=True,
)
ret.check_returncode()
outfilename.unlink()
del df

################################################################################
### HUC6 - HUC12
################################################################################
# have to render all to zoom 14 or boundaries mismatch
huc_zoom_levels = {"HUC6": ["0", MAX_ZOOM], "HUC8": ["0", MAX_ZOOM], "HUC10": ["6", MAX_ZOOM], "HUC12": ["8", MAX_ZOOM]}

for huc, (minzoom, maxzoom) in huc_zoom_levels.items():
    print(f"\nCreating {huc} tiles")
    df = gp.read_feather(src_dir / f"{huc}.feather").rename(columns={huc: "id"}).to_crs(GEO_CRS)

    # only keep units that actually overlap the region at each level
    tree = shapely.STRtree(df.geometry.values)
    ix = tree.query(bnd, predicate="intersects")
    df = df.loc[ix]

    outfilename = tmp_dir / f"{huc}.fgb"
    write_dataframe(df, outfilename)
    pmtiles_filename = out_dir / f"{huc}.pmtiles"
    ret = subprocess.run(
        tippecanoe_args
        + ["-Z", minzoom, "-z", maxzoom]
        + ["-l", huc]
        + get_col_types(df)
        + ["-o", f"{pmtiles_filename!s}", str(outfilename)],
        check=True,
    )
    ret.check_returncode()
    outfilename.unlink()
    del df


################################################################################
### Combine all unit tiles into a single tileset
################################################################################
print("\nMerging all summary unit tiles")
ret = subprocess.run(
    [
        tile_join,
        "-f",
        "-pg",
        "--no-tile-size-limit",
        "-o",
        f"{out_dir}/map_units.pmtiles",
    ]
    + [
        f"{out_dir}/{layer}.pmtiles"
        for layer in [
            "region_boundary",
            "mask_lowres",
            "mask_highres",
            "State",
            "County",
            "CongressionalDistrict",
            "HUC2",
            "HUC6",
            "HUC8",
            "HUC10",
            "HUC12",
            "StateWRA",
            "fhp_boundary",
        ]
    ],
    check=True,
)
ret.check_returncode()

print("All done!")
