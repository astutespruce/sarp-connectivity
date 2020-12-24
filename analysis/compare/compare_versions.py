from pathlib import Path
from datetime import date

import pandas as pd
import geopandas as gp

prev_version = "May2020"

data_dir = Path("data/barriers/master")
out_dir = Path("data/versions")


cols = [
    "ManualReview",
    "Recon",
    "Feasibility",
    "dropped",
    "excluded",
    "duplicate",
    "snapped",
]
had_manual_review = [4, 5, 8, 10, 11, 13, 14, 15]

read_cols = ["SARPID"] + cols

df = pd.read_feather(data_dir / "dams.feather", columns=read_cols)
prev = pd.read_feather(
    data_dir / "archive" / prev_version / "dams.feather",
    columns=read_cols,
)

filename = out_dir / f"dams_{date.today()}_vs_{prev_version}"

with pd.ExcelWriter(f"{filename}.xlsx") as xlsx, open(f"{filename}.md", "w") as out:
    out.write(f"# Dams {date.today()} vs {prev_version}\n\n")

    stats = pd.DataFrame(
        {"latest": [len(df)], "prev": [len(prev)], "diff": [len(df) - len(prev)]}
    )
    stats.to_excel(xlsx, sheet_name="Overall", index=False)

    out.write("## Overall stats\n")
    out.write(stats.to_markdown(index=False))

    for col in cols:
        stats = (
            pd.DataFrame(df.groupby(col).size().rename("latest"))
            .join(prev.groupby(col).size().rename("prev"))
            .fillna(0)
            .astype("int")
        )
        stats["diff"] = stats.latest - stats.prev

        out.write(f"\n\n## {col}\n")
        out.write(stats.to_markdown())
        stats.to_excel(xlsx, sheet_name=col)

    # Again for Recon but filtered by ManualReview
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
        .astype("int")
    )
    stats["diff"] = stats.latest - stats.prev

    out.write(f"\n\n## Recon for only those that were manually reviewed\n")
    out.write(f"ManualReview one of {had_manual_review}\n\n")
    out.write(stats.to_markdown())
    stats.to_excel(xlsx, sheet_name="Recon (only for manually reviewed dams)")

    # now look at pairs of dams based on SARPID
    joined = df.set_index("SARPID")[cols].join(
        prev.set_index("SARPID")[cols], rsuffix="_prev"
    )
    for col in cols:
        stats = joined.groupby([f"{col}_prev", col]).size().reset_index()
        stats = stats.loc[stats[col] != stats[f"{col}_prev"]].set_index(
            [f"{col}_prev", col]
        )

        out.write(f"\n\n## {col} - change by dam\n")
        out.write(stats.to_markdown())
        stats.to_excel(xlsx, sheet_name=f"{col}_change")
