from fastapi import APIRouter, Depends
from fastapi.requests import Request
import pyarrow as pa
import pyarrow.compute as pc

from analysis.rank.lib.tiers import calculate_tiers, METRICS

from api.constants import (
    TIER_FIELDS,
)
from api.data import dams, small_barriers
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

    df = extractor.extract(
        dams,
        columns=["id", "lat", "lon"] + METRICS,
        ranked=True,
    )
    log.info(f"selected {len(df)} dams for ranking")

    # extract extent
    xmin, xmax = pc.min_max(df["lon"]).as_py().values()
    ymin, ymax = pc.min_max(df["lat"]).as_py().values()
    bounds = [xmin, ymin, xmax, ymax]

    tiers = calculate_tiers(df).add_column(0, df.schema.field("id"), df["id"])
    return feather_response(tiers, bounds=bounds)


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

    df = extractor.extract(
        small_barriers,
        columns=["id", "lat", "lon"] + METRICS,
        ranked=True,
    )
    log.info(f"selected {len(df)} barriers for ranking")

    # extract extent
    xmin, xmax = pc.min_max(df["lon"]).as_py().values()
    ymin, ymax = pc.min_max(df["lat"]).as_py().values()
    bounds = [xmin, ymin, xmax, ymax]

    tiers = calculate_tiers(df).add_column(0, df.schema.field("id"), df["id"])
    return feather_response(tiers, bounds=bounds)
