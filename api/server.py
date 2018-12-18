import os
import tempfile
import time
from datetime import date
import pandas as pd
import geopandas as gp
from feather import read_dataframe
from flask import Flask, abort, request, send_file, make_response
from flask_cors import CORS

from api.calculate_tiers import calculate_tiers, SCENARIOS


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
log = app.logger

LAYERS = ("HUC6", "HUC8", "HUC12", "State")
FORMATS = ("csv",)  # TODO: "shp"

FILTER_FIELDS = [
    "HeightClass",
    "RareSppClass",
    "GainMilesClass",
    "LandcoverClass",
    "SizeClasses",
    "StreamOrderClass",
]


# Read source data into memory
dams = read_dataframe("data/src/dams.feather").set_index(["id"])

dams_with_network = dams.loc[dams.HasNetwork]

print("Data loaded")


def validate_layer(layer):
    if not layer in LAYERS:
        abort(
            400,
            "layer is not valid: {0}; must be one of {1}".format(
                layer, ", ".join(LAYERS)
            ),
        )


def validate_format(format):
    if not format in FORMATS:
        abort(400, "format is not valid; must be one of {0}".format(", ".join(FORMATS)))


# TODO: log incoming request parameters
@app.route("/api/v1/dams/rank/<layer>")
def rank(layer="HUC8"):
    """Rank a subset of dams data.

    Query parameters:
    * id: list of ids
    * filter: TBD

    Parameters
    ----------
    layer : str (default: HUC8)
        Layer to use for subsetting by ID.  One of: HUC6, HUC8, HUC12, State, ... TBD
    """

    args = request.args

    validate_layer(layer)

    ids = request.args.get("id", "").split(",")
    if not ids:
        abort(400, "id must be non-empty")

    # TODO: validate that rows were returned for these ids
    df = dams_with_network[dams[layer].isin(ids)].copy()
    nrows = len(df.index)

    log.info("selected {} dams".format(nrows))

    # TODO: return a 204 instead?
    if not nrows:
        abort(
            404,
            "no dams are contained in selected ids {0}:{1}".format(
                layer, ",".join(ids)
            ),
        )

    tiers_df = calculate_tiers(df, SCENARIOS)
    df = df[["lat", "lon"]].join(tiers_df)

    for col in tiers_df.columns:
        if col.endswith("_tier"):
            df[col] = df[col].astype("int8")
        elif col.endswith("_score"):
            # Convert to a 100% scale
            df[col] = (df[col] * 100).round().astype("uint16")

    resp = make_response(df.to_csv(index_label="id"))
    resp.headers["Content-Type"] = "text/csv"
    return resp


@app.route("/api/v1/dams/query/<layer>")
def query(layer="HUC8"):
    """Filter dams and return key properties for filtering.  ONLY for those with networks.

    Query parameters:
    * id: list of ids

    Parameters
    ----------
    layer : str (default: HUC8)
        Layer to use for subsetting by ID.  One of: HUC6, HUC8, HUC12, State, ... TBD
    """

    args = request.args

    validate_layer(layer)

    ids = request.args.get("id", "").split(",")
    if not ids:
        abort(400, "id must be non-empty")

    # TODO: validate that rows were returned for these ids
    df = dams_with_network[dams[layer].isin(ids)][FILTER_FIELDS].copy()
    nrows = len(df.index)

    log.info("selected {} dams".format(nrows))

    resp = make_response(df.to_csv(index_label="id"))
    resp.headers["Content-Type"] = "text/csv"
    return resp


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

    validate_layer(layer)
    validate_format(format)

    include_unranked = args.get("include_unranked", True)

    ids = request.args.get("id", "").split(",")
    if not ids:
        abort(400, "id must be non-empty")

    # TODO: validate that rows were returned for these ids
    df = dams[dams[layer].isin(ids)].copy()
    nrows = len(df.index)

    log.info("selected {} dams".format(nrows))

    if not nrows:
        abort(
            404,
            "no dams are contained in selected ids {0}:{1}".format(
                layer, ",".join(ids)
            ),
        )

    is_custom = False

    if len(ids) > 1 or layer not in ("State", "HUC8"):
        is_custom = True
        tiers_df = calculate_tiers(df, SCENARIOS, prefix="custom")

        # TODO: join type is based on include_unranked
        join_type = "left" if include_unranked else "right"
        df = df.join(tiers_df, how=join_type)

        # Fill n/a with -1 for tiers and cast columns to integers
        df[tiers_df.columns] = df[tiers_df.columns].fillna(-1)
        for scenario in SCENARIOS:
            int_fields = [scenario] + [
                f for f in tiers_df.columns if f.endswith("_p") or f.endswith("_top")
            ]
            for col in int_fields:
                df[col] = df[col].astype("int8")

    # Serialize to format
    # TODO: bundle this into zip file
    filename = "sarp_{0}_ranks_{1}".format(
        "custom" if is_custom else "{0}_{1}".format(layer, ids[0]),
        date.today().isoformat(),
    )
    if format == "csv":
        resp = make_response(df.to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename={}.csv".format(
            filename
        )
        resp.headers["Content-Type"] = "text/csv"
        return resp

    else:
        raise NotImplementedError("Not done yet!")

    # Should never get here
    return "Done"


if __name__ == "__main__":
    app.run(debug=True)
