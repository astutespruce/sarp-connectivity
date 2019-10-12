import geopandas as gp


def spatial_join(left, right):
    left.sindex
    right.sindex

    joined = gp.sjoin(left, right, how="left").drop(columns=["index_right"])

    # WARNING: some places have overlapping areas (e.g., protected areas), this creates extra records!
    # Take the first entry in each case
    grouped = joined.groupby(level=0)
    if grouped.size().max() > 1:
        print(
            "WARNING: multiple target areas returned in spatial join for a single point"
        )

        # extract the right side indexed by the left, and take first record
        right = grouped[
            [c for c in right.columns if not c == right._geometry_column_name]
        ].first()
        joined = left.join(right)

    # pending https://github.com/geopandas/geopandas/issues/846
    # we have to reassign the original index name
    joined.index.name = left.index.name

    return joined


def unique(items):
    """Convert a sorted list of items into a unique list, taking the 
    first occurrence of each duplicate item.
    
    Parameters
    ----------
    items : list-like
    
    Returns
    -------
    list
    """

    s = set()
    result = []
    for item in items:
        if not item in s:
            result.append(item)
            s.add(item)

    return result
