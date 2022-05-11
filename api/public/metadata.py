import json
from pathlib import Path
from datetime import date

import pyarrow.compute as pc
from fastapi import APIRouter
from fastapi.requests import Request

from api.constants import (
    DAM_FIELD_DEFINITIONS,
    DAM_PUBLIC_EXPORT_FIELDS,
    SB_FIELD_DEFINITIONS,
    SB_PUBLIC_EXPORT_FIELDS,
)
from api.data import dams, barriers
from api.metadata import description, terms_of_use


with open(Path(__file__).resolve().parent.parent.parent / "ui/package.json") as infile:
    INFO = json.loads(infile.read())


router = APIRouter()


def get_core_metadata(url):
    return {
        "url": str(url),
        "data_version": INFO["version"],
        "data_publish_date": INFO["date"],
        "contact_person": "Kat Hoenke (Spatial Ecologist, Southeast Aquatic Resources Partnership)",
        "contact_email": "kat@southeastaquatics.net",
        "citation": f"Southeast Aquatic Resources Partnership (SARP). {date.today().year}. Comprehensive Southeast Aquatic Barrier Inventory. https://southeastaquatics.net/. (dowloaded {date.today().strftime('%m/%d/%Y')} from {url}). SARP/USFWS.",
        "description": description,
        "terms_of_use": terms_of_use,
    }


# Get list of states that have dams or barriers
dam_states = sorted(pc.unique(dams["State"]).tolist())
barrier_states = sorted(pc.unique(barriers["State"]).tolist())


@router.get("/dams/metadata")
def get_dams_metadata(
    request: Request,
):
    """Return basic metadata describing the dams data."""

    metadata = {
        "count": len(dams),
        "available_states": dam_states,
        "fields": {
            k: v
            for k, v in DAM_FIELD_DEFINITIONS.items()
            if k in DAM_PUBLIC_EXPORT_FIELDS
        },
    }

    metadata.update(get_core_metadata(request.base_url))

    return metadata


@router.get("/barriers/metadata")
def get_barriers_metadata(
    request: Request,
):
    """Return basic metadata describing the small barriers data."""

    metadata = {
        "count": len(barriers),
        "available_states": barrier_states,
        "fields": {
            k: v
            for k, v in SB_FIELD_DEFINITIONS.items()
            if k in SB_PUBLIC_EXPORT_FIELDS
        },
    }

    metadata.update(get_core_metadata(request.base_url))

    return metadata
