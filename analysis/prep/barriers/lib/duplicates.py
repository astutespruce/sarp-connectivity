import pandas as pd
import geopandas as gp
import pygeos as pg
from pyogrio import write_dataframe

from analysis.lib.pygeos_util import dissolve, neighborhoods
from analysis.constants import CRS, ONSTREAM_MANUALREVIEW


def find_duplicates(df, to_dedup, tolerance, next_group_id=0):
    """Find duplicate barriers that are within tolerance of each other.

    Parameters
    ----------
    df : GeoDataFrame
        will be updated with deduplication results
    to_dedup : DataFrame
        contains pygeos geometries in "geometry"
    tolerance : number
        distance within which to consider barriers duplicates
    next_group_id : int, optional (default: 0)

    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
        df, to_dedup (remaining to be deduplicated)
    """
    groups = (
        pd.DataFrame(
            neighborhoods(
                pd.Series(to_dedup.geometry.values.data, index=to_dedup.index),
                tolerance,
            )
        )
        .join(df[["dropped", "excluded", "ManualReview", "dup_sort"]])
        .sort_values(by="dup_sort")
    )

    # reset drop status of those that were dropped because they were duplicates
    # or we risk dropping clusters that include them
    groups.loc[groups.ManualReview == 11, "dropped"] = False

    groups["group"] = groups.group + next_group_id
    grouped = groups.groupby("group")
    count = grouped.size().rename("dup_count")
    groups = groups.join(count, on="group")

    ix = groups.index
    df.loc[ix, "dup_group"] = groups.loc[ix].group
    df.loc[ix, "dup_count"] = groups.loc[ix].dup_count
    df.loc[ix, "dup_log"] = "kept: duplicated by other barriers within {}m".format(
        tolerance
    )

    keep = groups.reset_index().rename(columns={"index": "id"}).groupby("group").first()
    ix = groups.loc[~groups.index.isin(keep.id.unique())].index
    df.loc[ix, "duplicate"] = True
    df.loc[ix, "dup_log"] = "duplicate: other barriers within {}m".format(tolerance)

    to_dedup = to_dedup.loc[~to_dedup.index.isin(groups.index)].copy()

    print(f"Found {len(ix):,} duplicates within {tolerance}m")

    # Drop all records from any groups that have a dropped record
    # UNLESS the one being kept is manually reviewed and not dropped

    keep_ix = keep.ManualReview.isin(ONSTREAM_MANUALREVIEW) & ~keep.dropped

    # Also keep any small barriers that were not specifically excluded or dropped
    # because they are individually evaluated
    if "SeverityClass" in df.columns:
        keep_ix = keep_ix | keep.id.isin(df.loc[~(df.dropped | df.excluded)].index)

    trusted_keepers = keep.loc[keep_ix]

    drop_groups = grouped.dropped.max()
    drop_groups = drop_groups.loc[
        drop_groups & ~drop_groups.index.isin(trusted_keepers.index)
    ].index

    count_dropped = len(df.loc[df.dup_group.isin(drop_groups) & ~df.dropped])
    print(
        f"Dropped {count_dropped:,} barriers that were in duplicate groups with dams that were dropped"
    )

    ix = df.dup_group.isin(drop_groups)
    df.loc[ix, "dropped"] = True
    df.loc[ix, "dup_log"] = "dropped: at least one of duplicates marked to drop"

    # Exclude all records from groups that have an excluded record
    exclude_groups = grouped.excluded.max()
    exclude_groups = exclude_groups.loc[
        exclude_groups & ~exclude_groups.index.isin(trusted_keepers.index)
    ].index

    count_excluded = len(df.loc[df.dup_group.isin(exclude_groups) & ~df.excluded])
    print(
        f"Excluded {count_excluded:,} barriers that were in duplicate groups with barriers that were excluded"
    )

    ix = df.dup_group.isin(exclude_groups)
    df.loc[ix, "excluded"] = True
    df.loc[ix, "dup_log"] = "excluded: at least one of duplicates marked to exclude"

    return df, to_dedup


def export_duplicate_areas(dups, path):
    """Export duplicate barriers for QA.

    Parameters
    ----------
    dups : GeoDataFrame
        contains "geometry" and "dup_group"
        to indicate group
    path : str or Path
        output path
    """

    print("Exporting duplicate areas")

    dups = dups.copy()
    dups["geometry"] = pg.buffer(dups.geometry.values.data, dups.dup_tolerance)
    dissolved = dissolve(dups[["geometry", "dup_group"]], by="dup_group")
    groups = gp.GeoDataFrame(
        dups[["id", "SARPID", "dup_group"]]
        .join(dissolved.geometry, on="dup_group")
        .groupby("dup_group")
        .agg({"geometry": "first", "SARPID": "unique", "id": "unique"}),
        crs=dups.crs,
    )
    groups["id"] = groups.id.apply(lambda x: ", ".join([str(s) for s in x]))
    groups["SARPID"] = groups.SARPID.apply(lambda x: ", ".join([str(s) for s in x]))
    write_dataframe(groups, path)
