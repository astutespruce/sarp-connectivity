from io import BytesIO

from fastapi import APIRouter, HTTPException, Response
from fastapi.requests import Request
import pyarrow.compute as pc
import pyarrow as pa
from pyarrow.feather import write_feather

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
    query = query.strip().replace(",", "")

    invalid_layers = set(layers).difference(UNIT_FIELDS)
    if invalid_layers:
        raise HTTPException(400, detail=f"invalid layers: {', '.join(invalid_layers)}")

    # use case-insensitive search
    matches = units.to_table(
        filter=pc.field("layer").isin(layers)
        & pc.match_substring(pc.field("key"), query.lower(), ignore_case=True)
    )

    # discard pandas metadata and store count
    matches = matches.replace_schema_metadata({"count": str(len(matches))})

    # find those where the substring is closest to the left of the name and
    # have the shortest names, based on priority order of different unit types
    matches = (
        pa.Table.from_pydict(
            {
                **{col: matches[col] for col in matches.column_names},
                "name_ipos": pc.find_substring(matches["key"], query, ignore_case=True),
                "name_len": pc.utf8_length(matches["name"]),
            }
        )
        .sort_by(
            [
                ["priority", "ascending"],
                ["name_ipos", "ascending"],
                ["name_len", "ascending"],
                ["state", "ascending"],
            ]
        )
        .select(["id", "layer", "name", "bbox"])[:10]
    )

    stream = BytesIO()
    write_feather(
        matches,
        stream,
        compression="uncompressed",
    )
    return Response(content=stream.getvalue(), media_type="application/octet-stream")
