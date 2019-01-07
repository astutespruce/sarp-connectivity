"""
Dictionaries of domain values to labels.

Mostly created using extract_domains.py

"""

# Mussel_Presence
# Note: this used to apply to ProtectedLand, but it is actually 0 (no intersection) and 1 (intersected)
YES_NO_DOMAIN = {0: "Unknown", 1: "Yes", 2: "No"}

# Off_Network
OFF_NETWORK_DOMAIN = {0: "On Network", 1: "Off Network"}


# Not used
# STATE_DOMAIN = {
#     1: "Tennessee",
#     2: "North Carolina",
#     3: "Kentucky",
#     4: "Alabama",
#     5: "Virginia",
#     6: "Georgia",
#     7: "Mississippi",
#     8: "Florida",
#     12: "South Carolina",
#     13: "Arkansas",
#     14: "Louisiana",
#     15: "Missouri",
#     16: "Oklahoma",
#     17: "Texas",
# }

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

# Just for SARP states
SARP_STATE_FIPS_DOMAIN = {
    "12": "Florida",
    "37": "North Carolina",
    "22": "Louisiana",
    "13": "Georgia",
    "01": "Alabama",
    "48": "Texas",
    "45": "South Carolina",
    "40": "Oklahoma",
    "47": "Tennessee",
    "21": "Kentucky",
    "05": "Arkansas",
    "28": "Mississippi",
    "29": "Missouri",
    "72": "Puerto Rico",
    "51": "Virginia",
}

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
    # -1: "N/A",  # Filter these out
    0: "Unknown",
    1: "Not feasible",
    2: "Likely infeasible",
    3: "Possibly feasible",
    4: "Likely feasible",
}

