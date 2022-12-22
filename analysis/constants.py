"""Constants used in other scripts."""

# Mapping of network type to barrier kinds that break that network
NETWORK_TYPES = {
    "dams": ["waterfall", "dam"],
    "small_barriers": ["waterfall", "dam", "small_barrier"],
    # "road_crossing": ["waterfall", "dam", "small_barrier", "road_crossing"],
}

# Full Southeast + USFWS R2 / R6 region + OR / WA / ID
STATES = {
    "AL": "Alabama",
    "AR": "Arkansas",
    "AZ": "Arizona",
    "CO": "Colorado",
    "FL": "Florida",
    "GA": "Georgia",
    "IA": "Iowa",  # not officially part of SE / R2 & R6, but important and mostly covered anyway
    "ID": "Idaho",
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
    "OR": "Oregon",
    "PR": "Puerto Rico",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
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
    # Southeast is SARP states plus WV (SECAS not SARP state)
    "se": SARP_STATES + ["WV"],
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
    "pnw": ["ID", "OR", "WA"],
    "sw": ["AZ", "NM", "OK", "TX"],
}


# ID ranges for each type; this is added to the original index of each barrier type
WATERFALLS_ID_OFFSET = 1  # 1 - 1M
DAMS_ID_OFFSET = 1e6  # 1M - 5M
SMALL_BARRIERS_ID_OFFSET = 5 * 1e6  # 5M - 10M
CROSSINGS_ID_OFFSET = 1e7  # >= 10M


# Use USGS CONUS Albers (EPSG:102003): https://epsg.io/102003    (same as other SARP datasets)
# use Proj JSON syntax, since GeoPandas doesn't properly recognize it's EPSG Code.
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
    "type": "crs",
}


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
    "ManualReview",  # for western states and NC (which also has Snap2018)
    "NIDID",
    "SourceDBID",
    "DB_Source",
    "Barrier_Name",
    "Other_Barrier_Name",
    "OwnerType",
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
    "Recon2",
    "Recon3",
    "PotentialFeasibility",  # only present in some states, backfilled from Recon
    "InvasiveSpecies",
    "BarrierStatus",
    "PassageFacility",
    "StructureCategory",
    "StructureClass",
    "Diversion",
    "FishScreen",
    "ScreenType",
    "BarrierSeverity",
    "LowheadDam",
    "LowheadDam1",  # temporary, for Oregon
    "ImpoundmentType",
    "EditDate",
    "Editor",
    "Link",
]


SMALL_BARRIER_COLS = [
    "SARPUniqueID",
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
    "Year_Removed",
    "EditDate",
    "Editor",
    "OwnerType",
    "Constriction"
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
    "SARPUniqueId",
    "fall_id",
    "fall_type",
    "Source",
    "LocalID",
    "name",
    "gnis_name_",
    "watercours",
    "Recon",
    "ManualReview",
    "BarrierSeverity",
]


# Used to filter small barriers by Potential_Project (small barriers)
# based on guidance from Kat; others are intentionally excluded
KEEP_POTENTIAL_PROJECT = [
    "Severe Barrier",
    "Moderate Barrier",
    "Significant Barrier",
    "Indeterminate",
    "Potential Project",
    "Proposed Project",
]

UNRANKED_POTENTIAL_PROJECT = ["No Upstream Channel", "No Upstream Habitat"]
REMOVED_POTENTIAL_PROJECT = ["Past Project", "Completed Project"]

# These are DROPPED from all analysis and mapping
DROP_POTENTIAL_PROJECT = ["No Crossing"]

# NOTE: everything other than above is marked as excluded from analysis


# Used to filter small barriers and dams by SNAP2018, based on guidance from Kat
# Note: dropped barriers are NOT shown on the map, and not included in the network analysis
# Note: 0 value indicates N/A
DROP_MANUALREVIEW = [
    6,  # Delete: ambiguous, might be duplicate or not exist
    11,  # Duplicate
    14,  # Error: dam does not exist
]

# These are excluded from network analysis / prioritization, but included for mapping
# NOTE: off-network barriers (5) are excluded separately because they are not allowed to snap
EXCLUDE_MANUALREVIEW = []

REMOVED_MANUALREVIEW = [
    8,  # Removed (no longer exists): Dam removed for conservation
]

