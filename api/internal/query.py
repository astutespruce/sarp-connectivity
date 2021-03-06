from fastapi import APIRouter, Depends
from fastapi.requests import Request


from api.constants import (
    DAM_FILTER_FIELDS,
    SB_FILTER_FIELDS,
)
from api.data import dams_with_networks, barriers_with_networks
from api.dependencies import DamsRecordExtractor, BarriersRecordExtractor
from api.logger import log, log_request
from api.response import csv_response


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

    df = extractor.extract(dams_with_networks)[DAM_FILTER_FIELDS].copy()
    log.info(f"query selected {len(df.index)} dams")

    return csv_response(df)


@router.get("/barriers/query/{layer}")
def query_barriers(request: Request, extractor: BarriersRecordExtractor = Depends()):
    """Return subset of small barriers based on summary unit ids within layer.

    Path parameters:
    layer : one of LAYERS

    Query parameters:
    id: list of ids
    """

    log_request(request)

    df = extractor.extract(barriers_with_networks)[SB_FILTER_FIELDS].copy()
    log.info(f"barriers query selected {len(df.index)} barriers")

    return csv_response(df)