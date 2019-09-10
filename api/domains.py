"""
Dictionaries of domain values to labels.  Domain values are assigned in ArcGIS prior to processing, or assigned during
various prep scripts.
"""

# Mussel_Presence
# Note: this used to apply to ProtectedLand, but it is actually 0 (no intersection) and 1 (intersected)
YES_NO_DOMAIN = {0: "Unknown", 1: "Yes", 2: "No"}

# Off_Network
OFF_NETWORK_DOMAIN = {0: "On Network", 1: "Off Network"}

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
}

# Created here to capture values below
FEASIBILITY_DOMAIN = {
    # -1: "N/A",  # These are filtered out in preprocessing - not barriers
    0: "Unknown",
    1: "Not feasible",
    2: "Likely infeasible",
    3: "Possibly feasible",
    4: "Likely feasible",
    5: "No conservation benefit",
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
    0: "Unknown",
    1: "Federal",
    2: "State",
    3: "Regional / Local",
    4: "Native American Land",
    5: "Private",
}

