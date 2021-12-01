from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, NamedStyle
from openpyxl.utils import get_column_letter

from api.constants import DOMAINS

primary_col_style = NamedStyle(
    name="PrimaryColumnStyle", alignment=Alignment(horizontal="left", wrap_text=True)
)


current_version = "Nov2021"

data_dir = Path("data/barriers/master")
out_dir = Path("data/versions")

had_manual_review = [4, 5, 8, 10, 11, 13, 14, 15]

common_status_fields = [
    "snapped",
    "excluded",
    "dropped",
    "duplicate",
    "unranked",
    "loop",
]
barrier_status_fields = {
    "dams": common_status_fields + ["is_estimated",],
    "small_barriers": common_status_fields.copy(),
}


common_summary_fields = [
    "ManualReview",
    "log",
    "snap_log",
]
barrier_summary_fields = {
    "dams": ["Recon",] + common_summary_fields,
    "small_barriers": common_summary_fields
    + ["PotentialProject", "SeverityClass", "ConditionClass", "CrossingType"],
}


for barrier_type in ["dams", "small_barriers"]:
    print(f"Summarizing {barrier_type}...")
    type_label = "dams" if barrier_type == "dams" else "road-related barriers"

    status_fields = barrier_status_fields[barrier_type]
    summary_fields = barrier_summary_fields[barrier_type]

    df = pd.read_feather(
        data_dir / f"{barrier_type}.feather",
        columns=["id"] + summary_fields + status_fields + ["State", "HUC2"],
    )
    api_df = pd.read_feather(
        f"data/api/{barrier_type}.feather",
        columns=["id", "OwnerType", "ProtectedLand", "HasNetwork", "Ranked"],
    ).set_index("id")

    df = df.join(api_df, on="id")
    df["analyzed"] = (df.snapped & ~(df.duplicate | df.dropped | df.excluded)).astype(
        "uint8"
    )
    df["is_manualreviewed"] = df.ManualReview.isin(had_manual_review).astype("uint8")

    if barrier_type == "dams":
        df["is_reconned"] = (df.Recon > 0).astype("uint8")

    for col in status_fields + ["HasNetwork", "Ranked", "ProtectedLand", "OwnerType"]:
        df[col] = df[col].fillna(0).astype("uint8")

    status_fields += ["ProtectedLand"]
    summary_fields += ["OwnerType"]

    states = sorted(x for x in df.State.unique() if x)
    huc2 = sorted(x for x in df.HUC2.unique() if x)

    with pd.ExcelWriter(
        out_dir / f"{barrier_type}_{current_version}_summary.xlsx"
    ) as xlsx, open(
        out_dir / f"{barrier_type}_{current_version}_summary.md", "w"
    ) as md:

        ### Totals
        data = {
            "total": len(df),
            "protectedland": df.ProtectedLand.sum(),
            "invasive": df.unranked.sum(),
        }

        if barrier_type == "dams":
            data["estimated"] = df.is_estimated.sum()

        data.update(
            {
                "dropped": df.dropped.sum(),
                "excluded": df.excluded.sum(),
                "duplicate": df.duplicate.sum(),
                "snapped": df.snapped.sum(),
                "loop": df.loop.sum(),
                "analyzed": df.analyzed.sum(),
                "has_networkresults": df.HasNetwork.sum(),
                "ranked": df.Ranked.sum(),
            }
        )

        total = pd.DataFrame([data]).melt()
        total.columns = ["", "count"]
        sheet_name = f"All {type_label}"
        total.to_excel(xlsx, sheet_name=sheet_name, index=False)
        ws = xlsx.sheets[sheet_name]
        ws.column_dimensions["A"].width = 32

        md.write(f"## All {type_label}\n")
        md.write(total.to_markdown(floatfmt=",.0f", index=False))
        md.write("\n\n\n\n")

        ### Totals by state
        agg = {
            "id": "count",
            "ProtectedLand": "sum",
            "dropped": "sum",
            "excluded": "sum",
            "duplicate": "sum",
            "snapped": "sum",
            "loop": "sum",
        }

        if barrier_type == "dams":
            agg["is_estimated"] = "sum"
            agg["is_reconned"] = "sum"

        agg.update(
            {
                "is_manualreviewed": "sum",
                "analyzed": "sum",
                "HasNetwork": "sum",
                "Ranked": "sum",
            }
        )

        rename_cols = {
            "id": "total",
            "ProtectedLand": "protectedland",
            "is_estimated": "estimated",
            "HasNetwork": "has_networkresults",
            "Ranked": "ranked",
        }

        stats = df.groupby("State").agg(agg).rename(columns=rename_cols)
        sheet_name = f"{type_label} by state"
        stats.to_excel(xlsx, sheet_name=sheet_name)
        ws = xlsx.sheets[sheet_name]
        ws.column_dimensions["A"].width = 24
        for idx in range(2, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(idx)].width = 16

        for row in list(ws.rows)[1:]:
            row[0].style = primary_col_style

        md.write(f"## {type_label} by state\n")
        md.write(stats.to_markdown(floatfmt=",.0f"))
        md.write("\n\n\n\n")

        ### Totals by HUC2
        stats = df.groupby("HUC2").agg(agg).rename(columns=rename_cols)
        sheet_name = f"{type_label} by HUC2"
        stats.to_excel(xlsx, sheet_name=sheet_name)
        ws = xlsx.sheets[sheet_name]
        ws.column_dimensions["A"].width = 6
        for idx in range(2, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(idx)].width = 16

        for row in list(ws.rows)[1:]:
            row[0].style = primary_col_style

        md.write(f"## {type_label} by HUC2\n")
        md.write(stats.to_markdown(floatfmt=",.0f"))
        md.write("\n\n\n\n")

        for col in summary_fields:
            agg = {
                "id": "count",
                "ProtectedLand": "sum",
                "dropped": "sum",
                "excluded": "sum",
                "duplicate": "sum",
                "snapped": "sum",
                "loop": "sum",
            }

            if barrier_type == "dams":
                agg["is_estimated"] = "sum"
                if col != "Recon":
                    agg["is_reconned"] = "sum"

            if col != "ManualReview":
                agg["is_manualreviewed"] = "sum"

            agg.update(
                {"analyzed": "sum", "HasNetwork": "sum", "Ranked": "sum",}
            )

            rename_cols = {
                "id": "total",
                "ProtectedLand": "protectedland",
                "is_estimated": "estimated",
                "HasNetwork": "has_networkresults",
                "Ranked": "ranked",
            }

            stats = df.groupby(col).agg(agg).rename(columns=rename_cols)

            if col in DOMAINS:
                stats.index = (
                    stats.index.astype(str)
                    + ": "
                    + stats.index.map(DOMAINS[col]).fillna("")
                )

            sheet_name = f"{col} {type_label}"
            stats.to_excel(xlsx, sheet_name=sheet_name)
            ws = xlsx.sheets[sheet_name]
            ws.column_dimensions["A"].width = 60
            for idx in range(2, ws.max_column + 1):
                ws.column_dimensions[get_column_letter(idx)].width = 16

            for row in list(ws.rows)[1:]:
                row[0].style = primary_col_style

            md.write(f"## {col} {type_label}\n")
            md.write(stats.to_markdown(floatfmt=",.0f"))
            md.write("\n\n\n\n")

            ### Crosstab by state
            values = df[col].copy()
            if col in DOMAINS:
                values = (
                    df[col].astype(str) + ": " + df[col].map(DOMAINS[col]).fillna("")
                )

            crosstab = pd.crosstab(values, df.State,)

            sheet_name = f"{col} {type_label} state crosstab (total)"
            crosstab.to_excel(xlsx, sheet_name=sheet_name)
            ws = xlsx.sheets[sheet_name]
            ws.column_dimensions["A"].width = 60
            for idx in range(2, ws.max_column + 1):
                ws.column_dimensions[get_column_letter(idx)].width = 16

            for row in list(ws.rows)[1:]:
                row[0].style = primary_col_style

            md.write(f"## {col} {type_label} state crosstab (total)\n")
            md.write(crosstab.to_markdown(floatfmt=",.0f"))
            md.write("\n\n\n\n")

            ### Values by state
            stats = (
                df.groupby(["State", col])
                .agg(agg)
                .rename(columns=rename_cols)
                .reset_index()
            )
            if col in DOMAINS:
                stats[col] = (
                    stats[col].astype(str)
                    + ": "
                    + stats[col].map(DOMAINS[col]).fillna("")
                )

            sheet_name = f"{col} {type_label} by state"
            stats.to_excel(xlsx, sheet_name=sheet_name, index=False)
            ws = xlsx.sheets[sheet_name]
            ws.column_dimensions["A"].width = 24
            ws.column_dimensions["B"].width = 60
            for idx in range(3, ws.max_column + 1):
                ws.column_dimensions[get_column_letter(idx)].width = 16

            for row in list(ws.rows)[1:]:
                row[0].style = primary_col_style
                row[1].style = primary_col_style

            md.write(f"## {col} {type_label} by state\n")
            md.write(stats.to_markdown(floatfmt=",.0f", index=False))
            md.write("\n\n\n\n")

            ### Crosstab by HUC2
            values = df[col].copy()
            if col in DOMAINS:
                values = (
                    df[col].astype(str) + ": " + df[col].map(DOMAINS[col]).fillna("")
                )

            crosstab = pd.crosstab(values, df.HUC2)

            sheet_name = f"{col} {type_label} HUC2 crosstab (total)"
            crosstab.to_excel(xlsx, sheet_name=sheet_name)
            ws = xlsx.sheets[sheet_name]
            ws.column_dimensions["A"].width = 60
            for idx in range(2, ws.max_column + 1):
                ws.column_dimensions[get_column_letter(idx)].width = 16

            for row in list(ws.rows)[1:]:
                row[0].style = primary_col_style

            md.write(f"## {col} {type_label} HUC2 crosstab (total)\n")
            md.write(crosstab.to_markdown(floatfmt=",.0f"))
            md.write("\n\n\n\n")

            ### Values by HUC2
            stats = (
                df.groupby(["HUC2", col])
                .agg(agg)
                .rename(columns=rename_cols)
                .reset_index()
            )
            if col in DOMAINS:
                stats[col] = (
                    stats[col].astype(str)
                    + ": "
                    + stats[col].map(DOMAINS[col]).fillna("")
                )

            sheet_name = f"{col} {type_label} by HUC2"
            stats.to_excel(xlsx, sheet_name=sheet_name, index=False)
            ws = xlsx.sheets[sheet_name]
            ws.column_dimensions["A"].width = 6
            ws.column_dimensions["B"].width = 60
            for idx in range(3, ws.max_column + 1):
                ws.column_dimensions[get_column_letter(idx)].width = 16

            for row in list(ws.rows)[1:]:
                row[0].style = primary_col_style
                row[1].style = primary_col_style

            md.write(f"## {col} {type_label} by HUC2\n")
            md.write(stats.to_markdown(floatfmt=",.0f", index=False))
            md.write("\n\n\n\n")

