from enum import Enum

from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
import pyarrow as pa
import pyarrow.compute as pc

from api.constants import (
    STATES,
    DAM_PUBLIC_EXPORT_FIELDS,
    SB_PUBLIC_EXPORT_FIELDS,
)
from api.lib.domains import unpack_domains
from api.data import dams, small_barriers, removed_dams
from api.logger import log, log_request
from api.response import csv_response


router = APIRouter()


class PublicAPIBarrierTypes(str, Enum):
    dams = "dams"
    # NOTE: small_barriers is referred to as barriers for public API
    barriers = "barriers"


@router.get("/{barrier_type}/state")
async def query_by_state(
    request: Request, barrier_type: PublicAPIBarrierTypes, id: str
):
    """Return subset of barrier_type based on state abbreviations.

    Query parameters:
    id: list of state abbreviations
    """

    log_request(request)

    dataset = None
    columns = []
    match barrier_type:
        case "dams":
            dataset = dams
            columns = DAM_PUBLIC_EXPORT_FIELDS
        case "barriers":
            dataset = small_barriers
            columns = SB_PUBLIC_EXPORT_FIELDS

    ids = [id.upper() for id in id.split(",") if id]
    if not ids:
        raise HTTPException(400, detail="id must be non-empty")

    invalid = set(ids).difference(STATES)
    if invalid:
        raise HTTPException(400, detail=f"ids are not valid: {', '.join(invalid)}")

    ids = pa.array(ids)

    df = (
        dataset.scanner(columns=columns, filter=pc.is_in(pc.field("State"), ids))
        .to_table()
        .sort_by("HasNetwork")
    )
    df = unpack_domains(df)

    log.info(f"public query selected {len(df):,} {barrier_type.replace('_', ' ')}")

    return csv_response(df)


@router.get("/removed_dams")
async def query_removed_dams(
    request: Request,
):
    """Return dams that were removed for conservation"""

    log_request(request)
    df = unpack_domains(removed_dams.to_table())

    return csv_response(df)
