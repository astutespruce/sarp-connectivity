from datetime import date
from enum import Enum
import json
from io import BytesIO, StringIO
import logging
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import Response, StreamingResponse
from fastapi.middleware.gzip import GZipMiddleware
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware


from analysis.rank.lib.tiers import calculate_tiers

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
    PASSAGEFACILITY_DOMAIN,
    BARRIER_SEVERITY_DOMAIN,
    BOOLEAN_DOMAIN,
    OWNERTYPE_DOMAIN,
    HUC8_USFS_DOMAIN,
    HUC8_COA_DOMAIN,
    HUC8_SGCN_DOMAIN,
)

from api.settings import ALLOWED_ORIGINS, LOGGING_LEVEL, SENTRY_DSN

### create maps of fields to lower case equivalents
dam_filter_field_map = {f.lower(): f for f in DAM_FILTER_FIELDS}
barrier_filter_field_map = {f.lower(): f for f in SB_FILTER_FIELDS}


### Setup templates
template_path = Path(__file__).parent.resolve() / "templates"
env = Environment(loader=FileSystemLoader(template_path))

### Setup logging
log = logging.getLogger("api")
log.setLevel(LOGGING_LEVEL)

### Setup Sentry
if SENTRY_DSN:
    log.info("setting up sentry")
    sentry_sdk.init(dsn=SENTRY_DSN)


### Read version from UI package.json
with open(Path(__file__).resolve().parent.parent / "ui/package.json") as infile:
    VERSION = json.loads(infile.read())["version"]

### Include logo in download package
LOGO_PATH = Path(__file__).resolve().parent.parent / "ui/src/images/sarp_logo.png"

### Enums for validating incoming values
class BarrierTypes(str, Enum):
    dams = "dams"
    barriers = "barriers"


class Layers(str, Enum):
    HUC6 = "HUC6"
    HUC8 = "HUC8"
    HUC12 = "HUC12"
    State = "State"
    County = "County"
    ECO3 = "ECO3"
    ECO4 = "ECO4"


class Formats(str, Enum):
    csv = "csv"


class Scenarios(str, Enum):
    NC = "NC"
    WC = "WC"
    NCWC = "NCWC"


### Read source data into memory
try:
    data_dir = Path("data/api")
    dams = pd.read_feather(data_dir / "dams.feather").set_index(["id"])
    dams_with_networks = dams.loc[dams.HasNetwork]

    barriers = pd.read_feather(data_dir / "small_barriers.feather").set_index(["id"])
    barriers_with_networks = barriers.loc[barriers.HasNetwork]

    print("Data loaded")

except Exception as e:
    print("ERROR: not able to load data")
    log.error(e)


### Create the main API app
app = FastAPI()


### Setup middleware
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    """Middleware that wraps HTTP requests and catches exceptions.

    These need to be caught here in order to ensure that the
    CORS middleware is used for the response, otherwise the client
    gets CORS related errors instead of the actual error.

    Parameters
    ----------
    request : Request
    call_next : func
        next func in the chain to call
    """
    try:
        return await call_next(request)

    except Exception as ex:
        log.error(f"Error processing request: {ex}")
        return Response("Internal server error", status_code=500)


### Add sentry to app
app.add_middleware(SentryAsgiMiddleware)

### Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/api/v1/{barrier_type}/query/{layer}")
def query(id: str, barrier_type: BarrierTypes = "dams", layer: Layers = "HUC8"):
    """Filter dams and return key properties for filtering.  ONLY for those with networks.

    Path parameters:
    barrier_type : one of TYPES
    layer : one of LAYERS

    Query parameters:
    id: list of ids

    Parameters
    ----------
    layer : str (default: HUC8)
        Layer to use for subsetting by ID.  One of: HUC6, HUC8, HUC12, State, ... TBD
    """

    if layer == "County":
        layer = "COUNTYFIPS"

    ids = [id for id in id.split(",") if id]
    if not ids:
        raise HTTPException(400, detail="id must be non-empty")

    if barrier_type == "dams":
        df = dams_with_networks
        fields = DAM_FILTER_FIELDS
    else:
        df = barriers_with_networks
        fields = SB_FILTER_FIELDS

    df = df.loc[df[layer].isin(ids)][fields].copy()
    log.info("selected {} {}".format(len(df.index), barrier_type))

    csv_stream = StringIO(
        df.to_csv(index_label="id", header=[c.lower() for c in df.columns])
    )
    return StreamingResponse(csv_stream, media_type="text/csv")


@app.get("/api/v1/{barrier_type}/rank/{layer}")
def rank(
    request: Request,
    id: str,
    barrier_type: BarrierTypes = "dams",
    layer: Layers = "HUC8",
):
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

    if layer == "County":
        layer = "COUNTYFIPS"

    ids = [id for id in id.split(",") if id]
    if not ids:
        raise HTTPException(400, detail="id must be non-empty")

    if barrier_type == "dams":
        df = dams_with_networks
        field_map = dam_filter_field_map
    else:
        df = barriers_with_networks
        field_map = barrier_filter_field_map

    filters = df[layer].isin(ids)

    filter_keys = {q for q in request.query_params if not q == "id"}

    invalid_filters = filter_keys.difference(field_map)
    if invalid_filters:
        raise HTTPException(
            400, detail=f"Filters are invalid: {','.join(invalid_filters)}"
        )

    for filter in filter_keys:
        # convert all incoming to integers
        values = [int(x) for x in request.query_params.get(filter).split(",")]
        filters = filters & df[field_map[filter]].isin(values)

    df = df.loc[filters].copy()
    nrows = len(df.index)

    log.info(f"selected {nrows} {barrier_type}")

    if not nrows:
        raise HTTPException(
            404, detail=f"no barriers are contained in selected ids {layer}:{ids}"
        )

    # just return tiers and lat/lon
    cols = ["lat", "lon"] + TIER_FIELDS + CUSTOM_TIER_FIELDS
    df = calculate_tiers(df)[cols]

    csv_stream = StringIO(
        df.to_csv(index_label="id", header=[c.lower() for c in df.columns])
    )
    return StreamingResponse(csv_stream, media_type="text/csv")


