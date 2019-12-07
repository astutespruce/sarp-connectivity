from time import time

import geopandas as gp
import pandas as pd

from nhdnet.geometry.lines import calculate_sinuosity
from nhdnet.nhd.joins import update_joins


def cut_lines_by_waterbodies(flowlines, joins, waterbodies, wb_joins):
    start = time()
    ### Extract line segments that overlap for further analysis
    intersect_wb = flowlines.loc[
        wb_joins.lineID.unique(), ["geometry", "length"]
    ].copy()
    intersect_wb.sindex

    wb_lines = (
        intersect_wb.join(wb_joins.set_index("lineID"), how="inner")
        .reset_index()
        .set_index(["lineID", "wbID"])
    )

    wb = waterbodies[["geometry"]]
    wb.sindex

    print("Identifying flowlines completely within waterbodies...")
    join_start = time()
    inside = (
        gp.sjoin(intersect_wb, wb, how="inner", op="within")[["index_right"]]
        .reset_index()
        .rename(columns={"index": "lineID", "index_right": "wbID"})
    )

    print(
        "Identified {:,} flowlines completely contained by waterbodies in {:.2f}s".format(
            len(inside), time() - join_start
        )
    )
    # Screen for potential errors
    # these may indicate duplicate waterbodies are still present, or other geometry-related
    # issues
    error = (inside.groupby("lineID").size() > 1).sum()
    if error:
        print(
            "WARNING: {:,} lines claim to be contained by multiple polygons".format(
                error
            )
        )

    inside["inside"] = True
    wb_lines = wb_lines.join(inside.set_index(["lineID", "wbID"]))
    wb_lines.inside = wb_lines.inside.fillna(False)

    to_cut = (
        wb_lines.loc[~wb_lines.inside]
        .reset_index()
        .join(wb.geometry.rename("waterbody"), on="wbID")
        .set_index(["lineID", "wbID"])
    )

    wb_joins = wb_joins.set_index(["lineID", "wbID"])

    print("Determining which flowlines actually cross into waterbodies...")
    # Most lines only touch waterbodies
    # find the ones that cross for further evaluation
    # this is SLOW!!
    boundary = gp.GeoSeries(to_cut.waterbody).boundary
    crosses = to_cut.crosses(boundary)

    # Any that do not cross and are not completely within waterbodies should be dropped now
    # Can only drop joins by BOTH lineID and wbID (the index here)
    ix = to_cut.loc[~crosses, []].index
    wb_lines = wb_lines.loc[~wb_lines.index.isin(ix)].copy()
    wb_joins = wb_joins.loc[~wb_joins.index.isin(ix)].copy()

    # Calculate geometric difference between lines and boundary
    # this should produce cut lines
    # WARNING: if lines share a common edge, they will be dropped here
    to_cut = to_cut[crosses].copy()
    boundary = boundary[crosses]

    print(
        "Cutting {:,} flowlines that intersect with waterbodies (not all may be retained)".format(
            len(to_cut)
        )
    )

    # Fun fact: all new segments from differences are oriented from the upstream end of the
    # original line to the downstream end
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
        .reset_index()
        .join(wb.geometry.rename("waterbody"), on="wbID")
        .join(flowlines["length"].rename("origLength"), on="lineID")
        .set_index(["lineID", "wbID"])
    )

    # mark those parts of the cut lines that are within waterbodies
    new_lines["iswithin"] = new_lines.within(gp.GeoSeries(new_lines.waterbody))

    # calculate total length of parts within and outside waterbodies
    new_lines["length"] = (new_lines.length).astype("float32")
    length = (
        new_lines.reset_index()
        .groupby(["lineID", "wbID", "iswithin"])
        .agg({"length": "sum", "origLength": "first"})
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

    # For any that are unchanged and within waterbodies, set them to the inside and remove from here
    ix = is_within.loc[is_within].index
    wb_lines.loc[wb_lines.index.isin(ix), "inside"] = True

    # For any that are unchanged and NOT within waterbodies,
    # remove them from wb_lines and wb_joins
    ix = is_within.loc[~is_within].index
    wb_lines = wb_lines.loc[~wb_lines.index.isin(ix)].copy()
    wb_joins = wb_joins.loc[~wb_joins.index.isin(ix)].copy()

    # Remove any that are unchanged from intersection analysis
    new_lines = new_lines.loc[~new_lines.index.isin(is_within.index)].copy()

    print(
        "Created {:,} new flowlines by splitting at waterbody edges".format(
            len(new_lines)
        )
    )

    ### These are our final new lines to add
    # remove their lineIDs from flowlines and append
    # replace their outer joins to these ones and add intermediates

    # Join in previous line information from flowlines
    new_lines = (
        new_lines.reset_index()
        .set_index("lineID")
        .join(flowlines.drop(columns=["geometry", "length", "sinuosity"]))
        .reset_index()
        .drop(columns=["origLength", "waterbody", "level_0"])
        .rename(
            columns={"lineID": "origLineID", "iswithin": "waterbody", "level_1": "i"}
        )
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

    # recalculate sinuosity
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
    print(
        "Removing {:,} flowlines now replaced by new segments".format(
            len(new_lines.origLineID.unique())
        )
    )
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
        flowlines.index.isin(
            wb_lines.loc[wb_lines.inside].reset_index().lineID.unique()
        ),
        "waterbody",
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
