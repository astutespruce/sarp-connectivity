from fastapi import HTTPException
from fastapi.requests import Request
import pyarrow as pa
import pyarrow.compute as pc

from api.constants import (
    DAM_FILTER_FIELD_MAP,
    SB_FILTER_FIELD_MAP,
    RC_FILTER_FIELD_MAP,
    MULTIPLE_VALUE_FIELDS,
    Layers,
)


class RecordExtractor:
    """Base class for extracting records that are within summary unit ids
    in layer, and according to optional filters.

    Must be subclassed to provide field_map in order to provide optional filters.
    """

    field_map = None  # must be set by deriving class to enable filters

    def __init__(self, request: Request, id: str, layer: Layers = "State"):
        if layer == "County":
            layer = "COUNTYFIPS"

        self.layer = layer

        ids = [id for id in id.split(",") if id]
        if not ids:
            raise HTTPException(400, detail="id must be non-empty")

        self.ids = pa.array(ids)

        # extract optional filters
        self.filters = dict()
        if self.field_map:
            filter_keys = {q for q in request.query_params if q in self.field_map}

            # convert all incoming filter keys to their uppercase field name
            for key in filter_keys:
                field = self.field_map[key]
                if field in MULTIPLE_VALUE_FIELDS:
                    self.filters[field] = (
                        "in_string",
                        request.query_params.get(key).split(","),
                    )
                else:
                    self.filters[field] = (
                        "in_array",
                        [int(x) for x in request.query_params.get(key).split(",")],
                    )

    def extract(self, ds, columns=None, ranked=False):
        ix = pc.field(self.layer).isin(self.ids)

        if ranked:
            ix = ix & (pc.field("Ranked") == True)

        # fields are evaluated using AND logic
        for key, (match_type, values) in self.filters.items():
            if match_type == "in_string":
                # test if incoming string is present within the set of comma-delimited
                # values in the field using OR logic
                match_ix = pc.match_substring(pc.field(key), values[0])
                for value in values[1:]:
                    match_ix = match_ix | pc.match_substring(pc.field(key), value)

                ix = ix & match_ix

            else:
                # test that the field value is present in the set of incoming values
                ix = ix & (pc.is_in(pc.field(key), pa.array(values)))

        return ds.scanner(columns=columns, filter=ix).to_table()


class DamsRecordExtractor(RecordExtractor):
    field_map = DAM_FILTER_FIELD_MAP


class BarriersRecordExtractor(RecordExtractor):
    field_map = SB_FILTER_FIELD_MAP


class RoadCrossingsRecordExtractor(RecordExtractor):
    field_map = RC_FILTER_FIELD_MAP
