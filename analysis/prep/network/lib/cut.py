from time import time

import geopandas as gp
import pandas as pd
import pygeos as pg
import numpy as np
from geofeather.pygeos import to_geofeather

from nhdnet.nhd.joins import update_joins
from analysis.pygeos_compat import to_pygeos, from_pygeos, explode
from analysis.prep.network.lib.lines import calculate_sinuosity
from analysis.constants import CRS


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

    fl_geom = flowlines.loc[flowlines.index.isin(wb_joins.lineID), ["geometry"]].copy()

    # Many waterbodies have interior polygons (islands); these break the analysis below for cutting lines
    # Extract a new polygon of just their outer boundary
    wb_geom = waterbodies[["geometry"]].copy()
    wb_geom["waterbody"] = pg.polygons(pg.get_exterior_ring(wb_geom.geometry))

    print("Validating waterbodies...")
    ix = ~pg.is_valid(wb_geom.waterbody)
    invalid_count = ix.sum()
    if invalid_count:
        print("{:,} invalid waterbodies found, repairing...".format(invalid_count))

        # Buffer by 0 to fix
        # TODO: may need to do this by a small fraction and simplify instead
        repair_start = time()
        wb_geom.loc[ix, "waterbody"] = pg.buffer(wb_geom.loc[ix].waterbody, 0)
        waterbodies.loc[ix, "geometry"] = wb_geom.loc[ix].waterbody
        print("Repaired geometry in {:.2f}s".format(time() - repair_start))

    # Set indices and create combined geometry object for analysis
    wb_joins = wb_joins.set_index(["lineID", "wbID"])
    geoms = wb_joins.join(fl_geom, how="inner").join(wb_geom.waterbody)

    ### Find contained geometries
    print(
        "Identifying flowlines completely within waterbodies out of {:,} flowline / waterbody combinations...".format(
            len(geoms)
        )
    )
    contained_start = time()
    geoms["inside"] = pg.contains(geoms.waterbody.values, geoms.geometry.values)

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
            crs=CRS,
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

    # FIXME: for closely adjacent waterbodies, these are important to keep
    # Need to cut them by their multiple polys, update their joins, and feed back into following analysis
    # pg.intersection_all might work here

    # check for multiple crossings - these are errors from NHD that we can drop from here
    errors = geoms.groupby(level=0).size() > 1
    if errors.max():
        print(
            "Found {:,} flowlines that cross multiple waterbodies.  These are bad data and will be dropped from waterbody intersection.".format(
                errors.sum()
            )
        )

        to_geofeather(
            flowlines.loc[errors.index].reset_index(),
            out_dir / "error_crosses_multiple.feather",
            crs=CRS,
        )

        # completely remove the flowlines from intersections and drop the waterbodies
        wb_joins = wb_joins.loc[
            ~wb_joins.index.get_level_values(0).isin(errors.loc[errors].index)
        ].copy()
        waterbodies = waterbodies.loc[
            waterbodies.index.isin(wb_joins.index.get_level_values(1))
        ].copy()
        geoms = geoms.loc[geoms.index.isin(wb_joins.index)].copy()

    print("Calculating geometric intersection of flowlines and waterbodies...")
    int_start = time()
    geoms = geoms[["geometry", "waterbody"]].join(flowlines.length.rename("origLength"))

    # First, calculate the geometric intersection between the lines and waterbodies
    # WARNING: this intersection may return LineString, MultiLineString, Point, GeometryCollection
    geoms["intersection"] = pg.intersection(geoms.geometry, geoms.waterbody)
    types = pg.get_type_id(geoms.intersection)
    # NOTE: all the points should be captured by the above logic for crosses
    is_point = types.isin([0, 4])
    is_line = types.isin([1, 5])

    others = types[~(is_point | is_line)].unique()
    # GeometryCollection indicates a mess, skip those
    if len(others):
        print(
            "WARNING: Found other types of geometric intersection: {} (n={:,}), these will be dropped".format(
                others, len(types[~(is_point | is_line)])
            )
        )

    # Any that intersect only at a point are OUTSIDE
    outside = geoms.loc[is_point].index  # TODO: confirm this works
    wb_joins = wb_joins.loc[~wb_joins.index.isin(outside)].copy()
    print("Identified {:,} more flowlines outside waterbodies".format(len(outside)))

    # Drop those that are not lines from further analysis
    geoms = geoms.loc[is_line].copy()

    # Inspect amount of overlay - if the intersected length is within 1m of final length, it is completely within
    # if it is near 0, it is completely outside
    geoms["length"] = pg.length(geoms.intersection)
    outside = geoms.length < 1
    inside = (geoms.origLength - geoms.length).abs() < 1

    print(
        "Found {:,} more completely outside, {:,} completely inside".format(
            outside.sum(), inside.sum()
        )
    )

    # drop the ones that are outside
    wb_joins = wb_joins.loc[~wb_joins.index.isin(outside[outside].index)].copy()

    # cut the ones that aren't completely inside or outside
    geoms = geoms.loc[~(inside | outside)].copy()

    print("Done evaluating intersection in {:.2f}s".format(time() - int_start))

    if len(geoms):
        print("Cutting {:,} flowlines ...".format(len(geoms)))
        cut_start = time()
        geoms = geoms[["geometry", "waterbody", "origLength"]]

        # WARNING: difference is not precise, the point of split is not exactly at the intersection between lines
        # but within some tolerance.  This will cause them to fail the contains() test below.
        boundary = pg.boundary(geoms.waterbody)
        geoms["geometry"] = pg.difference(geoms.geometry, boundary)

        errors = ~pg.is_valid(geoms.geometry)
        if errors.max():
            print("WARNING: geometry errors for {:,} cut lines".format(errors.sum()))

        length = pg.length(geoms.geometry)
        errors = (length - geoms.origLength).abs() > 1
        if errors.max():
            print(
                "WARNING: {:,} lines were not completely cut by waterbodies (maybe shared edge?).\nThese will not be cut".format(
                    errors.sum()
                )
            )
            to_geofeather(
                flowlines.loc[
                    errors.loc[errors].index.get_level_values(0).unique()
                ].reset_index(),
                out_dir / "error_incomplete_cut.feather",
                crs=CRS,
            )

            # remove these from the cut geoms and retain their originals
            geoms = geoms.loc[~errors].copy()

        # Explode the multilines into single line segments
        geoms["geometry"] = explode(geoms.geometry)
        geoms = geoms.explode("geometry")

        # mark those parts of the cut lines that are within waterbodies
        # WARNING: this is not capturing all that should be inside after cutting!
        geoms["iswithin"] = pg.contains(geoms.waterbody, geoms.geometry)

        errors = geoms.groupby(level=0).iswithin.max() == False
        if errors.max():
            print(
                "WARNING: {:,} flowlines that cross waterbodies had no parts contained within those waterbodies".format(
                    errors.sum()
                )
            )
            to_geofeather(
                flowlines.loc[errors.index].reset_index(),
                out_dir / "error_crosses_but_not_contained.feather",
                crs=CRS,
            )

            # If they cross, assume they are within
            print("Attempting to correct these based on which ones cross")
            ix = geoms.loc[
                geoms.index.get_level_values(0).isin(errors.loc[errors].index)
            ].index
            geoms.loc[ix, "iswithin"] = pg.crosses(
                geoms.loc[ix].geometry, geoms.loc[ix].waterbody
            )

            errors = geoms.groupby(level=0).iswithin.max() == False
            print("{:,} still have no part in a waterbody".format(errors.sum()))

        # calculate total length of within and outside parts
        geoms["length"] = pg.length(geoms.geometry)

        # drop any new segments that are < 1m, these are noise
        print("Dropping {:,} new segments < 1m".format((geoms.length < 1).sum()))
        geoms = geoms.loc[geoms.length >= 1].copy()

        if len(geoms) > 1:
            length = geoms.groupby(["lineID", "wbID", "iswithin"]).agg(
                {"length": "sum", "origLength": "first"}
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
            unchanged = (
                length.reset_index().set_index(["lineID", "wbID"]).join(unchanged)
            )
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
            geoms = geoms.loc[~geoms.index.isin(is_within.index)].copy()

            print(
                "Created {:,} new flowlines by splitting {:,} flowlines at waterbody edges in {:.2f}".format(
                    len(geoms),
                    len(geoms.index.get_level_values(0).unique()),
                    time() - cut_start,
                )
            )

            if len(geoms) > 1:
                ### These are our final new lines to add
                # remove their lineIDs from flowlines and append
                # replace their outer joins to these ones and add intermediates

                # Join in previous line information from flowlines
                new_lines = (
                    geoms[["geometry", "length", "iswithin"]]
                    .reset_index()
                    .set_index("lineID")
                    .join(flowlines.drop(columns=["geometry", "length", "sinuosity"]))
                    .reset_index()
                    .rename(columns={"lineID": "origLineID", "iswithin": "waterbody"})
                )

                error = (
                    new_lines.groupby("origLineID").wbID.unique().apply(len).max() > 1
                )
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
                new_lines["length"] = pg.length(new_lines.geometry).astype("float32")
                new_lines["sinuosity"] = calculate_sinuosity(new_lines.geometry).astype(
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
                    joins,
                    first,
                    last,
                    downstream_col="downstream_id",
                    upstream_col="upstream_id",
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
                    .join(
                        flowlines[["NHDPlusID", "loop"]].rename(
                            columns={"NHDPlusID": "upstream"}
                        ),
                        on="origLineID",
                    )
                )
                # NHDPlusID is same for both sides
                new_joins["downstream"] = new_joins.upstream
                new_joins["type"] = "internal"
                new_joins = new_joins[
                    [
                        "upstream",
                        "downstream",
                        "upstream_id",
                        "downstream_id",
                        "type",
                        "loop",
                    ]
                ]

                joins = joins.append(
                    new_joins, ignore_index=True, sort=False
                ).sort_values(["downstream_id", "upstream_id"])

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

                # End cut geometries

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

