import geopandas as gp


def spatial_join(left, right):
    # TODO: evaluate if having sindex in advance helps
    left.sindex
    right.sindex

    joined = gp.sjoin(left, right, how="left").drop(columns=["index_right"])

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
