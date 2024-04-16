from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import pyarrow.compute as pc

from api.constants import Layers, SUMMARY_UNIT_FIELDS
from api.data import units
from api.logger import log_request


router = APIRouter()


@router.get("/units/{layer}/{id}")
async def unit_details(request: Request, layer: Layers, id: str):
    log_request(request)

    filter = (pc.field("layer") == layer) & (pc.field("id") == id)

    record = units.to_table(columns=SUMMARY_UNIT_FIELDS, filter=filter).slice(0)

    if not len(record):
        raise HTTPException(404, detail=f"record not found for {layer}: {id}")

    # use the bulk converter to dict (otherwise float32 serialization issues)
    # and return singular first item
    return JSONResponse(content=record.to_pylist()[0])
