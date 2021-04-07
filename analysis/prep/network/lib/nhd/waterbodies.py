import pygeos as pg
from pyogrio import read_dataframe

from analysis.lib.geometry import make_valid


WATERBODY_COLS = [
    "NHDPlusID",
    "FType",
    "FCode",
    "GNIS_ID",
    "GNIS_Name",
    "AreaSqKm",
    "geometry",
]


def extract_waterbodies(gdb_path, target_crs, exclude_ftypes=[], min_area=0):
    """Extract waterbodies from NHDPlusHR data product.

    Parameters
    ----------
    gdb_path : str
        path to the NHD HUC4 Geodatabase
    target_crs: GeoPandas CRS object
        target CRS to project NHD to for analysis, like length calculations.
        Must be a planar projection.
    exclude_ftypes : list, optional (default: [])
        list of FTypes to exclude.
    min_area : int, optional (default: 0)
        If provided, only waterbodies that are >= this value are retained

    Returns
    -------
    GeoDataFrame
    """
    print("Reading waterbodies")
    df = read_dataframe(
        gdb_path, layer="NHDWaterbody", columns=[WATERBODY_COLS], force_2d=True
    )
    print("Read {:,} waterbodies".format(len(df)))

    df = df.loc[
        (df.AreaSqKm >= min_area) & (~df.FType.isin(exclude_ftypes))
    ].reset_index(drop=True)
    print(
        "Retained {:,} waterbodies after dropping those below size threshold or in exclude FTypes".format(
            len(df)
        )
    )

    # Convert multipolygons to polygons
    # those we checked that are true multipolygons are errors
    df.geometry = pg.get_geometry(df.geometry.values.data, 0)
    df.geometry = make_valid(df.geometry.values.data)

    print("projecting to target projection")
    df = df.to_crs(target_crs)

    df.NHDPlusID = df.NHDPlusID.astype("uint64")
    df.AreaSqKm = df.AreaSqKm.astype("float32")
    df.FType = df.FType.astype("uint16")

    ### Add calculated fields
    df["wbID"] = df.index.values.astype("uint32") + 1

    return df


def find_nhd_waterbody_breaks(geometries, nhd_lines):
    """Some large waterbody complexes are divided by dams; these breaks
    need to be preserved.  This is done by finding the shared edges between
    adjacent waterbodies that fall near NHD lines (which include dams) and
    buffering them by 10 meters (arbitrary, from trial and error).

    This should be skipped if nhd_lines is empty.

    Parameters
    ----------
    df : GeoDataFrame
    nhd_lines : GeoDataFrame

    Returns
    -------
    MultiPolygon containing all buffered lines between waterbodies that are near
        NHD lines.  Returns None if no adjacent waterbodies meet these criteria
    """

    # find all nhd lines that intersect waterbodies
    # first, buffer them slightly
    nhd_lines = pg.get_parts(pg.union_all(pg.buffer(nhd_lines, 0.1)))
    tree = pg.STRtree(geometries)
    left, right = tree.query_bulk(nhd_lines, predicate="intersects")

    # add these to the return
    keep_nhd_lines = nhd_lines[np.unique(left)]

    # find connected boundaries
    boundaries = pg.polygons(pg.get_exterior_ring(geometries))
    tree = pg.STRtree(boundaries)
    left, right = tree.query_bulk(boundaries, predicate="intersects")
    # drop self intersections
    ix = left != right
    left = left[ix]
    right = right[ix]

    # extract unique pairs (dedup symmetric pairs)
    pairs = np.array([left, right]).T
    pairs = (
        pd.DataFrame({"left": pairs.min(axis=1), "right": pairs.max(axis=1)})
        .groupby(["left", "right"])
        .first()
        .reset_index()
    )

    # calculate geometric intersection
    i = pg.intersection(
        geometries.take(pairs.left.values), geometries.take(pairs.right.values)
    )

    # extract individual parts (may be geom collections)
    parts = pg.get_parts(pg.get_parts(pg.get_parts(i)))

    # extract only the lines or polygons
    t = pg.get_type_id(parts)
    parts = parts[((t == 1) | (t == 3)) & (~pg.is_empty(parts))].copy()

    # buffer and merge
    split_lines = pg.get_parts(pg.union_all(pg.buffer(parts, 10)))

    # now find the ones that are within 100m of nhd lines
    nhd_lines = pg.get_parts(nhd_lines)
    tree = pg.STRtree(nhd_lines)
    left, right = tree.nearest_all(split_lines, max_distance=100)

    split_lines = split_lines[np.unique(left)]

    if len(split_lines) or len(keep_nhd_lines):
        return pg.union_all(np.append(split_lines, keep_nhd_lines))

    return None

