"""
Dictionaries of domain values to labels.

Mostly created using extract_domains.py

"""

# Mussel_Presence
# Note: this used to apply to ProtectedLand, but it is actually 0 (no intersection) and 1 (intersected)
YES_NO_DOMAIN = {0: "Unknown", 1: "Yes", 2: "No"}

# Off_Network
OFF_NETWORK_DOMAIN = {0: "On Network", 1: "Off Network"}


STATE_DOMAIN = {
    1: "Tennessee",
    2: "North Carolina",
    3: "Kentucky",
    4: "Alabama",
    5: "Virginia",
    6: "Georgia",
    7: "Mississippi",
    8: "Florida",
    12: "South Carolina",
    13: "Arkansas",
    14: "Louisiana",
    15: "Missouri",
    16: "Oklahoma",
    17: "Texas",
}

# Extracted from CENSUS TIGER dataset
# gp.read_file('data/src/tl_2018_us_state/tl_2018_us_state.shp')[['STATEFP', 'NAME']].set_index('STATEFP').NAME.to_dict()
STATE_FIPS_DOMAIN = {
    "54": "West Virginia",
    "12": "Florida",
    "17": "Illinois",
    "27": "Minnesota",
    "24": "Maryland",
    "44": "Rhode Island",
    "16": "Idaho",
    "33": "New Hampshire",
    "37": "North Carolina",
    "50": "Vermont",
    "09": "Connecticut",
    "10": "Delaware",
    "35": "New Mexico",
    "06": "California",
    "34": "New Jersey",
    "55": "Wisconsin",
    "41": "Oregon",
    "31": "Nebraska",
    "42": "Pennsylvania",
    "53": "Washington",
    "22": "Louisiana",
    "13": "Georgia",
    "01": "Alabama",
    "49": "Utah",
    "39": "Ohio",
    "48": "Texas",
    "08": "Colorado",
    "45": "South Carolina",
    "40": "Oklahoma",
    "47": "Tennessee",
    "56": "Wyoming",
    "15": "Hawaii",
    "38": "North Dakota",
    "21": "Kentucky",
    "78": "United States Virgin Islands",
    "69": "Commonwealth of the Northern Mariana Islands",
    "66": "Guam",
    "23": "Maine",
    "36": "New York",
    "32": "Nevada",
    "02": "Alaska",
    "60": "American Samoa",
    "26": "Michigan",
    "05": "Arkansas",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "20": "Kansas",
    "18": "Indiana",
    "72": "Puerto Rico",
    "46": "South Dakota",
    "25": "Massachusetts",
    "51": "Virginia",
    "11": "District of Columbia",
    "19": "Iowa",
    "04": "Arizona",
}

# typos fixed and trailing periods removed
RECON_DOMAIN = {
    0: "Not yet evaluated",  # added
    2: "Dam needs follow-up with landowner",
    3: "Removal is unlikely.  Social conditions unfavorable",
    4: "Removal is extremely infeasible.  Large reservoirs, etc.",
    5: "Dam may be removed or error",
    7: "Dam was deliberately removed",
    8: "Dam location is incorrect and needs to be moved",  # fixed phrasing
    9: "Dam is breached and no impoundment visible",
    10: "Dam was once considered, need to revisit",
    11: "Removal planned",
    13: "Unsure, need second opinion",
    1: "Good candidate for removal. Move forward with landowner contact",  # expanded acronym
    14: "Take immediate action, abandoned-looking dam in poor condition",
    15: "No conservation benefit",
    16: "Invasive species barrier",
    6: "Infeasible in short term via landowner contact",
    18: "Dam failed",
    19: "Proposed dam",
    17: "Risky for mussels",
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

CONDITION_DOMAIN = {
    0: "Not Rated",
    1: "Satisfactory",
    2: "Fair",
    3: "Poor",
    4: "Unsatisfactory",
}

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
