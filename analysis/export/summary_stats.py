from pathlib import Path

import pandas as pd

from api.constants import DOMAINS

current_version = "Dec2020"

data_dir = Path("data/barriers/master")
out_dir = Path("data/versions")

df = pd.read_feather(data_dir / "dams.feather")

# temporary shim (TODO: remove)
df["is_estimated"] = df.snap_group == 1


with pd.ExcelWriter(out_dir / f"dams_{current_version}_summary.xlsx") as xlsx:
    # create breakdown of dams by estimated and other columns
    for field in ["Recon", "ManualReview", "snapped", "excluded", "dropped"]:
        group = [field]
        if field in DOMAINS:
            label_field = f"{field}_label"
            df[label_field] = df[field].map(DOMAINS[field])
            group.append(label_field)

        df.groupby(group).size().rename("count").reset_index().to_excel(
            xlsx, sheet_name=f"Dams by {field}", index=False
        )

        group.insert(0, "is_estimated")

        stats = (
            df.groupby(group)
            .size()
            .rename("count")
            .reset_index()
            .to_excel(xlsx, sheet_name=f"Estimated Dams by {field}", index=False)
        )
