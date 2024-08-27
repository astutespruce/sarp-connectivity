from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import pyarrow.compute as pc

from api.constants import NetworkTypes
from api.data import db, waterfalls
from api.logger import log_request


router = APIRouter()


@router.get("/{network_type}/details/{sarp_id}")
async def details(
    request: Request,
    network_type: NetworkTypes,
    sarp_id: str,
):
    log_request(request)

    if sarp_id.startswith("f"):
        # waterfalls use pyarrow search due to lack of unique index
        # NOTE: these have one record per network type
        dataset = waterfalls
        filter = pc.field("SARPID") == sarp_id
        filter = filter & (pc.field("network_type") == network_type)
        record = dataset.to_table(filter=filter).slice(0)

    else:
        if sarp_id.startswith("cr"):
            table = "road_crossings"
        else:
            table = network_type

        record = db.sql(f"SELECT * FROM {table} WHERE SARPID=? LIMIT 1", params=(sarp_id,)).arrow()

    if not len(record):
        raise HTTPException(404, detail=f"record not found for SARPID: {sarp_id}")

    # use the bulk converter to dict (otherwise float32 serialization issues)
    # and return singular first item
    return JSONResponse(content=record.rename_columns([c.lower() for c in record.schema.names]).to_pylist()[0])