EXCLUDE_PASSAGEFACILITY = [
    13,  # Natural Breach
    14,  # Removal
]

ONSTREAM_MANUALREVIEW = [
    4,  # Onstream checked by SARP
    13,  # Onstream, did not have to move (close to correct location)
    15,  # Onstream, moved (moved to close to correct location)
]

OFFSTREAM_MANUALREVIEW = [
    5,  # offstream, checked by SARP
    11,  # duplicate barrier, delete from analysis
]

# Used to filter dams by Recon
# based on guidance from Kat
DROP_RECON = [
    5,  # Dam may be removed or error (no longer visible)
    19,  # Proposed dam
]

DROP_FEASIBILITY = [
    7,  # Error
]

# These are excluded from network analysis / prioritization, but included for mapping
REMOVED_RECON = [
    7,  # Dam was deliberately removed
]

EXCLUDE_RECON = []

REMOVED_FEASIBILITY = [
    8,  # Dam removed for conservation benefit
]

EXCLUDE_FEASIBILITY = [
    13,  # Dam breached with full flow
]

# limited to just dams
EXCLUDE_BARRIER_SEVERITY = [7]  # No Barrier

INVASIVE_MANUALREVIEW = [
    10,  # invasive barriers; these break the network, but not included in prioritization
]

INVASIVE_RECON = [
    16  # invasive barriers; these break the network, but not included in prioritization
]

INVASIVE_FEASIBILITY = [
    9  # invasive barriers; these break the network, but not included in prioritization
]

