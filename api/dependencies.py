from fastapi import HTTPException
from fastapi.requests import Request

from api.constants import DAM_FILTER_FIELD_MAP, SB_FILTER_FIELD_MAP, Layers


class RecordExtractor:
    """Base class for extracting records that are within summary unit ids
    in layer, and according to optional filters.

    Must be subclassed to provide field_map in order to provide optional filters.
    """

    field_map = None  # must be set by deriving class to enable filters

    def __init__(self, request: Request, id: str, layer: Layers = "HUC8"):
        if layer == "County":
            layer = "COUNTYFIPS"

        self.layer = layer

        ids = [id for id in id.split(",") if id]
        if not ids:
            raise HTTPException(400, detail="id must be non-empty")

        self.ids = ids

        # extract optional filters
        self.filters = dict()
        if self.field_map:
            filter_keys = {q for q in request.query_params if q in self.field_map}

            # convert all incoming filter keys to their uppercase field name and
            # all values to integers
            for key in filter_keys:
                self.filters[self.field_map[key]] = [
                    int(x) for x in request.query_params.get(key).split(",")
                ]

    def extract(self, df):
        ix = df[self.layer].isin(self.ids)

        for key, values in self.filters.items():
            ix = ix & df[key].isin(values)

        return df.loc[ix]


class DamsRecordExtractor(RecordExtractor):
    field_map = DAM_FILTER_FIELD_MAP


class BarriersRecordExtractor(RecordExtractor):
    field_map = SB_FILTER_FIELD_MAP
