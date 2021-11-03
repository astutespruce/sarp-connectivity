from enum import Enum

### Enums for validating incoming request values
class BarrierTypes(str, Enum):
    dams = "dams"
    small_barriers = "small_barriers"


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
UNIT_FIELDS = ["HUC6", "HUC8", "HUC12", "State", "County", "ECO3", "ECO4"]


# metric fields that are only valid for barriers with networks
METRIC_FIELDS = [
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
    "SE_NC_tier",
    "SE_WC_tier",
    "SE_NCWC_tier",
    "SE_PNC_tier",
    "SE_PWC_tier",
    "SE_PNCWC_tier",
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
    "StreamOrderClass",
    "PercentAlteredClass",
    "OwnerType",
    "Intermittent",
    "HUC8_COA",
    "HUC8_SGCN",
]

DAM_FILTER_FIELDS = [
    "Feasibility",
    "Purpose",
    "Condition",
    "HeightClass",
    "BarrierSeverity",
    "LowheadDam",
    "PassageFacilityClass",
    "WaterbodySizeClass",
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
    "Intermittent",
    "Year",
    "Height",
    "Width",
    "Construction",
    "Purpose",
    "Condition",
    "PassageFacility",
    "BarrierSeverity",
    "Diversion",
    "LowheadDam",
    "WaterbodyKM2",
    "WaterbodySizeClass",
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
    # Watershed names
    "Basin",
    "Subbasin",
    "Subwatershed",
]

DAM_API_FIELDS = (
    DAM_CORE_FIELDS
    + UNIT_FIELDS
    + [
        "HasNetwork",
        "Excluded",
        "Ranked",
        "FlowsToOcean",
        "NumBarriersDownstream",
        "upNetID",
        "downNetID",
    ]
    + METRIC_FIELDS
    + TIER_FIELDS
    + DAM_FILTER_FIELDS
    + ["COUNTYFIPS"]
)

# reduce to unique list, since there are overlaps with filters and core fields
DAM_API_FIELDS = unique(DAM_API_FIELDS)

# Drop fields that can be calculated on frontend
DAM_TILE_FIELDS = [
    c
    for c in DAM_API_FIELDS
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
    }
]


DAM_EXPORT_FIELDS = (
    DAM_CORE_FIELDS
    + UNIT_FIELDS
    + ["HasNetwork", "Excluded", "Ranked", "FlowsToOcean", "NumBarriersDownstream",]
    + METRIC_FIELDS
    + TIER_FIELDS
    + CUSTOM_TIER_FIELDS
)
# remove recon
DAM_EXPORT_FIELDS.remove("Recon")

DAM_EXPORT_FIELDS = unique(DAM_EXPORT_FIELDS)

DAM_PUBLIC_EXPORT_FIELDS = unique(
    DAM_CORE_FIELDS + UNIT_FIELDS + ["HasNetwork", "Excluded"] + METRIC_FIELDS
)

DAM_PUBLIC_EXPORT_FIELDS.remove("Recon")


SB_CORE_FIELDS = [
    "lat",
    "lon",
    "Name",
    "SARPID",
    "LocalID",
    "CrossingCode",
    "Source",
    "Stream",
    "Intermittent",
    "Road",
    "RoadType",
    "CrossingType",
    "Condition",
    "PotentialProject",
    "SeverityClass",
    "SARP_Score",
    "TESpp",
    "StateSGCNSpp",
    "RegionalSGCNSpp",
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

SB_API_FIELDS = (
    SB_CORE_FIELDS
    + UNIT_FIELDS
    + [
        "HasNetwork",
        "Excluded",
        "Ranked",
        "FlowsToOcean",
        "NumBarriersDownstream",
        "upNetID",
        "downNetID",
    ]
    + METRIC_FIELDS
    + TIER_FIELDS
    + SB_FILTER_FIELDS
    + ["COUNTYFIPS"]
)

SB_API_FIELDS = unique(SB_API_FIELDS)

# Drop fields from tiles that are calculated on frontend
SB_TILE_FIELDS = [
    c
    for c in SB_API_FIELDS
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
    }
]


SB_EXPORT_FIELDS = (
    SB_CORE_FIELDS
    + UNIT_FIELDS
    + ["HasNetwork", "Excluded", "Ranked", "FlowsToOcean", "NumBarriersDownstream",]
    + METRIC_FIELDS
    + TIER_FIELDS
    + CUSTOM_TIER_FIELDS
)

SB_EXPORT_FIELDS = unique(SB_EXPORT_FIELDS)
SB_PUBLIC_EXPORT_FIELDS = unique(
    SB_CORE_FIELDS + UNIT_FIELDS + ["HasNetwork", "Excluded"] + METRIC_FIELDS
)

