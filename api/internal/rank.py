from fastapi import APIRouter, Depends
from fastapi.requests import Request


from analysis.rank.lib.tiers import calculate_tiers

from api.constants import (
    TIER_FIELDS,
    CUSTOM_TIER_FIELDS,
)
from api.data import ranked_dams, ranked_barriers
from api.dependencies import DamsRecordExtractor, BarriersRecordExtractor
from api.logger import log, log_request
from api.response import feather_response


router = APIRouter()


@router.get("/dams/rank/{layer}")
def rank_dams(request: Request, extractor: DamsRecordExtractor = Depends()):
    """Rank a subset of dams data.

    Path parameters:
    <layer> : one of LAYERS

    Query parameters:
    * id: list of ids
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    """

    log_request(request)

    df = extractor.extract(ranked_dams).copy()
    log.info(f"selected {len(df)} dams for ranking")

    df = df.join(calculate_tiers(df))

    # just return tiers and lat/lon
    cols = [
        c
        for c in ["id", "lat", "lon"] + TIER_FIELDS + CUSTOM_TIER_FIELDS
        if c in df.columns
    ]
    df = df[cols]

    # extract extent
    bounds = df[["lon", "lat"]].agg(["min", "max"]).values.flatten().round(3)

    return feather_response(df, bounds=bounds)


@router.get("/small_barriers/rank/{layer}")
def rank_barriers(request: Request, extractor: BarriersRecordExtractor = Depends()):
    """Rank a subset of small barriers data.

    Path parameters:
    <layer> : one of LAYERS

    Query parameters:
    * id: list of ids
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    """

    log_request(request)

    df = extractor.extract(ranked_barriers).copy()
    log.info(f"selected {len(df)} barriers for ranking")

    df = df.join(calculate_tiers(df))

    # just return tiers and lat/lon
    cols = [
        c
        for c in ["id", "lat", "lon"] + TIER_FIELDS + CUSTOM_TIER_FIELDS
        if c in df.columns
    ]
    df = df[cols]

    # extract extent
    bounds = df[["lon", "lat"]].agg(["min", "max"]).values.flatten().round(3)

    return feather_response(df, bounds=bounds)
