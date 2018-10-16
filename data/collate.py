"""Collate together the various data files for use in the frontend

"""

import json
import pandas as pd

units = (
    "states",
    "HUC2",
    "HUC4",
    "HUC8",
    "ecoregion1",
    "ecoregion2",
    "ecoregion3",
    "ecoregion4",
)

field_lut = {
    "states": "NAME",
    "HUC2": "HUC2",
    "HUC4": "HUC4",
    "HUC8": "HUC8",
    "ecoregion1": "NA_L1CODE",
    "ecoregion2": "NA_L2CODE",
    "ecoregion3": "NA_L3CODE",
    "ecoregion4": "L4_KEY",
}

data = {}

# TODO: drop containing unit IDs
for unit in units:
    field = field_lut[unit]
    dtype = {field: "str"}
    summary_df = pd.read_csv("data/summary/{}.csv".format(unit), dtype=dtype).set_index(
        field
    )[["dams", "connectedmiles"]]
    summary_df["connectedmiles"] = summary_df.apply(
        lambda row: round(row.connectedmiles, 2), axis=1
    )
    summary_df["id"] = summary_df.index

    geo_df = pd.read_csv(
        "data/src/sarp_{}_centroids.csv".format(unit), dtype=dtype
    ).set_index(field)

    geo_df["center"] = geo_df.apply(
        lambda row: [round(row.x, 5), round(row.y, 5)], axis=1
    )
    geo_df["bbox"] = geo_df.apply(lambda row: json.loads(row.bbox), axis=1)

    df = summary_df.join(geo_df[["center", "bbox"]], how="inner")
    # df.to_csv("ui/src/data/{}.csv".format(unit))

    data[unit] = df.to_dict(orient="records")

with open("ui/src/data/units.json", "w") as out:
    out.write(json.dumps(data))
