from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request

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

        self.ids = {STATES[id] for id in ids}

    def extract(self, df):
        return df.loc[df.State.isin(self.ids)]


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

    df = extractor.extract(dams)[DAM_PUBLIC_EXPORT_FIELDS].copy()
    df = df.sort_values(by="HasNetwork", ascending=False)
    df = unpack_domains(df)

    log.info(f"public query selected {len(df.index)} dams")

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

    df = extractor.extract(barriers)[SB_PUBLIC_EXPORT_FIELDS].copy()
    df = df.sort_values(by="HasNetwork", ascending=False)
    df = unpack_domains(df)

    log.info(f"public query selected {len(df.index)} barriers")

    return csv_response(df)
