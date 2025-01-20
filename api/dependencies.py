from fastapi import HTTPException, status
from fastapi.requests import Request
import pyarrow as pa

from api.constants import (
    DAM_FILTER_FIELD_MAP,
    SB_FILTER_FIELD_MAP,
    COMBINED_FILTER_FIELD_MAP,
    ROAD_CROSSING_FILTER_FIELD_MAP,
    MULTIPLE_VALUE_FIELDS,
    BOOLEAN_FILTER_FIELDS,
    FullySupportedBarrierTypes,
)


def get_unit_ids(
    # unit types must be specified manually in order to extract individually from query parameters
    HUC2: str = None,
    HUC6: str = None,
    HUC8: str = None,
    HUC10: str = None,
    HUC12: str = None,
    State: str = None,
    County: str = None,
    CongressionalDistrict: str = None,
    # FishHabitatPartnership specifically excluded here; is handled as a filter below
):
    """Extract unit ids for each unit type from the URL query parameters

    Parameters
    ----------
    HUC2 : str, optional
        comma-delimited list of HUC2 values for unit_ids
    HUC6 : str, optional
        comma-delimited list of HUC6 values for unit_ids
    HUC8 : str, optional
        comma-delimited list of HUC8 values for unit_ids
    HUC10 : str, optional
        comma-delimited list of HUC10 values for unit_ids
    HUC12 : str, optional
        comma-delimited list of HUC12 values for unit_ids
    State : str, optional
        comma-delimited list of State values for unit_ids
    County : str, optional
        comma-delimited list of County FIPS values for unit_ids
    CongressionalDistrict : str, optional
        comma-delimited list of congressional district values for unit_ids

    Returns
    -------
    dict
        dict of {<unit type>:[...unit ids...], ...}
    """
    units = {
        "HUC2": HUC2,
        "HUC6": HUC6,
        "HUC8": HUC8,
        "HUC10": HUC10,
        "HUC12": HUC12,
        "State": State,
        "COUNTYFIPS": County,
        "CongressionalDistrict": CongressionalDistrict,
    }
    unit_ids = {}
    for key, ids in units.items():
        if ids is not None:
            if ids == "":
                unit = key
                if key == "COUNTYFIPS":
                    unit = "County"

                raise HTTPException(400, detail=f"ids for {unit} must be non-empty")

            unit_ids[key] = pa.array([id for id in ids.split(",") if id])

    return unit_ids


def get_filter_params(
    request: Request,
    barrier_type: FullySupportedBarrierTypes,
):
    """Parse request query parameters into field-level parameters that can be
    used to filter the pyarrow Dataset

    Parameters
    ----------
    request : fastapi.requests.Request
    barrier_type : BarrierTypes


    Returns
    -------
    dict
        dict of {<field>: (<filter type>, <filter values>), ...}
    """
    field_map = {}

    # units specifically handled for extracting ids in above function
    prefiltered_units = {
        "HUC2",
        "HUC6",
        "HUC8",
        "HUC10",
        "HUC12",
        "State",
        "COUNTYFIPS",
        "CongressionalDistrict",
    }

    match barrier_type:
        case "dams":
            field_map = DAM_FILTER_FIELD_MAP

        case "small_barriers":
            field_map = SB_FILTER_FIELD_MAP

        case "combined_barriers":
            field_map = COMBINED_FILTER_FIELD_MAP

        case "largefish_barriers":
            field_map = COMBINED_FILTER_FIELD_MAP

        case "smallfish_barriers":
            field_map = COMBINED_FILTER_FIELD_MAP

        case "road_crossings":
            field_map = ROAD_CROSSING_FILTER_FIELD_MAP

        case _:
            # this should be caught by API handler before getting here
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"this operation is not supported for {barrier_type.value}",
            )

    # extract optional filters
    filters = dict()
    if field_map:
        filter_keys = {q for q in request.query_params if q in field_map and q not in prefiltered_units}

        # convert all incoming filter keys to their uppercase field name
        for key in filter_keys:
            field = field_map[key]
            if field in MULTIPLE_VALUE_FIELDS:
                filters[field] = (
                    "in_string",
                    request.query_params.get(key).split(","),
                )
            elif field in BOOLEAN_FILTER_FIELDS:
                filters[field] = (
                    "in_array",
                    [bool(x) for x in request.query_params.get(key).split(",")],
                )
            else:
                filters[field] = (
                    "in_array",
                    [int(x) for x in request.query_params.get(key).split(",")],
                )

    return filters
