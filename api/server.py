import os
from io import BytesIO
from zipfile import ZipFile
import time
import logging
from datetime import date
import pandas as pd
from feather import read_dataframe
from flask import Flask, abort, request, send_file, make_response, render_template
from flask_cors import CORS
from raven.contrib.flask import Sentry
from raven.handlers.logging import SentryHandler
from raven.conf import setup_logging

from api.calculate_tiers import calculate_tiers, SCENARIOS
from api.domains import (
    FEASIBILITY_DOMAIN,
    PURPOSE_DOMAIN,
    CONSTRUCTION_DOMAIN,
    DAM_CONDITION_DOMAIN,
    BARRIER_SEVERITY_DOMAIN,
)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
log = app.logger

SENTRY_DSN = os.getenv("SENTRY_DSN", None)
sentry = Sentry(app, dsn=SENTRY_DSN)
if SENTRY_DSN is not None:
    print("Configuring Sentry logging...")
    handler = SentryHandler(SENTRY_DSN)
    handler.setLevel(logging.ERROR)
    setup_logging(handler)
else:
    print("Sentry not configured")


TYPES = ("dams", "barriers")
LAYERS = ("HUC6", "HUC8", "HUC12", "State", "County", "ECO3", "ECO4")
FORMATS = ("csv",)  # TODO: "shp"


DAM_FILTER_FIELDS = [
    "Feasibility",
    "HeightClass",
    "Condition",
    "Construction",
    "Purpose",
    "RareSppClass",
    "StreamOrderClass",
    "GainMilesClass",
    # "LandcoverClass",
    "SizeClasses",
]

dam_filter_field_map = {f.lower(): f for f in DAM_FILTER_FIELDS}

BARRIER_FILTER_FIELDS = [
    "ConditionClass",
    "SeverityClass",
    "CrossingTypeClass",
    "RoadTypeClass",
    "RareSppClass",
    "GainMilesClass",
    # "LandcoverClass",
    "SizeClasses",
]
barrier_filter_field_map = {f.lower(): f for f in BARRIER_FILTER_FIELDS}


DAM_EXPORT_COLUMNS = [
    "lat",
    "lon",
    # ID and source info
    "SARPID",
    "NIDID",
    "Source",
    # Basic info
    "Name",
    "County",
    "State",
    "Basin",
    # Species info
    "RareSpp",
    # River info
    "River",
    "StreamOrder",
    "NHDplusVersion",
    "HasNetwork",
    # Location info
    "ProtectedLand",
    "HUC6",
    "HUC8",
    "HUC12",
    "ECO3",
    "ECO4",
    # Dam info
    "Height",
    "Year",
    "Construction",
    "Purpose",
    "Condition",
    # "Recon",  # intentionally omitted
    "Feasibility",
    # Metrics
    "GainMiles",
    "UpstreamMiles",
    "DownstreamMiles",
    "TotalNetworkMiles",
    "Landcover",
    "Sinuosity",
    "SizeClasses",
    # Tiers
    "NC_tier",
    "WC_tier",
    "NCWC_tier",
    "SE_NC_tier",
    "SE_WC_tier",
    "SE_NCWC_tier",
    "State_NC_tier",
    "State_WC_tier",
    "State_NCWC_tier",
]

BARRIER_EXPORT_COLUMNS = [
    "lat",
    "lon",
    # ID and source info
    "SARPID",
    "CrossingCode",
    "LocalID",
    "Source",
    # Basic info
    "Name",
    "County",
    "State",
    "Basin",
    # Species info
    "RareSpp",
    # River info
    "Stream",
    "HasNetwork",
    # Road info
    "Road",
    "RoadType",
    # Barrier info
    "CrossingType",
    "Condition",
    "PotentialProject",
    "SeverityClass",
    # Location info
    "ProtectedLand",
    "HUC6",
    "HUC8",
    "HUC12",
    "ECO3",
    "ECO4",
    # Metrics
    "GainMiles",
    "UpstreamMiles",
    "DownstreamMiles",
    "TotalNetworkMiles",
    "Landcover",
    "Sinuosity",
    "SizeClasses",
    # Tiers
    "NC_tier",
    "WC_tier",
    "NCWC_tier",
    "SE_NC_tier",
    "SE_WC_tier",
    "SE_NCWC_tier",
    "State_NC_tier",
    "State_WC_tier",
    "State_NCWC_tier",
]


