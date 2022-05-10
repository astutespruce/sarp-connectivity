from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
import pyarrow.compute as pc

from api.constants import UNIT_FIELDS
from api.data import units
from api.logger import log, log_request


router = APIRouter()


@router.get("/units/search")
def search_units(request: Request, layer: str, query: str):
    """Return top 10 units based on text search

    Query parameters:
    layer: comma-delimited list of layers (e.g., "HUC2,HUC6")
    query: text search
    """

    log_request(request)

    layers = layer.split(",")
    query = query.strip()

    invalid_layers = set(layers).difference(UNIT_FIELDS)
    if invalid_layers:
        raise HTTPException(400, detail=f"invalid layers: {', '.join(invalid_layers)}")

    # use case-insensitive search
    matches = units.to_table(
        filter=pc.field("layer").isin(layers)
        & pc.match_substring(pc.field("name"), query.lower(), ignore_case=True)
    )

    # find those where the substring is closest to the left of the name and
    # have the shortest names, based on priority order of different unit types
    matches = (
        matches.append_column(
            "name_ipos", pc.find_substring(matches["name"], query, ignore_case=True)
        ).append_column("name_len", pc.utf8_length(matches["name"]))
    ).sort_by(
        [
            ["priority", "ascending"],
            ["name_ipos", "ascending"],
            ["name_len", "ascending"],
            ["state", "ascending"],
        ]
    )

    df = matches[:10].to_pandas()
    df["bbox"] = df.bbox.apply(list)
    count = len(matches)
    remaining = count - 10 if count > 10 else 0

    return {
        "meta": {"remaining": remaining},
        "results": df[["layer", "id", "state", "name", "bbox"]].to_dict(
            orient="records"
        ),
    }
