from enum import Enum


### Enums for validating incoming request values
class BarrierTypes(str, Enum):
    dams = "dams"
    small_barriers = "small_barriers"
    combined_barriers = "combined_barriers"
    road_crossings = "road_crossings"


class Layers(str, Enum):
    HUC2 = "HUC2"
    HUC6 = "HUC6"
    HUC8 = "HUC8"
    HUC10 = "HUC10"
    HUC12 = "HUC12"
    State = "State"
    County = "County"


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


# Fields that have multiple values present, encoded as comma-delimited string
MULTIPLE_VALUE_FIELDS = ["SalmonidESU", "DisadvantagedCommunity"]


# Summary unit fields
UNIT_FIELDS = [
    "HUC2",
    "HUC6",
    "HUC8",
    "HUC10",
    "HUC12",
    "State",
    "County",
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
    "UpstreamDrainageArea",
]

# Per guidance from SARP, only expose upstream functional network counts
# and total upstream crossings (but not other total upstream counts),
# and exclude count of downstream crossings
UPSTREAM_COUNT_FIELDS = [
    "UpstreamWaterfalls",
    "UpstreamDams",
    "UpstreamSmallBarriers",
    "UpstreamRoadCrossings",
    "UpstreamHeadwaters",
    # "TotalUpstreamWaterfalls",
    # "TotalUpstreamDams",
    # "TotalUpstreamSmallBarriers",
    "TotalUpstreamRoadCrossings",
    # "TotalUpstreamHeadwaters",
]

# these fields remain constant regardless of network type
DOWNSTREAM_LINEAR_NETWORK_FIELDS = [
    "TotalDownstreamWaterfalls",
    "TotalDownstreamDams",
    "TotalDownstreamSmallBarriers",
    # "TotalDownstreamRoadCrossings",
    "MilesToOutlet",
    "FlowsToOcean",
    "FlowsToGreatLakes",
    "ExitsRegion",
]

# metric fields not used in tiles because they can be calculated on frontend or are not used
UNUSED_TILE_METRIC_FIELDS = [
    "IntermittentUpstreamMiles",
    "FreeIntermittentDownstreamMiles",
    "GainMiles",
    "PerennialGainMiles",
    "TotalNetworkMiles",
    "TotalPerennialNetworkMiles",
    "PercentUnaltered",
    "PercentPerennialUnaltered",
    "UpstreamDrainageArea",
] + UPSTREAM_COUNT_FIELDS


# Only present when custom prioritization is performed
CUSTOM_TIER_FIELDS = [
    "NC_tier",
    "PNC_tier",
    "WC_tier",
    "PWC_tier",
    "NCWC_tier",
    "PNCWC_tier",
]

# Only present for dams
STATE_TIER_FIELDS = [f"State_{c}" for c in CUSTOM_TIER_FIELDS]


FILTER_FIELDS = [
    "GainMilesClass",
    "Condition",
    "TESppClass",
    "StateSGCNSppClass",
    "Trout",
    "SalmonidESU",
    "SalmonidESUCount",
    "StreamOrderClass",
    "PercentAlteredClass",
    "OwnerType",
    "BarrierOwnerType",
    "Intermittent",
    "FlowsToOcean",
    "DownstreamOceanMilesClass",
    "DownstreamOceanBarriersClass",
    "FlowsToGreatLakes",
    "DownstreamGreatLakesMilesClass",
    "DownstreamGreatLakesBarriersClass",
    "CoastalHUC8",
    "PassageFacilityClass",
    "DisadvantagedCommunity",
]

DAM_FILTER_FIELDS = FILTER_FIELDS + [
    "FERCRegulated",
    "StateRegulated",
    "Passability",
    "FeasibilityClass",
    "Purpose",
    "HeightClass",
    "LowheadDam",
    "WaterbodySizeClass",
]
DAM_FILTER_FIELD_MAP = {f.lower(): f for f in DAM_FILTER_FIELDS}

SB_FILTER_FIELDS = FILTER_FIELDS + [
    "BarrierSeverity",
    "Constriction",
    "RoadType",
    "CrossingType",
]
SB_FILTER_FIELD_MAP = {f.lower(): f for f in SB_FILTER_FIELDS}

# BarrierSeverity included for API but not filtering
COMBINED_FILTER_FIELDS = [
    c
    for c in unique(DAM_FILTER_FIELDS + SB_FILTER_FIELDS)
    if not c == "BarrierSeverity"
]
COMBINED_FILTER_FIELD_MAP = {f.lower(): f for f in COMBINED_FILTER_FIELDS}

# Road crossing filters not currently used
RC_FILTER_FIELDS = ["CrossingType"]
RC_FILTER_FIELD_MAP = {f.lower(): f for f in RC_FILTER_FIELDS}


### Fields used for export
# common API fields
GENERAL_API_FIELDS1 = [
    "lat",
    "lon",
    "Name",
    "SARPID",
    "Source",
    "NHDPlusID",
    "StreamSizeClass",
]

GENERAL_API_FIELDS2 = (
    [
        "Removed",
        "YearRemoved",
        "Condition",
        "PassageFacility",
        "TESpp",
        "StateSGCNSpp",
        "RegionalSGCNSpp",
        "Trout",
        "OwnerType",
        "BarrierOwnerType",
        "ProtectedLand",
        "Link",
        "EJTract",
        "EJTribal",
        # Watershed names
        "Basin",
        "Subbasin",
        "Subwatershed",
    ]
    + UNIT_FIELDS
    + ["Excluded", "Invasive", "OnLoop"]
    + METRIC_FIELDS
    + UPSTREAM_COUNT_FIELDS
    + DOWNSTREAM_LINEAR_NETWORK_FIELDS
)