NOSTRUCTURE_STRUCTURECATEGORY = [
    3  # Diversion (canal / ditch) without associated dam structure
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
    11: 12,
    13: 6,
    14: 4,
    15: 5,
    16: 9,
    17: 6,
    18: 3,
    19: 10,  # should be removed from analysis
    20: 5,
    21: 6,
    22: 11,  # exclude if BarrierSeverity == No Barrier or Unknown / blank
    23: 11,  # exclude if BarrierSeverity == No Barrier or Unknown / blank
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
#   # 12: 'Removal planned'
#   # 13: 'Breached - full flow'
# }

# NOTE: values with 10 are NOT shown in filters in the UI; 0 is reserved for missing values
FEASIBILITY_TO_DOMAIN = {
    0: 1,  # not assessed
    1: 5,  # not feasible
    2: 4,  # likely infeasible
    3: 3,  # possibly feasible
    4: 2,  # likely feasible
    5: 6,  # no conservation benefit
    6: 1,  # unknown
    7: 10,  # error (filtered out)
    8: 10,  # dam removed for conservation benefit (filtered out)
    9: 10,  # invasive species barrier (filtered out)
    10: 10,  # proposed dam
    11: 9,  # fish passage installed
    12: 7,  # removal planned
    13: 8,  # breached - full flow
}


CROSSING_TYPE_TO_DOMAIN = {
    "bridge": 5,
    "bridge adequate": 5,
    "buried stream": 11,
    "culvert": 8,
    "dam": 0,  # dams should be removed from the small barriers dataset
    "ford": 6,
    "low water crossing": 6,
    "inaccessible": 1,
    "multiple culvert": 8,
    "multiple culverts": 8,
    "natural ford": 7,
    "no crossing": 2,
    "none": 0,
    "no upstream channel": 3,
    "other": 0,
    "partially inaccessible": 1,
    "removed crossing": 2,
    "slab": 6,
    "unknown": 0,
    "vented ford": 6,
    "vented slab": 6,
    "": 0,
    "tide gate": 10,
    "tidegate": 10,
    # only for uninventoried road crossings
    "assumed culvert": 9,
}

CONSTRICTION_TO_DOMAIN = {
    "unknown": 0,
    "": 0,
    "no data": 0,
    "spans full channel & banks": 1,
    "not constricted": 1,
    "spans only bankfull/active channel": 2,
    "constricted to some degree": 3,
    "minor": 4,
    "moderate": 5,
    "severe": 6,
}

ROAD_TYPE_TO_DOMAIN = {
    "asphalt": 2,
    "concrete": 2,
    "dirt": 1,
    "driveway": 0,
    "gravel": 1,
    "other": 0,
    "paved": 2,
    "railroad": 3,
    "trail": 1,
    "unknown": 0,
    "unpaved": 1,
    "no data": 0,
    "nodata": 0,
    "": 0,
}

# Dam barrier condition comes in as domain values,
# map small barrier condition to match
BARRIER_CONDITION_TO_DOMAIN = {
    "": 0,
    "unknown": 0,
    "no data": 0,
    "failing": 3,
    "poor": 3,
    "ok": 1,
    "new": 1,
}

# Dams and small barriers are mapped to SEVERITY_DOMAIN
DAM_BARRIER_SEVERITY_TO_DOMAIN = {
    "": 0,
    "0": 0,  # TEMP: coding error
    "na": 0,
    "unknown": 0,
    "complete": 1,
    "severe barrier": 1,
    "complete barrier": 1,
    "partial": 2,
    "partial passability - non salmonid": 3,
    "partial passibility - non salmonid": 3,
    "partial passability - salmonid": 4,
    "seasonably passable - non salmonid": 5,
    "seasonably passable - non salmond": 5,
    "seasonably passable - salmonid": 6,
    "no barrier": 7,
}

POTENTIALPROJECT_TO_SEVERITY = {
    "": 0,
    "na": 0,
    "unknown": 0,
    "inaccessible": 0,
    "indeterminate": 0,  # removed from processing
    "insignificant barrier": 7,
    "minor barrier": 7,
    "moderate barrier": 2,
    "no barrier": 7,  # removed from processing
    "no crossing": 7,
    "no upstream channel": 7,
    "no upstream habitat": 7,
    "buried stream": 7,
    "not scored": 0,
    "no": 7,
    "unassessed": 0,
    "completed project": 0,  # removed from processing
    "past project": 0,  # removed from processing
    "potential project": 0,
    "proposed project": 0,
    "severe barrier": 1,
    "significant barrier": 1,
    "small project": 0,
    "sri only": 0,
    "other": 0,
    "no score - missing data": 0,
}


# recoded to better align with OWNERTYPE domain
BARRIEROWNERTYPE_TO_DOMAIN = {
    0: 0,  # <missing>
    1: 2,  # "Federal",
    2: 3,  # "State",
    3: 4,  # "Local Government",
    4: 5,  # "Public Utility",
    5: 0,  # "Private",
    6: 0,  # "Not Listed",
    7: 0,  # "Unknown",
    8: 0,  # "Other",
    9: 6,  # "Tribe",
    10: 1,  # "USDA Forest Service",
}


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
# WARNING: you may need to remove the corresponding segments or joins that
# were previously identified as loops
CONVERT_TO_NONLOOP = {
    "05": [
        # this is a loop at the junction of 05/06 that needs to be retained as a non-loop
        # for networks to be built correctly
        24000100384878
    ],
    "10": [
        23001300034513,
        23001300009083,
        23001300078683,
        23001300043943,
    ],
    "17": [
        # fix flowlines at Big Sheep Creek
        55000500146043,
        55000500199027,
    ],
    "18": [
        # these are to preserve the mainstem of the Link River
        50000400082908,
        50000400125776,
        50000400253622,
        # This is main part of South Fork Putah Creek
        50000900219269,
        50000900189338,
        50000900397299,
        50000900397462,
        50000900367742,
        50000900278888,
        50000900397622,
        50000900160157,
        50000900249280,
        50000900397804,
        50000900427377,
        50000900219954,
        50000900160338,
        50000900308919,
        50000900427502,
        50000900397960,
        # this preserves the join to the Middle Fork Eel river
        50000400146877,
        # This preserves the join to Indian Creek
        50000900432339,
        50000900017559,
        50000900432337,
        # This preserves the join to Kittredge Canal into main network
        # from Williamson river
        50000400211221,
    ],
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
    ],
    "17": [
        55000400069574,
        55000300390045,
        55000300261512,
        # fix flowlines at Big Sheep Creek
        55000500199026,
        55000500304567,
    ],
    "18": [
        # These are to remove a canal alongside the Link River
        50000400339083,
        50000400296557,
        # this is to preserve the mainstem of Putah Creek above
        50000900397125,
        50000900130045,
        # this is to preserve the Williamson River join to main network
        # via Kittredge Canal
        50000400299323,
    ],
}

