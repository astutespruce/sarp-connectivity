from enum import Enum

import numpy as np
import pyarrow as pa
import pandas as pd


### Enums for validating incoming request values
class BarrierTypes(str, Enum):
    dams = "dams"
    small_barriers = "small_barriers"


class Layers(str, Enum):
    HUC2 = "HUC2"
    HUC6 = "HUC6"
    HUC8 = "HUC8"
    HUC10 = "HUC10"
    HUC12 = "HUC12"
    State = "State"
    County = "County"
    ECO3 = "ECO3"
    ECO4 = "ECO4"


class Formats(str, Enum):
    csv = "csv"


class Scenarios(str, Enum):
    NC = "NC"
    PNC = "PNC"
    WC = "WC"
    NCWC = "NCWC"
    PNCWC = "PNCWC"


def unique(items):
    """Convert a sorted list of items into a unique list, taking the
    first occurrence of each duplicate item.

    Parameters
    ----------
    items : list-like

    Returns
    -------
    list
    """

    s = set()
    result = []
    for item in items:
        if not item in s:
            result.append(item)
            s.add(item)

    return result


# Summary unit fields
UNIT_FIELDS = [
    "HUC2",
    "HUC6",
    "HUC8",
    "HUC10",
    "HUC12",
    "State",
    "County",
    "ECO3",
    "ECO4",
]


# metric fields that are only valid for barriers with networks
METRIC_FIELDS = [
    "HasNetwork",
    "Ranked",
    "Intermittent",
    "StreamOrder",
    "Landcover",
    "SizeClasses",
    "TotalUpstreamMiles",
    "PerennialUpstreamMiles",
    "IntermittentUpstreamMiles",
    "AlteredUpstreamMiles",
    "UnalteredUpstreamMiles",
    "PerennialUnalteredUpstreamMiles",
    "TotalDownstreamMiles",
    "FreeDownstreamMiles",
    "FreePerennialDownstreamMiles",
    "FreeIntermittentDownstreamMiles",
    "FreeAlteredDownstreamMiles",
    "FreeUnalteredDownstreamMiles",
    "GainMiles",
    "PerennialGainMiles",
    "TotalNetworkMiles",
    "TotalPerennialNetworkMiles",
    "PercentUnaltered",
    "PercentPerennialUnaltered",
]

TIER_FIELDS = [
    "State_NC_tier",
    "State_WC_tier",
    "State_NCWC_tier",
    "State_PNC_tier",
    "State_PWC_tier",
    "State_PNCWC_tier",
]

# Only present when custom prioritization is performed
CUSTOM_TIER_FIELDS = [
    "NC_tier",
    "WC_tier",
    "NCWC_tier",
    "PNC_tier",
    "PWC_tier",
    "PNCWC_tier",
]


FILTER_FIELDS = [
    "GainMilesClass",
    "TESppClass",
    "StateSGCNSppClass",
    "Trout",
    "StreamOrderClass",
    "PercentAlteredClass",
    "OwnerType",
    "Intermittent",
    "HUC8_COA",
    "HUC8_SGCN",
]

DAM_FILTER_FIELDS = FILTER_FIELDS + [
    "Feasibility",
    "Purpose",
    "Condition",
    "HeightClass",
    "BarrierSeverity",
    "LowheadDam",
    "PassageFacilityClass",
    "WaterbodySizeClass",
]
DAM_FILTER_FIELD_MAP = {f.lower(): f for f in DAM_FILTER_FIELDS}

SB_FILTER_FIELDS = FILTER_FIELDS + [
    "ConditionClass",
    "CrossingTypeClass",
    "Constriction",
    "RoadTypeClass",
    "SeverityClass",
]
SB_FILTER_FIELD_MAP = {f.lower(): f for f in SB_FILTER_FIELDS}


### Fields used for export
# common API fields
GENERAL_API_FIELDS1 = [
    "lat",
    "lon",
    "Name",
    "SARPID",
    "Source",
]

GENERAL_API_FIELDS2 = (
    [
        "Condition",
        "TESpp",
        "StateSGCNSpp",
        "RegionalSGCNSpp",
        "Trout",
        "OwnerType",
        "ProtectedLand",
        # Priority watersheds
        "HUC8_USFS",
        "HUC8_COA",
        "HUC8_SGCN",
        # Watershed names
        "Basin",
        "Subbasin",
        "Subwatershed",
    ]
    + UNIT_FIELDS
    + ["Excluded", "Invasive", "OnLoop"]
    + METRIC_FIELDS
)

# This order should mostly match FIELD_DEFINITIONS below
# NOTE: make sure the resultant set is unique!
DAM_CORE_FIELDS = (
    GENERAL_API_FIELDS1
    + [
        "NIDID",
        "Link",
        "Estimated",
        "River",
        "NHDPlusID",
        "StreamSizeClass",
        "AnnualVelocity",
        "AnnualFlow",
        "TotDASqKm",
        "Year",
        "YearRemoved",
        "Height",
        "Width",
        "Construction",
        "Purpose",
        "PassageFacility",
        "Feasibility",
        # IMPORTANT: Recon is intentionally omitted per direction from SARP
        # "Recon",
        "BarrierSeverity",
        "Diversion",
        "LowheadDam",
        "NoStructure",
        "WaterbodyKM2",
        "WaterbodySizeClass",
    ]
    + GENERAL_API_FIELDS2
    # the following are dam-specific network results
    + ["FlowsToOcean", "NumBarriersDownstream"]
)