# This order should mostly match FIELD_DEFINITIONS below
# NOTE: make sure the resultant set is unique!
DAM_CORE_FIELDS = (
    GENERAL_API_FIELDS1
    + [
        "NIDID",
        "Estimated",
        "River",
        "AnnualVelocity",
        "AnnualFlow",
        "TotDASqKm",
        "YearCompleted",
        "FERCRegulated",
        "StateRegulated",
        "Height",
        "Length",
        "Width",
        "Construction",
        "Purpose",
        "Passability",
        "FishScreen",
        "ScreenType",
        "Feasibility",
        "Recon",
        "Diversion",
        "LowheadDam",
        "NoStructure",
        "WaterbodyKM2",
        "WaterbodySizeClass",
    ]
    + GENERAL_API_FIELDS2
)

DAM_CORE_FIELDS = unique(DAM_CORE_FIELDS)

# Internal API includes tiers
# IMPORTANT: Recon is intentionally omitted per direction from SARP

DAM_EXPORT_FIELDS = [
    c
    for c in unique(DAM_CORE_FIELDS + STATE_TIER_FIELDS + CUSTOM_TIER_FIELDS)
    if not c == "Recon"
]

DAM_API_FIELDS = unique(
    DAM_CORE_FIELDS
    + STATE_TIER_FIELDS
    + DAM_FILTER_FIELDS
    + ["upNetID", "downNetID", "COUNTYFIPS", "Unranked"]
)

# Public API does not include tier or filter fields
DAM_PUBLIC_EXPORT_FIELDS = [c for c in DAM_CORE_FIELDS if not c == "Recon"]


# Drop fields that can be calculated on frontend or are not used
DAM_TILE_FIELDS = [
    c
    for c in DAM_API_FIELDS + ["packed", "symbol"]
    if c
    not in {
        "NHDPlusID",
        "Basin",
        "HUC2",
        "ProtectedLand",
        "AnnualVelocity",
        "AnnualFlow",
        "FishScreen",
        "ScreenType",
        "Width",
        "Length",
        "EJTract",
        "EJTribal",
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
        "Diversion",
        "Recon",
        "Feasibility",  # not used, only FeasibilityClass used in UI
        "PassageFacility",
        "TotalDownstreamSmallBarriers",
        "TotalDownstreamRoadCrossings",
        "ExitsRegion",
    }.union(UNUSED_TILE_METRIC_FIELDS)
]

DAM_TILE_FILTER_FIELDS = unique(
    DAM_FILTER_FIELDS + [f for f in UNIT_FIELDS if not f == "HUC2"]
)

DAM_PACK_BITS = [
    {"field": "StreamOrder", "bits": 4},
    {"field": "Recon", "bits": 5},
    {"field": "PassageFacility", "bits": 5},
    {"field": "Diversion", "bits": 2},
    {"field": "NoStructure", "bits": 1},
    {"field": "Estimated", "bits": 1},
    {"field": "HasNetwork", "bits": 1},
    {"field": "Excluded", "bits": 1},
    {"field": "OnLoop", "bits": 1},
    {"field": "unsnapped", "bits": 1},
    {"field": "Unranked", "bits": 1},
    {"field": "Invasive", "bits": 1},
]


SB_CORE_FIELDS = (
    GENERAL_API_FIELDS1
    + [
        "LocalID",
        "CrossingCode",
        "Stream",
        "AnnualVelocity",
        "AnnualFlow",
        "TotDASqKm",
        "Road",
        "RoadType",
        "CrossingType",
        "Constriction",
        "PotentialProject",
        "BarrierSeverity",
        "SARP_Score",
        "Recon",
    ]
    + GENERAL_API_FIELDS2
)

SB_CORE_FIELDS = unique(SB_CORE_FIELDS)

# NOTE: state tiers are excluded based on SARP direction
SB_EXPORT_FIELDS = [
    c for c in unique(SB_CORE_FIELDS + CUSTOM_TIER_FIELDS) if not c == "Recon"
]
SB_API_FIELDS = unique(
    SB_CORE_FIELDS
    + SB_FILTER_FIELDS
    + ["upNetID", "downNetID", "COUNTYFIPS", "Unranked"]
)

# Public API does not include tier fields
SB_PUBLIC_EXPORT_FIELDS = [c for c in SB_CORE_FIELDS if not c == "Recon"]


# Drop fields from tiles that are calculated on frontend or not used
SB_TILE_FIELDS = [
    c
    for c in SB_API_FIELDS + ["packed", "symbol"]
    if c
    not in {
        "NHDPlusID",
        "ProtectedLand",
        "Basin",
        "HUC2",
        "AnnualVelocity",
        "AnnualFlow",
        "PotentialProject",
        "EJTract",
        "EJTribal",
        # unit name fields are retrieved from summary tiles
        "Subbasin",
        "Subwatershed",
        "County",
        # included in "packed": (note: some fields included above since used for processing tiles)
        "Excluded",
        "OnLoop",
        "StreamOrder",
        "Invasive",
        "Recon",
        "PassageFacility",
        # metric fields that can be calculated on frontend or not used
        "TotalDownstreamRoadCrossings",
        "ExitsRegion",
    }.union(UNUSED_TILE_METRIC_FIELDS)
]

