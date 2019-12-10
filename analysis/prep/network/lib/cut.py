from time import time

import geopandas as gp
import pandas as pd
import pygeos as pg
import numpy as np
from geofeather import to_geofeather

from nhdnet.geometry.lines import calculate_sinuosity
from nhdnet.nhd.joins import update_joins
from analysis.pygeos_compat import to_pygeos, from_pygeos

# TEMPORARY: this shimmed until pygeos support is available in geopandas
# doing these operations in native geopandas is extremely slow.
# To get around this, we load and do certain operations in pygeos.
# WARNING: Due to incompatibilities between shapely and pygeos, this may
# break in future versions, and is also why we have to do intersections in shapely
# instead of pygeos here.


def cut_lines_by_waterbodies(flowlines, joins, waterbodies, wb_joins, out_dir):
    """
    Cut lines by waterbodies.
    1. Intersects all previously intersected flowlines with waterbodies.
    2. For those that cross but are not completely contained by waterbodies, cut them.
    3. Evaluate the cuts, only those that have substantive cuts inside and outside are retained as cuts.
    4. Any flowlines that are not contained or crossing waterbodies are dropped from joins

    Parameters
    ----------
    flowlines : GeoDataFrame
    joins : DataFrame
        flowline joins
    waterbodies : GeoDataFrame
    wb_joins : DataFrame
        waterbody flowline joins
    outdir : pathlib.Path
        output directory for writing error files, if needed

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame, GeoDataFrame, DataFrame)
        (flowlines, joins, waterbodies, waterbody joins)
    """

    start = time()

    print("Converting geometries to pygeos")
    convert_start = time()
    fl_geom = flowlines.loc[flowlines.index.isin(wb_joins.lineID), ["geometry"]].copy()
    fl_geom["geometry"] = to_pygeos(fl_geom.geometry)

    # WARNING: if geometry is not valid, conversion will create extra records and will
    # fail later processing.  To keep conversion from growing rows on invalid geoms,
    # use a dataframe instead
    wb_geom = waterbodies[["geometry"]].copy()
    wb_geom["waterbody"] = to_pygeos(wb_geom.geometry)
    print("Conversion done in {:.2f}s".format(time() - convert_start))

    print("Validating waterbodies...")
    ix = ~pg.is_valid(wb_geom.waterbody)
    invalid_count = ix.sum()
    if invalid_count:
        print("{:,} invalid waterbodies found, repairing...".format(invalid_count))

        # Buffer by 0 to fix
        repair_start = time()
        wb_geom.loc[ix, "waterbody"] = pg.buffer(wb_geom.waterbody, 0)
        waterbodies.loc[ix, "geometry"] = from_pygeos(wb_geom.loc[ix].waterbody)
        print("Repaired geometry in {:.2f}s".format(time() - repair_start))

    wb_joins = wb_joins.set_index(["lineID", "wbID"])
    geoms = wb_joins.join(fl_geom, how="inner").join(wb_geom.waterbody)

    ### Find contained geometries
    print("Identifying flowlines completely within waterbodies...")
    contained_start = time()
    geoms["inside"] = pg.contains(geoms.waterbody, geoms.geometry)

    print(
        "Identified {:,} flowlines completely contained by waterbodies in {:.2f}s".format(
            geoms.inside.sum(), time() - contained_start
        )
    )

    # Check for logic errors - no flowline should be completely contained by more than 1 waterbody
    errors = geoms.groupby(level=[0]).inside.sum().astype("uint8") > 1
    if errors.max():
        # this most likely indicates duplicate waterbodies, which should have been resolved before this
        print(
            "ERROR: major logic error - some flowlines claim to be completely contained by multiple waterbodies"
        )
        print(
            "===> error flowlines written to {}/contained_errors.feather".format(
                out_dir
            )
        )
        to_geofeather(
            flowlines.loc[flowlines.index.isin(errors)],
            out_dir / "contained_errors.feather",
        )

    ### Check those that aren't contained to see if they cross
    print("Determining which flowlines actually cross into waterbodies...")
    cross_start = time()
    geoms = geoms.loc[~geoms.inside].copy()
    geoms["crosses"] = pg.crosses(geoms.geometry, geoms.waterbody)

    outside = geoms.loc[~(geoms["crosses"] | geoms.inside)].index

    # keep the ones that cross for further processing
    geoms = geoms.loc[geoms.crosses].copy()

    print(
        "Identified {:,} flowlines completely outside waterbodies and {:,} flowlines that cross waterbody boundaries in {:.2f}s".format(
            len(outside), len(geoms), time() - cross_start
        )
    )

    # Any that do not cross and are not completely within waterbodies should be dropped now
    # Can only drop joins by BOTH lineID and wbID (the index here)
    # Also drop associated waterbodies that no longer have joins
    wb_joins = wb_joins.loc[~wb_joins.index.isin(outside)].copy()

    # check for multiple crossings - these are errors from NHD that we can drop from here
    errors = geoms.groupby(level=0).size() > 1
    if errors.max():
        print(
            "Found {:,} flowlines that cross multiple waterbodies.  These are bad data and will be dropped from waterbody intersection.".format(
                errors.sum()
            )
        )

        # completely remove the flowlines from intersections and drop the waterbodies
        wb_joins = wb_joins.loc[
            ~wb_joins.index.get_level_values(0).isin(errors.loc[errors].index)
        ].copy()
        waterbodies = waterbodies.loc[
            waterbodies.index.isin(wb_joins.index.get_level_values(1))
        ].copy()
        geoms = geoms.loc[geoms.index.isin(wb_joins.index)].copy()

    # TODO: reimplement the following
    # Due to GEOS conflicts between pygeos and shapely, we need to cut the geometries using shapely
    # can do this all in pygeos once merged into geopandas.
    to_cut = gp.GeoDataFrame(
        geoms[[]]
        .join(flowlines[["geometry", "length"]])
        .join(waterbodies.geometry.rename("waterbody")),
        crs=flowlines.crs,
    )
    boundary = gp.GeoSeries(to_cut.waterbody).boundary

    # Fun fact: all new segments from differences are oriented from the upstream end of the
    # original line to the downstream end
    # WARNING: this isn't perfect - not all lines cut by waterbody boundaries are perfectly contained
    # by waterbodies
    print("Cutting flowlines...")
    cut_start = time()
    difference = to_cut.difference(boundary)
    length = difference.length
    error = ((length - to_cut["length"]).abs() > 1).sum()
    if error:
        print(
            "WARNING: {:,} lines were not completely cut by waterbodies (maybe shared edge?).\nThere are now missing edges"
        )

    new_lines = (
        gp.GeoDataFrame(difference.rename("geometry").reset_index(), crs=flowlines.crs)
        .explode()
        .reset_index(drop=True)
    )

    # Create pygeos geoms again for the exploded lines
    geoms = new_lines[["lineID", "wbID", "geometry"]].copy()
    geoms["geometry"] = to_pygeos(geoms.geometry)
    geoms = geoms.join(wb_geom.waterbody, on="wbID").join(
        flowlines.length.rename("origLength"), on="lineID"
    )

    # mark those parts of the cut lines that are within waterbodies
    geoms["iswithin"] = pg.contains(geoms.waterbody, geoms.geometry)
    # we can do this because indices are still the same
    new_lines["iswithin"] = geoms.iswithin

    # calculate total length of within and outside parts
    geoms["length"] = pg.length(geoms.geometry)
    length = (
        # geoms.reset_index()
        geoms.groupby(["lineID", "wbID", "iswithin"]).agg(
            {"length": "sum", "origLength": "first"}
        )
    )

    # Anything within 1 meter of original length is considered unchanged
    # This is so that we ignore slivers
    length["unchanged"] = (length.origLength - length["length"]).abs() < 1
    unchanged = (
        length[["unchanged"]]
        .reset_index()
        .groupby(["lineID", "wbID"])
        .unchanged.max()
        .rename("max_unchanged")
    )
    unchanged = length.reset_index().set_index(["lineID", "wbID"]).join(unchanged)
    is_within = (
        unchanged.loc[unchanged.max_unchanged]
        .reset_index()
        .set_index(["lineID", "wbID"])
        .iswithin
    )

    # For any that are unchanged and NOT within waterbodies,
    # remove them from wb_joins
    ix = is_within.loc[~is_within].index
    wb_joins = wb_joins.loc[~wb_joins.index.isin(ix)].copy()

    # Remove any that are unchanged from intersection analysis
    new_lines = new_lines.set_index(["lineID", "wbID"])
    new_lines = new_lines.loc[~new_lines.index.isin(is_within.index)].reset_index()

    print(
        "Created {:,} new flowlines by splitting {:,} flowlines at waterbody edges in {:.2f}".format(
            len(new_lines), len(new_lines.lineID.unique()), time() - cut_start
        )
    )

    ### These are our final new lines to add
    # remove their lineIDs from flowlines and append
    # replace their outer joins to these ones and add intermediates

    # Join in previous line information from flowlines
    new_lines = (
        new_lines.set_index("lineID")
        .join(flowlines.drop(columns=["geometry", "length", "sinuosity"]))
        .reset_index()
        .rename(columns={"lineID": "origLineID", "iswithin": "waterbody"})
    )

    error = new_lines.groupby("origLineID").wbID.unique().apply(len).max() > 1
    if error:
        # Watch for errors - if a flowline is cut by multiple waterbodies
        # there will be problems with our logic for splicing in new lines
        # also - our intersection logic above is wrong
        print(
            """\n========\n
        MAJOR LOGIC ERROR: multiple waterbodies associated with a single flowline that as been cut.
        \n========\n
        """
        )

    # recalculate length and sinuosity
    new_lines["length"] = new_lines.geometry.length.astype("float32")
    new_lines["sinuosity"] = new_lines.geometry.apply(calculate_sinuosity).astype(
        "float32"
    )

    # calculate new IDS
    next_segment_id = int(flowlines.index.max() + 1)
    new_lines["lineID"] = next_segment_id + new_lines.index
    new_lines.lineID = new_lines.lineID.astype("uint32")

    ### Update waterbody joins
    # remove joins replaced by above
    ix = new_lines.set_index(["origLineID", "wbID"]).index
    wb_joins = wb_joins.loc[~wb_joins.index.isin(ix)].copy()

    # add new joins
    wb_joins = (
        wb_joins.reset_index()
        .append(
            new_lines.loc[new_lines.waterbody, ["lineID", "wbID"]],
            ignore_index=True,
            sort=False,
        )
        .set_index(["lineID", "wbID"])
    )

    ### Update flowline joins
    # transform new lines to create new joins
    l = new_lines.groupby("origLineID").lineID
    # the first new line per original line is the furthest upstream, so use its
    # ID as the new downstream ID for anything that had this origLineID as its downstream
    first = l.first().rename("new_downstream_id")
    # the last new line per original line is the furthest downstream...
    last = l.last().rename("new_upstream_id")

    # Update existing joins with the new lineIDs we created at the upstream or downstream
    # ends of segments we just created
    joins = update_joins(
        joins, first, last, downstream_col="downstream_id", upstream_col="upstream_id"
    )

    ### Create new line joins for any that weren't inserted above
    # Transform all groups of new line IDs per original lineID, wbID
    # into joins structure
    pairs = lambda a: pd.Series(zip(a[:-1], a[1:]))
    new_joins = (
        new_lines.groupby(["origLineID", "wbID"])
        .lineID.apply(pairs)
        .apply(pd.Series)
        .reset_index()
        .rename(columns={0: "upstream_id", 1: "downstream_id"})
        .join(flowlines.NHDPlusID.rename("upstream"), on="origLineID")
    )
    # NHDPlusID is same for both sides
    new_joins["downstream"] = new_joins.upstream
    new_joins["type"] = "internal"
    new_joins = new_joins[
        ["upstream", "downstream", "upstream_id", "downstream_id", "type"]
    ]

    joins = joins.append(new_joins, ignore_index=True, sort=False).sort_values(
        ["downstream_id", "upstream_id"]
    )

    ### Update flowlines
    # remove originals now replaced by cut versions here
    flowlines = (
        flowlines.loc[~flowlines.index.isin(new_lines.origLineID)]
        .reset_index()
        .append(
            new_lines[["lineID"] + list(flowlines.columns) + ["waterbody"]],
            ignore_index=True,
            sort=False,
        )
        .sort_values("lineID")
        .set_index("lineID")
    )

    # Update waterbody bool for other flowlines based on those that completely intersected
    # above
    flowlines.loc[
        flowlines.index.isin(wb_joins.index.get_level_values(0).unique()), "waterbody"
    ] = True
    flowlines.waterbody = flowlines.waterbody.fillna(False)

    ### Update waterbodies and calculate flowline stats
    wb_joins = wb_joins.reset_index()
    stats = (
        wb_joins.join(flowlines.length.rename("flowlineLength"), on="lineID")
        .groupby("wbID")
        .flowlineLength.sum()
        .astype("float32")
    )
    waterbodies = waterbodies.loc[waterbodies.index.isin(wb_joins.wbID)].join(stats)

    print("Done cutting flowlines by waterbodies in {:.2f}s".format(time() - start))

    return flowlines, joins, waterbodies, wb_joins