DAM_CORE_FIELDS = unique(DAM_CORE_FIELDS)

# Internal API includes tiers
DAM_EXPORT_FIELDS = unique(DAM_CORE_FIELDS + TIER_FIELDS + CUSTOM_TIER_FIELDS)
DAM_API_FIELDS = unique(
    DAM_CORE_FIELDS
    + TIER_FIELDS
    + DAM_FILTER_FIELDS
    + ["upNetID", "downNetID", "COUNTYFIPS"]
)

# Public API does not include tier fields
DAM_PUBLIC_EXPORT_FIELDS = DAM_CORE_FIELDS


# Drop fields that can be calculated on frontend or are not used
DAM_TILE_FIELDS = [
    c
    for c in DAM_API_FIELDS + ["packed"]
    if not c
    in {
        "IntermittentUpstreamMiles",
        "FreeIntermittentDownstreamMiles",
        "GainMiles",
        "PerennialGainMiles",
        "TotalNetworkMiles",
        "TotalPerennialNetworkMiles",
        "PercentUnaltered",
        "PercentPerennialUnaltered",
        "FlowsToOcean",
        "NumBarriersDownstream",
        "YearRemoved",
        "NHDPlusID",
        "Basin",
        "HUC2",
        "ProtectedLand",
        "AnnualVelocity",
        "AnnualFlow",
        # unit name fields are retrieved from summary tiles
        "Subbasin",
        "Subwatershed",
        "County",
        # included in "packed": (note: some fields included above since used for processing tiles)
        "Excluded",
        "OnLoop",
        "StreamOrder",
        "Estimated",
        "Invasive",
        "NoStructure",
        "HUC8_USFS",
        "Diversion",
        "Recon",  # excluded from API_FIELDS (important!)
        "PassageFacility",
    }
]

DAM_TILE_FILTER_FIELDS = unique(
    ["lat", "lon"] + DAM_FILTER_FIELDS + [f for f in UNIT_FIELDS if not f == "HUC2"]
)

DAM_PACK_BITS = [
    {"field": "StreamOrder", "bits": 4},
    {"field": "Recon", "bits": 5},
    {"field": "HUC8_USFS", "bits": 2},
    {"field": "PassageFacility", "bits": 5},
    {"field": "Diversion", "bits": 2},
    {"field": "Estimated", "bits": 1},
    {"field": "HasNetwork", "bits": 1},
    {"field": "Excluded", "bits": 1},
    {"field": "OnLoop", "bits": 1},
    {"field": "Unranked", "bits": 1},
    {"field": "Invasive", "bits": 1},
    {"field": "NoStructure", "bits": 1},
]


SB_CORE_FIELDS = (
    GENERAL_API_FIELDS1
    + [
        "LocalID",
        "CrossingCode",
        "Stream",
        "NHDPlusID",
        "AnnualVelocity",
        "AnnualFlow",
        "TotDASqKm",
        "Road",
        "RoadType",
        "CrossingType",
        "Constriction",
        "PotentialProject",
        "SeverityClass",
        "SARP_Score",
        "YearRemoved",
        "StreamSizeClass",
    ]
    + GENERAL_API_FIELDS2
)

SB_CORE_FIELDS = unique(SB_CORE_FIELDS)

# Internal API includes tiers
SB_EXPORT_FIELDS = unique(SB_CORE_FIELDS + TIER_FIELDS + CUSTOM_TIER_FIELDS)
SB_API_FIELDS = unique(
    SB_CORE_FIELDS
    + TIER_FIELDS
    + SB_FILTER_FIELDS
    + ["upNetID", "downNetID", "COUNTYFIPS"]
)

# Public API does not include tier fields
SB_PUBLIC_EXPORT_FIELDS = SB_CORE_FIELDS


# Drop fields from tiles that are calculated on frontend or not used
SB_TILE_FIELDS = [
    c
    for c in SB_API_FIELDS + ["packed"]
    if not c
    in {
        "IntermittentUpstreamMiles",
        "FreeIntermittentDownstreamMiles",
        "GainMiles",
        "PerennialGainMiles",
        "TotalNetworkMiles",
        "TotalPerennialNetworkMiles",
        "PercentUnaltered",
        "PercentPerennialUnaltered",
        "YearRemoved",
        "NHDPlusID",
        "ProtectedLand",
        "Basin",
        "HUC2",
        "AnnualVelocity",
        "AnnualFlow",
        "PotentialProject",
        # fields where we only use domain rather than string values
        "RoadType",
        "Condition",
        "CrossingType",
        # unit name fields are retrieved from summary tiles
        "Subbasin",
        "Subwatershed",
        "County",
        # included in "packed": (note: some fields included above since used for processing tiles)
        "Excluded",
        "OnLoop",
        "StreamOrder",
        "Invasive",
        "HUC8_USFS",
        "Recon",  # excluded from API_FIELDS (important!)
    }
]

SB_PACK_BITS = [
    {"field": "StreamOrder", "bits": 4},
    {"field": "Recon", "bits": 5},
    {"field": "HUC8_USFS", "bits": 2},
    {"field": "HasNetwork", "bits": 1},
    {"field": "Excluded", "bits": 1},
    {"field": "OnLoop", "bits": 1},
    {"field": "Unranked", "bits": 1},
    {"field": "Invasive", "bits": 1},
]


SB_TILE_FILTER_FIELDS = unique(
    ["lat", "lon"] + SB_FILTER_FIELDS + [f for f in UNIT_FIELDS if not f == "HUC2"]
)

