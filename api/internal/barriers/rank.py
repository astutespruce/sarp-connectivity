from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request
import pyarrow as pa
import pyarrow.compute as pc

from api.lib.compression import pack_bits
from api.lib.tiers import calculate_tiers, METRICS
from api.constants import RankedBarrierTypes
from api.dependencies import get_unit_ids, get_filter_params
from api.lib.extract import extract_records
from api.logger import log, log_request
from api.response import feather_response


router = APIRouter()


@router.get("/{barrier_type}/rank")
async def rank(
    request: Request,
    barrier_type: RankedBarrierTypes,
    unit_ids: get_unit_ids = Depends(),
    filters: get_filter_params = Depends(),
):
    """Rank a subset of barrier_type data.

    Path parameters:
    <layer> : one of LAYERS

    Query parameters:
    * id: list of ids
    * filters are defined using a lowercased version of column name and a comma-delimited list of values
    """

    log_request(request)

    if len(unit_ids) == 0 and len(filters) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one summary unit layer must have ids present or at least one filter must be defined",
        )

    barrier_type = barrier_type.value

    df = extract_records(
        barrier_type, unit_ids=unit_ids, filters=filters, columns=["id", "lat", "lon"] + METRICS, ranked_only=True
    )
    log.info(f"selected {len(df):,} {barrier_type.replace('_', ' ')} for ranking")

    # extract extent
    xmin, xmax = pc.min_max(df["lon"]).as_py().values()
    ymin, ymax = pc.min_max(df["lat"]).as_py().values()
    bounds = [xmin, ymin, xmax, ymax]

    tiers = calculate_tiers(df)

    # pack each tier scenario into a separate 16 bit number to save space
    # 5 bits holds values 0...21 after subtracting offset
    tier_scenarios = ["NC", "WC", "NCWC"]
    full_tier_pack_bits = [{"field": f"{scenario}_tier", "bits": 5, "value_shift": 1} for scenario in tier_scenarios]
    perennial_tier_pack_bits = [
        {"field": f"P{scenario}_tier", "bits": 5, "value_shift": 1} for scenario in tier_scenarios
    ]
    mainstem_tier_pack_bits = [
        {"field": f"M{scenario}_tier", "bits": 5, "value_shift": 1} for scenario in tier_scenarios
    ]

    tiers = pa.Table.from_pydict(
        {
            "id": df["id"],
            "full": pack_bits(tiers, full_tier_pack_bits),
            "perennial": pack_bits(tiers, perennial_tier_pack_bits),
            "mainstem": pack_bits(tiers, mainstem_tier_pack_bits),
        }
    )

    return feather_response(tiers, bounds=bounds)
