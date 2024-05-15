from io import BytesIO

from fastapi import APIRouter, Response
from fastapi.requests import Request
import pyarrow as pa
import pyarrow.compute as pc
from pyarrow.feather import write_feather

from api.constants import Layers, SUMMARY_UNIT_FIELDS
from api.data import units
from api.logger import log_request


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

    filter = (pc.field("layer") == layer) & (pc.field("id").isin(pa.array(id.split(","))))

    # FIXME
    matches = units.to_table(columns=SUMMARY_UNIT_FIELDS, filter=filter)

    stream = BytesIO()
    write_feather(
        matches,
        stream,
        compression="uncompressed",
    )
    return Response(content=stream.getvalue(), media_type="application/octet-stream")
