"""Constants used in other scripts."""


# Full Southeast + USFWS R2 / R6 region
STATES = {
    "AL": "Alabama",
    "AR": "Arkansas",
    "AZ": "Arizona",
    "CO": "Colorado",
    "FL": "Florida",
    "GA": "Georgia",
    "IA": "Iowa",  # not officially part of SE / R2 & R6, but important and mostly covered anyway
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MO": "Missouri",
    "MS": "Mississippi",
    "MT": "Montana",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NM": "New Mexico",
    "OK": "Oklahoma",
    "PR": "Puerto Rico",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "WY": "Wyoming",
}

SARP_STATES = [
    "AL",
    "AR",
    "FL",
    "GA",
    "KY",
    "LA",
    "MO",
    "MS",
    "NC",
    "OK",
    "PR",
    "SC",
    "TN",
    "TX",
    "VA",
]


# NETWORK_TYPES determines the type of network analysis we are doing
# natural: only include waterfalls in analysis
# dams: include waterfalls and dams in analysis
# small_barriers: include waterfalls, dams, and small barriers in analysis
NETWORK_TYPES = ("natural", "dams", "small_barriers")


# Mapping of region to HUC4 IDs that are present within the SARP boundary
# REGIONS = {
#     # "02": [7, 8],
#     # "03": list(range(1, 19)),
#     # "05": [5, 7, 9, 10, 11, 13, 14],
#     # "06": list(range(1, 5)),
#     # "07": [10, 11, 14],
#     # "08": list(range(1, 10)),
#     # "10": [24, 27, 28, 29, 30],
#     # "11": [1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
#     # "12": list(range(1, 12)),
#     # "13": [3, 4, 5, 6, 7, 8, 9],
#     # "21": [1, 2],
# }

# Mapping of region to subregions for easier processing of giant datasets (e.g., catchments)
# SUBREGIONS = {
#     # "03": [list(range(1, 8)), list(range(8, 13)), list(range(13, 19))],
#     # "07": [[10, 11, 14]],  # TODO: R2 / R6
#     # "08": [list(range(1, 10))],
#     # "10": [[24, 27, 28, 29, 30]],  # TODO: R2 / R6
#     # "11": [[1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]],  # TODO: R2 / R6
#     # "12": [[1, 2, 3, 4, 7], [9, 10, 11], [5, 6, 8]],
#     # "13": [[3, 4, 5, 6, 7, 8, 9]],  # TODO: R2 / R6
#     # "21": [[1, 2]],
# }


# Listing of regions that are connected
# CONNECTED_REGIONS = ["05_06", "07_10", "08_11"]


# Group regions based on which ones flow into each other
# Note: many of these flow into region 08, which is not yet available
# The total size of the region group needs to be limited based on available memory and the size of the output shapefiles
# from the network analysis, which cannot exceed 2 GB.

# REGION_GROUPS = {
#     # "02": ["02"],
#     # "03": ["03"],
#     # "05_06": ["05", "06"],
#     # "07_10": ["07", "10"],
#     # "07": ["07"],
#     # "10": ["10"],
#     # "08_11": ["08", "11"],
#     "08": ["08"],
#     # "11": ["11"],
#     # "12": ["12"],
#     # "13": ["13"],
#     # "21": ["21"],
# }


# Use USGS CONUS Albers (EPSG:102003): https://epsg.io/102003    (same as other SARP datasets)
# use Proj4 syntax, since GeoPandas doesn't properly recognize it's EPSG Code.
# CRS = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"
CRS = {
    "proj": "aea",
    "lat_1": 29.5,
    "lat_2": 45.5,
    "lat_0": 37.5,
    "lon_0": -96,
    "x_0": 0,
    "y_0": 0,
    "datum": "NAD83",
    "units": "m",
    "no_defs": True,
}

CRS_WKT = """PROJCS["USA_Contiguous_Albers_Equal_Area_Conic",GEOGCS["GCS_North_American_1983",DATUM["North_American_Datum_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["longitude_of_center",-96],PARAMETER["Standard_Parallel_1",29.5],PARAMETER["Standard_Parallel_2",45.5],PARAMETER["latitude_of_center",37.5],UNIT["Meter",1],AUTHORITY["EPSG","102003"]]"""

