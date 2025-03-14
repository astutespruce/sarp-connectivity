from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request
import pyarrow as pa
import pyarrow.compute as pc

from api.constants import (
    FullySupportedBarrierTypes,
    DAM_FILTER_FIELDS,
    SB_FILTER_FIELDS,
    COMBINED_FILTER_FIELDS,
    ROAD_CROSSING_FILTER_FIELDS,
)

from api.dependencies import get_unit_ids, get_filter_params
from api.lib.extract import extract_records
from api.logger import log, log_request
from api.response import feather_response


router = APIRouter()


@router.get("/{barrier_type}/query")
async def query(
    request: Request,
    barrier_type: FullySupportedBarrierTypes,
    unit_ids: get_unit_ids = Depends(),
    filters: get_filter_params = Depends(),
):
    """Return subset of barrier_type based on summary unit ids within layer.

    Path parameters:
    layer : one of LAYERS

    Query parameters:
    id: list of ids
    """

    log_request(request)

    if len(unit_ids) == 0 and len(filters) == 0:
        raise HTTPException(
            400,
            detail="At least one summary unit layer must have ids present or at least one filter must be defined",
        )

    barrier_type = barrier_type.value

    filter_fields = None
    match barrier_type:
        case "dams":
            filter_fields = DAM_FILTER_FIELDS
        case "small_barriers":
            filter_fields = SB_FILTER_FIELDS
        case "combined_barriers" | "largefish_barriers" | "smallfish_barriers":
            # NOTE: BarrierType is used for counting barriers by type after
            # applying filters
            filter_fields = ["BarrierType"] + COMBINED_FILTER_FIELDS
        case "road_crossings":
            filter_fields = ROAD_CROSSING_FILTER_FIELDS

        case _:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"query is not supported for {barrier_type}"
            )

    # always extract ranked barriers unless type is road_crossings (not applicable)
    df = extract_records(
        barrier_type,
        unit_ids=unit_ids,
        filters=filters,
        columns=["id", "lon", "lat"] + filter_fields,
        ranked_only=barrier_type != "road_crossings",
    )

    # extract extent
    xmin, xmax = pc.min_max(df["lon"]).as_py().values()
    ymin, ymax = pc.min_max(df["lat"]).as_py().values()
    bounds = [xmin, ymin, xmax, ymax]

    # group by filter fields
    counts = df.group_by(filter_fields).aggregate([("id", "count")])
    schema = counts.schema
    # cast count to uint32
    fields = [pa.field("id_count", "uint32") if c == "id_count" else schema.field(c) for c in schema.names]
    counts = counts.cast(pa.schema(fields))

    counts = counts.rename_columns(["_count" if c == "id_count" else c for c in counts.column_names])

    log.info(
        f"query selected {len(df):,} {barrier_type.replace('_', ' ')} ({len(counts):,} unique combinations of fields)"
    )

    return feather_response(counts, bounds)
