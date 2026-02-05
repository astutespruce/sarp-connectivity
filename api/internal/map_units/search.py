from io import BytesIO
from time import time

from fastapi import APIRouter, HTTPException, Response
from fastapi.requests import Request
from pyarrow.feather import write_feather

from api.constants import UNIT_FIELDS, SUMMARY_UNIT_FIELDS
from api.data import db
from api.logger import log_request, log


NUM_UNIT_SEARCH_RESULTS = 10


router = APIRouter()


@router.get("/units/search")
async def search_units(request: Request, layer: str, query: str):
    """Return top 10 units based on text search

    Query parameters:
    -----------------

    layer: comma-delimited list of layers (e.g., "HUC2,HUC6")
    query: text search

    Returns
    -------
    Arrow table
    """

    log_request(request)

    layers = layer.split(",")
    query = query.lower().strip().replace(",", "")

    invalid_layers = set(layers).difference(UNIT_FIELDS)
    if invalid_layers:
        raise HTTPException(400, detail=f"invalid layers: {', '.join(invalid_layers)}")

    layers_placeholder = ", ".join(["?"] * len(layers))

    start = time()

    total_count = db.sql(
        f"SELECT count(*) FROM map_units WHERE layer IN ({layers_placeholder}) AND key LIKE ?",
        params=(layers + [f"%{query.replace(' ', '%')}%"]),
    ).fetchone()[0]

    sql_query = f"""
    SELECT *, instr(key, ?) AS ipos, length(key) as len
    FROM map_units
    WHERE layer IN ({layers_placeholder}) AND key LIKE ?
    ORDER BY priority ASC, ipos ASC, len ASC, state ASC
    LIMIT {NUM_UNIT_SEARCH_RESULTS}
    """
    matches = (
        db.sql(sql_query, params=[query] + layers + [f"%{query.replace(' ', '%')}%"]).to_arrow_table().combine_chunks()
    )

    log.info(f"query by name: {time() - start}s")

    # discard pandas metadata and store total count
    matches = matches.select(SUMMARY_UNIT_FIELDS).replace_schema_metadata({"count": str(total_count)})

    stream = BytesIO()
    write_feather(
        matches,
        stream,
        compression="uncompressed",
    )
    return Response(content=stream.getvalue(), media_type="application/octet-stream")