# NOTE: waterfalls have network metrics for both dams and small barriers; these
# are not repeated for general flowline properties
WF_METRIC_FIELDS = [
    c
    for c in METRIC_FIELDS
    if not c
    in {
        "HasNetwork",
        "Ranked",
        "Intermittent",
        "StreamOrder",
    }
]

WF_CORE_FIELDS = (
    GENERAL_API_FIELDS1
    + [
        "Stream",
        "FallType",
        "NHDPlusID",
        "AnnualVelocity",
        "AnnualFlow",
        "TotDASqKm",
        # from GENERAL_API_FIELDS2
        "TESpp",
        "StateSGCNSpp",
        "RegionalSGCNSpp",
        "Trout",
        "OwnerType",
        "ProtectedLand",
        # Priority watersheds
        "HUC8_USFS",
        "HUC8_COA",
        "HUC8_SGCN",
        # Watershed names
        "Basin",
        "Subbasin",
        "Subwatershed",
        "Excluded",
    ]
    + ["HUC8", "HUC10", "HUC12", "State", "County", "COUNTYFIPS"]
    + [f"{c}_dams" for c in WF_METRIC_FIELDS]
    + ["upNetID_dams", "downNetID_dams"]
    + [f"{c}_small_barriers" for c in WF_METRIC_FIELDS]
    + ["upNetID_small_barriers", "downNetID_small_barriers"]
)
WF_CORE_FIELDS = unique(WF_CORE_FIELDS)


WF_TILE_FIELDS = [
    c
    for c in WF_CORE_FIELDS + ["packed"]
    if not c
    in {
        # network fields are for both dams
        "FreeIntermittentDownstreamMiles_dams",
        "GainMiles_dams",
        "IntermittentUpstreamMiles_dams",
        "PerennialGainMiles_dams",
        "PercentUnaltered_dams",
        "PercentPerennialUnaltered_dams",
        "TotalNetworkMiles_dams",
        "TotalPerennialNetworkMiles_dams",
        # and small barriers
        "FreeIntermittentDownstreamMiles_small_barriers",
        "GainMiles_small_barriers",
        "IntermittentUpstreamMiles_small_barriers",
        "PerennialGainMiles_small_barriers",
        "PercentUnaltered_small_barriers",
        "PercentPerennialUnaltered_small_barriers",
        "TotalNetworkMiles_small_barriers",
        "TotalPerennialNetworkMiles_small_barriers",
        # not used for tiles
        "NHDPlusID",
        "Basin",
        "HUC2",
        "ProtectedLand",
        "AnnualVelocity",
        "AnnualFlow",
        # unit name fields are retrieved from summary tiles
        "Subbasin",
        "Subwatershed",
        "County",
        # included in "packed": (note: some fields included above since used for processing tiles)
        "Excluded",
        "OnLoop",
        "StreamOrder",
        "HUC8_USFS",
    }
]

WF_PACK_BITS = [
    {"field": "StreamOrder", "bits": 4},
    {"field": "HUC8_USFS", "bits": 2},
    {"field": "HasNetwork", "bits": 1},
    {"field": "Excluded", "bits": 1},
    {"field": "OnLoop", "bits": 1},
]


### Bit-packing for tiers

TIER_BITS = 5  # holds values 0...21 after subtracting offset
STATE_TIER_PACK_BITS = [
    {"field": c, "bits": TIER_BITS, "value_shift": 1} for c in TIER_FIELDS
]


### Domains for coded values in exported data

# typos fixed and trailing periods removed
RECON_DOMAIN = {
    0: "Not yet evaluated",  # added
    1: "Good candidate for removal. Move forward with landowner contact",  # expanded acronym
    2: "Dam needs follow-up with landowner",
    3: "Removal is unlikely.  Social conditions unfavorable",
    4: "Removal is extremely infeasible.  Large reservoirs, etc.",
    5: "Dam may be removed or error",
    6: "Infeasible in short term via landowner contact",
    7: "Dam was deliberately removed",
    8: "Dam location is incorrect and needs to be moved",  # fixed phrasing
    9: "Dam is breached and no impoundment visible",
    10: "Dam was once considered, need to revisit",
    11: "Removal planned",
    13: "Unsure, need second opinion",
    14: "Take immediate action, abandoned-looking dam in poor condition",
    15: "No conservation benefit",
    16: "Invasive species barrier",
    17: "Risky for mussels",
    18: "Dam failed",
    19: "Proposed dam",
    20: "Farm pond - no conservation benefit",
    21: "Potential thermal issues",
    22: "Removal unlikely; fish passage installed",
    23: "Duplicate fish passage project structure",
}

# Created here to capture values below
FEASIBILITY_DOMAIN = {
    # -1: "N/A",  # These are filtered out in preprocessing - not barriers
    0: "Not assessed",
    1: "Not feasible",
    2: "Likely infeasible",
    3: "Possibly feasible",
    4: "Likely feasible",
    5: "No conservation benefit",
    9: "Invasive species barrier",
    11: "Fish passage installed",
    12: "Removal planned",
    13: "Breached - full flow",
    # not shown to user (filtered out for other reasons)
    6: "Unknown",
    7: "Error",
    8: "Dam removed for conservation benefit",
    10: "Proposed dam",
}


PURPOSE_DOMAIN = {
    0: "Unknown",  # added
    1: "Agriculture",
    2: "Flood Control",
    3: "Water Supply",
    4: "Navigation",
    5: "Recreation",
    6: "Hydropower",
    7: "Aquatic Resource Management",
    8: "Other",
    9: "Tailings",
    10: "Not Rated",
    13: "Mine or Industrial Waste",
    11: "Grade Stabilization",
}