# Read source data into memory
try:
    dams = read_dataframe("data/derived/dams.feather").set_index(["id"])
    dams_with_networks = dams.loc[dams.HasNetwork]

    barriers = read_dataframe("data/derived/small_barriers.feather").set_index(["id"])
    barriers_with_networks = barriers.loc[barriers.HasNetwork]

    print("Data loaded")

except:
    print("ERROR: not able to load data")
    sentry.captureException()


def validate_type(barrier_type):
    if not barrier_type in TYPES:
        abort(
            400,
            "type is not valid: {0}; must be one of {1}".format(
                barrier_type, ", ".join(TYPES)
            ),
        )


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


@app.route("/api/v1/<barrier_type>/query/<layer>", methods=["GET"])
def query(barrier_type="dams", layer="HUC8"):
    """Filter dams and return key properties for filtering.  ONLY for those with networks.

    Path parameters:
    <barrier_type> : one of TYPES
    <layer> : one of LAYERS

    Query parameters:
    * id: list of ids

    Parameters
    ----------
    layer : str (default: HUC8)
        Layer to use for subsetting by ID.  One of: HUC6, HUC8, HUC12, State, ... TBD
    """

    validate_type(barrier_type)
    validate_layer(layer)

    if layer == "County":
        layer = "COUNTYFIPS"

    ids = request.args.get("id", "").split(",")
    if not ids:
        abort(400, "id must be non-empty")

    if barrier_type == "dams":
        df = dams_with_networks
        field_map = dam_filter_field_map
        fields = DAM_FILTER_FIELDS
    else:
        df = barriers_with_networks
        field_map = barrier_filter_field_map
        fields = BARRIER_FILTER_FIELDS

    df = df.loc[df[layer].isin(ids)][fields].copy()
    nrows = len(df.index)
    log.info("selected {} dams".format(nrows))

    resp = make_response(
        df.to_csv(index_label="id", header=[c.lower() for c in df.columns])
    )

    resp.headers["Content-Type"] = "text/csv"
    return resp


# TODO: log incoming request parameters
@app.route("/api/v1/<barrier_type>/rank/<layer>", methods=["GET"])
def rank(barrier_type="dams", layer="HUC8"):
    """Rank a subset of dams data.

    Path parameters:
    <barrier_type> : one of TYPES
    <layer> : one of LAYERS

    Query parameters:
    * id: list of ids
    * filters are defined using a lowercased version of column name and a comma-delimited list of values

    Parameters
    ----------
    layer : str (default: HUC8)
        Layer to use for subsetting by ID.  One of: HUC6, HUC8, HUC12, State, ... TBD
    """

    args = request.args

    validate_type(barrier_type)
    validate_layer(layer)

    if layer == "County":
        layer = "COUNTYFIPS"

    ids = request.args.get("id", "").split(",")
    if not ids:
        abort(400, "id must be non-empty")

    if barrier_type == "dams":
        df = dams_with_networks
        field_map = dam_filter_field_map
    else:
        df = barriers_with_networks
        field_map = barrier_filter_field_map

    filters = df[layer].isin(ids)

    filterKeys = [a for a in request.args if not a == "id"]
    # TODO: make this more efficient
    for filter in filterKeys:
        # convert all incoming to integers
        values = [int(x) for x in request.args.get(filter).split(",")]
        filters = filters & df[field_map[filter]].isin(values)

    df = df.loc[filters].copy()
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

    resp = make_response(
        df.to_csv(index_label="id", header=[c.lower() for c in df.columns])
    )
    resp.headers["Content-Type"] = "text/csv"
    return resp


