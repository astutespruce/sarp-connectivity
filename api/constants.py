from enum import Enum

### Enums for validating incoming request values
class BarrierTypes(str, Enum):
    dams = "dams"
    barriers = "barriers"


class Layers(str, Enum):
    HUC6 = "HUC6"
    HUC8 = "HUC8"
    HUC12 = "HUC12"
    State = "State"
    County = "County"
    ECO3 = "ECO3"
    ECO4 = "ECO4"


class Formats(str, Enum):
    csv = "csv"


class Scenarios(str, Enum):
    NC = "NC"
    WC = "WC"
    NCWC = "NCWC"


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
UNIT_FIELDS = ["HUC6", "HUC8", "HUC12", "State", "County", "ECO3", "ECO4"]

# metric fields that are only valid for barriers with networks
METRIC_FIELDS = [
    "StreamOrder",
    "Landcover",
    "Sinuosity",
    "SizeClasses",
    "TotalUpstreamMiles",
    "TotalDownstreamMiles",
    "FreeUpstreamMiles",
    "FreeDownstreamMiles",
    "GainMiles",
    "TotalNetworkMiles",
]

TIER_FIELDS = [
    "SE_NC_tier",
    "SE_WC_tier",
    "SE_NCWC_tier",
    "State_NC_tier",
    "State_WC_tier",
    "State_NCWC_tier",
]

# Only present when custom prioritization is performed
CUSTOM_TIER_FIELDS = ["NC_tier", "WC_tier", "NCWC_tier"]


FILTER_FIELDS = [
    "SizeClasses",
    "GainMilesClass",
    "TESppClass",
    "StateSGCNSppClass",
    "RegionalSGCNSppClass",
    "StreamOrderClass",
    "OwnerType",
    "HUC8_USFS",
    "HUC8_COA",
    "HUC8_SGCN",
]

DAM_FILTER_FIELDS = [
    "Feasibility",
    "Construction",
    "Purpose",
    "Condition",
    "HeightClass",
    "PassageFacilityClass",
] + FILTER_FIELDS
DAM_FILTER_FIELD_MAP = {f.lower(): f for f in DAM_FILTER_FIELDS}

SB_FILTER_FIELDS = [
    "ConditionClass",
    "CrossingTypeClass",
    "RoadTypeClass",
    "SeverityClass",
] + FILTER_FIELDS
SB_FILTER_FIELD_MAP = {f.lower(): f for f in SB_FILTER_FIELDS}


### Fields used for export
DAM_CORE_FIELDS = [
    "lat",
    "lon",
    "Name",
    "SARPID",
    "NIDID",
    "Source",
    "River",
    "Year",
    "Height",
    "Construction",
    "Purpose",
    "Condition",
    "PassageFacility",
    # Recon is intentionally omitted from download below
    "Recon",
    "Feasibility",
    "TESpp",
    "StateSGCNSpp",
    "RegionalSGCNSpp",
    "OwnerType",
    "ProtectedLand",
    # Priority watersheds
    "HUC8_USFS",
    "HUC8_COA",
    "HUC8_SGCN",
    "Basin",
]

DAM_API_FIELDS = (
    DAM_CORE_FIELDS
    + UNIT_FIELDS
    + ["HasNetwork", "Excluded"]
    + METRIC_FIELDS
    + TIER_FIELDS
    + DAM_FILTER_FIELDS
    + ["COUNTYFIPS"]
)

# reduce to unique list, since there are overlaps with filters and core fields
DAM_API_FIELDS = unique(DAM_API_FIELDS)

DAM_EXPORT_FIELDS = (
    DAM_CORE_FIELDS
    + UNIT_FIELDS
    + ["HasNetwork", "Excluded"]
    + METRIC_FIELDS
    + TIER_FIELDS
    + CUSTOM_TIER_FIELDS
)
# remove recon
DAM_EXPORT_FIELDS.remove("Recon")

DAM_EXPORT_FIELDS = unique(DAM_EXPORT_FIELDS)


SB_CORE_FIELDS = [
    "lat",
    "lon",
    "Name",
    "SARPID",
    "LocalID",
    "CrossingCode",
    "Source",
    "Stream",
    "Road",
    "RoadType",
    "CrossingType",
    "Condition",
    "PotentialProject",
    "SeverityClass",
    "TESpp",
    "StateSGCNSpp",
    "RegionalSGCNSpp",
    "OwnerType",
    "ProtectedLand",
    # Priority watersheds
    "HUC8_USFS",
    "HUC8_COA",
    "HUC8_SGCN",
    "Basin",
]

SB_API_FIELDS = (
    SB_CORE_FIELDS
    + UNIT_FIELDS
    + ["HasNetwork", "Excluded"]
    + METRIC_FIELDS
    + TIER_FIELDS
    + SB_FILTER_FIELDS
    + ["COUNTYFIPS"]
)

SB_API_FIELDS = unique(SB_API_FIELDS)

SB_EXPORT_FIELDS = (
    SB_CORE_FIELDS
    + UNIT_FIELDS
    + ["HasNetwork", "Excluded"]
    + METRIC_FIELDS
    + TIER_FIELDS
    + CUSTOM_TIER_FIELDS
)

SB_EXPORT_FIELDS = unique(SB_EXPORT_FIELDS)

WF_CORE_FIELDS = ["lat", "lon", "Name"]


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
    # not shown to user
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

SINUOSITY_DOMAIN = {
    # -1: "no network", # filter this out
    0: "low",  # <1.2
    1: "moderate",  # 1.2 - 1.5
    2: "high",  # > 1.5
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


# mapping of field name to domains
DOMAINS = {
    "HasNetwork": BOOLEAN_DOMAIN,
    "Excluded": BOOLEAN_DOMAIN,
    "OwnerType": OWNERTYPE_DOMAIN,
    "ProtectedLand": BOOLEAN_DOMAIN,
    "HUC8_USFS": HUC8_USFS_DOMAIN,
    "HUC8_COA": HUC8_COA_DOMAIN,
    "HUC8_SGCN": HUC8_SGCN_DOMAIN,
    # dam fields
    "Condition": DAM_CONDITION_DOMAIN,
    "Construction": CONSTRUCTION_DOMAIN,
    "Purpose": PURPOSE_DOMAIN,
    "Feasibility": FEASIBILITY_DOMAIN,
    "PassageFacility": PASSAGEFACILITY_DOMAIN,
    # barrier fields
    "SeverityClass": BARRIER_SEVERITY_DOMAIN,
}


def unpack_domains(df):
    """Unpack domain codes to values.

    Parameters
    ----------
    df : DataFrame
    """
    df = df.copy()
    for field, domain in DOMAINS.items():
        if field in df.columns:
            df[field] = df[field].map(domain)

    return df