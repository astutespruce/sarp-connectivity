from io import BytesIO

from fastapi import APIRouter, Response, HTTPException
from fastapi.requests import Request
from pyarrow.feather import write_feather

from api.constants import Layers, SUMMARY_UNIT_FIELDS
from api.data import db
from api.logger import log_request, log


MAX_RECORDS = 100

router = APIRouter()


@router.get("/units/{layer}/list")
async def unit_list(request: Request, layer: Layers, id: str):
    """Return list of units within a layer by ID

    Query parameters:
    -----------------
    id: comma-separated list of ids

    Returns
    -------
    Arrow table
    """

    log_request(request)

    layer = layer.value

    col_expr = ", ".join(SUMMARY_UNIT_FIELDS)
    ids = id.split(",")
    id_placeholder = ", ".join(["?"] * len(ids))

    records = db.sql(
        f"SELECT {col_expr} FROM map_units WHERE layer=? AND id IN ({id_placeholder})", params=[layer] + ids
    ).fetch_arrow_table()

    if len(records) > MAX_RECORDS:
        raise HTTPException(400, "Too many records requested")

    stream = BytesIO()
    write_feather(
        records,
        stream,
        compression="uncompressed",
    )
    return Response(content=stream.getvalue(), media_type="application/octet-stream")
