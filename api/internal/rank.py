from fastapi import APIRouter, Depends
from fastapi.requests import Request
import pyarrow as pa
import pyarrow.compute as pc

from api.lib.compression import pack_bits
from api.lib.tiers import calculate_tiers, METRICS
from api.constants import CUSTOM_TIER_PACK_BITS, BarrierTypes
from api.dependencies import RecordExtractor
from api.logger import log, log_request
from api.response import feather_response


router = APIRouter()


@router.get("/{barrier_type}/rank")
async def rank(
    request: Request,
    barrier_type: BarrierTypes,
    extractor: RecordExtractor = Depends(RecordExtractor),
):
    """Rank a subset of barrier_type data.

    Path parameters:
    <layer> : one of LAYERS

    Query parameters:
    * id: list of ids
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    """

    log_request(request)

    if barrier_type == "road_crossings":
        raise NotImplementedError("rank is not supported for road crossings")

    df = extractor.extract(
        columns=["id", "lat", "lon"] + METRICS,
        ranked=True,
    )
    log.info(f"selected {len(df):,} {barrier_type.replace('_', ' ')} for ranking")

    # extract extent
    xmin, xmax = pc.min_max(df["lon"]).as_py().values()
    ymin, ymax = pc.min_max(df["lat"]).as_py().values()
    bounds = [xmin, ymin, xmax, ymax]

    tiers = pa.Table.from_pydict({"id": df["id"], "tiers": pack_bits(calculate_tiers(df), CUSTOM_TIER_PACK_BITS)})

    return feather_response(tiers, bounds=bounds)