GEO_CRS = "EPSG:4326"


# distance within which points snapping to a line will snap to endpoint of the line
SNAP_ENDPOINT_TOLERANCE = 1  # meters

# Exclude swamp/marsh (466), estuaries (493), playas (361).
# NOTE: they do not cut the flowlines in the same
# way as other waterbodies, so they will cause issues.
WATERBODY_EXCLUDE_FTYPES = [361, 466, 493]

WATERBODY_MIN_SIZE = 0

# Arbitrary cutoffs, but per visual inspection looks reasonable
LARGE_WB_FLOWLINE_LENGTH = 1000
LARGE_WB_AREA = 0.25

# Arbitrary cutoff, but seemed reasonable from visual inspection
MAX_PIPELINE_LENGTH = 250  # meters


# NOTE: not all feature services have all columns
DAM_FS_COLS = [
    "SARPUniqueID",
    "SNAP2018",  # renamed to ManualReview
    "Snap2018",  # renamed to ManualReview
    "NIDID",
    "SourceDBID",
    "DB_Source",
    "Barrier_Name",
    "Other_Barrier_Name",
    "River",
    "PurposeCategory",
    "Year_Completed",
    "Year_Removed",
    "Height",
    "Length",
    "Width",
    "StructureCondition",
    "ConstructionMaterial",
    "Recon",
    "BarrierStatus",
    "PotentialFeasibility",  # only present in NC
    "PassageFacility",
    "Diversion",
    "FishScreen",
    "ScreenType",
]

DAM_COLS = [
    "SARPID",
    "ManualReview",  # renamed from SNAP2018
    "NIDID",
    "SourceDBID",
    "Barrier_Name",
    "Other_Barrier_Name",
    "River",
    "PurposeCategory",
    "Year_Completed",
    "Year_Removed",
    "Height",
    "StructureCondition",
    "ConstructionMaterial",
    "DB_Source",
    "Recon",
    "PassageFacility",
    "BarrierStatus",
    "PotentialFeasibility",
    "Diversion",
    "FishScreen",
    "ScreenType",
]


SMALL_BARRIER_COLS = [
    "SARPUniqueID",
    "AnalysisId",
    "ManualReview",
    "LocalID",
    "Crossing_Code",
    "StreamName",
    "Road",
    "RoadTypeId",
    "CrossingTypeId",
    "CrossingConditionId",
    "Potential_Project",
    "Source",
    # Not used:
    # "NumberOfStructures",
    # "CrossingComment",
    # "Assessed", # check me
    # "SRI_Score",
    # "Coffman_Strong",
    # "Coffman_Medium",
    # "Coffman_Weak",
    # "SARP_Score",
    # "SE_AOP",
    # "NumberRareSpeciesHUC12", # we add this later
]

WATERFALL_COLS = [
    "fall_id",
    "fall_type",
    "Source",
    "LocalID",
    "name",
    "gnis_name_",
    "watercours",
]


# Used to filter small barriers by Potential_Project (small barriers)
# based on guidance from Kat
KEEP_POTENTIAL_PROJECT = [
    "Severe Barrier",
    "Moderate Barrier",
    "Inaccessible",
    "Significant Barrier",
    "Indeterminate",
    "Potential Project",
    "Proposed Project",
]

# "No Upstream Habitat", "No Upstream Channel" excluded intentionally from above


# Used to filter Potential_Project (small barriers)
# These are DROPPED from all analysis and mapping
DROP_POTENTIAL_PROJECT = ["No", "No Barrier", "No Crossing", "Past Project"]


# Used to filter small barriers and dams by SNAP2018, based on guidance from Kat
# Note: dropped barriers are NOT shown on the map, and not included in the network analysis
# Note: 0 value indicates N/A
DROP_MANUALREVIEW = [
    6,  # Delete: ambiguous, might be duplicate or not exist
    11,  # Duplicate TODO: handle correctly
    14,  # Error: dam does not exist
]