SB_PACK_BITS = [
    {"field": "StreamOrder", "bits": 4},
    {"field": "Recon", "bits": 5},
    {"field": "PassageFacility", "bits": 5},
    {"field": "HasNetwork", "bits": 1},
    {"field": "Excluded", "bits": 1},
    {"field": "OnLoop", "bits": 1},
    {"field": "unsnapped", "bits": 1},
    {"field": "Unranked", "bits": 1},
    {"field": "Invasive", "bits": 1},
]


SB_TILE_FILTER_FIELDS = unique(
    SB_FILTER_FIELDS + [f for f in UNIT_FIELDS if not f == "HUC2"]
)


COMBINED_API_FIELDS = [
    c
    for c in unique(["BarrierType"] + DAM_API_FIELDS + SB_API_FIELDS)
    if c not in STATE_TIER_FIELDS
]

COMBINED_EXPORT_FIELDS = [
    c
    for c in unique(["BarrierType"] + DAM_EXPORT_FIELDS + SB_EXPORT_FIELDS)
    if c not in STATE_TIER_FIELDS
]


COMBINED_TILE_FILTER_FIELDS = [
    c
    for c in unique(DAM_TILE_FILTER_FIELDS + SB_TILE_FILTER_FIELDS)
    if not c == "BarrierSeverity"
]

COMBINED_TILE_FIELDS = [
    c for c in unique(DAM_TILE_FIELDS + SB_TILE_FIELDS) if c not in STATE_TIER_FIELDS
]


ROAD_CROSSING_CORE_FIELDS = (
    GENERAL_API_FIELDS1
    + [
        "TESpp",
        "StateSGCNSpp",
        "RegionalSGCNSpp",
        "Trout",
        # "SalmonidESU", # not used for downloads
        "OwnerType",
        # "BarrierOwnerType", # not available
        "ProtectedLand",
        # Watershed names
        "Basin",
        "Subbasin",
        "Subwatershed",
        "CrossingType",
        # "OnLoop", # not useful
        "Intermittent",
        "StreamOrder",
    ]
    + UNIT_FIELDS
)

ROAD_CROSSING_CORE_FIELDS = unique(ROAD_CROSSING_CORE_FIELDS)

ROAD_CROSSING_API_FIELDS = unique(ROAD_CROSSING_CORE_FIELDS + ["COUNTYFIPS"])

# Manually-selected subset of fields to keep size small
# NOTE: all retained road crossings are snapped
ROAD_CROSSING_TILE_FIELDS = [
    "id",
    "SARPIDName",
    "Source",
    "County",
    "State",
    "HUC8",
    "HUC12",
    "Road",
    "Stream",
    "TESpp",
    "RegionalSGCNSpp",
    "StateSGCNSpp",
    "SalmonidESU",
    "StreamSizeClass",
    "packed",
    # merged into separate field
    # "SARPID",
    # "Name",
    # included in packed bits
    # "StreamOrder",
    # "OwnerType",
    # "crossingtype",
    # "Trout",
    # "Intermittent",
    # "ProtectedLand",
    # "EJTract", # and following combined back to DisadvantagedCommunity
    # "EJTribal"
]

# Fields that are used for filtering other barrier types can be bit-packed instead
# for road crossings (they aren't filtered)
ROAD_CROSSING_PACK_BITS = [
    {"field": "StreamOrder", "bits": 4},
    {"field": "OnLoop", "bits": 1},
    {"field": "OwnerType", "bits": 4},
    {"field": "crossingtype", "bits": 4},
    {"field": "Trout", "bits": 1},
    {"field": "Intermittent", "bits": 1},
    {"field": "ProtectedLand", "bits": 1},
    {"field": "EJTract", "bits": 1},
    {"field": "EJTribal", "bits": 1},
]


# NOTE: waterfalls have network metrics for both dams and small barriers; these
# are not repeated for general flowline properties
WF_METRIC_FIELDS = [
    c
    for c in METRIC_FIELDS + UPSTREAM_COUNT_FIELDS
    if c
    not in {
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
        "AnnualVelocity",
        "AnnualFlow",
        "TotDASqKm",
        "Passability",
        # from GENERAL_API_FIELDS2
        "TESpp",
        "StateSGCNSpp",
        "RegionalSGCNSpp",
        "Trout",
        "SalmonidESU",
        "OwnerType",
        "ProtectedLand",
        # Watershed names
        "Basin",
        "Subbasin",
        "Subwatershed",
        "Excluded",
    ]
    + ["HUC8", "HUC10", "HUC12", "State", "County", "COUNTYFIPS"]
    + [
        "Intermittent",
        "StreamOrder",
    ]
    + [f"{c}_dams" for c in WF_METRIC_FIELDS]
    + ["upNetID_dams", "downNetID_dams"]
    + [f"{c}_small_barriers" for c in WF_METRIC_FIELDS]
    + ["upNetID_small_barriers", "downNetID_small_barriers"]
    + DOWNSTREAM_LINEAR_NETWORK_FIELDS
)
WF_CORE_FIELDS = unique(WF_CORE_FIELDS)


WF_TILE_FIELDS = [
    c
    for c in WF_CORE_FIELDS + ["packed"]
    if c
    not in {
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
        "Intermittent",
        "TotalDownstreamRoadCrossings",
        "ExitsRegion",
        # Not used
        "HUC10",
        "OwnerType",
        "CoastalHUC8",
    }
    .union({f"{c}_dams" for c in UNUSED_TILE_METRIC_FIELDS})
    .union({f"{c}_small_barriers" for c in UNUSED_TILE_METRIC_FIELDS})
]

