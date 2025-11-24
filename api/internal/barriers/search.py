from io import BytesIO
import re
from time import time

from fastapi import APIRouter, Response
from fastapi.requests import Request
from pyarrow.feather import write_feather

from api.constants import BARRIER_SEARCH_RESULT_FIELDS
from api.data import db
from api.logger import log_request, log


router = APIRouter()


SARPID_REGEX = re.compile(r"^\S\S\d+")

NUM_BARRIER_SEARCH_RESULTS = 10


@router.get("/barriers/search")
async def search(request: Request, query: str):
    """Return top 10 barriers based on text search of name fields or by SARPID
    (combined name search field created in advance)

    Query parameters:
    query: text search
    """

    log_request(request)

    query = query.strip()
    total = 0

    col_expr = ", ".join([f"search_barriers.{col} AS {col.lower()}" for col in BARRIER_SEARCH_RESULT_FIELDS])

    # search on SARPID
    if SARPID_REGEX.match(query):
        # NOTE: case must match

        # strip whitespace if user copy/pasted from sidebar
        query = query.replace(" ", "") + "%"

        total = db.sql("SELECT COUNT(*) FROM search_barriers WHERE SARPID LIKE ?", params=(query,)).fetchone()[0]

        matches = db.sql(
            f"""SELECT {col_expr} FROM search_barriers
            WHERE SARPID LIKE ?
            ORDER BY length(SARPID) ASC, SARPID ASC
            LIMIT {NUM_BARRIER_SEARCH_RESULTS}""",
            params=(query,),
        ).to_arrow_table()

        # discard pandas metadata and store total count
        matches = matches.replace_schema_metadata({"count": str(total)})

    else:
        # use a simple like query for faster performance, and Jaccard similarity
        # NOTE: we use the row_number() to preserve the row order through the join
        start = time()
        total = db.sql(
            "SELECT count(*) FROM search_barriers_name WHERE search_key LIKE ?",
            params=(f"%{query.replace(' ', '%')}%",),
        ).fetchone()[0]

        sql_query = f"""WITH hits AS (
            SELECT SARPID, priority, search_key,
                jaccard(search_key, '{query}') as similarity,
                instr(search_key, '{query}') AS ipos,
                length(search_key) as len,
                row_number() over (ORDER BY similarity DESC, len ASC, ipos ASC, priority ASC) as ix
                FROM search_barriers_name
                WHERE search_key LIKE ?
                ORDER BY ix
                LIMIT {NUM_BARRIER_SEARCH_RESULTS}
            )
            SELECT {col_expr}
            FROM hits INNER JOIN search_barriers
            ON (search_barriers.SARPID = hits.SARPID)
            ORDER BY ix
        """
        matches = db.sql(sql_query, params=(f"%{query.replace(' ', '%')}%",)).to_arrow_table().combine_chunks()

        log.info(f"query by name: {time() - start}s")

    # discard pandas metadata and store total count
    matches = matches.replace_schema_metadata({"count": str(total)})

    stream = BytesIO()
    write_feather(
        matches,
        stream,
        compression="uncompressed",
    )
    return Response(content=stream.getvalue(), media_type="application/octet-stream")
