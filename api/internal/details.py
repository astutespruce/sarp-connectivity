from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from api.constants import (
    DAM_FILTER_FIELDS,
    SB_FILTER_FIELDS,
)
from api.data import dams, barriers
from api.logger import log, log_request


router = APIRouter()


@router.get("/dams/details/{sarp_id}")
def get_dam(request: Request, sarp_id: str):
    log_request(request)

    matches = dams.loc[dams.SARPID == sarp_id]
    if not len(matches):
        raise HTTPException(404, detail=f"dam not found for SARPID: {sarp_id}")

    # in case there are multiple dams per SARPID, take the first
    # (data error, should only present during testing)
    dam = matches.iloc[0:1].reset_index(drop=True)
    dam.columns = [c.lower() for c in dam.columns]

    # use the bulk converter to dict (otherwise float32 serialization issues)
    # and return singular first item
    return JSONResponse(content=dam.to_dict(orient="records")[0])


@router.get("/small_barriers/details/{sarp_id}")
def get_small_barrier(request: Request, sarp_id: str):
    log_request(request)

    matches = barriers.loc[barriers.SARPID == sarp_id]
    if not len(matches):
        raise HTTPException(404, detail=f"barrier not found for SARPID: {sarp_id}")

    # in case there are multiple dams per SARPID, take the first
    # (data error, should only present during testing)
    barrier = matches.iloc[0:1].reset_index(drop=True)
    barrier.columns = [c.lower() for c in barrier.columns]

    # use the bulk converter to dict (otherwise float32 serialization issues)
    # and return singular first item
    return JSONResponse(content=barrier.to_dict(orient="records")[0])
