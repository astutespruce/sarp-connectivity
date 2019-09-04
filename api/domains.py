"""
Dictionaries of domain values to labels.

Mostly created using extract_domains.py

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

# in constants.py
# Applies to Recon values, omitted values should be filtered out
# RECON_TO_FEASIBILITY = {
#     0: 0,
#     1: 3,
#     2: 3,
#     3: 2,
#     4: 1,
#     5: 0,  # should be N/A
#     6: 2,
#     7: 0,  # should be N/A
#     8: 0,
#     9: 0,
#     10: 0,
#     11: 4,
#     13: 0,
#     14: 4,
#     15: 5,
#     16: 0,
#     17: 0,
#     18: 0,
#     19: 0,  # should be N/A
#     20: 5,
#     21: 0,
# }


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


# in constants.py
# POTENTIAL_TO_SEVERITY = {
#     "Inaccessible": 0,
#     "Indeterminate": 0,
#     "Insignificant Barrier": 1,
#     "Minor Barrier": 1,
#     "Moderate Barrier": 2,
#     "No Barrier": 1,  # removed from processing
#     "No Crossing": 1,
#     "No Upstream Channel": 1,
#     "No Upstream Habitat": 1,
#     "Not Scored": 0,
#     "No": 1,
#     "Past Project": 0,  # removed from processing
#     "Potential Project": 0,
#     "Proposed Project": 0,
#     "Severe Barrier": 3,
#     "Significant Barrier": 3,
#     "Small Project": 0,
#     "SRI Only": 0,
# }

CROSSING_TYPE_DOMAIN = {
    0: "Unknown",
    1: "Not a barrier",
    2: "Bridge",
    3: "Culvert",
    4: "Ford",
    5: "Dam",
    6: "Buried stream",
}

# in constants.py
# CROSSING_TYPE_TO_DOMAIN = {
#     "Bridge": 2,
#     "Bridge Adequate": 2,
#     "Buried Stream": 6,
#     "Culvert": 3,
#     "Dam": 5,
#     "Ford": 4,
#     "Inaccessible": 0,
#     "Multiple Culvert": 3,
#     "Multiple Culverts": 3,
#     "Natural Ford": 4,
#     "No Crossing": 1,
#     "No Upstream Channel": 1,
#     "Other": 0,
#     "Partially Inaccessible": 0,
#     "Removed Crossing": 1,
#     "Slab": 4,
#     "Unknown": 0,
#     "Vented Ford": 4,
#     "Vented Slab": 4,
# }


ROAD_TYPE_DOMAIN = {0: "Unknown", 1: "Unpaved", 2: "Paved", 3: "Railroad"}


# in constants.py
# ROAD_TYPE_TO_DOMAIN = {
#     "Asphalt": 2,
#     "Concrete": 2,
#     "Dirt": 1,
#     "Driveway": 0,
#     "Gravel": 1,
#     "Other": 0,
#     "Paved": 2,
#     "Railroad": 3,
#     "Trail": 1,
#     "Unknown": 0,
#     "Unpaved": 1,
#     "No Data": 0,
#     "Nodata": 0,
# }

BARRIER_CONDITION_DOMAIN = {0: "Unknown", 1: "Failing", 2: "Poor", 3: "OK", 4: "New"}

# in constants.py
# BARRIER_CONDITION_TO_DOMAIN = {"Failing": 1, "New": 4, "OK": 3, "Poor": 2, "Unknown": 0}


# for domain in ("ProtectedLand",):
#     df[domain] = df[domain].map({0: "Unknown", 1: "Yes", 2: "No"})

# domain = "Off_Network"
# df[domain] = df[domain].map()


######## To extract domains to dictionaries
# NOTE: a 0 value was added to all domains for "Unknown" or n/a if there wasn't already a 0 value

# import pandas as pd

# Domains were exported using the ArcGIS Domain to Table tool, with domain name as the key and "value" as the value column
# print("Joining in domains")
# for domain in (
#     "State",
#     "StructureCondition",
#     "ConstructionMaterial",
#     "PurposeCategory",
#     "Recon",
# ):
#     print("\n------{}-----\n".format(domain))
#     print(
#         pd.read_csv("data/src/{}_domain.csv".format(domain))
#         .set_index(domain)["value"]
#         .to_dict()
#     )