# List of NHDPlusIDs to remove due to issues with NHD
REMOVE_IDS = {
    "17": [
        # Fix flowlines at Big Sheep Creek
        55000500251842
    ],
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
        20001000056287,
        20001000004549,
        20001000055997,
        20001000017440,
        20001000055731,
        20001000042883,
        15001500182760,
        15001500101306,
        15000600194575,
        15000600191114,
        15000700048412,
        15000700000084,
        15001200035170,
        20001000056286,
        20001000017755,
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
    "17": [
        55000100855363,
        55000100282765,
        55000100718685,
        55000100872564,
        55000100526544,
        55000100308793,
        55000100688852,
        55000100751667,
        55000800048292,
        55000800085983,
        55000800084485,
        55000800008877,
        55000300344170,
        55000300368116,
        55000300393790,
        55000800193117,
        55000800127717,  # this is not actually marine; it is a shim for the Fraser River in CAN so that these flowlines are marked as flowing to ocean too
        55000100856434,
        55000100324331,
        55000100497886,
        55000100474507,
        55000100782369,
        55000100378844,
    ],
    "18": [50000400299351, 50000400256410, 50000400001171, 50000900133268],
}


# List of NHDPlusIDs that are of pipeline type and greater than MAX_PIPELINE_LENGTH
# but must be kept as they flow through dams; removing them would break networks
KEEP_PIPELINES = {
    "02": [10000200568875, 10000200523449],
    "05": [
        24000900019974,
    ],
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
    "17": [
        55001200060404,
        55000900261393,
        55000900055928,
        55000900055929,
        # Boise River at Lucky Peak dam
        55000700377451,
        # drain pipe at Keystone Ferry
        55000800273180,
        # Chambers Creek near Steilacoom
        55000800008877,
    ],
    "18": [
        50000900133268,
        50000400323321,
        50000400237762,
        50000400280625,
        50000900123418,
        50000900301457,
    ],
    "21": [85000100010153],
}

# data structure of NHDPlusIDs where upstream, downstream are the original values (used to join into data)
# to be replaced with new_upstream or new_downstream
# IMPORTANT: this only works where the original flowlines have not been split
JOIN_FIXES = {
    "05": [
        # this adds a missing join between the Tennessee River and the Ohio River at the junction of 05 / 06
        {
            "upstream": 25000100061139,
            "downstream": 24000100644691,
            "new_upstream": 25000102104038,
        }
    ],
    "06": [
        # this adds a missing join between the Tennessee River and the Ohio River at the junction of 05 / 06
        {"upstream": 25000102104038, "downstream": 0, "new_downstream": 24000100644691},
    ],
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
        # This segment has a gap between North and South Shoshone River within
        # a reservoir and should be connected
        {"upstream": 23002600053413, "downstream": 0, "new_downstream": 23002600082094},
        # fixes a divergence for Bijou Creek
        {
            "upstream": 23001900141172,
            "downstream": 23001900199640,
            "new_downstream": 23001900170513,
        },
    ],
    "17": [
        # Fix disconnected network at Sage Creek
        {"upstream": 55001100203950, "downstream": 0, "new_downstream": 55001100330944},
        {"upstream": 0, "downstream": 55001100330944, "new_upstream": 55001100203950},
    ],
    "18": [
        # Following entries fix middle fork of Eel River at confluence
        {"upstream": 50000400146877, "downstream": 0, "new_downstream": 50000400232348},
        {"upstream": 50000400061370, "downstream": 0, "new_downstream": 50000400146877},
        # Following entries fix the Williamson River join to main network
        # via Kittredge Canal; flow is in wrong direction
        {"upstream": 50000900432337, "downstream": 0, "new_downstream": 50000900432336},
        {"upstream": 50000900017559, "downstream": 0, "new_downstream": 50000900432337},
    ],
}

### data structure of NHDPlusIDs where upstream, downstream are the original values (used to join into data)
# to be removed; they are likely replaced by other fixes
REMOVE_JOINS = {
    "10": [
        {"upstream": 23001300034497, "downstream": 0},
        # replaced by fix above for Bijou Creek
        {"upstream": 0, "downstream": 23001900170513},
    ],
    "18": [
        # Part of fixes for Eel River above; this join is backwards flow
        {"upstream": 50000400317905, "downstream": 50000400146877},
        # Part of fixes for Williamson River above
        {"upstream": 50000900254664, "downstream": 50000900432337},
        # For fix above, this eliminates a duplicate origin point
        {"upstream": 50000900432617, "downstream": 50000900017560},
    ],
}


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
}
