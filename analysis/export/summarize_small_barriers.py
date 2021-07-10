from pathlib import Path

import pandas as pd

from api.constants import DOMAINS

current_version = "DEV"

data_dir = Path("data/barriers/master")
out_dir = Path("data/versions")

df = pd.read_feather(data_dir / "small_barriers.feather")
api_df = pd.read_feather("data/api/small_barriers_all.feather")


with pd.ExcelWriter(out_dir / f"small_barriers_{current_version}_summary.xlsx") as xlsx:
    # state level summary
    state_total = df.groupby("State").size().rename("Raw total")
    state_dropped = df.loc[df.dropped].groupby("State").size().rename("dropped")
    state_excluded = df.loc[df.excluded].groupby("State").size().rename("excluded")
    state_duplicate = df.loc[df.duplicate].groupby("State").size().rename("duplicate")
    state_snapped = df.loc[df.snapped].groupby("State").size().rename("snapped")
    state_analyzed = (
        df.loc[df.snapped & ~(df.duplicate | df.dropped | df.excluded)]
        .groupby("State")
        .size()
        .rename("analyzed")
    )

    state_stats = (
        pd.DataFrame(state_total)
        .join(state_dropped)
        .join(state_excluded)
        .join(state_duplicate)
        .join(state_snapped)
        .join(state_analyzed)
        .fillna(0)
        .astype("uint")
    )

    state_stats.reset_index().to_excel(xlsx, sheet_name="State stats", index=False)

    # create breakdown of small barriers by estimated and other columns
    for field in [
        "PotentialProject",
        "SeverityClass",
        "ConditionClass",
        "CrossingType",
        "ManualReview",
        "snapped",
        "excluded",
        "dropped",
    ]:
        group = [field]
        if field in DOMAINS:
            label_field = f"{field}_label"
            df[label_field] = df[field].map(DOMAINS[field])
            group.append(label_field)

        raw = df.groupby(group).size().rename("Raw total")
        analyzed = (
            df.loc[df.snapped & ~(df.duplicate | df.dropped | df.excluded)]
            .groupby(group)
            .size()
            .rename("analyzed")
        )

        pd.DataFrame(raw).join(analyzed).fillna(0).astype(
            "uint"
        ).reset_index().to_excel(xlsx, sheet_name=f"Barriers by {field}", index=False)

    # add Ownership stats - from api dataset
    for field in ["OwnerType", "ProtectedLand"]:
        group = [field]
        if field in DOMAINS:
            label_field = f"{field}_label"
            api_df[label_field] = api_df[field].map(DOMAINS[field])
            group.append(label_field)

        api_df.loc[api_df.HasNetwork].groupby(group).size().rename(
            "analyzed"
        ).reset_index().to_excel(xlsx, sheet_name=f"Analyzed Barriers by {field}")

