from fastapi import APIRouter, Depends

from api.logger import log
from analysis.rank.lib.tiers import calculate_tiers

from api.constants import (
    TIER_FIELDS,
    CUSTOM_TIER_FIELDS,
)
from api.data import dams_with_networks, barriers_with_networks
from api.dependencies import DamsRecordExtractor, BarriersRecordExtractor
from api.response import csv_response


router = APIRouter()


@router.get("/api/v1/dams/rank/{layer}")
def rank_dams(extractor: DamsRecordExtractor = Depends()):
    """Rank a subset of dams data.

    Path parameters:
    <layer> : one of LAYERS

    Query parameters:
    * id: list of ids
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    """

    df = extractor.extract(dams_with_networks).copy()
    log.info(f"selected {len(df)} dams for ranking")

    # just return tiers and lat/lon
    cols = ["lat", "lon"] + TIER_FIELDS + CUSTOM_TIER_FIELDS
    df = calculate_tiers(df)[cols]

    return csv_response(df)


@router.get("/api/v1/barriers/rank/{layer}")
def rank_barriers(extractor: BarriersRecordExtractor = Depends()):
    """Rank a subset of small barriers data.

    Path parameters:
    <layer> : one of LAYERS

    Query parameters:
    * id: list of ids
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    """

    df = extractor.extract(barriers_with_networks).copy()
    log.info(f"selected {len(df)} barriers for ranking")

    # just return tiers and lat/lon
    cols = ["lat", "lon"] + TIER_FIELDS + CUSTOM_TIER_FIELDS
    df = calculate_tiers(df)[cols]

    return csv_response(df)
