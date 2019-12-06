import geopandas as gp


def cut_lines_by_waterbodies(flowlines, joins, waterbodies, wb_joins):
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

    print(
        "Identifying flowlines completely within waterbodies, this might take a while"
    )
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

    print(
        "Determining which flowlines actually cross into waterbodies, this might take a while"
    )
    # Most polygons only touch, find the ones that cross for further evaluation
    # this is SLOW!!
    boundary = gp.GeoSeries(to_cut.waterbody).boundary
    crosses = to_cut.crosses(boundary)

    # Any that do not cross and are not completely within waterbodies should be dropped now
    # Can only drop joins by BOTH lineID and wbID
    drop_ids = to_cut.loc[~crosses, []]

    # Calculate geometric difference between lines and boundary
    # this should produce cut lines
    # WARNING: if lines share a common edge, they will be dropped here
    to_cut = to_cut[crosses].copy()
    boundary = boundary[crosses]

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
    )

    # mark those parts of the cut lines that are within waterbodies
    new_lines["iswithin"] = new_lines.within(gp.GeoSeries(new_lines.waterbody))

    # Anything within 1 meter of original length is considered unchanged
    # This is so that we ignore slivers
    new_lines["unchanged"] = (new_lines.origLength - new_lines.length).abs() <= 1

    # For any that are unchanged and within waterbodies, set them to the inside and remove from here
    ix = (
        new_lines.loc[new_lines.iswithin & new_lines.unchanged, ["lineID", "wbID"]]
        .drop_duplicates()
        .set_index(["lineID", "wbID"])
        .index
    )
    wb_lines.loc[ix, "inside"] = True
    # TODO: remove from intersection analysis

    # For any that are unchanged and NOT within waterbodies, remove them from wb_lines and wb_joins, and from here
    ix = (
        new_lines.loc[~new_lines.iswithin & new_lines.unchanged, ["lineID", "wbID"]]
        .drop_duplicates()
        .set_index(["lineID", "wbID"])
        .index
    )
    wb_lines = wb_lines.loc[~wb_lines.index.isin(ix)].copy()
    wb_joins = wb_joins.set_index(["lineID", "wbID"])
    wb_joins = wb_joins.loc[~wb_joins.index.isin(ix)].reset_index()

    # Remove any that are unchanged from intersection analysis
    ix = (
        new_lines.loc[new_lines.unchanged, ["lineID", "wbID"]]
        .drop_duplicates()
        .set_index(["lineID", "wbID"])
        .index
    )
    new_lines = new_lines.set_index(["lineID", "wbID"])
    new_lines = new_lines.loc[~new_lines.index.isin(ix)].copy()

    # These are our final new lines to add
    # remove their lineIDs from flowlines and append
    # replace their outer joins to these ones and add intermediates

