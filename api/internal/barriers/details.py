from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import pyarrow.compute as pc

from api.constants import NetworkTypes
from api.data import (
    dams,
    combined_barriers,
    largefish_barriers,
    smallfish_barriers,
    road_crossings,
    waterfalls,
)
from api.logger import log_request


router = APIRouter()


@router.get("/{network_type}/details/{sarp_id}")
async def details(
    request: Request,
    network_type: NetworkTypes,
    sarp_id: str,
):
    log_request(request)

    filter = pc.field("SARPID") == sarp_id

    if sarp_id.startswith("cr"):
        # road crossing
        dataset = road_crossings

    elif sarp_id.startswith("f"):
        # waterfall
        # NOTE: these have one record per network type
        dataset = waterfalls
        filter = filter & (pc.field("network_type") == network_type)

    else:
        match network_type:
            case "dams":
                dataset = dams
            case "combined_barriers":
                dataset = combined_barriers
            case "largefish_barriers":
                dataset = largefish_barriers
            case "smallfish_barriers":
                dataset = smallfish_barriers

    record = dataset.to_table(filter=filter).slice(0).rename_columns([c.lower() for c in dataset.schema.names])

    if not len(record):
        raise HTTPException(404, detail=f"record not found for SARPID: {sarp_id}")

    # use the bulk converter to dict (otherwise float32 serialization issues)
    # and return singular first item
    return JSONResponse(content=record.to_pylist()[0])