# Applies to Recon values, omitted values should be filtered out
RECON_TO_FEASIBILITY = {
    0: 0,
    1: 3,
    2: 3,
    3: 2,
    4: 1,
    5: 0,  # should be N/A
    6: 2,
    7: 0,  # should be N/A
    8: 0,
    9: 0,
    10: 0,
    11: 4,
    13: 0,
    14: 4,
    15: 0,
    16: 0,
    17: 0,
    18: 0,
    19: 0,  # should be N/A
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

# gp.read_file('data/src/HUC6.shp')[['HUC6', 'NAME']].set_index('HUC6').NAME.to_dict()
HUC6_DOMAIN = {
    "031502": "Alabama",
    "031401": "Florida Panhandle Coastal",
    "031501": "Coosa-Tallapoosa",
    "031601": "Black Warrior-Tombigbee",
    "031602": "Mobile Bay-Tombigbee",
    "060300": "Middle Tennessee-Elk",
    "080201": "Lower Mississippi-Helena",
    "080203": "Lower White",
    "080204": "Lower Arkansas",
    "080401": "Upper Ouachita",
    "111102": "Lower Arkansas-Fourche La Fave",
    "080202": "St. Francis",
    "110100": "Upper White",
    "080101": "Lower Mississippi-Memphis",
    "030801": "St. Johns",
    "030802": "East Florida Coastal",
    "030901": "Kissimmee",
    "030902": "Southern Florida",
    "031001": "Peace",
    "031002": "Tampa Bay",
    "031101": "Aucilla-Waccasassa",
    "031402": "Choctawhatchee",
    "031403": "Escambia",
    "030702": "St. Marys-Satilla",
    "031102": "Suwannee",
    "031200": "Ochlockonee",
    "031300": "Apalachicola",
    "030602": "Ogeechee",
    "030701": "Altamaha",
    "060200": "Middle Tennessee-Hiwassee",
    "071000": "Des Moines",
    "070801": "Upper Mississippi-Skunk-Wapsipinicon",
    "071100": "Upper Mississippi-Salt",
    "071401": "Upper Mississippi-Meramec",
    "102701": "Kansas",
    "051001": "Licking",
    "051002": "Kentucky",
    "051100": "Green",
    "051402": "Lower Ohio",
    "051401": "Lower Ohio-Salt",
    "050902": "Middle Ohio-Little Miami",
    "080403": "Lower Red",
    "080500": "Boeuf-Tensas",
    "080701": "Lower Mississippi-Baton Rouge",
    "080702": "Lake Maurepas",
    "080703": "Lower Grand",
    "080801": "Atchafalaya-Vermillion",
    "080802": "Calcasieu-Mermentau",
    "080901": "Lower Mississippi-New Orleans",
    "080902": "Lake Pontchartrain",
    "080903": "Central Louisiana Coastal",
    "080402": "Lower Ouachita",
    "111402": "Red-Saline",
    "080302": "Yazoo",
    "080601": "Lower Mississippi-Natchez",
    "080301": "Lower Mississippi-Greenville",
    "020700": "Potomac",
    "102802": "Chariton",
    "102902": "Gasconade",
    "103002": "Lower Missouri",
    "102801": "Grand",
    "102901": "Osage",
    "103001": "Lower Missouri-Blackwater",
    "102400": "Missouri-Nishnabotna",
    "080602": "Big Black-Homochitto",
    "031700": "Pascagoula",
    "031800": "Pearl",
    "030201": "Pamlico",
    "030202": "Neuse",
    "030203": "Onslow Bay",
    "030300": "Cape Fear",
    "030401": "Upper Pee Dee",
    "060102": "Upper Tennessee",
    "060101": "French Broad-Holston",
    "030101": "Roanoke",
    "030102": "Albemarle-Chowan",
    "050500": "Kanawha",
    "110800": "Upper Canadian",
    "130600": "Upper Pecos",
    "110400": "Upper Cimarron",
    "130301": "Rio Grande-Caballo",
    "050600": "Scioto",
    "110500": "Lower Cimarron",
    "110902": "Lower Canadian",
    "111003": "Lower North Canadian",
    "111101": "Robert S. Kerr Reservoir",
    "111303": "Washita",
    "110702": "Neosho",
    "110600": "Arkansas-Keystone",
    "110701": "Verdigris",
    "111202": "Salt Fork Red",
    "111203": "North Fork Red",
    "210200": "Virgin Islands",
    "030402": "Lower Pee Dee",
    "030502": "Edisto-South Carolina Coastal",
    "030601": "Savannah",
    "030501": "Santee",
    "051302": "Lower Cumberland",
    "051301": "Upper Cumberland",
    "060400": "Lower Tennessee",
    "080102": "Hatchie-Obion",
    "111002": "Lower Beaver",
    "120200": "Neches",
    "120301": "Upper Trinity",
    "120302": "Lower Trinity",
    "120401": "San Jacinto",
    "120402": "Galveston Bay-Sabine Lake",
    "120500": "Brazos Headwaters",
    "120601": "Middle Brazos-Clear Fork",
    "120602": "Middle Brazos-Bosque",
    "120701": "Lower Brazos",
    "120702": "Little",
    "120800": "Upper Colorado",
    "120901": "Middle Colorado-Concho",
    "120902": "Middle Colorado-Llano",
    "120903": "Lower Colorado",
    "120904": "San Bernard Coastal",
    "121001": "Lavaca",
    "121002": "Guadalupe",
    "121003": "San Antonio",
    "121004": "Central Texas Coastal",
    "121101": "Nueces",
    "121102": "Southwestern Texas Coastal",
    "130401": "Rio Grande-Fort Quitman",
    "130402": "Rio Grande-Amistad",
    "130403": "Devils",
    "130700": "Lower Pecos",
    "130800": "Rio Grande-Falcon",
    "111403": "Big Cypress-Sulphur",
    "120100": "Sabine",
    "130900": "Lower Rio Grande",
    "110901": "Middle Canadian",
    "111201": "Prairie Dog Town Fork Red",
    "130500": "Rio Grande Closed Basins",
    "111001": "Upper Beaver",
    "111301": "Red-Pease",
    "111302": "Red-Lake Texoma",
    "111401": "Red-Little",
    "020802": "James",
    "050702": "Big Sandy",
    "020801": "Lower Chesapeake",
    "020403": "Mid Atlantic Coastal",
    "050901": "Middle Ohio-Raccoon",
    "210100": "Puerto Rico",
    "080103": "Town of Madrid-Saint Johns Bayou",
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
    1: "Not a barrier", # includes minor barriers
    2: "Moderate barrier",
    3: "Major barrier",
}


POTENTIAL_TO_SEVERITY = {
    "Inaccessible": 0,
    "Indeterminate": 0,
    "Insignificant Barrier": 1,
    "Minor Barrier": 1,
    "Moderate Barrier": 2,
    "No Barrier": 1,
    "No Crossing": 1,
    "No Upstream Channel": 1,
    "Not Scored": 0,
    "Past Project": 0,
    "Potential Project": 0,
    "Proposed Project": 0,
    "Severe Barrier": 3,
    "Significant Barrier": 3,
    "Small Project": 0,
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

CROSSING_TYPE_TO_DOMAIN = {
    "Bridge": 2,
    "Bridge Adequate": 2,
    "Buried Stream": 6,
    "Culvert": 3,
    "Dam": 5,
    "Ford": 4,
    "Inaccessible": 0,
    "Multiple Culvert": 3,
    "Multiple Culverts": 3,
    "Natural Ford": 4,
    "No Crossing": 1,
    "No Upstream Channel": 1,
    "Other": 0,
    "Partially Inaccessible": 0,
    "Removed Crossing": 1,
    "Slab": 4,
    "Unknown": 0,
    "Vented Ford": 4,
    "Vented Slab": 4,
}


ROAD_TYPE_DOMAIN = {0: "Unknown", 1: "Unpaved", 2: "Paved", 3: "Railroad"}

ROAD_TYPE_TO_DOMAIN = {
    "Asphalt": 2,
    "Concrete": 2,
    "Dirt": 1,
    "Driveway": 0,
    "Gravel": 1,
    "Other": 0,
    "Paved": 2,
    "Railroad": 3,
    "Trail": 1,
    "Unknown": 0,
    "Unpaved": 1,
}

BARRIER_CONDITION_DOMAIN = {0: "Unknown", 1: "Failing", 2: "Poor", 3: "OK", 4: "New"}

BARRIER_CONDITION_TO_DOMAIN = {"Failing": 1, "New": 4, "OK": 3, "Poor": 2, "Unknown": 0}


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
