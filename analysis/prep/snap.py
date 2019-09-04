from pathlib import Path

from nhdnet.io import deserialize_gdf, deserialize_sindex
from nhdnet.geometry.lines import snap_to_line


nhd_dir = Path("../data/sarp/derived/nhd/region")


def snap_by_region(df, regions, tolerance):
    """Snap barriers 
    
    Parameters
    ----------
    df : GeoDataFrame
        Input barriers to be snapped
    regions : dict
        Dictionary of region IDs to list of units in region
    tolerance : float
        distance within which to allow snapping to flowlines
    
    Returns
    -------
    GeoDataFrame
        snapped barriers (unsnapped are dropped) with additional fields from snapping:
        lineID, NHDPlusID, snap_dist, nearby
    """

    merged = None

    for region in regions:
        print("\n----- {} ------\n".format(region))
        region_dir = nhd_dir / region

        print("Reading flowlines")
        flowlines = deserialize_gdf(region_dir / "flowline.feather").set_index(
            "lineID", drop=False
        )
        print("Read {0} flowlines".format(len(flowlines)))

        print("Reading spatial index on flowlines")
        sindex = deserialize_sindex(region_dir / "flowline.sidx")

        # Extract out waterfalls in this HUC
        in_region = df.loc[df.HUC2.isin(regions[region])]
        print("Selected {0} barriers in region".format(len(in_region)))

        print("Snapping to flowlines")
        snapped = snap_to_line(in_region, flowlines, tolerance, sindex=sindex)
        print("{} barriers were successfully snapped".format(len(snapped)))

        if merged is None:
            merged = snapped
        else:
            merged = merged.append(snapped, sort=False, ignore_index=True)

    return merged
