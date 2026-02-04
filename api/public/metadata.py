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
from api.data import dams, small_barriers
from api.metadata import description, terms_of_use
from api.settings import DATA_VERSION, DATA_DATE


router = APIRouter()


def get_core_metadata(url):
    return {
        "url": str(url),
        "data_version": DATA_VERSION,
        "data_publish_date": DATA_DATE,
        "contact_person": "Kat Hoenke (Spatial Ecologist, Southeast Aquatic Resources Partnership)",
        "contact_email": "kat@southeastaquatics.net",
        "citation": f"National Aquatic Connectivity Collaborative (NACC). {date.today().year}. National Aquatic Barrier Inventory v{DATA_VERSION} ({DATA_DATE}). Compiled by the Southeast Aquatic Resources Partnership (https://southeastaquatics.net) and the National Fish Habitat Partnership (https://www.fishhabitat.org/).  [Downloaded {date.today().strftime('%m/%d/%Y')} from {url}].",
        "description": description,
        "terms_of_use": terms_of_use,
    }


# Get list of states that have dams or barriers
dam_states = sorted(pc.unique(dams.scanner(columns=["State"]).to_table()["State"]).tolist())
barrier_states = sorted(pc.unique(small_barriers.scanner(columns=["State"]).to_table()["State"]).tolist())


@router.get("/dams/metadata")
async def get_dams_metadata(
    request: Request,
):
    """Return basic metadata describing the dams data."""

    metadata = {
        "count": dams.count_rows(),
        "available_states": dam_states,
        "fields": {k: v for k, v in DAM_FIELD_DEFINITIONS.items() if k in DAM_PUBLIC_EXPORT_FIELDS},
    }

    metadata.update(get_core_metadata(request.base_url))

    return metadata


@router.get("/barriers/metadata")
async def get_barriers_metadata(
    request: Request,
):
    """Return basic metadata describing the small barriers data."""

    metadata = {
        "count": small_barriers.count_rows(),
        "available_states": barrier_states,
        "fields": {k: v for k, v in SB_FIELD_DEFINITIONS.items() if k in SB_PUBLIC_EXPORT_FIELDS},
    }

    metadata.update(get_core_metadata(request.base_url))

    return metadata