# TODO: log incoming request parameters
@app.route("/api/v1/<barrier_type>/<format>/<layer>", methods=["GET"])
def download_dams(barrier_type="dams", layer="HUC8", format="CSV"):
    """Download subset of dams data.

    Path parameters:
    <barrier_type> : one of TYPES
    <layer> : one of LAYERS

    Query parameters:
    * ids: list of ids
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    * include_unranked: bool

    Parameters
    ----------
    layer : str (default: HUC8)
        Layer to use for subsetting by ID.  One of: HUC6, HUC8, HUC12, State, ... TBD
            
    format : str (default: csv)
        Format for download.  One of: csv, shp
    """

    args = request.args

    validate_type(barrier_type)
    validate_layer(layer)
    validate_format(format)

    if layer == "County":
        layer = "COUNTYFIPS"

    include_unranked = args.get("include_unranked", True)

    ids = args.get("id", "").split(",")
    if not ids:
        abort(400, "id must be non-empty")

    if barrier_type == "dams":
        df = dams_with_networks
        field_map = dam_filter_field_map
        export_columns = DAM_EXPORT_COLUMNS
    else:
        df = barriers_with_networks
        field_map = barrier_filter_field_map
        export_columns = BARRIER_EXPORT_COLUMNS

    if not include_unranked:
        df = df.loc[df.HasNetwork]

    filters = df[layer].isin(ids)
    filterKeys = [a for a in request.args if not a == "id"]
    for filter in filterKeys:
        # convert all incoming to integers
        values = [int(x) for x in request.args.get(filter).split(",")]
        filters = filters & df[field_map[filter]].isin(values)

    df = df.loc[filters].copy()
    nrows = len(df.index)

    log.info("selected {} dams".format(nrows))

    tiers_df = calculate_tiers(df, SCENARIOS)

    # TODO: join type is based on include_unranked
    join_type = "left" if include_unranked else "right"
    df = df.join(tiers_df, how=join_type)

    # Fill n/a with -1 for tiers and cast columns to integers
    df[tiers_df.columns] = df[tiers_df.columns].fillna(-1)

    # drop unneeded columns
    df = df[export_columns]

    # map domain fields to values
    df.HasNetwork = df.HasNetwork.map({True: "yes", False: "no"})
    df.ProtectedLand = df.ProtectedLand.map({1: "yes", 0: "no"})

    if barrier_type == "dams":
        df.Condition = df.Condition.map(DAM_CONDITION_DOMAIN)
        df.Construction = df.Construction.map(CONSTRUCTION_DOMAIN)
        df.Purpose = df.Purpose.map(PURPOSE_DOMAIN)
        df.Feasibility = df.Feasibility.map(FEASIBILITY_DOMAIN)

    else:
        df.SeverityClass = df.SeverityClass.map(BARRIER_SEVERITY_DOMAIN)

    filename = "aquatic_barrier_ranks_{0}.{1}".format(date.today().isoformat(), format)

    # create readme
    template_values = {
        "date": date.today(),
        "url": request.host_url,
        "filename": filename,
        "layer": layer,
        "ids": ", ".join(ids),
    }

    readme = render_template("{}_readme.txt".format(barrier_type), **template_values)
    # csv_bytes = BytesIO()
    # df.to_csv(csv_bytes)

    zf_bytes = BytesIO()
    with ZipFile(zf_bytes, "w") as zf:
        zf.writestr(filename, df.to_csv(index=False))
        zf.writestr("README.txt", readme)

    resp = make_response(zf_bytes.getvalue())
    resp.headers["Content-Disposition"] = "attachment; filename={0}".format(
        filename.replace(format, "zip")
    )
    resp.headers["Content-Type"] = "application/zip"
    return resp


if __name__ == "__main__":
    app.run(debug=True)
