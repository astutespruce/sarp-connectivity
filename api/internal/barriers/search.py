from io import BytesIO
import re

from fastapi import APIRouter, Response
from fastapi.requests import Request
import pyarrow.compute as pc
import pyarrow as pa
from pyarrow.feather import write_feather
from rapidfuzz import fuzz

from api.constants import BARRIER_SEARCH_RESULT_FIELDS
from api.data import db, search_barriers
from api.logger import log_request


router = APIRouter()


SARPID_REGEX = re.compile(r"^\S\S\d+")

NUM_BARRIER_SEARCH_RESULTS = 10


def rank_similarity(values, query):
    return pa.array([fuzz.WRatio(value, query) for value in values], type=pa.float32())


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

    # search on SARPID
    if SARPID_REGEX.match(query):
        # NOTE: case must match

        # strip whitespace if user copy/pasted from sidebar
        query = query.replace(" ", "") + "%"

        total = db.sql("SELECT COUNT(*) FROM search_barriers WHERE SARPID LIKE ?", params=(query,)).fetchone()[0]

        col_expr = ", ".join([f"{col} AS {col.lower()}" for col in BARRIER_SEARCH_RESULT_FIELDS])

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
        # replace spaces with regex that allows any whitespace or intermediate words
        # make sure to search whole words, but can be stem of following due to type-ahead
        filter = re.escape(query).replace(",", "").replace("\\ ", r"(((\s)+(\s|\S|\d)*)|(\s))+")
        filter = rf"(^|\s){filter}"

        matches = search_barriers.to_table(
            filter=pc.match_substring_regex(pc.field("search_key"), filter, ignore_case=True),
            columns=BARRIER_SEARCH_RESULT_FIELDS + ["search_key", "priority"],
        )[: 1000 + NUM_BARRIER_SEARCH_RESULTS]

        total = len(matches)

        matches = pa.Table.from_pydict(
            {
                **{col.lower(): matches[col] for col in matches.column_names},
                "sim": rank_similarity(
                    matches["search_key"].to_numpy(),
                    query,
                ),
                # find position of first word, further left is better
                "ipos": pc.find_substring(matches["search_key"], query.split(" ")[0], ignore_case=True),
            }
        ).sort_by([["sim", "descending"], ["ipos", "ascending"], ["priority", "ascending"]])

        matches = matches.select([c.lower() for c in BARRIER_SEARCH_RESULT_FIELDS])

    matches = matches[:NUM_BARRIER_SEARCH_RESULTS].combine_chunks()

    # discard pandas metadata and store total count
    matches = matches.replace_schema_metadata({"count": str(total)})

    stream = BytesIO()
    write_feather(
        matches,
        stream,
        compression="uncompressed",
    )
    return Response(content=stream.getvalue(), media_type="application/octet-stream")
