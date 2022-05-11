from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
import pyarrow as pa
import pyarrow.compute as pc

from api.constants import (
    STATES,
    DAM_PUBLIC_EXPORT_FIELDS,
    SB_PUBLIC_EXPORT_FIELDS,
    unpack_domains,
)
from api.data import dams, barriers, get_removed_dams
from api.logger import log, log_request
from api.response import csv_response


router = APIRouter()


class StateRecordExtractor:
    def __init__(self, id: str):
        ids = [id.upper() for id in id.split(",") if id]
        if not ids:
            raise HTTPException(400, detail="id must be non-empty")

        invalid = set(ids).difference(STATES)
        if invalid:
            raise HTTPException(400, detail=f"ids are not valid: {', '.join(invalid)}")

        self.ids = pa.array(ids)

    def extract(self, df):
        return df.filter(pc.is_in(df["State"], self.ids))


@router.get("/dams/state")
def query_dams(
    request: Request,
    extractor: StateRecordExtractor = Depends(),
):
    """Return subset of dams based on state abbreviations.

    Query parameters:
    id: list of state abbreviations
    """

    log_request(request)

    df = extractor.extract(dams).select(DAM_PUBLIC_EXPORT_FIELDS).sort_by("HasNetwork")
    df = unpack_domains(df)

    log.info(f"public query selected {len(df):,} dams")

    return csv_response(df)


@router.get("/removed_dams")
def query_removed_dams(
    request: Request,
):
    """Return dams that were removed for conservation"""

    log_request(request)
    df = unpack_domains(get_removed_dams())

    return csv_response(df)


@router.get("/barriers/state")
def query_barriers(request: Request, extractor: StateRecordExtractor = Depends()):
    """Return subset of barriers based on state abbreviations.

    Query parameters:
    id: list of state abbreviations
    """

    log_request(request)

    df = (
        extractor.extract(barriers)
        .select(SB_PUBLIC_EXPORT_FIELDS)
        .sort_by("HasNetwork")
    )
    df = unpack_domains(df)

    log.info(f"public query selected {len(df):,} barriers")

    return csv_response(df)
