from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import pyarrow.compute as pc

from api.constants import BarrierTypes
from api.data import dams, small_barriers, combined_barriers
from api.logger import log_request


router = APIRouter()


@router.get("/{barrier_type}/details/{sarp_id}")
async def get_dam(request: Request, barrier_type: BarrierTypes, sarp_id: str):
    log_request(request)

    match barrier_type:
        case "dams":
            dataset = dams
        case "small_barriers":
            dataset = small_barriers
        case "combined_barriers":
            dataset = combined_barriers

    record = (
        dataset.to_table(filter=pc.field("SARPID") == sarp_id)
        .slice(0)
        .rename_columns([c.lower() for c in dataset.schema.names])
    )

    if not len(record):
        raise HTTPException(404, detail=f"record not found for SARPID: {sarp_id}")

    # use the bulk converter to dict (otherwise float32 serialization issues)
    # and return singular first item
    return JSONResponse(content=record.to_pylist()[0])
