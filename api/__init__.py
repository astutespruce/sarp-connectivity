import os
import tempfile
import time
from datetime import date
import pandas as pd
import geopandas as gp
from flask import Flask, abort, request, send_file, make_response

from api.calculate_tiers import calculate_tiers, SCENARIOS


app = Flask(__name__)
log = app.logger

LAYERS = ("HUC6", "HUC8", "HUC12", "State")
FORMATS = ("csv", "shp")


# Read source data into memory
dams_df = pd.read_csv(
    "data/src/dams.csv",
    dtype={"HUC6": str, "HUC8": str, "HUC12": str, "ECO3": str, "ECO4": str},
).set_index(["id"])
print("Data loaded")


# TODO: log incoming request parameters
@app.route("/api/v1/dams/<format>/<layer>")
def download_dams(layer="HUC8", format="CSV"):
    """Download subset of dams data.

    Query parameters:
    * ids: list of ids
    * filter: TBD
    * include_unranked: bool

    Parameters
    ----------
    layer : str (default: HUC8)
        Layer to use for subsetting by ID.  One of: HUC6, HUC8, HUC12, State, ... TBD
            
    format : str (default: CSV)
        Format for download.  One of: CSV, SHP
    """

    args = request.args

    if not layer in LAYERS:
        abort(
            400,
            "layer is not valid: {0}; must be one of {1}".format(
                layer, ", ".join(LAYERS)
            ),
        )

    if not format in FORMATS:
        abort(
            400,
            "format is not valid: {0}; must be one of {1}".format(
                layer, ", ".join(FORMATS)
            ),
        )

    include_unranked = args.get("include_unranked", True)

    ids = request.args.get("id", "").split(",")
    if not ids:
        abort(400, "id must be non-empty")

    # TODO: validate that rows were returned for these ids
    df = dams_df[dams_df[layer].isin(ids)].copy()
    nrows = len(df.index)

    log.info("selected {} dams".format(nrows))

    if not nrows:
        abort(
            404,
            "no dams are contained in selected ids {0}:{1}".format(
                layer, ",".join(ids)
            ),
        )

    tiers_df = calculate_tiers(df, SCENARIOS, prefix="custom")

    # TODO: join type is based on include_unranked
    join_type = "left" if include_unranked else "right"
    df = df.join(tiers_df, how=join_type)

    print("df.columns", df.columns)

    # Fill n/a with -1 for tiers and cast columns to integers
    df[tiers_df.columns] = df[tiers_df.columns].fillna(-1)
    for scenario in SCENARIOS:
        for col in (scenario, "{}_p".format(scenario), "{}_top".format(scenario)):
            df[col] = df[col].astype("int8")

    # Serialize to format
    # TODO: bundle this into zip file
    filename = "sarp_custom_ranks_{}".format(date.today().isoformat())
    if format == "csv":
        resp = make_response(df.to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename={}.csv".format(
            filename
        )
        resp.headers["Content-Type"] = "text/csv"
        return resp

    # Should never get here
    return 'Done'


if __name__ == "__main__":
    app.run(debug=True)