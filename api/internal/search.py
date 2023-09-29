from io import BytesIO
import re

from fastapi import APIRouter, HTTPException, Response
from fastapi.requests import Request
import pyarrow.compute as pc
import pyarrow as pa
from pyarrow.feather import write_feather
from rapidfuzz import fuzz

from api.constants import UNIT_FIELDS
from api.data import combined_barriers, units
from api.logger import log_request


router = APIRouter()


SARPID_REGEX = re.compile("^\S\S\d+")
BARRIER_SEARCH_RESULT_COLUMNS = [
    "SARPID",
    "Name",
    "River",
    "Stream",
    "State",
    "BarrierType",
    "lat",
    "lon",
]
NUM_BARRIER_SEARCH_RESULTS = 10


@router.get("/units/search")
async def search_units(request: Request, layer: str, query: str):
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
        .select(
            [
                "id",
                "layer",
                "name",
                "bbox",
                "state",
                "dams",
                "ranked_dams",
                "total_small_barriers",
                "ranked_small_barriers",
                "ranked_largefish_barriers_dams",
                "ranked_largefish_barriers_small_barriers",
                "ranked_smallfish_barriers_dams",
                "ranked_smallfish_barriers_small_barriers",
                "crossings",
            ]
        )[:10]
    )

    stream = BytesIO()
    write_feather(
        matches,
        stream,
        compression="uncompressed",
    )
    return Response(content=stream.getvalue(), media_type="application/octet-stream")


def rank_similarity(values, query):
    return pa.array([fuzz.WRatio(value, query) for value in values], type=pa.float32())


@router.get("/combined_barriers/search")
async def search_barriers(request: Request, query: str):
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
        # NOTE: case must match,
        matches = combined_barriers.to_table(
            filter=pc.starts_with(pc.field("SARPID"), query),
            columns=BARRIER_SEARCH_RESULT_COLUMNS,
        )[: 1000 + NUM_BARRIER_SEARCH_RESULTS]

        total = len(matches)

        # discard pandas metadata and store count, then limit to top 10
        matches = matches.replace_schema_metadata({"count": str(len(matches))})

        # sort to prioritize results with shortest IDs (will be closest matches)
        matches = pa.Table.from_pydict(
            {
                **{col.lower(): matches[col] for col in matches.column_names},
                "id_len": pc.utf8_length(matches["SARPID"]),
            }
        ).sort_by([["id_len", "ascending"], ["sarpid", "ascending"]])

    else:
        # replace spaces with regex that allows any whitespace or intermediate words
        # make sure to search whole words, but can be stem of following due to type-ahead
        filter = (
            re.escape(query)
            .replace(",", "")
            .replace("\\ ", r"(((\s)+(\s|\S|\d)*)|(\s))+")
        )
        filter = rf"(^|\s){filter}"

        matches = combined_barriers.to_table(
            filter=pc.match_substring_regex(
                pc.field("search_key"), filter, ignore_case=True
            ),
            columns=BARRIER_SEARCH_RESULT_COLUMNS + ["search_key"],
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
                "ipos": pc.find_substring(
                    matches["search_key"], query.split(" ")[0], ignore_case=True
                ),
            }
        ).sort_by([["sim", "descending"], ["ipos", "ascending"]])

        matches = matches.select([c.lower() for c in BARRIER_SEARCH_RESULT_COLUMNS])

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