CONSTRUCTION_DOMAIN = {
    0: "Unknown",  # added
    1: "Cement",
    2: "Concrete/Roller-compacted Concrete",
    3: "Masonry/Stone",
    4: "Steel",
    5: "Timber",
    6: "Earthfill (Gravel, Sand, Silt, Clay)",
    7: "Rockfill (Rock, Composite)",
    8: "Corrugated Metal",
    9: "Polyvinyl chloride (PVC)",
    10: "Cast Iron",
    11: "Other",
}

DAM_CONDITION_DOMAIN = {
    0: "Not Rated",
    1: "Satisfactory",
    2: "Fair",
    3: "Poor",
    4: "Unsatisfactory",
    5: "Dam failed",  # note: new code mapped from Recon
    6: "Dam breached",  # note: new code mapped from BarrierStatus
}


# Created here
# Height in feet
HEIGHT_DOMAIN = {
    0: "Unknown",
    1: "< 5",
    2: "5 - 10",
    3: "10 - 25",
    4: "25 - 50",
    5: "50 - 100",
    6: ">= 100",
}

GAINMILES_DOMAIN = {
    # -1: "no network", # filter this out
    0: "< 1",
    1: "1 - 5",
    2: "5 - 10",
    3: "10 - 25",
    4: "25 - 100",
    5: ">= 100",
}

RARESPP_DOMAIN = {0: "0", 1: "1", 2: "1 - 4", 3: "5 - 9", 4: ">= 10"}

LANDCOVER_DOMAIN = {
    # -1: "no network", # filter this out
    0: "< 50",
    1: "50 - 75",
    2: "75 - 90",
    3: ">= 90",
}


STREAM_ORDER_DOMAIN = {
    # -1: "no network", # filter this out
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: ">= 6",
}

WATERBODY_SIZECLASS_DOMAIN = {
    -1: "Not associated with a pond or lake",
    0: "Pond (< 0.01 km2)",
    1: "Very small lake (0.01 - 0.09 km2)",
    2: "Small lake (0.1 - 0.9 km2)",
    3: "Medium lake (1 - 9.9 km2)",
    4: "Large lake (>= 10 km2)",
}


BARRIER_SEVERITY_DOMAIN = {
    0: "Unknown",
    1: "Not a barrier",  # includes minor barriers
    2: "Moderate barrier",
    3: "Major barrier",
}

CROSSING_TYPE_DOMAIN = {
    0: "Unknown",
    1: "Not a barrier",
    2: "Bridge",
    3: "Culvert",
    4: "Ford",
    5: "Dam",
    6: "Buried stream",
}

CONSTRICTION_DOMAIN = {
    0: "Unknown",
    1: "Spans Full Channel & Banks",
    2: "Spans Only Bankfull/Active Channel",
    3: "Moderate",
    4: "Severe",
}

DIVERSION_DOMAIN = {0: "Unknown", 1: "Yes", 2: "No"}

# Note: -1 and 2 are made up here, not part of original domain
LOWHEADDAM_DOMAIN = {-1: "Unknown", 0: "No", 1: "Yes", 2: "Likely"}

FISHSCREEN_DOMAIN = {0: "Unknown", 1: "Yes", 2: "No"}

SCREENTYPE_DOMAIN = {
    0: "Unknown",
    1: "Horizontal",
    2: "Vertical",
    3: "Cone",
    4: "Pipe",
    5: "Drum",
    6: "Other",
}

DAM_BARRIER_SEVERITY_DOMAIN = {
    0: "Unknown",
    1: "Complete",
    2: "Partial",
    3: "Partial Passability - Non Salmonid",
    4: "Partial Passability - Salmonid",
    5: "Seasonably Passable - Non Salmonid",
    6: "Seasonably Passable - Salmonid",
    7: "No Barrier",
}


ROAD_TYPE_DOMAIN = {0: "Unknown", 1: "Unpaved", 2: "Paved", 3: "Railroad"}

BARRIER_CONDITION_DOMAIN = {0: "Unknown", 1: "Failing", 2: "Poor", 3: "OK", 4: "New"}

OWNERTYPE_DOMAIN = {
    # 0: "Unknown",
    1: "US Fish and Wildlife Service land",
    2: "USDA Forest Service land",
    3: "Federal land",
    4: "State land",
    5: "Joint Ownership or Regional land",
    6: "Native American land",
    7: "Private easement",
    8: "Other private conservation land",
}

BOOLEAN_DOMAIN = {False: "no", True: "yes"}

HUC8_USFS_DOMAIN = {
    0: "Not a priority / not assessed",
    1: "Highest priority",
    2: "Moderate priority",
    3: "Lowest priority",
}

HUC8_COA_DOMAIN = {
    0: "Not a conservation opportunity area",
    1: "Conservation opportunity area",
}

HUC8_SGCN_DOMAIN = {
    0: "Not within top 10 watersheds per state",
    1: "Within top 10 watersheds per state",
}

PASSAGEFACILITY_CLASS_DOMAIN = {
    0: "No known fish passage structure",
    1: "Fish passage structure present",
}

