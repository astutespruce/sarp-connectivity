from pathlib import Path

from nhdnet.io import deserialize_gdf, deserialize_sindex
from nhdnet.geometry.lines import snap_to_line


nhd_dir = Path("data/nhd/flowlines")


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
        flowlines = (
            deserialize_gdf(region_dir / "flowline.feather")[
                ["geometry", "lineID", "NHDPlusID", "streamorder", "sizeclass"]
            ]
            .rename(columns={"streamorder": "StreamOrder", "sizeclass": "SizeClass"})
            .set_index("lineID", drop=False)
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


def update_from_snapped(df, snapped):
    """Update snapped coordinates into dataset.
    
    Parameters
    ----------
    df : GeoDataFrame
        Master dataset to update with snapped coordinates
    snapped : GeoDataFrame
        Snapped dataset with coordinates to apply
    
    Returns
    -------
    GeoDataFrame
    """

    df["snapped"] = False
    df = df.join(
        snapped.set_index("id")[
            ["geometry", "snap_dist", "lineID", "NHDPlusID", "StreamOrder", "SizeClass"]
        ],
        on="id",
        rsuffix="_snapped",
    )
    idx = df.loc[df.lineID.notnull()].index
    df.loc[idx, "geometry"] = df.loc[idx].geometry_snapped
    df.loc[idx, "snapped"] = True
    df = df.drop(columns=["geometry_snapped"])

    return df