# These are excluded from network analysis / prioritization, but included for mapping
EXCLUDE_MANUALREVIEW = [
    5,  # offstream (DO NOT SNAP!)
    8,  # Removed (no longer exists): Dam removed for conservation
    10,  # invasive barriers
]

ONSTREAM_MANUALREVIEW = [
    4,  # Onstream checked by SARP
    13,  # Onstream, did not have to move (close to correct location)
    15,  # Onstream, moved (moved to close to correct location)
]

# Used to filter dams by Recon
# based on guidance from Kat
DROP_RECON = [5, 19]
DROP_FEASIBILITY = [7]

# These are excluded from network analysis / prioritization, but included for mapping
EXCLUDE_RECON = [7, 16, 22]
EXCLUDE_FEASIBILITY = [8]

# Applies to Recon values, omitted values should be filtered out
RECON_TO_FEASIBILITY = {
    0: 0,
    1: 3,
    2: 3,
    3: 2,
    4: 1,
    5: 7,  # should be removed from analysis
    6: 2,
    7: 8,  # should be removed from analysis
    8: 6,
    9: 6,
    10: 6,
    11: 4,
    13: 6,
    14: 4,
    15: 5,
    16: 9,
    17: 6,
    18: 3,
    19: 10,  # should be removed from analysis
    20: 5,
    21: 6,
    22: 11,
}

# Associated recon values
# FEASIBILITY = {
#   0: 'Not assessed',
#   1: 'Not feasible',
#   2: 'Likely infeasible',
#   3: 'Possibly feasible',
#   4: 'Likely feasible',
#   5: 'No conservation benefit',
#   6: 'Unknown',
#   # not shown to user
#   # 7: 'Error',
#   # 8: 'Dam removed for conservation benefit'
#   # 9: 'Invasive species barrier',
#   # 10: 'Proposed dam'
#   # 11: 'Fish passage installed'
# }


POTENTIAL_TO_SEVERITY = {
    "Inaccessible": 0,
    "Indeterminate": 0,
    "Insignificant Barrier": 1,
    "Minor Barrier": 1,
    "Moderate Barrier": 2,
    "No Barrier": 1,  # removed from processing
    "No Crossing": 1,
    "No Upstream Channel": 1,
    "No Upstream Habitat": 1,
    "Not Scored": 0,
    "No": 1,
    "Past Project": 0,  # removed from processing
    "Potential Project": 0,
    "Proposed Project": 0,
    "Severe Barrier": 3,
    "Significant Barrier": 3,
    "Small Project": 0,
    "SRI Only": 0,
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
    "No Data": 0,
    "Nodata": 0,
}

BARRIER_CONDITION_TO_DOMAIN = {"Failing": 1, "New": 4, "OK": 3, "Poor": 2, "Unknown": 0}

OWNERTYPE_TO_DOMAIN = {
    # Unknown types are not useful
    # "Unknown": 0,
    # "Designation": 0,
    "US Fish and Wildlife Service": 1,
    "USDA Forest Service": 2,
    "Federal Land": 3,
    "State Land": 4,
    "Local Land": 5,
    "Joint Ownership": 5,
    "Regional Agency Special Distribution": 5,
    "Native American Land": 6,
    "Easement": 7,
    "Private Conservation Land": 8,
}

# Map of owner type domain above to whether or not the land is
# considered public
OWNERTYPE_TO_PUBLIC_LAND = {1: True, 2: True, 3: True, 4: True, 5: True}


# List of NHDPlusIDs to convert from loops to non-loops;
# they are coded incorrectly in NHD
# WARNING: you must remove the corresponding segments that
# were previously identified as loops
CONVERT_TO_NONLOOP = {"02": [10000300070616, 10000300132189, 10000300132190]}

# List of NHDPlusIDs to remove due to issues with NHD
REMOVE_IDS = {
    # Invalid loops
    "02": [10000300073811, 10000300021333]
}