PASSAGEFACILITY_DOMAIN = {
    0: "Unknown or None",
    1: "Trap & Truck",
    2: "Fish Ladder - unspecified",
    3: "Locking",
    4: "Rock Rapids",
    5: "Eelway",
    6: "Alaskan Steeppass",
    7: "Herring Passage",
    8: "Reservation",
    9: "Exemption",
    10: "Notch",
    11: "Denil Fishway",
    12: "Fish Lift",
    13: "Partial Breach",
    14: "Removal",
    15: "Pool and Weir Fishway",
    16: "Vertical Slot Fishway",
    17: "Nature-like Fishway",
    18: "Bypass Channel Fishway",
    19: "Crossvane",
    20: "Screen Bypass",
    21: "Fishway Unspecified",
    22: "Other",
}

# Not used directly
# BARRIERSTATUS_DOMAIN = {
#     0: "Unknown",
#     1: "Impounding",
#     2: "Full breach",
#     3: "Partial breach",
#     4: "Drained",
#     5: "Dry detention",
# }

MANUALREVIEW_DOMAIN = {
    2: "NABD Dams",
    4: "Onstream checked by SARP",
    5: "Offstream checked by SARP - do not snap",
    6: "Delete - Error, checked by SARP",
    7: "Assumed offstream, >100 meters from flowline",
    8: "Dam removed for conservation",
    9: "Assumed offstream, >200 meters from flowline",
    10: "Invasive barriers, do not prioritize",
    11: "Delete (Duplicate)",
    13: "Onstream checked by SARP - Did not have to move",
    14: "Delete (No Dam)",
    15: "Onstream - moved to correct location",
    20: "Estimated dam",
    21: "Dam likely off network (source from Amber Ignatius ACF project)",
}


STREAMTYPE_DOMAIN = {
    0: "Not on a stream / river",  # not snapped to flowline,
    1: "Perennial stream / river",
    2: "Intermittent stream / river",
    3: "Artificial path / unspecified connector",
    4: "Canal / ditch",
    5: "Pipeline",
}

BOOLEAN_OFFNETWORK_DOMAIN = {-1: "off network", 0: "no", 1: "yes"}


### Not exported
# IMPOUNDMENTTYPE_DOMAIN = {1: "Run of river", 2: "Lake-like", 3: "Large reservoir"}


# STRUCTURECATEGORY_DOMAIN = {
#     0: "Unknown",
#     1: "Fish Management",
#     2: "Road Crossing",
#     3: "Diversion",
#     4: "Culvert",
#     5: "Natural",
#     6: "Non-structural",
#     7: "Debris",
#     8: "Other",
#     9: "Dam",
# }

# STRUCTURECLASS_DOMAIN = {
#     11: "Fish Mgnt: Fishway",
#     12: "Fish Mgnt: Fish Ladder",
#     13: "Fish Mgnt: Fish Trap",
#     14: "Fish Mgnt: Fish Lock",
#     15: "Fish Mgnt: Rock-Ramp",
#     16: "Fish Mgnt: Vertical-Slot",
#     17: "Fish Mgnt: Baffle",
#     21: "Road Crossing: Railroad",
#     22: "Road Crossing: Bridge-Free Span",
#     23: "Road Crossing: Instream Crossing",
#     24: "Road Crossing: Road Crosses Stream",
#     25: "Road Crossing: Bridge",
#     26: "Road Crossing: Low Water Crossing",
#     31: "Diversion: Unscreened",
#     32: "Diversion: Screened",
#     33: "Diversion: Canal",
#     34: "Diversion: Channel",
#     35: "Diversion: Pump",
#     36: "Diversion: Ditch",
#     37: "Diversion: Vertical",
#     38: "Diversion: Centrifugal",
#     39: "Diversion: Slant",
#     310: "Diversion: Floodgate",
#     311: "Diversion: Siphon",
#     312: "Diversion: Submersible",
#     41: "Culvert: Corrugated metal",
#     43: "Culvert: Circular",
#     44: "Culvert: Open Bottom",
#     45: "Culvert: Pipe Arch",
#     46: "Culvert: Arch",
#     47: "Culvert: Bottomless",
#     49: "Culvert: Pipe-multiple",
#     411: "Culvert: Box",
#     51: "Natural: Waterfall",
#     511: "Natural: Cascade",
#     52: "Natural: Beaver Dam",
#     53: "Natural: Rocks Blockage",
#     61: "Non-structural: High Velocity",
#     62: "Non-structural: Temperature",
#     63: "Non-structural: Low Flow",
#     64: "Non-structural: Chemical",
#     65: "Non-structural: Steep Gradient",
#     66: "Non-structural: Oxygen Depleted",
#     67: "Non-structural: Salinity",
#     68: "Non-structural: Low Light",
#     71: "Debris: Log Jam",
#     72: "Debris: Trash (non-natural)",
#     73: "Debris: Landslide",
#     74: "Debris: Boulders-Rocks (man-made)",
#     75: "Debris: Debris Jam",
#     81: "Other: Levee",
#     82: "Other: Gabion",
#     83: "Other: Locks",
#     84: "Other: Tailing",
#     85: "Other: Waterfall (man-made)",
#     86: "Other: Dike",
#     97: "Dam: Buttress",
#     98: "Dam: Arch",
#     99: "Dam: Multi-Arch",
#     910: "Dam: Embankment",
#     911: "Dam: Grade",
#     916: "Dam: Lowhead or Weir",
#     917: "Dam: Dam Other",
#     918: "Dam: Gravity",
# }


