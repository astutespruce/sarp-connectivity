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
    BOOLEAN_FILTER_FIELDS,
    BarrierTypes,
)
from api.data import (
    dams,
    small_barriers,
    combined_barriers,
    largefish_barriers,
    smallfish_barriers,
    road_crossings,
)


class RecordExtractor:
    """Class for extracting records that are within summary unit ids
    in layer, and according to optional filters.
    """

    field_map = None  # must be set by deriving class to enable filters

    def __init__(
        self,
        request: Request,
        barrier_type: BarrierTypes,
        # unit types must be specified manually
        HUC2: str = None,
        HUC6: str = None,
        HUC8: str = None,
        HUC10: str = None,
        HUC12: str = None,
        State: str = None,
        County: str = None,
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

            case "largefish_barriers":
                field_map = COMBINED_FILTER_FIELD_MAP
                self.dataset = largefish_barriers

            case "smallfish_barriers":
                field_map = COMBINED_FILTER_FIELD_MAP
                self.dataset = smallfish_barriers

            case "road_crossings":
                field_map = RC_FILTER_FIELD_MAP
                self.dataset = road_crossings

            case _:
                raise NotImplementedError(f"RecordExtractor is not supported for {barrier_type}")

        units = {
            "HUC2": HUC2,
            "HUC6": HUC6,
            "HUC8": HUC8,
            "HUC10": HUC10,
            "HUC12": HUC12,
            "State": State,
            "COUNTYFIPS": County,
        }
        self.unit_ids = {}
        for key, ids in units.items():
            if ids is not None:
                if ids == "":
                    raise HTTPException(
                        400, detail=f"ids for {'County' if key=='COUNTYFIPS' else key} must be non-empty"
                    )

                self.unit_ids[key] = pa.array([id for id in ids.split(",") if id])

        if len(self.unit_ids) == 0:
            raise HTTPException(400, detail="At least one summary unit layer must have ids present")

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
                elif field in BOOLEAN_FILTER_FIELDS:
                    self.filters[field] = (
                        "in_array",
                        [bool(x) for x in request.query_params.get(key).split(",")],
                    )
                else:
                    self.filters[field] = (
                        "in_array",
                        [int(x) for x in request.query_params.get(key).split(",")],
                    )

    def extract(self, columns=None, ranked=False):
        # evaluate unit ids using OR logic
        layers = list(self.unit_ids.keys())
        ix = pc.field(layers[0]).isin(self.unit_ids[layers[0]])
        for layer in layers[1:]:
            ix = ix | pc.field(layer).isin(self.unit_ids[layer])

        if ranked:
            ix = ix & (pc.field("Ranked") == True)  # noqa

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