@app.get("/api/v1/{barrier_type}/{format}/{layer}")
def download(
    request: Request,
    id: str,
    custom: bool = False,
    unranked=False,
    sort: Scenarios = "NCWC",
    barrier_type: BarrierTypes = "dams",
    format: Formats = "csv",
    layer: Layers = "HUC8",
):
    """Download subset of dams or small barriers data.

    If `unranked` is `True`, all barriers in the summary units are downloaded.

    Path parameters:
    <barrier_type> : one of TYPES
    <layer> : one of LAYERS

    Query parameters:
    * id: list of ids
    * custom: bool (default: False); set to true to perform custom ranking of subset defined here
    * unranked: bool (default: False); set to true to include unranked barriers in output
    * sort: str, one of 'NC', 'WC', 'NCWC'
    * filters are defined using a lowercased version of column name and a comma-delimited list of values

    Parameters
    ----------
    layer : str (default: HUC8)
        Layer to use for subsetting by ID.  One of: HUC6, HUC8, HUC12, State, ... TBD

    format : str (default: csv)
        Format for download.  One of: csv, shp
    """

    include_unranked = unranked
    custom_ranks = custom

    # query parameters that are NOT filters
    exclude_query_params = ("id", "unranked", "sort", "custom")

    if layer == "County":
        layer = "COUNTYFIPS"

    ids = [id for id in id.split(",") if id]
    if not ids:
        raise HTTPException(400, detail="id must be non-empty")

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
    log.info(f"selected {len(df)} dams in geographic area")

    if include_unranked:
        full_df = df.copy()

    filter_keys = {q for q in request.query_params if not q in exclude_query_params}

    invalid_filters = filter_keys.difference(field_map)
    if invalid_filters:
        raise HTTPException(
            400, detail=f"Filters are invalid: {','.join(invalid_filters)}"
        )

    filters = None
    for filter in filter_keys:
        # convert all incoming to integers
        values = [int(x) for x in request.query_params.get(filter).split(",")]
        filter_expr = df[field_map[filter]].isin(values)
        filters = filters & filter_expr if filters is not None else filter_expr

    if filters is not None:
        df = df.loc[filters].copy()

    log.info("selected {} dams that meet filters".format(len(df.index)))

    if custom_ranks:
        df = calculate_tiers(df)

    if include_unranked:
        # join back to full dataset
        tier_cols = df.columns.difference(full_df.columns)
        df = full_df.join(df[tier_cols], how="left")

        df[tier_cols] = df[tier_cols].fillna(-1).astype("int8")

    df = df[df.columns.intersection(export_columns)]

    # Sort by tier
    if "{}_tier" in df.columns:
        sort_field = "{}_tier".format(sort)
    else:
        sort_field = "SE_{}_tier".format(sort)

    df = df.sort_values(by=["HasNetwork", sort_field], ascending=[False, True])

    # map domain fields to values
    df.HasNetwork = df.HasNetwork.map(BOOLEAN_DOMAIN)
    df.Excluded = df.Excluded.map(BOOLEAN_DOMAIN)

    df.OwnerType = df.OwnerType.map(OWNERTYPE_DOMAIN)
    df.ProtectedLand = df.ProtectedLand.map(BOOLEAN_DOMAIN)
    df.HUC8_USFS = df.HUC8_USFS.map(HUC8_USFS_DOMAIN)
    df.HUC8_COA = df.HUC8_COA.map(HUC8_COA_DOMAIN)
    df.HUC8_SGCN = df.HUC8_SGCN.map(HUC8_SGCN_DOMAIN)

    if barrier_type == "dams":
        df.Condition = df.Condition.map(DAM_CONDITION_DOMAIN)
        df.Construction = df.Construction.map(CONSTRUCTION_DOMAIN)
        df.Purpose = df.Purpose.map(PURPOSE_DOMAIN)
        df.Feasibility = df.Feasibility.map(FEASIBILITY_DOMAIN)
        df.PassageFacility = df.PassageFacility.map(PASSAGEFACILITY_DOMAIN)

    else:
        df.SeverityClass = df.SeverityClass.map(BARRIER_SEVERITY_DOMAIN)

    filename = "aquatic_barrier_ranks_{0}.{1}".format(date.today().isoformat(), format)

    ### create readme and terms of use
    template_values = {
        "date": date.today(),
        "version": VERSION,
        "url": request.base_url,
        "filename": filename,
        "layer": layer,
        "ids": ", ".join(ids),
    }

    readme = env.get_template(f"{barrier_type}_readme.txt").render(**template_values)
    terms = env.get_template("terms.txt").render(
        year=date.today().year, **template_values
    )

    zip_stream = BytesIO()
    with ZipFile(zip_stream, "w", compression=ZIP_DEFLATED, compresslevel=5) as zf:
        zf.writestr(filename, df.to_csv(index=False))
        zf.writestr("README.txt", readme)
        zf.writestr("TERMS_OF_USE.txt", terms)
        zf.write(LOGO_PATH, "SARP_logo.png")

    # rewind to beginning
    zip_stream.seek(0)

    return StreamingResponse(
        zip_stream,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename.replace(format, 'zip')}"
        },
    )