WF_CORE_FIELDS = [
    "HUC8",
    "HUC12",
    "lat",
    "lon",
    "Name",
    "Source",
    "Stream",
    "FallType",
    "StreamOrder",
    "Intermittent",
    "Excluded",
    "TESpp",
    "StateSGCNSpp",
    "RegionalSGCNSpp",
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
    22: "Duplicate fish passage project structure",
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
    5: "Seasonbly Passable - Non Salmonid",
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
    20: "Estimated dam (based on name containing 'Estimated')",
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


# Not exported
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


# mapping of field name to domains
DOMAINS = {
    "HasNetwork": BOOLEAN_DOMAIN,
    "Excluded": BOOLEAN_DOMAIN,
    "Ranked": BOOLEAN_DOMAIN,
    "Intermittent": BOOLEAN_OFFNETWORK_DOMAIN,
    "FlowsToOcean": BOOLEAN_OFFNETWORK_DOMAIN,
    "OwnerType": OWNERTYPE_DOMAIN,
    "ProtectedLand": BOOLEAN_DOMAIN,
    "HUC8_USFS": HUC8_USFS_DOMAIN,
    "HUC8_COA": HUC8_COA_DOMAIN,
    "HUC8_SGCN": HUC8_SGCN_DOMAIN,
    "ManualReview": MANUALREVIEW_DOMAIN,
    # dam fields
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
    # barrier fields
    "SeverityClass": BARRIER_SEVERITY_DOMAIN,
    "ConditionClass": BARRIER_CONDITION_DOMAIN,
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
    "River": "River name where {type} occurs, if available.",
    "Year": "year that construction was completed, if available.  0 = data not available.",
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
    "PotentialProject": "reconnaissance information about the crossing, including severity of the barrier and / or potential for removal project.",
    "SeverityClass": "potential severity of barrier, based on reconnaissance.",
    "SARP_Score": "The best way to consider the aquatic passability scores is that they represent the degree to which crossings deviate from an ideal crossing. We assume that those crossings that are very close to the ideal (scores > 0.6) will present only a minor or insignificant barrier to aquatic organisms. Those structures that are farthest from the ideal (scores < 0.4) are likely to be either significant or severe barriers. These are, however, arbitrary distinctions imposed on a continuous scoring system and should be used with that in mind. -1 = not available.",
    # other general fields
    "Condition": "condition of the {type} as of last assessment, if known. Note: assessment dates are not known.",
    "TESpp": "number of federally-listed threatened or endangered aquatic species, compiled from element occurrence data within the same subwatershed (HUC12) as the {type}. Note: rare species information is based on occurrences within the same subwatershed as the barrier.  These species may or may not be impacted by this {type}.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.",
    "StateSGCNSpp": "Number of state-listed Species of Greatest Conservation Need (SGCN), compiled from element occurrence data within the same subwatershed (HUC12) as the {type}.  Note: rare species information is based on occurrences within the same subwatershed as the {type}.  These species may or may not be impacted by this {type}.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.",
    "RegionalSGCNSpp": "Number of regionally-listed Species of Greatest Conservation Need (SGCN), compiled from element occurrence data within the same subwatershed (HUC12) as the {type}.  Note: rare species information is based on occurrences within the same subwatershed as the {type}.  These species may or may not be impacted by this {type}.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.",
    "OwnerType": "Land ownership type. This information is derived from the CBI Protected Areas Database and TNC Secured Lands Database, to highlight ownership types of particular importance to partners.  NOTE: does not include most private land.",
    "ProtectedLand": "Indicates if the {type} occurs on public land as represented within the CBI Protected Areas Database of the U.S. and TNC Secured Lands Database.",
    "HUC8_USFS": "U.S. Forest Service (USFS) priority watersheds (HUC8 level) within USFS Southeast Region.",
    "HUC8_COA": "SARP conservation opportunity areas.",
    "HUC8_SGCN": "Top 10 watersheds per state based on number of Species of Greatest Conservation Need (SGCN).",
    "Basin": "Name of the hydrologic basin (HUC6) where the {type} occurs.",
    "Subbasin": "Name of the hydrologic subbasin (HUC8) where the {type} occurs.",
    "Subwatershed": "Name of the hydrologic subwatershed (HUC12) where the {type} occurs.",
    "HUC6": "Hydrologic basin identifier where the {type} occurs.",
    "HUC8": "Hydrologic subbasin identifier where the {type} occurs.",
    "HUC12": "Hydrologic subwatershed identifier where the {type} occurs.",
    "County": "County where {type} occurs.",
    "State": "State where {type} occurs.",
    "ECO3": "EPA Level 3 Ecoregion Identifier.",
    "ECO4": "EPA Level 4 Ecoregion Identifier.",
    "HasNetwork": "indicates if this {type} was snapped to the aquatic network for analysis.  1 = on network, 0 = off network.  Note: network metrics and scores are not available for {type}s that are off network.",
    "Excluded": "this {type} was excluded from the connectivity analysis based on field reconnaissance or manual review of aerial imagery.",
    "Ranked": "this {type} was included for prioritization.  Some barriers that are beneficial to restricting the movement of invasive species are excluded from ranking.",
    "StreamOrder": "NHDPlus Modified Strahler stream order. -1 = not available.",
    "Intermittent": "indicates if this {type} was snapped to a a stream or river reach coded by NHDPlusHR as an intermittent or ephemeral. -1 = not available.",
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
    "SE_NC_tier": "network connectivity tier for all on-network {type}s within hydrologic basins that fall completely or partly within the Southeastern US states.  Tier 1 represents the {type}s within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "SE_WC_tier": "watershed condition tier for all on-network {type}s within hydrologic basins that fall completely or partly within the Southeastern US states.  Tier 1 represents the {type}s within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "SE_NCWC_tier": "combined network connectivity and watershed condition tier for all on-network {type}s within hydrologic basins that fall completely or partly within the Southeastern US states.  Tier 1 represents the {type}s within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "SE_PNC_tier": "perennial network connectivity tier for all on-network {type}s within hydrologic basins that fall completely or partly within the Southeastern US states.  Tier 1 represents the {type}s within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "SE_PWC_tier": "perennial watershed condition tier for all on-network {type}s within hydrologic basins that fall completely or partly within the Southeastern US states.  Tier 1 represents the {type}s within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "SE_PNCWC_tier": "combined perennial network connectivity and watershed condition tier for all on-network {type}s within hydrologic basins that fall completely or partly within the Southeastern US states.  Tier 1 represents the {type}s within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
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
