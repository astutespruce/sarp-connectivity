from io import BytesIO

from fastapi import APIRouter, Response, HTTPException
from fastapi.requests import Request
import pyarrow as pa
import pyarrow.compute as pc
from pyarrow.feather import write_feather

from api.constants import Layers, SUMMARY_UNIT_FIELDS
from api.data import units
from api.logger import log_request


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

    filter = (pc.field("layer") == layer) & (pc.field("id").isin(pa.array(id.split(","))))

    records = units.to_table(columns=SUMMARY_UNIT_FIELDS, filter=filter)

    if len(records) > MAX_RECORDS:
        raise HTTPException(400, "Too many records requested")

    stream = BytesIO()
    write_feather(
        records,
        stream,
        compression="uncompressed",
    )
    return Response(content=stream.getvalue(), media_type="application/octet-stream")
