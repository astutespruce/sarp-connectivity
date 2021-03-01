from fastapi import APIRouter, Depends

from api.constants import (
    DAM_FILTER_FIELDS,
    SB_FILTER_FIELDS,
)
from api.data import dams_with_networks, barriers_with_networks
from api.dependencies import DamsRecordExtractor, BarriersRecordExtractor
from api.logger import log
from api.response import csv_response


router = APIRouter()


@router.get("/api/v1/dams/query/{layer}")
def query_dams(extractor: DamsRecordExtractor = Depends()):
    """Return subset of dams based on summary unit ids within layer.

    Path parameters:
    layer : one of LAYERS

    Query parameters:
    id: list of ids
    """

    print(f"layer: {extractor.layer}, ids: {extractor.ids}")

    df = extractor.extract(dams_with_networks)[DAM_FILTER_FIELDS].copy()
    log.info(f"query selected {len(df.index)} dams")

    return csv_response(df)


@router.get("/api/v1/barriers/query/{layer}")
def query_barriers(extractor: BarriersRecordExtractor = Depends()):
    """Return subset of small barriers based on summary unit ids within layer.

    Path parameters:
    layer : one of LAYERS

    Query parameters:
    id: list of ids
    """

    print(f"layer: {extractor.layer}, ids: {extractor.ids}")

    df = extractor.extract(barriers_with_networks)[SB_FILTER_FIELDS].copy()
    log.info(f"barriers query selected {len(df.index)} barriers")

    return csv_response(df)