# state abbrev to name, from CENSUS Tiger
STATES = {
    "AK": "Alaska",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MP": "Commonwealth of the Northern Mariana Islands",
    "MS": "Mississippi",
    "MT": "Montana",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VI": "United States Virgin Islands",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}


# mapping of field name to domains
DOMAINS = {
    "State": STATES,
    "HasNetwork": BOOLEAN_DOMAIN,
    "OnLoop": BOOLEAN_DOMAIN,
    "Excluded": BOOLEAN_DOMAIN,
    "Ranked": BOOLEAN_DOMAIN,
    "Invasive": BOOLEAN_DOMAIN,
    "Intermittent": BOOLEAN_OFFNETWORK_DOMAIN,
    "FlowsToOcean": BOOLEAN_OFFNETWORK_DOMAIN,
    "OwnerType": OWNERTYPE_DOMAIN,
    "ProtectedLand": BOOLEAN_DOMAIN,
    "HUC8_USFS": HUC8_USFS_DOMAIN,
    "HUC8_COA": HUC8_COA_DOMAIN,
    "HUC8_SGCN": HUC8_SGCN_DOMAIN,
    "ManualReview": MANUALREVIEW_DOMAIN,
    # dam fields
    # note Recon domain is just used for internal exports; excluded from public exports
    "Recon": RECON_DOMAIN,
    "Condition": DAM_CONDITION_DOMAIN,
    "Construction": CONSTRUCTION_DOMAIN,
    "Purpose": PURPOSE_DOMAIN,
    "Feasibility": FEASIBILITY_DOMAIN,
    "PassageFacility": PASSAGEFACILITY_DOMAIN,
    "Diversion": DIVERSION_DOMAIN,
    "LowheadDam": LOWHEADDAM_DOMAIN,
    "FishScreen": FISHSCREEN_DOMAIN,
    "ScreenType": SCREENTYPE_DOMAIN,
    "BarrierSeverity": DAM_BARRIER_SEVERITY_DOMAIN,
    "WaterbodySizeClass": WATERBODY_SIZECLASS_DOMAIN,
    "NoStructure": BOOLEAN_DOMAIN,
    # barrier fields
    "SeverityClass": BARRIER_SEVERITY_DOMAIN,
    "ConditionClass": BARRIER_CONDITION_DOMAIN,
    "Constriction": CONSTRICTION_DOMAIN,
}


def unpack_field(arr, lookup):
    """Unpack domain codes to string values for a single field, using numpy.
    Values that are not present in lookup are assigned empty string.

    Parameters
    ----------
    column : array-like
    lookup : dict
        lookup of codes to values

    Returns
    -------
    np.array
    """
    u, inv = np.unique(arr, return_inverse=True)
    return np.array([lookup.get(x, "") for x in u], dtype=str)[inv].reshape(inv.shape)


def unpack_domains(df):
    """Unpack domain codes to values.

    Parameters
    ----------
    df : DataFrame or pyarrow.Table
    """

    if isinstance(df, pd.DataFrame):
        df = df.copy()
        for field, domain in DOMAINS.items():
            if field in df.columns:
                df[field] = df[field].map(domain)
    else:
        schema = df.schema.remove_metadata()
        arrays = [
            unpack_field(df[field], DOMAINS[field]) if field in DOMAINS else df[field]
            for field in schema.names
        ]

        for i, field in enumerate(schema.names):
            if field in DOMAINS:
                schema = schema.set(i, pa.field(field, "string"))

        df = pa.Table.from_arrays(
            arrays,
            schema=schema,
        )

    return df


# Lookup of field to description, for download / APIs
# Note: replace {type} with appropriate type when rendering
FIELD_DEFINITIONS = {
    # general fields
    "lat": "latitude in WGS84 geographic coordinates.",
    "lon": "longitude in WGS84 geographic coordinates.",
    "Name": "{type} name, if available.",
    "SARPID": "SARP Identifier.",
    # dam-specific fields
    "NIDID": "National Inventory of Dams Identifier.",
    "Source": "Source of this record in the inventory.",
    "Link": "Link to additional information about this {type}",
    "Estimated": "Dam represents an estimated dam location based on NHD high resolution waterbodies or other information",
    "NoStructure": "this location is a water diversion without an associated barrier structure and is not ranked",
    "River": "River name where {type} occurs, if available.",
    "Year": "year that construction was completed, if available.  0 = data not available.",
    "YearRemoved": "year that dam was removed, if available.  0 = data not available or dam not removed.",
    "Height": "{type} height in feet, if available.  0 = data not available.",
    "Width": "{type} width in feet, if available.  0 = data not available.",
    "Construction": "material used in {type} construction, if known.",
    "Purpose": "primary purpose of {type}, if known.",
    "PassageFacility": "type of fish passage facility, if known.",
    "Feasibility": "feasibility of {type} removal, based on reconnaissance.  Note: reconnaissance information is available only for a small number of {type}s.",
    "BarrierSeverity": "passability of the barrier, if known.",
    "Diversion": "Identifies if dam is known to be a diversion.  Note: diversion information is available only for a small number of dams.",
    "LowheadDam": "Identifies if dam is known or estimated to be a lowhead dam.  Note: lowhead dam information is available only for a small number of dams.",
    "WaterbodyKM2": "area of associated waterbody in square kilometers.  -1 = no associated waterbody",
    "WaterbodySizeClass": "size class of associated waterbody.",
    # barrier-specific fields
    "LocalID": "local identifier.",
    "CrossingCode": "crossing identifier.",
    "Stream": "stream or river name where barrier occurs, if available.",
    "Road": "road name, if available.",
    "RoadType": "type of road, if available.",
    "CrossingType": "type of road / stream crossing, if known.",
    "Constriction": "type of constriction at road / stream crossing, if known.",
    "PotentialProject": "reconnaissance information about the crossing, including severity of the barrier and / or potential for removal project.",
    "SeverityClass": "potential severity of barrier, based on reconnaissance.",
    "SARP_Score": "The best way to consider the aquatic passability scores is that they represent the degree to which crossings deviate from an ideal crossing. We assume that those crossings that are very close to the ideal (scores > 0.6) will present only a minor or insignificant barrier to aquatic organisms. Those structures that are farthest from the ideal (scores < 0.4) are likely to be either significant or severe barriers. These are, however, arbitrary distinctions imposed on a continuous scoring system and should be used with that in mind. -1 = not available.",
    # other general fields
    "NHDPlusID": "Unique NHD Plus High Resolution flowline identifier to which the barrier is snapped.  -1 = not snapped to a flowline.  Note: not all barriers snapped to flowlines are used in the network connectivity analysis.",
    "StreamSizeClass": "Stream size class based on total catchment drainage area in square kilometers.  1a: <10 km2, 1b: 10-100 km2, 2: 100-518 km2, 3a: 518-2,590 km2, 3b: 2,590-10,000 km2, 4: 10,000-25,000 km2, 5: >= 25,000 km2.",
    "TotDASqKm": "Total catchment drainage area at the downstream end of the NHD Plus High Resolution flowline to which this {type} has been snapped, in square kilometers.  -1 if not snapped to flowline or otherwise not available",
    "AnnualFlow": "Annual flow at the downstream end of the NHD Plus High Resolution flowline to which this {type} has been snapped, in square cubic feet per second.  -1 if not snapped to flowline or otherwise not available",
    "AnnualVelocity": "Annual velocity at the downstream end of the NHD Plus High Resolution flowline to which this {type} has been snapped, in square feet per second.  -1 if not snapped to flowline or otherwise not available",
    "Condition": "Condition of the {type} as of last assessment, if known. Note: assessment dates are not known.",
    "TESpp": "Number of federally-listed threatened or endangered aquatic species, compiled from element occurrence data within the same subwatershed (HUC12) as the {type}. Note: rare species information is based on occurrences within the same subwatershed as the barrier.  These species may or may not be impacted by this {type}.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.",
    "StateSGCNSpp": "Number of state-listed Species of Greatest Conservation Need (SGCN), compiled from element occurrence data within the same subwatershed (HUC12) as the {type}.  Note: rare species information is based on occurrences within the same subwatershed as the {type}.  These species may or may not be impacted by this {type}.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.",
    "RegionalSGCNSpp": "Number of regionally-listed Species of Greatest Conservation Need (SGCN), compiled from element occurrence data within the same subwatershed (HUC12) as the {type}.  Note: rare species information is based on occurrences within the same subwatershed as the {type}.  These species may or may not be impacted by this {type}.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.",
    "Trout": "1 if one or more trout species are present within the same subwatershed (HUC12) as the {type}, 0 if trout species were not recorded in available natural heritage data.",
    "OwnerType": "Land ownership type. This information is derived from the CBI Protected Areas Database and TNC Secured Lands Database, to highlight ownership types of particular importance to partners.  NOTE: does not include most private land.",
    "ProtectedLand": "Indicates if the {type} occurs on public land as represented within the CBI Protected Areas Database of the U.S. and TNC Secured Lands Database.",
    "HUC8_USFS": "U.S. Forest Service (USFS) priority watersheds (HUC8 level) within USFS Southeast Region.",
    "HUC8_COA": "SARP conservation opportunity areas.",
    "HUC8_SGCN": "Top 10 watersheds per state based on number of Species of Greatest Conservation Need (SGCN).",
    "Basin": "Name of the hydrologic basin (HUC6) where the {type} occurs.",
    "Subbasin": "Name of the hydrologic subbasin (HUC8) where the {type} occurs.",
    "Subwatershed": "Name of the hydrologic subwatershed (HUC12) where the {type} occurs.",
    "HUC2": "Hydrologic region identifier where the {type} occurs",
    "HUC6": "Hydrologic basin identifier where the {type} occurs.",
    "HUC8": "Hydrologic subbasin identifier where the {type} occurs.",
    "HUC10": "Hydrologic watershed identifier where the {type} occurs.",
    "HUC12": "Hydrologic subwatershed identifier where the {type} occurs.",
    "County": "County where {type} occurs.",
    "State": "State where {type} occurs.",
    "ECO3": "EPA Level 3 Ecoregion Identifier.",
    "ECO4": "EPA Level 4 Ecoregion Identifier.",
    "HasNetwork": "indicates if this {type} was snapped to the aquatic network for analysis.  1 = on network, 0 = off network.  Note: network metrics and scores are not available for {type}s that are off network.",
    "Excluded": "this {type} was excluded from the connectivity analysis based on field reconnaissance or manual review of aerial imagery.",
    "Ranked": "this {type} was included for prioritization.  Some barriers that are beneficial to restricting the movement of invasive species or that are water diversions without associated barriers are excluded from ranking.",
    "Invasive": "this {type} is identified as a beneficial to restricting the movement of invasive species and is not ranked",
    "OnLoop": "this {type} occurs on a loop within the NHD High Resolution aquatic network and is considered off-network for purposes of network analysis and ranking",
    "Intermittent": "indicates if this {type} was snapped to a a stream or river reach coded by NHDPlusHR as an intermittent or ephemeral. -1 = not available.",
    "StreamOrder": "NHDPlus Modified Strahler stream order. -1 = not available.",
    "Landcover": "average amount of the river floodplain in the upstream network that is in natural landcover types.  -1 = not available.",
    "SizeClasses": "number of unique upstream size classes that could be gained by removal of this {type}. -1 = not available.",
    "TotalUpstreamMiles": "number of miles in the upstream river network from this {type}, including miles in waterbodies. -1 = not available.",
    "PerennialUpstreamMiles": "number of perennial miles in the upstream river network from this {type}, including miles in waterbodies.  Perennial reaches are all those not specifically coded by NHD as ephemeral or intermittent, and include other types, such as canals and ditches that may not actually be perennial.  Networks are constructed using all flowlines, not just perennial reaches. -1 = not available.",
    "IntermittentUpstreamMiles": "number of ephemeral and intermittent miles in the upstream river network from this {type}, including miles in waterbodies.  Ephemeral and intermittent reaches are all those that are specifically coded by NHD as ephemeral or intermittent, and specifically excludes other types, such as canals and ditches that may actually be ephemeral or intermittent in their flow frequency.  -1 = not available.",
    "AlteredUpstreamMiles": "number of altered miles in the upstream river network from this {type}, including miles in waterbodies.  Limited to reaches specifically coded by NHD as canals or ditches. -1 = not available.",
    "UnalteredUpstreamMiles": "number of unaltered miles in the upstream river network from this {type}, including miles in waterbodies.  Unaltered miles exclude reaches specifically coded by NHD as canals or ditches. -1 = not available.",
    "PerennialUnalteredUpstreamMiles": "number of unaltered perennial miles in the upstream river network from this {type}, including miles in waterbodies.  Unaltered miles exclude reaches specifically coded by NHD as canals or ditches. -1 = not available.",
    "PercentUnaltered": "percent of the total upstream river network length from this {type} that is not specifically coded as NHD as canals or ditches.  -1 = not available.",
    "PercentPerennialUnaltered": "percent of the perennial upstream river network length from this {type} that is not specifically coded as NHD as canals or ditches.  See PerennialUpstreamMiles.  -1 = not available.",
    "TotalDownstreamMiles": "number of miles in the complete downstream river network from this {type}, including miles in waterbodies.  Note: this measures the length of the complete downstream network including all tributaries, and is not limited to the shortest downstream path.  -1 = not available.",
    "FreeDownstreamMiles": "number of free-flowing miles in the downstream river network (TotalDownstreamMiles minus miles in waterbodies). -1 = not available.",
    "FreePerennialDownstreamMiles": "number of free-flowing perennial miles in the downstream river network.  Excludes miles in waterbodies.  See PerennialUpstreamMiles. -1 = not available.",
    "FreeIntermittentDownstreamMiles": "number of free-flowing ephemeral and intermittent miles in the downstream river network.  Excludes miles in waterbodies.  See IntermittentUpstreamMiles. -1 = not available.",
    "FreeAlteredDownstreamMiles": "number of free-flowing altered miles in the downstream river network from this {type}.  Excludes miles in waterbodies or reaches specifically coded by NHD as canals or ditches. -1 = not available.",
    "FreeUnalteredDownstreamMiles": "number of free-flowing altered miles in the downstream river network from this {type}.  Limited to reaches specifically coded by NHD as canals or ditches.  Excludes miles in waterbodies. -1 = not available.",
    "GainMiles": "absolute number of miles that could be gained by removal of this {type}.  Calculated as the minimum of the TotalUpstreamMiles and FreeDownstreamMiles. -1 = not available.",
    "PerennialGainMiles": "absolute number of perennial miles that could be gained by removal of this {type}.  Calculated as the minimum of the PerennialUpstreamMiles and FreePerennialDownstreamMiles. -1 = not available.",
    "TotalNetworkMiles": "sum of TotalUpstreamMiles and FreeDownstreamMiles. -1 = not available.",
    "TotalPerennialNetworkMiles": "sum of PerennialUpstreamMiles and FreePerennialDownstreamMiles. -1 = not available.",
    "FlowsToOcean": "indicates if this {type} was snapped to a stream or river that flows into the ocean.  Note: this underrepresents any networks that traverse regions outside the analysis region that would ultimately connect the networks to the ocean.",
    "NumBarriersDownstream": "number of barriers downstream to the downstream-most point of the downstream river network, which may be the ocean.  -1 = not available (not on network).  Note: only includes downstream barriers within the analysis region; there may be additional barriers downstream of a given network outside the analysis region.",
    "State_NC_tier": "network connectivity tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_WC_tier": "watershed condition tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_NCWC_tier": "combined network connectivity and watershed condition tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_PNC_tier": "network connectivity tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_PWC_tier": "perennial watershed condition tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_PNCWC_tier": "combined perennial network connectivity and watershed condition tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "NC_tier": "network connectivity tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "WC_tier": "watershed condition tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "NCWC_tier": "combined network connectivity and watershed condition tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "PNC_tier": "perennial network connectivity tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "PWC_tier": "perennial watershed condition tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "PNCWC_tier": "combined perennial network connectivity and watershed condition tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
}

DAM_FIELD_DEFINITIONS = {
    k: v.replace("{type}", "dam") for k, v in FIELD_DEFINITIONS.items()
}
SB_FIELD_DEFINITIONS = {
    k: v.replace("{type}", "road-related barrier") for k, v in FIELD_DEFINITIONS.items()
}
