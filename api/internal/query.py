from fastapi import APIRouter, Depends
from fastapi.requests import Request
import pyarrow.compute as pc

from api.constants import (
    DAM_FILTER_FIELDS,
    SB_FILTER_FIELDS,
)
from api.data import ranked_dams, ranked_barriers
from api.dependencies import DamsRecordExtractor, BarriersRecordExtractor
from api.logger import log, log_request
from api.response import feather_response


router = APIRouter()


@router.get("/dams/query/{layer}")
def query_dams(request: Request, extractor: DamsRecordExtractor = Depends()):
    """Return subset of dams based on summary unit ids within layer.

    Path parameters:
    layer : one of LAYERS

    Query parameters:
    id: list of ids
    """

    log_request(request)

    df = extractor.extract(ranked_dams)

    # extract extent
    xmin, xmax = pc.min_max(df["lon"]).as_py().values()
    ymin, ymax = pc.min_max(df["lat"]).as_py().values()
    bounds = [xmin, ymin, xmax, ymax]

    df = df.select(["id"] + DAM_FILTER_FIELDS)

    log.info(f"query selected {len(df):,} dams")

    return feather_response(df, bounds)


@router.get("/small_barriers/query/{layer}")
def query_barriers(request: Request, extractor: BarriersRecordExtractor = Depends()):
    """Return subset of small barriers based on summary unit ids within layer.

    Path parameters:
    layer : one of LAYERS

    Query parameters:
    id: list of ids
    """

    log_request(request)

    df = extractor.extract(ranked_barriers)

    # extract extent
    xmin, xmax = pc.min_max(df["lon"]).as_py().values()
    ymin, ymax = pc.min_max(df["lat"]).as_py().values()
    bounds = [xmin, ymin, xmax, ymax]

    df = df.select(["id"] + SB_FILTER_FIELDS)
    log.info(f"barriers query selected {len(df):,} barriers")

    return feather_response(df, bounds)
