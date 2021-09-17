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

SARP_STATE_NAMES = [STATES[s] for s in SARP_STATES]


# Note: some states overlap multiple regions
REGION_STATES = {
    # Southeast is SARP states
    "se": SARP_STATES,
    # great plains / intermountain west
    "gpiw": [
        "CO",
        "IA",  # NOTE: temporary member
        "KS",
        "MT",
        "ND",
        "NE",
        "SD",
        "WY",
        "UT",
    ],
    "sw": ["AZ", "NM", "OK", "TX"],
}


# NETWORK_TYPES determines the type of network analysis we are doing
# natural: only include waterfalls in analysis
# dams: include waterfalls and dams in analysis
# small_barriers: include waterfalls, dams, and small barriers in analysis
NETWORK_TYPES = ("natural", "dams", "small_barriers")


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
# WARNING: there are dams that have longer pipelines; these can usually be detected
# after building networks by inspecting the flows_to_ocean attribute.
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
    "BarrierSeverity",
    "PotentialFeasibility",
    "Diversion",
    "FishScreen",
    "ScreenType",
]


SMALL_BARRIER_COLS = [
    "SARPUniqueID",
    "AnalysisId",
    "Recon",
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
    "SARP_Score",
    # Not used:
    # "NumberOfStructures",
    # "CrossingComment",
    # "Assessed", # check me
    # "SRI_Score",
    # "Coffman_Strong",
    # "Coffman_Medium",
    # "Coffman_Weak",
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
EXCLUDE_RECON = [7, 22]
EXCLUDE_FEASIBILITY = [8]

UNRANKED_MANUALREVIEW = [
    10,  # invasive barriers; these break the network, but not included in prioritization
]

UNRANKED_RECON = [
    16  # invasive barriers; these break the network, but not included in prioritization
]

UNRANKED_FEASIBILITY = [
    9  # invasive barriers; these break the network, but not included in prioritization
]

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


# Map of NHD FCode to stream type
FCODE_TO_STREAMTYPE = {
    -1: 0,  # not a stream / river or not snapped to one
    46000: 1,  # stream / river
    46006: 1,  # stream / river (perennial)
    46003: 2,  # stream / river (intermittent)
    46007: 2,  # stream / river (ephemeral)
    55800: 3,  # artificial path
    33600: 4,  # canal / ditch
    33601: 4,  # canal / ditch
    33603: 4,  # canal / ditch
    33400: 3,  # unspecified connector
    42800: 5,  # pipeline
    42801: 5,  # pipeline
    42802: 5,  # pipeline
    42803: 5,  # pipeline
    42804: 5,  # pipeline
    42805: 5,  # pipeline
    42806: 5,  # pipeline
    42807: 5,  # pipeline
    42808: 5,  # pipeline
    42809: 5,  # pipeline
    42810: 5,  # pipeline
    42811: 5,  # pipeline
    42812: 5,  # pipeline
    42813: 5,  # pipeline
    42814: 5,  # pipeline
    42815: 5,  # pipeline
    42816: 5,  # pipeline
}


# List of NHDPlusIDs to convert from loops to non-loops;
# they are coded incorrectly in NHD
# WARNING: you may need to remove the corresponding segments that
# were previously identified as loops
CONVERT_TO_NONLOOP = {
    "02": [10000300070616, 10000300132189, 10000300132190],
    "05": [
        # this is a loop at the junction of 05/06 that needs to be retained as a non-loop
        # for networks to be built correctly
        24000100384878
    ],
    "10": [23001300034513, 23001300009083, 23001300078683, 23001300043943],
}

# List of NHDPlusIDs to convert from non-loops to loops based on inspection of
# the network topology
CONVERT_TO_LOOP = {
    "03": [15000600190797],
    "07": [22000200040459],
    "10": [
        23001200078773,
        23001200056308,
        23000900105437,
        23000900021463,
        23000900147355,
        23001300009084,
        23001300078800,
    ],
    "12": [
        30000600405017,
        30000600473005,
        30000600322829,
        30000100041107,
        30000600358059,
        30000100041107,
        30000600405017,
        30000600473005,
    ],
    "14": [41000500061307, 41000500103219],
    "15": [
        40000500295847,
        40000500338303,
        40000200002386,
        40000200028407,
        40000200028408,
        40000200037070,
        40000400082917,
        40000300030341,
    ],
}

# List of NHDPlusIDs to remove due to issues with NHD
REMOVE_IDS = {
    # Invalid loops
    "02": [10000300073811, 10000300021333],
}

# List of NHDPlusIDs that flow into marine based on visual inspection
CONVERT_TO_MARINE = {
    "03": [
        15001800056287,
        15001800004549,
        15001800030490,
        15001800016978,
        15001800094530,
        15001800042883,
        15001800017194,
        15001800094785,
        15001800055997,
        15001800017440,
        15001800029679,
    ],
    "12": [30000800214326, 30000100041238, 30000100041306, 30000100041205],
    "13": [35000100017108],
    "15": [
        # not sure why Sea of Cortez is missing; only tried to get larger flowlines
        40000100109305,
        40000100063029,
        40000100076858,
        40000100047410,
        40000100047193,
        40000200019148,
        40000200045053,
        40000100063066,
        40000100030662,
        40000100045950,
        40000100076853,
        40000100001623,
        40000100078479,
        40000100030661,
        40000100109150,
        40000100063029,
        40000100047645,
        40000100001679,
        40000100016964,
        40000100032417,
        40000100076858,
        40000100047685,
        40000100047686,
        40000100063067,
        40000100109187,
        40000100017000,
        40000100063070,
        40000100001715,
        40000100017001,
        40000100109152,
        40000100016967,
        40000100063030,
        40000100109151,
        40000100109153,
        40000100109155,
        40000100016970,
        40000100063031,
        40000100047593,
        40000100122808,
        40000100107531,
        40000100122809,
        40000100032240,
        40000100047410,
        40000100016768,
        40000100108886,
        40000100078233,
        40000100001269,
        40000100001242,
        40000100047216,
        40000100093593,
        40000100108755,
        40000100047218,
        40000100031951,
        40000100062602,
        40000100047193,
        40000100047194,
        40000100108732,
        40000100078120,
        40000100001245,
        40000100015372,
        40000100092443,
        40000100030648,
        40000100000001,
        40000100016389,
        40000100046974,
        40000100016387,
        40000100016338,
        40000100093330,
        40000100000808,
        40000100000747,
        40000100031432,
        40000100077558,
        40000100046545,
        40000100000606,
        40000100061775,
        40000100000468,
        40000100107954,
        40000100061707,
        40000100107861,
        40000100046251,
        40000100122810,
        40000100092750,
        40000100061669,
        40000100107841,
        40000100046247,
        40000100015654,
        40000200021993,
        40000200030671,
        40000200056366,
        40000200047448,
        40000200004051,
        40000200038593,
        40000200003898,
        40000200064738,
        40000200021128,
        40000200038262,
        40000200038150,
        40000200046714,
        40000200064305,
        40000200003384,
        40000200046627,
        40000200029305,
        40000200011917,
        40000200020689,
        40000200037816,
        40000200046432,
        40000200069667,
        40000200019148,
        40000200002612,
        40000200001852,
        40000200010314,
    ],
}


# List of NHDPlusIDs that are of pipeline type and greater than MAX_PIPELINE_LENGTH
# but must be kept as they flow through dams; removing them would break networks
KEEP_PIPELINES = {
    "02": [10000200114743],
    "05": [24000900019974,],
    "10": [23001800189071, 23001900161939, 23001900224128, 23001300078800],
    "11": [
        21000300167343,
        21000100003686,
        21000100195231,
        21000200033207,
        21000200088822,
        21001200028686,
        21000300088386,
    ],
    "12": [
        30000200076102,
        30000200079902,
        30000200050128,
        30000200094873,
        30000700052449,
        30000600420287,
        30000600395555,
        30000400078280,
        30000200014136,
    ],
    "13": [35000600209336],
    "14": [41000300075075, 41000300083432],
    "17": [55001200060404],
    "21": [85000100010153],
}

# data structure of NHDPlusIDs where upstream, downstream are the original values (used to join into data)
# to be replaced with new_upstream or new_downstream
# IMPORTANT: this only works where the original flowlines have not been split
JOIN_FIXES = {
    "10": [
        # These two segments are Teton River into Marias River, which are backwards in NHD
        {
            "upstream": 23001300022801,
            "downstream": 23001300034513,
            "new_upstream": 23001300034497,
        },
        {
            "upstream": 23001300034513,
            "downstream": 0,
            "new_downstream": 23001300080880,
        },
    ]
}

### data structure of NHDPlusIDs where upstream, downstream are the original values (used to join into data)
# to be removed; they are likely replaced by other fixes
REMOVE_JOINS = {"10": [{"upstream": 23001300034497, "downstream": 0}]}


# List of NHDPlusIDs that are exit points draining a given HUC2
# NOTE: these are only applicable for HUC2s that drain into other HUCS2s outside the analysis region
# they are not specified for HUC2s that can be traversed to the ocean
HUC2_EXITS = {
    "09": [65000200059360, 65000100013652],
    "14": [41000100046769, 41000100047124],
    "15": [
        # NOTE: the first two are irrigation ditches
        40000200002291,
        40000200063130,
        40000100060519,
    ],
    # Note: 16 is internally draining and omitted here
    # Note: 17 has many exit points because it is a partial HUC2; most of these
    # can be removed if the whole HUC2 is analyzed
    "17": [
        55001200000017,
        55001200064544,
        55001100042595,
        55001100129754,
        55001100087083,
    ],
}

