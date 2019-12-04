import os
import json
from pathlib import Path
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

from analysis.rank.lib.tiers import calculate_tiers, SCENARIOS

from api.constants import (
    DAM_FILTER_FIELDS,
    DAM_EXPORT_FIELDS,
    SB_FILTER_FIELDS,
    SB_EXPORT_FIELDS,
    TIER_FIELDS,
    CUSTOM_TIER_FIELDS,
    # domains to invert before download
    FEASIBILITY_DOMAIN,
    PURPOSE_DOMAIN,
    CONSTRUCTION_DOMAIN,
    DAM_CONDITION_DOMAIN,
    BARRIER_SEVERITY_DOMAIN,
    BOOLEAN_DOMAIN,
    OWNERTYPE_DOMAIN,
    USFS_PRIORITY_DOMAIN,
    COA_DOMAIN,
    SEBIO_DOMAIN,
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


# Read version from UI package.json
with open(Path(__file__).resolve().parent.parent / "ui/package.json") as infile:
    VERSION = json.loads(infile.read())["version"]

# Include logo in download package
LOGO_PATH = Path(__file__).resolve().parent.parent / "ui/src/images/sarp_logo.png"

TYPES = ("dams", "barriers")
LAYERS = ("HUC6", "HUC8", "HUC12", "State", "County", "ECO3", "ECO4")
FORMATS = ("csv",)  # TODO: "shp"

# create maps of fields to lower case equivalents
dam_filter_field_map = {f.lower(): f for f in DAM_FILTER_FIELDS}
barrier_filter_field_map = {f.lower(): f for f in SB_FILTER_FIELDS}


# Read source data into memory
try:
    data_dir = Path("data/api")
    dams = read_dataframe(data_dir / "dams.feather").set_index(["id"])
    dams_with_networks = dams.loc[dams.HasNetwork]

    barriers = read_dataframe(data_dir / "small_barriers.feather").set_index(["id"])
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


def validate_sort(sort):
    if not sort in SCENARIOS.keys():
        abort(
            400,
            "sort is not valid; must be one of {0}".format(
                ", ".join(list(SCENARIOS.keys()))
            ),
        )


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

    ids = [id for id in request.args.get("id", "").split(",") if id]
    if not ids:
        abort(400, "id must be non-empty")

    if barrier_type == "dams":
        df = dams_with_networks
        # field_map = dam_filter_field_map
        fields = DAM_FILTER_FIELDS
    else:
        df = barriers_with_networks
        # field_map = barrier_filter_field_map
        fields = SB_FILTER_FIELDS

    df = df.loc[df[layer].isin(ids)][fields].copy()
    log.info("selected {} {}".format(len(df.index), barrier_type))

    resp = make_response(
        df.to_csv(index_label="id", header=[c.lower() for c in df.columns])
    )

    resp.headers["Content-Type"] = "text/csv"
    return resp


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

    ids = [id for id in args.get("id", "").split(",") if id]
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

    # just return tiers and lat/lon
    cols = ["lat", "lon"] + TIER_FIELDS + CUSTOM_TIER_FIELDS
    df = calculate_tiers(df)[cols]

    resp = make_response(
        df.to_csv(index_label="id", header=[c.lower() for c in df.columns])
    )
    resp.headers["Content-Type"] = "text/csv"
    return resp


@app.route("/api/v1/<barrier_type>/<format>/<layer>", methods=["GET"])
def download(barrier_type="dams", layer="HUC8", format="CSV"):
    """Download subset of dams or small barriers data.

    If `unranked` is `True`, all barriers in the summary units are downloaded.

    Path parameters:
    <barrier_type> : one of TYPES
    <layer> : one of LAYERS

    Query parameters:
    * id: list of ids
    * unranked: bool (default: False)
    * sort: str, one of 'NC', 'WC', 'NCWC'
    * filters are defined using a lowercased version of column name and a comma-delimited list of values

    Parameters
    ----------
    layer : str (default: HUC8)
        Layer to use for subsetting by ID.  One of: HUC6, HUC8, HUC12, State, ... TBD

    format : str (default: csv)
        Format for download.  One of: csv, shp
    """

    args = request.args

    # query parameters that are NOT filters
    query_params = ("id", "unranked", "sort")

    validate_type(barrier_type)
    validate_layer(layer)
    validate_format(format)

    sort = args.get("sort", "NCWC")
    validate_sort(sort)

    if layer == "County":
        layer = "COUNTYFIPS"

    include_unranked = bool(args.get("unranked", False))

    ids = [id for id in args.get("id", "").split(",") if id]
    if not ids:
        abort(400, "id must be non-empty")

    if barrier_type == "dams":
        df = dams
        field_map = dam_filter_field_map
        export_columns = DAM_EXPORT_FIELDS
    else:
        df = barriers
        field_map = barrier_filter_field_map
        export_columns = SB_EXPORT_FIELDS

    # drop off-network barriers if we aren't including them
    if not include_unranked:
        df = df.loc[df.HasNetwork]

    # filter to summary units
    df = df.loc[df[layer].isin(ids)].copy()
    log.info("selected {} dams in geographic area".format(len(df)))

    if include_unranked:
        full_df = df.copy()

    filters = None
    filterKeys = [a for a in request.args if not a in query_params]
    for filter in filterKeys:
        # convert all incoming to integers
        values = [int(x) for x in request.args.get(filter).split(",")]
        filter_expr = df[field_map[filter]].isin(values)

        if filters is None:
            filters = filter_expr
        else:
            filters = filters & filter_expr

    if filters is not None:
        df = df.loc[filters].copy()

    log.info("selected {} dams that meet filters".format(len(df.index)))

    df = calculate_tiers(df)

    if include_unranked:
        # join back to full dataset
        tier_cols = df.columns.difference(full_df.columns)
        df = full_df.join(df[tier_cols], how="left")

        df[tier_cols] = df[tier_cols].fillna(-1)

    df = df[export_columns]

    # Sort by tier
    df = df.sort_values(
        by=["HasNetwork", "{}_tier".format(sort)], ascending=[False, True]
    )

    # map domain fields to values
    df.HasNetwork = df.HasNetwork.map(BOOLEAN_DOMAIN)

    df.OwnerType = df.OwnerType.map(OWNERTYPE_DOMAIN)
    df.ProtectedLand = df.ProtectedLand.map(BOOLEAN_DOMAIN)
    df.USFS = df.USFS.map(USFS_PRIORITY_DOMAIN)
    df.COA = df.COA.map(COA_DOMAIN)
    df.SEBIO = df.SEBIO.map(SEBIO_DOMAIN)

    if barrier_type == "dams":
        df.Condition = df.Condition.map(DAM_CONDITION_DOMAIN)
        df.Construction = df.Construction.map(CONSTRUCTION_DOMAIN)
        df.Purpose = df.Purpose.map(PURPOSE_DOMAIN)
        df.Feasibility = df.Feasibility.map(FEASIBILITY_DOMAIN)

    else:
        df.SeverityClass = df.SeverityClass.map(BARRIER_SEVERITY_DOMAIN)

    filename = "aquatic_barrier_ranks_{0}.{1}".format(date.today().isoformat(), format)

    ### reate readme
    template_values = {
        "date": date.today(),
        "version": VERSION,
        "url": request.host_url,
        "filename": filename,
        "layer": layer,
        "ids": ", ".join(ids),
    }

    readme = render_template("{}_readme.txt".format(barrier_type), **template_values)

    ### Create terms of use
    terms = render_template("terms.txt", year=date.today().year, **template_values)

    zf_bytes = BytesIO()
    with ZipFile(zf_bytes, "w") as zf:
        zf.writestr(filename, df.to_csv(index=False))
        zf.writestr("README.txt", readme)
        zf.writestr("TERMS_OF_USE.txt", terms)
        zf.write(LOGO_PATH, "SARP_logo.png")

    resp = make_response(zf_bytes.getvalue())
    resp.headers["Content-Disposition"] = "attachment; filename={0}".format(
        filename.replace(format, "zip")
    )
    resp.headers["Content-Type"] = "application/zip"
    return resp


if __name__ == "__main__":
    app.run(debug=True)
