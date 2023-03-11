from fastapi import HTTPException
from fastapi.requests import Request
import pyarrow as pa
import pyarrow.compute as pc

from api.constants import (
    DAM_FILTER_FIELD_MAP,
    SB_FILTER_FIELD_MAP,
    COMBINED_FILTER_FIELD_MAP,
    RC_FILTER_FIELD_MAP,
    MULTIPLE_VALUE_FIELDS,
    BarrierTypes,
    Layers,
)
from api.data import dams, small_barriers, combined_barriers, road_crossings


class RecordExtractor:
    """Class for extracting records that are within summary unit ids
    in layer, and according to optional filters.
    """

    field_map = None  # must be set by deriving class to enable filters

    def __init__(
        self,
        request: Request,
        barrier_type: BarrierTypes,
        id: str,
        layer: Layers = "State",
    ):
        field_map = {}
        self.dataset = None

        match barrier_type:
            case "dams":
                field_map = DAM_FILTER_FIELD_MAP
                self.dataset = dams

            case "small_barriers":
                field_map = SB_FILTER_FIELD_MAP
                self.dataset = small_barriers

            case "combined_barriers":
                field_map = COMBINED_FILTER_FIELD_MAP
                self.dataset = combined_barriers

            case "road_crossings":
                field_map = RC_FILTER_FIELD_MAP
                self.dataset = road_crossings

        if layer == "County":
            layer = "COUNTYFIPS"

        self.layer = layer

        ids = [id for id in id.split(",") if id]
        if not ids:
            raise HTTPException(400, detail="id must be non-empty")

        self.ids = pa.array(ids)

        # extract optional filters
        self.filters = dict()
        if field_map:
            filter_keys = {q for q in request.query_params if q in field_map}

            # convert all incoming filter keys to their uppercase field name
            for key in filter_keys:
                field = field_map[key]
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

    def extract(self, columns=None, ranked=False):
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

        return self.dataset.scanner(columns=columns, filter=ix).to_table()