WF_PACK_BITS = [
    {"field": "StreamOrder", "bits": 4},
    {"field": "HasNetwork", "bits": 1},
    {"field": "Intermittent", "bits": 1},
    {"field": "Excluded", "bits": 1},
    {"field": "OnLoop", "bits": 1},
    {"field": "unsnapped", "bits": 1},
]


### Bit-packing for tiers

TIER_BITS = 5  # holds values 0...21 after subtracting offset
STATE_TIER_PACK_BITS = [
    {"field": c, "bits": TIER_BITS, "value_shift": 1} for c in STATE_TIER_FIELDS
]
CUSTOM_TIER_PACK_BITS = [
    {"field": c, "bits": TIER_BITS, "value_shift": 1} for c in CUSTOM_TIER_FIELDS
]


### Domains for coded values in exported data
BARRIERTYPE_DOMAIN = {
    "dams": "Dam",
    "small_barriers": "Assessed road-related barrier",
}


# typos fixed and trailing periods removed
RECON_DOMAIN = {
    0: "Not yet evaluated",  # added
    1: "Good candidate for removal. Move forward with landowner contact",  # expanded acronym
    2: "Dam needs follow-up with landowner",
    3: "Removal is unlikely.  Social conditions unfavorable",
    4: "Removal is extremely infeasible.  Large reservoirs, etc.",
    5: "Barrier may be removed or error",
    6: "Infeasible in short term via landowner contact",
    7: "Barrier was deliberately removed",
    8: "Location is incorrect and needs to be moved",  # fixed phrasing
    9: "Breached and no impoundment visible",
    10: "Was once considered, need to revisit",
    11: "Removal planned",
    13: "Unsure, need second opinion",
    14: "Good candidate for further exploration - dam appears to be in poor condition",  # new phrasing from Kat
    15: "No conservation benefit",
    16: "Invasive species barrier",
    17: "Risky for mussels",
    18: "Barrier failed",
    19: "Proposed dam",
    20: "Farm pond - no conservation benefit",
    21: "Potential thermal issues",
    22: "Removal unlikely; fish passage installed",
    23: "Duplicate fish passage project structure",
    24: "Treatment completed (removal vs fishway unspecified)",
    25: "Treatment planned",
}

# Created here to capture values below
FEASIBILITY_DOMAIN = {
    -1: "Not applicable (road-related barrier)",
    0: "Not assessed",
    1: "Not feasible",
    2: "Likely infeasible",
    3: "Possibly feasible",
    4: "Likely feasible",
    5: "No conservation benefit",
    11: "Fish passage installed",  # code no longer used
    12: "Removal planned",  # code no longer used; superseded by 16
    13: "Breached with full flow",
    14: "Fish passage installed for conservation benefit",
    15: "Treatment complete (removal vs fishway unspecified)",
    16: "Removal or fish passage planned",
    # not shown to user (filtered out for other reasons)
    6: "Unknown",
    7: "Error",
    8: "Dam removed for conservation benefit",
    9: "Invasive species barrier",
    10: "Proposed dam",  # code no longer used
}


