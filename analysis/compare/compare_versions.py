from pathlib import Path

import pandas as pd

pd.options.display.max_rows = 200


current_version = "DEV"
prev_version = "March2021"

data_dir = Path("data/barriers/master")
out_dir = Path("data/versions")


had_manual_review = [4, 5, 8, 10, 11, 13, 14, 15]

summary_unit_cols = ["State", "HUC2"]


status_cols = ["dropped", "excluded", "duplicate", "snapped"]

common_cols = [
    "ManualReview",
]

barrier_cols = {
    "dams": ["Recon", "Feasibility",],
    "small_barriers": ["PotentialProject", "SeverityClass",],
}


for barrier_type in ["dams", "small_barriers"]:
    print(f"Processing {barrier_type}...")

    cols = summary_unit_cols + status_cols + common_cols + barrier_cols[barrier_type]

    read_cols = ["SARPID"] + cols
    df = pd.read_feather(data_dir / f"{barrier_type}.feather", columns=read_cols)
    prev = pd.read_feather(
        data_dir / "archive" / prev_version / f"{barrier_type}.feather",
        columns=read_cols,
    )

    filename = out_dir / f"{barrier_type}_{current_version}_vs_{prev_version}"

    with pd.ExcelWriter(f"{filename}.xlsx") as xlsx, open(f"{filename}.md", "w") as out:
        out.write(f"# {current_version} vs {prev_version}\n\n")

        stats = pd.DataFrame(
            {
                "type": [
                    "total",
                    "included in network analysis",
                    "included in tool (not dropped or duplicate)",
                    "snapped (raw)",
                    "completely dropped (error, etc)",
                    "excluded from analysis (invasive barrier, removed, etc)",
                    "duplicate",
                    "manually reviewed",
                ],
                "latest": [
                    len(df),
                    (df.snapped & (~(df.dropped | df.excluded | df.duplicate))).sum(),
                    (~(df.dropped | df.duplicate)).sum(),
                    df.snapped.sum(),
                    df.dropped.sum(),
                    df.excluded.sum(),
                    df.duplicate.sum(),
                    df.ManualReview.isin(had_manual_review).sum(),
                ],
                "prev": [
                    len(prev),
                    (
                        prev.snapped
                        & (~(prev.dropped | prev.excluded | prev.duplicate))
                    ).sum(),
                    (~(prev.dropped | prev.duplicate)).sum(),
                    prev.snapped.sum(),
                    prev.dropped.sum(),
                    prev.excluded.sum(),
                    prev.duplicate.sum(),
                    prev.ManualReview.isin(had_manual_review).sum(),
                ],
            }
        )
        stats.latest = stats.latest.astype("float32")
        stats.prev = stats.prev.astype("float32")
        stats["diff"] = stats.latest - stats.prev
        stats.to_excel(xlsx, sheet_name="Overall", index=False)

        out.write("## Overall stats\n")
        out.write(stats.to_markdown(index=False, floatfmt=",.0f"))

        for col in cols:
            if col in status_cols:
                continue

            stats = (
                pd.DataFrame(df.groupby(col).size().rename("latest"))
                .join(prev.groupby(col).size().rename("prev"))
                .fillna(0)
                .astype("int")
            )
            stats.latest = stats.latest.astype("float32")
            stats.prev = stats.prev.astype("float32")
            stats["diff"] = stats.latest - stats.prev

            out.write(f"\n\n## {col} Total\n")
            out.write(stats.to_markdown(floatfmt=",.0f"))
            stats.to_excel(xlsx, sheet_name=f"{col}_total")

        # now look at pairs of dams based on SARPID
        joined = df.set_index("SARPID")[cols].join(
            prev.set_index("SARPID")[cols], rsuffix="_prev"
        )
        for col in cols:
            if col in summary_unit_cols:
                continue

            prev_col = f"{col}_prev"
            stats = joined.groupby([prev_col, col]).size().reset_index()
            stats = stats.loc[stats[col] != stats[prev_col]].set_index([prev_col, col])

            if len(stats):
                out.write(f"\n\n## {col} - change\n")
                out.write(stats.to_markdown(floatfmt=",.0f"))
                stats.to_excel(xlsx, sheet_name=f"{col}_change")

        if barrier_type == "dams":
            # Recon filtered by ManualReview
            stats = (
                pd.DataFrame(
                    df.loc[df.ManualReview.isin(had_manual_review)]
                    .groupby("Recon")
                    .size()
                    .rename("latest")
                )
                .join(
                    prev.loc[prev.ManualReview.isin(had_manual_review)]
                    .groupby("Recon")
                    .size()
                    .rename("prev")
                )
                .fillna(0)
            )
            stats.latest = stats.latest.astype("float32")
            stats.prev = stats.prev.astype("float32")
            stats["diff"] = stats.latest - stats.prev

            out.write(f"\n\n## Recon for only those that were manually reviewed\n")
            out.write(f"ManualReview one of {had_manual_review}\n\n")
            out.write(stats.to_markdown(floatfmt=",.0f"))
            stats.to_excel(xlsx, sheet_name="Recon (only for manually reviewed)")

    # compare network results
    read_cols = ["SARPID", "HasNetwork", "TotalUpstreamMiles", "TotalDownstreamMiles"]
    df = pd.read_feather(f"data/api/{barrier_type}_all.feather", columns=read_cols)
    prev = pd.read_feather(
        data_dir / "archive" / prev_version / f"api/{barrier_type}.feather",
        columns=read_cols,
    )

    df = df.join(prev.set_index("SARPID"), on="SARPID", how="left", rsuffix="_prev")
    for field in ["TotalUpstreamMiles", "TotalDownstreamMiles"]:
        df[f"{field}_diff"] = df[field] - df[f"{field}_prev"]
        df[f"{field}_absdiff"] = df[f"{field}_diff"].abs()

        if (df[f"{field}_absdiff"] > 0.1).any():
            print(f"Most differences between versions for {field}")
            print(
                df.sort_values(by=f"{field}_absdiff", ascending=False).head(100)[
                    [
                        "SARPID",
                        "HasNetwork",
                        "TotalUpstreamMiles",
                        "TotalUpstreamMiles_prev",
                        "TotalDownstreamMiles",
                        "TotalDownstreamMiles_prev",
                        f"{field}_diff",
                    ]
                ]
            )
