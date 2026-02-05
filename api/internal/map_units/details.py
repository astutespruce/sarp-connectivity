from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import pyarrow.compute as pc

from api.constants import Layers, SUMMARY_UNIT_FIELDS
from api.data import db
from api.logger import log_request


router = APIRouter()


@router.get("/units/{layer}/details/{id}")
async def unit_details(request: Request, layer: Layers, id: str):
    log_request(request)

    layer = layer.value

    col_expr = ", ".join(SUMMARY_UNIT_FIELDS)

    match = db.sql(f"SELECT {col_expr} FROM map_units WHERE layer=? AND id=?", params=(layer, id)).fetch_arrow_table()

    if not len(match):
        raise HTTPException(404, detail=f"record not found for {layer}: {id}")

    # use the bulk converter to dict (otherwise float32 serialization issues)
    # and return singular first item
    return JSONResponse(content=match.to_pylist()[0])