PURPOSE_DOMAIN = {
    -1: "Not applicable (road-related barrier)",
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
    -1: "Not applicable  (road-related barrier)",
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

CONDITION_DOMAIN = {
    0: "Unknown",
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
    0: "Not applicable (road-related barrier)",
    1: "Unknown",
    2: "< 5",
    3: "5 - 10",
    4: "10 - 25",
    5: "25 - 50",
    6: "50 - 100",
    7: ">= 100",
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

DOWNSTREAM_OCEAN_MILES_DOMAIN = {
    0: "not on aquatic network known to flow into the ocean",
    1: "< 1 miles",
    2: "1 - 5 miles",
    3: "5 - 10 miles",
    4: "10 - 25 miles",
    5: "25 - 100 miles",
    6: "100 - 250 miles",
    7: "250 - 500 miles",
    8: "500 - 1,000 miles",
    9: ">= 1,000 miles",
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

# NOTE: barrier count depends on network type
DOWNSTREAM_OCEAN_BARRIERS_DOMAIN = {
    0: "not on aquatic network known to flow into the ocean",
    1: "0",
    2: "1",
    3: "2-4",
    4: "5-9",
    5: ">= 10",
}


WATERBODY_SIZECLASS_DOMAIN = {
    0: "Not associated with a pond or lake",
    1: "Pond (< 0.01 km2)",
    2: "Very small lake (0.01 - 0.09 km2)",
    3: "Small lake (0.1 - 0.9 km2)",
    4: "Medium lake (1 - 9.9 km2)",
    5: "Large lake (>= 10 km2)",
}


CROSSING_TYPE_DOMAIN = {
    -1: "Not applicable (dam)",
    0: "Unknown",
    1: "Inaccessible",
    2: "No crossing",
    3: "No upstream habitat",
    4: "Not a barrier",
    5: "Bridge",
    6: "Ford / low water crossing",
    7: "Natural ford",
    8: "Culvert",
    9: "Assumed culvert",
    10: "Tide gate",
    11: "Buried stream",
}

CONSTRICTION_DOMAIN = {
    -1: "Not applicable (dam)",
    0: "Unknown",
    1: "Spans full channel & banks",
    2: "Spans only bankfull/active channel",
    3: "Constricted to some degree",
    4: "Minor",
    5: "Moderate",
    6: "Severe",
}

DIVERSION_DOMAIN = {
    -1: "Not applicable (road-related barrier)",
    0: "Unknown",
    1: "Yes",
    2: "No",
}

# NOTE: values do not match original domain; they are recoded
LOWHEADDAM_DOMAIN = {
    -1: "Not applicable (road-related barrier)",
    0: "Unknown",
    1: "Yes",
    2: "Likely",
    3: "No",
}

FISHSCREEN_DOMAIN = {
    -1: "Not applicable (road-related barrier)",
    0: "Unknown",
    1: "Yes",
    2: "No",
}

SCREENTYPE_DOMAIN = {
    -1: "Not applicable (road-related barrier)",
    0: "Unknown",
    1: "Horizontal",
    2: "Vertical",
    3: "Cone",
    4: "Pipe",
    5: "Drum",
    6: "Other",
}


BARRIER_SEVERITY_DOMAIN = {
    -1: "Not applicable (dam)",
    0: "Unknown",
    1: "Complete barrier",
    2: "Moderate barrier",
    3: "Indeterminate barrier",
    4: "Minor barrier",
    5: "Likely barrier",
    6: "Barrier - unknown severity",
    7: "No barrier",
    8: "No upstream habitat",
}

PASSABILITY_DOMAIN = {
    0: "Unknown",
    1: "Complete barrier",
    2: "Partial passability",
    3: "Partial passability - non salmonid",
    4: "Partial passability - salmonid",
    5: "Seasonably passable - non salmonid",
    6: "Seasonably passable - salmonid",
    7: "No barrier",
}

FERCREGULATED_DOMAIN = {
    -1: "Not applicable",  # small barriers only
    0: "Unknown",
    1: "Yes",
    2: "Preliminary permit",
    3: "Pending permit",
    4: "Exemption",
    5: "No",
}

STATE_REGULATED_DOMAIN = {
    -1: "Not applicable",  # small barriers only
    0: "Unknown",
    1: "Yes",
    2: "No",
}


HAZARD_DOMAIN = {0: "Unknown", 1: "High", 2: "Significant", 3: "Intermediate", 4: "Low"}


ROAD_TYPE_DOMAIN = {
    -1: "Not applicable (dam)",
    0: "Unknown",
    1: "Unpaved",
    2: "Paved",
    3: "Railroad",
}


OWNERTYPE_DOMAIN = {
    0: "",  # most likely private land, but just don't say anything
    1: "Bureau of Land Management",
    2: "Bureau of Reclamation",
    3: "Department of Defense",
    4: "National Park Service",
    5: "US Fish and Wildlife Service land",
    6: "USDA Forest Service land",
    7: "Other Federal land",
    8: "State land",
    9: "Joint Ownership or Regional land",
    10: "Native American land",
    11: "Private easement",
    12: "Other private conservation land",
}


BARRIEROWNERTYPE_DOMAIN = {
    0: "Unknown / private",
    1: "USDA Forest Service",
    2: "Federal",
    3: "State",
    4: "Local government",
    5: "Public utility",
    6: "Tribal",
}


BOOLEAN_DOMAIN = {False: "no", True: "yes"}


PASSAGEFACILITY_CLASS_DOMAIN = {
    0: "No known fish passage structure",
    1: "Fish passage structure present",
}

PASSAGEFACILITY_DOMAIN = {
    0: "Unknown or none",
    1: "Trap & truck",
    2: "Fish ladder - unspecified",
    3: "Locking",
    4: "Rock rapids",
    5: "Eelway",
    6: "Alaskan steeppass",
    7: "Herring passage",
    8: "Reservation",
    9: "Exemption",
    10: "Notch",
    11: "Denil fishway",
    12: "Fish lift",
    13: "Partial breach",
    14: "Removal",
    15: "Pool and weir fishway",
    16: "Vertical slot fishway",
    17: "Nature-like fishway",
    18: "Bypass channel fishway",
    19: "Crossvane",
    20: "Screen bypass",
    21: "Fishway unspecified",
    22: "Roughened channel",
    23: "Hybrid / multiple",
    24: "None (confirmed)",
}

MANUALREVIEW_DOMAIN = {
    0: "",
    1: "",
    2: "NABD Dams",
    4: "Onstream checked by SARP",
    5: "Offstream checked by SARP - do not snap",
    6: "Delete - Error, checked by SARP",
    7: "Assumed offstream, >100 meters from flowline",
    8: "Removed for conservation",
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
    5: "Pipeline / underground connector",
}

BOOLEAN_OFFNETWORK_DOMAIN = {-1: "off network", 0: "no", 1: "yes"}

TROUT_DOMAIN = {0: "not recorded", 1: "yes"}


# symbol domain - not used but included here as a reference for the codes used
# SYMBOL_DOMAIN = {
#     0: "regular barrier",
#     1: "unsnapped",
#     2: "assessed and not a barrier (fully passable)",
#     3: "invasive barrier",
#     4: "no-structure diversion",
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
    "BarrierType": BARRIERTYPE_DOMAIN,
    "State": STATES,
    "HasNetwork": BOOLEAN_DOMAIN,
    "OnLoop": BOOLEAN_DOMAIN,
    "Excluded": BOOLEAN_DOMAIN,
    "Ranked": BOOLEAN_DOMAIN,
    "Invasive": BOOLEAN_DOMAIN,
    "Intermittent": BOOLEAN_OFFNETWORK_DOMAIN,
    "FlowsToOcean": BOOLEAN_OFFNETWORK_DOMAIN,
    "FlowsToGreatLakes": BOOLEAN_OFFNETWORK_DOMAIN,
    "ExitsRegion": BOOLEAN_OFFNETWORK_DOMAIN,
    "OwnerType": OWNERTYPE_DOMAIN,
    "BarrierOwnerType": BARRIEROWNERTYPE_DOMAIN,
    "ProtectedLand": BOOLEAN_DOMAIN,
    "ManualReview": MANUALREVIEW_DOMAIN,
    "Recon": RECON_DOMAIN,
    "Condition": CONDITION_DOMAIN,
    "Trout": TROUT_DOMAIN,
    "Removed": BOOLEAN_DOMAIN,
    "EJTract": BOOLEAN_DOMAIN,
    "EJTribal": BOOLEAN_DOMAIN,
    # dam fields
    # note Recon domain is just used for internal exports; excluded from public exports
    "FERCRegulated": FERCREGULATED_DOMAIN,
    "StateRegulated": STATE_REGULATED_DOMAIN,
    "Construction": CONSTRUCTION_DOMAIN,
    "Purpose": PURPOSE_DOMAIN,
    "Feasibility": FEASIBILITY_DOMAIN,
    "Passability": PASSABILITY_DOMAIN,
    "PassageFacility": PASSAGEFACILITY_DOMAIN,
    "Diversion": DIVERSION_DOMAIN,
    "LowheadDam": LOWHEADDAM_DOMAIN,
    "FishScreen": FISHSCREEN_DOMAIN,
    "ScreenType": SCREENTYPE_DOMAIN,
    "WaterbodySizeClass": WATERBODY_SIZECLASS_DOMAIN,
    "Estimated": BOOLEAN_DOMAIN,
    # "NoStructure": BOOLEAN_DOMAIN,
    # barrier fields
    "BarrierSeverity": BARRIER_SEVERITY_DOMAIN,
    "Constriction": CONSTRICTION_DOMAIN,
    "CrossingType": CROSSING_TYPE_DOMAIN,
    "RoadType": ROAD_TYPE_DOMAIN,
}


# Lookup of field to description, for download / APIs
# Note: replace {type} with appropriate type when rendering
FIELD_DEFINITIONS = {
    # general fields
    "BarrierType": "Type of barrier",
    "lat": "Latitude in WGS84 geographic coordinates.",
    "lon": "Longitude in WGS84 geographic coordinates.",
    "Name": "{type} name, if available.",
    "SARPID": "SARP Identifier.",
    # dam-specific fields
    "NIDID": "National Inventory of Dams Identifier.",
    "Source": "Source of this record in the inventory.",
    "Link": "Link to additional information about this {type}",
    "FERCRegulated": "Identifies if the {type} is regulated at the federal level by the Federal Energy Regulatory Commission, if known.",
    "StateRegulated": "Identifies if the {type} is regulated at the state level, if known.",
    "Estimated": "Dam represents an estimated dam location based on NHD high resolution waterbodies or other information.",
    # "NoStructure": "this location is a water diversion without an associated barrier structure and is not ranked",
    "River": "River name where {type} occurs, if available.",
    "YearCompleted": "year that construction was completed, if available.  0 = data not available.",
    "Removed": "Identifies if the {type} has been removed for conservation, if known.  Removed barriers will not have values present for all fields.",
    "YearRemoved": "year that barrier was removed, if available.  All barriers removed prior to 2000 or where YearRemoved is unknown were lumped together for the network analysis.  0 = data not available or not removed.",
    "Height": "{type} height in feet, if available.  0 = data not available.",
    "Length": "{type} length in feet, if available.  0 = data not available.",
    "Width": "{type} width in feet, if available.  0 = data not available.",
    "Construction": "material used in {type} construction, if known.",
    "Purpose": "primary purpose of {type}, if known.",
    "PassageFacility": "type of fish passage facility, if known.",
    "FishScreen": "Whether or not a fish screen is present, if known.",
    "ScreenType": "Type of fish screen, if known.",
    "Feasibility": "feasibility of {type} removal, based on reconnaissance.  Note: reconnaissance information is available only for a small number of {type}s.",
    "Diversion": "Identifies if dam is known to be a diversion.  Note: diversion information is available only for a small number of dams.",
    "LowheadDam": "Identifies if dam is known or estimated to be a lowhead dam.  Note: lowhead dam information is available only for a small number of dams.",
    "WaterbodyKM2": "area of associated waterbody in square kilometers.  -1 = no associated waterbody",
    "WaterbodySizeClass": "size class of associated waterbody.  -1 = no associated waterbody",
    # barrier-specific fields
    "LocalID": "local identifier.",
    "CrossingCode": "crossing identifier.",
    "Stream": "stream or river name where this {type} occurs, if available.",
    "Road": "road name, if available.",
    "RoadType": "type of road, if available.",
    "CrossingType": "type of road / stream crossing, if known.",
    "Constriction": "type of constriction at road / stream crossing, if known.",
    "PotentialProject": "reconnaissance information about the crossing, including severity of the barrier and / or potential for removal project.",
    "BarrierSeverity": "barrier severity of the {type}, if known.   Note: assessment dates are not known.",
    "SARP_Score": "The best way to consider the aquatic passability scores is that they represent the degree to which crossings deviate from an ideal crossing. We assume that those crossings that are very close to the ideal (scores > 0.6) will present only a minor or insignificant barrier to aquatic organisms. Those structures that are farthest from the ideal (scores < 0.4) are likely to be either significant or severe barriers. These are, however, arbitrary distinctions imposed on a continuous scoring system and should be used with that in mind. -1 = not available.",
    # other general fields
    "Passability": "passability of the {type}, if known.   Note: assessment dates are not known.",
    "Condition": "Condition of the {type} as of last assessment, if known. Note: assessment dates are not known.",
    "NHDPlusID": "Unique NHD Plus High Resolution flowline identifier to which this {type} is snapped.  -1 = not snapped to a flowline.  Note: not all barriers snapped to flowlines are used in the network connectivity analysis.",
    "StreamSizeClass": "Stream size class based on total catchment drainage area in square kilometers.  1a: <10 km2, 1b: 10-100 km2, 2: 100-518 km2, 3a: 518-2,590 km2, 3b: 2,590-10,000 km2, 4: 10,000-25,000 km2, 5: >= 25,000 km2.",
    "TotDASqKm": "Total drainage area at the downstream end of the NHD Plus High Resolution flowline to which this {type} has been snapped, in square kilometers.  -1 if not snapped to flowline or otherwise not available",
    "AnnualFlow": "Annual flow at the downstream end of the NHD Plus High Resolution flowline to which this {type} has been snapped, in square cubic feet per second.  -1 if not snapped to flowline or otherwise not available",
    "AnnualVelocity": "Annual velocity at the downstream end of the NHD Plus High Resolution flowline to which this {type} has been snapped, in square feet per second.  -1 if not snapped to flowline or otherwise not available",
    "TESpp": "Number of federally-listed threatened or endangered aquatic species, compiled from element occurrence data within the same subwatershed (HUC12) as the {type}. Note: rare species information is based on occurrences within the same subwatershed as the barrier.  These species may or may not be impacted by this {type}.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.",
    "StateSGCNSpp": "Number of state-listed Species of Greatest Conservation Need (SGCN), compiled from element occurrence data within the same subwatershed (HUC12) as the {type}.  Note: rare species information is based on occurrences within the same subwatershed as the {type}.  These species may or may not be impacted by this {type}.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.",
    "RegionalSGCNSpp": "Number of regionally-listed Species of Greatest Conservation Need (SGCN), compiled from element occurrence data within the same subwatershed (HUC12) as the {type}.  Note: rare species information is based on occurrences within the same subwatershed as the {type}.  These species may or may not be impacted by this {type}.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.",
    "Trout": "Identifies if one or more interior or eastern native trout species (Apache, brook, bull, cutthroat, Gila, lake, and redband) are present within the same subwatershed (HUC12) as the {type} based on in available natural heritage data.  Note: absence means that occurrences were not present in the available natural heritage data and should not be interpreted as true absences.",
    "OwnerType": "Land ownership type. This information is derived from the BLM Surface Management Agency dataset for federal lands and CBI Protected Areas Database and TNC Secured Lands Database for non-federal lands, to highlight ownership types of particular importance to partners.  NOTE: does not include most private land.",
    "BarrierOwnerType": "Barrier ownership type, if available.",
    "ProtectedLand": "Indicates if the {type} occurs on public land as represented within the BLM Surface Management Agency dataset, CBI Protected Areas Database of the U.S., or TNC Secured Lands Database.",
    "EJTract": "Within an overburdened and underserved Census tracts a defined by the Climate and Environmental Justice Screening tool.",
    "EJTribal": "Within a disadvantaged tribal community as defined by the Climate and Environmental Justice Screening tool based on American Indian and Alaska Native areas as defined by the US Census Bureau.  Note: all tribal communities considered disadvantaged by the Climate and Environmental Justice Screening tool.",
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
    "AlteredUpstreamMiles": "number of altered miles in the upstream river network from this {type}, including miles in waterbodies.  Altered reaches are those specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration). -1 = not available.",
    "UnalteredUpstreamMiles": "number of unaltered miles in the upstream river network from this {type}, including miles in waterbodies.  Unaltered miles exclude reaches specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration). -1 = not available.",
    "PerennialUnalteredUpstreamMiles": "number of unaltered perennial miles in the upstream river network from this {type}, including miles in waterbodies.  Unaltered miles exclude reaches specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration). -1 = not available.",
    "PercentUnaltered": "percent of the total upstream river network length from this {type} that is not specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration).  -1 = not available.",
    "PercentPerennialUnaltered": "percent of the perennial upstream river network length from this {type} that is not specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration).  See PerennialUpstreamMiles.  -1 = not available.",
    "TotalDownstreamMiles": "number of miles in the complete downstream river network from this {type}, including miles in waterbodies.  Note: this measures the length of the complete downstream network including all tributaries, and is not limited to the shortest downstream path.  -1 = not available.",
    "FreeDownstreamMiles": "number of free-flowing miles in the downstream river network (TotalDownstreamMiles minus miles in waterbodies). -1 = not available.",
    "FreePerennialDownstreamMiles": "number of free-flowing perennial miles in the downstream river network.  Excludes miles in waterbodies.  See PerennialUpstreamMiles. -1 = not available.",
    "FreeIntermittentDownstreamMiles": "number of free-flowing ephemeral and intermittent miles in the downstream river network.  Excludes miles in waterbodies.  See IntermittentUpstreamMiles. -1 = not available.",
    "FreeAlteredDownstreamMiles": "number of free-flowing altered miles in the downstream river network from this {type}.  Excludes miles in waterbodies or reaches specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch or other channel alteration). -1 = not available.",
    "FreeUnalteredDownstreamMiles": "number of free-flowing altered miles in the downstream river network from this {type}.  Limited to reaches specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch or other channel alteration).  Excludes miles in waterbodies. -1 = not available.",
    "GainMiles": "absolute number of miles that could be gained by removal of this {type}.  Calculated as the minimum of the TotalUpstreamMiles and FreeDownstreamMiles. For removed barriers, this is based on the barriers present at the time this barrier was removed.  -1 = not available.",
    "PerennialGainMiles": "absolute number of perennial miles that could be gained by removal of this {type}.  Calculated as the minimum of the PerennialUpstreamMiles and FreePerennialDownstreamMiles.  For removed barriers, this is based on the barriers present at the time this barrier was removed.  -1 = not available.",
    "TotalNetworkMiles": "sum of TotalUpstreamMiles and FreeDownstreamMiles. -1 = not available.",
    "TotalPerennialNetworkMiles": "sum of PerennialUpstreamMiles and FreePerennialDownstreamMiles. -1 = not available.",
    "UpstreamDrainageArea": "approximate drainage area of all NHD High Resolution catchments within upstream functional network of {type}.  Includes the total catchment area of any NHD High Resolution flowlines that are cut by barriers in the analysis, which may overrepresent total drainage area of the network. -1 = not available.",
    "UpstreamWaterfalls": "number of waterfalls at the upstream ends of the functional network for this {type}. -1 = not available.",
    "UpstreamDams": "number of dams at the upstream ends of the functional network for this {type}.",
    "UpstreamSmallBarriers": "number of assessed road-related barriers within the functional network if this barrier is a dam or at the upstream ends of the functional network if this barrier is a road-related barrier. -1 = not available.",
    "UpstreamRoadCrossings": "number of uninventoried estimated road crossings within the functional network for this {type}. -1 = not available.",
    "UpstreamHeadwaters": "number of headwaters within the functional network for this {type}. -1 = not available.",
    "TotalUpstreamWaterfalls": "total number of waterfalls upstream of this {type}; includes in all functional networks above this {type}. -1 = not available.",
    "TotalUpstreamDams": "total number of dams upstream of this {type}; includes in all functional networks above this {type}. -1 = not available.",
    "TotalUpstreamSmallBarriers": "total number of assessed road-related barriers upstream of this {type}; includes in all functional networks above this {type}. -1 = not available.",
    "TotalUpstreamRoadCrossings": "total number of uninventroeid estimated road crossings upstream of this {type}; includes in all functional networks above this {type}. -1 = not available.",
    "TotalUpstreamHeadwaters": "total number of headwaters upstream of this {type}; includes in all functional networks above this {type}. -1 = not available.",
    "TotalDownstreamWaterfalls": "total number of waterfalls between this {type} and the downstream-most point the full aquatic network on which it occurs. -1 = not available.",
    "TotalDownstreamDams": "total number of dams between this {type} and the downstream-most point the full aquatic network on which it occurs (e.g., river mouth). -1 = not available.",
    "TotalDownstreamSmallBarriers": "total number of assessed road-related barriers between this {type} and the downstream-most point the full aquatic network on which it occurs. -1 = not available.",
    "TotalDownstreamRoadCrossings": "total number of uninventoried estimated road crossings between this {type} and the downstream-most point the full aquatic network on which it occurs. -1 = not available.",
    "MilesToOutlet": "miles between this {type} and the downstream-most point on the full aquatic network on which it occurs. -1 = not available.",
    "FlowsToOcean": "indicates if this {type} was snapped to a stream or river that is known to flow into the ocean.  Note: this underrepresents any networks that traverse regions outside the analysis region that would ultimately connect the networks to the ocean.",
    "FlowsToGreatLakes": "indicates if this {type} was snapped to a stream or river that is known to flow into the Great Lakes.  Note: this underrepresents any networks that traverse regions outside the analysis region that would ultimately connect the networks to the Great Lakes.",
    # "ExitsRegion": "indicates this {type} was snapped to a stream or river that exits the region of analysis (e.g., flows into Canada or Mexico) or flows into the ocean.",
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
COMBINED_FIELD_DEFINITIONS = {
    k: v.replace("{type}", "dam or road-related barrier")
    for k, v in FIELD_DEFINITIONS.items()
}
RC_FIELD_DEFINITIONS = {
    k: v.replace("{type}", "potential road-related barrier")
    for k, v in FIELD_DEFINITIONS.items()
}


### Domains not currently used

# Not used directly
# BARRIERSTATUS_DOMAIN = {
#     -1: "Not applicable",
#     0: "Unknown",
#     1: "Impounding",
#     2: "Full breach",
#     3: "Partial breach",
#     4: "Drained",
#     5: "Dry detention",
#     6: "Functions limited"
# }


### Not exported
# IMPOUNDMENTTYPE_DOMAIN = {1: "Run of river", 2: "Lake-like", 3: "Large reservoir"}


# STRUCTURECATEGORY_DOMAIN = {
#     -1: "Not applicable",
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
#     10: "Channel",
#     11: "Gravel/borrow pits",
#     12: "Utility crossing"
# }


# NOTE: structureclass is original name and not used as a class for filtering
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
