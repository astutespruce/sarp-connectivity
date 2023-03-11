from fastapi import APIRouter, Depends
from fastapi.requests import Request
import pyarrow.compute as pc

from api.constants import (
    BarrierTypes,
    DAM_FILTER_FIELDS,
    SB_FILTER_FIELDS,
    COMBINED_FILTER_FIELDS,
)

from api.dependencies import (
    RecordExtractor,
)
from api.logger import log, log_request
from api.response import feather_response


router = APIRouter()


@router.get("/{barrier_type}/query/{layer}")
async def query_dams(
    request: Request,
    barrier_type: BarrierTypes,
    extractor: RecordExtractor = Depends(RecordExtractor),
):
    """Return subset of barrier_type based on summary unit ids within layer.

    Path parameters:
    layer : one of LAYERS

    Query parameters:
    id: list of ids
    """

    log_request(request)
    columns = ["id", "lon", "lat"]
    match barrier_type:
        case "dams":
            columns += DAM_FILTER_FIELDS
        case "small_barriers":
            columns += SB_FILTER_FIELDS
        case "combined_barriers":
            columns += ["BarrierType"] + COMBINED_FILTER_FIELDS

        case _:
            raise NotImplementedError("query is not supported for road crossings")

    df = extractor.extract(columns=columns, ranked=True)

    # extract extent
    xmin, xmax = pc.min_max(df["lon"]).as_py().values()
    ymin, ymax = pc.min_max(df["lat"]).as_py().values()
    bounds = [xmin, ymin, xmax, ymax]

    df = df.select(["id"] + columns)

    log.info(f"query selected {len(df):,} {barrier_type.replace('_', ' ')}")

    return feather_response(df, bounds)
