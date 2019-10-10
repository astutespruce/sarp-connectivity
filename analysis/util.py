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

