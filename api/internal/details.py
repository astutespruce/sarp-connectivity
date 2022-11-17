from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import pyarrow.compute as pc

from api.data import dams, small_barriers
from api.logger import log_request


router = APIRouter()


@router.get("/dams/details/{sarp_id}")
def get_dam(request: Request, sarp_id: str):
    log_request(request)

    dam = (
        dams.filter(pc.equal(dams["SARPID"], sarp_id))
        .slice(0)
        .rename_columns([c.lower() for c in dams.schema.names])
    )

    if not len(dam):
        raise HTTPException(404, detail=f"dam not found for SARPID: {sarp_id}")

    # use the bulk converter to dict (otherwise float32 serialization issues)
    # and return singular first item
    return JSONResponse(content=dam.to_pandas().to_dict(orient="records")[0])


@router.get("/small_barriers/details/{sarp_id}")
def get_small_barrier(request: Request, sarp_id: str):
    log_request(request)

    barrier = (
        small_barriers.filter(pc.equal(small_barriers["SARPID"], sarp_id))
        .slice(0)
        .rename_columns([c.lower() for c in small_barriers.schema.names])
    )
    if not len(barrier):
        raise HTTPException(404, detail=f"barrier not found for SARPID: {sarp_id}")

    # use the bulk converter to dict (otherwise float32 serialization issues)
    # and return singular first item
    return JSONResponse(content=barrier.to_pandas().to_dict(orient="records")[0])
