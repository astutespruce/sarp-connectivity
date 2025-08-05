"""Constants used in other scripts."""

from datetime import datetime

# Mapping of network type to barrier kinds that break the network based
# on the value in the boolean column
NETWORK_TYPES = {
    "dams": {"kinds": ["waterfall", "dam"], "column": "primary_network"},
    "combined_barriers": {
        "kinds": ["waterfall", "dam", "small_barrier"],
        "column": "primary_network",
    },
    "largefish_barriers": {
        "kinds": ["waterfall", "dam", "small_barrier"],
        "column": "largefish_network",
    },
    "smallfish_barriers": {
        "kinds": ["waterfall", "dam", "small_barrier"],
        "column": "smallfish_network",
    },
    "road_crossings": {
        "kinds": ["waterfall", "dam", "small_barrier", "road_crossing"],
    },
    ## other one-off network analyses
    # "full": {"kinds": [], "column": "primary_network"},
    # "dams_only": {"kinds": ["dam"], "column": "primary_network"},
    ## extract only artificial barriers for all dams and road barriers >= minor barrier
    # per direction from Kat on 3/7/2025
    # "artificial_barriers": {
    #     "kinds": ["dam", "small_barrier"],
    #     "column": "smallfish_network",
    # },
}

# barrier types that are counted individually when calculating network stats
BARRIER_KINDS = [
    "waterfall",
    "dam",
    "small_barrier",
    "road_crossing",
]


# All states in analysis region
STATES = {
    "AK": "Alaska",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "IA": "Iowa",
    "IL": "Illinois",
    "IN": "Indiana",
    "ID": "Idaho",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
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
    "OK": "Oklahoma",
    "OH": "Ohio",
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
    "VI",
    "WV",
]

SARP_STATE_NAMES = [STATES[s] for s in SARP_STATES]


# Note: some states overlap multiple regions
REGION_STATES = {
    "alaska": ["AK"],
    "great_lakes": ["IA", "IL", "IN", "MI", "MN", "OH", "WI"],
    "great_plains_intermountain_west": [
        "CO",
        "KS",
        "MT",
        "ND",
        "NE",
        "SD",
        "WY",
        "UT",
    ],
    "hawaii": ["HI"],
    "northeast": ["CT", "DC", "DE", "MA", "MD", "ME", "NH", "NJ", "NY", "PA", "RI", "VT"],
    "northwest": ["ID", "OR", "WA"],
    "pacific_southwest": ["CA", "NV"],
    "southeast": SARP_STATES,
    "southwest": ["AZ", "NM", "OK", "TX"],
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

METERS_TO_MILES = 0.000621371
KM2_TO_ACRES = 247.105


# classify year removed and surveyed into 0, <2000, 2000-2009, 2010-2019, 2020, 2021, 2022, 2023, 2024
# NOTE: include 1 year beyond current year
YEAR_REMOVED_BINS = [0, 1, 2000, 2010, 2020] + list(range(2021, datetime.today().year + 2))
YEAR_SURVEYED_BINS = [0, 1, 2000, 2010, 2020] + list(range(2021, datetime.today().year + 2))

# distance within which points snapping to a line will snap to endpoint of the line
SNAP_ENDPOINT_TOLERANCE = 1  # meters

# Exclude estuaries (493), playas (361), glaciers (378).
# NOTE: they do not cut the flowlines in the same
# way as other waterbodies, so they will cause issues.
WATERBODY_EXCLUDE_FTYPES = [361, 378, 493]

WATERBODY_MIN_SIZE = 0

# Arbitrary cutoffs, but per visual inspection looks reasonable
LARGE_WB_FLOWLINE_LENGTH = 1000
LARGE_WB_AREA = 0.25

# Arbitrary cutoff, but seemed reasonable from visual inspection
# WARNING: there are dams that have longer pipelines; these can usually be detected
# after building networks by inspecting the flows_to_ocean attribute.
MAX_PIPELINE_LENGTH = 250  # meters

SIZECLASSES = ["1a", "1b", "2", "3a", "3b", "4", "5"]

FLOWLINE_JOIN_TYPES = ["origin", "terminal", "internal", "huc_in", "huc2_join", "huc2_drain", "former_pipeline_join"]


# NOTE: not all feature services have all columns
DAM_FS_COLS = [
    "SourceDBID",
    "UNIQUE_ID",  # PartnerID
    "DB_Source",
    "SARPUniqueID",
    "NIDID",
    "Barrier_Name",
    "Other_Barrier_Name",
    "StateAbbreviation",
    "RIVER",
    "Editor",
    "YEAR_COMPLETED",
    "HEIGHT",
    "WIDTH",
    "LENGTH",
    "StructureCategory",
    "StructureClass",
    "PurposeCategory",
    "OwnerType",
    "Hazard",
    "ImpoundmentType",
    "BarrierStatus",
    "StructureCondition",
    "ConstructionMaterial",
    "PassageFacility",
    "PotentialFeasibility",  # only present in some states, backfilled from Recon
    "Recon",
    "Recon2",
    "Recon3",
    "InvasiveSpecies",
    "Year_Removed",
    "YearFishPass",
    "Diversion",
    "FishScreen",
    "ScreenType",
    "BarrierSeverity",
    "LowheadDam",
    "FERC_Dam",
    "Fed_Regulatory_Agency",
    "STATE_REGULATED",
    "Regulatory_Agency",
    "Water_Right",
    "Water_Right_Status",
    "Beneficial_Use",
    "Link",
    "ManualReview",
    "Last_Updated",
    "Priority_Identified",
    "NORMSTOR",
    "FEDERAL_ID",  # new NID federal ID
    "Fatality",
    "NRCS_Dam",
    "Active150",
    "KeepOnActiveList",
    "Year_Reconned",
]


SMALL_BARRIER_COLS = [
    "SARPUniqueID",
    "UNIQUE_ID",  # PartnerID
    "LocalID",
    "Recon",
    "ManualReview",
    "Crossing_Code",
    "StreamName",
    "Road",
    "RoadTypeId",
    "CrossingTypeId",
    "CrossingConditionId",
    "Potential_Project",
    "Source",
    "SARP_Score",
    "Protocol_Used",
    "Year_Removed",
    "YearFishPass",
    "EditDate",
    "Editor",
    "OwnerType",
    "Constriction",
    "PassageFacility",
    "Link",
    # "Private", # set by service downloaded from
    "Priority_Identified",
    "ActiveList",
    "KeepOnActiveList",
    "Year_Surveyed",
    "Resurveyed",
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
    "UNIQUE_ID",  # PartnerID
    "LocalID",
    "fall_id",
    "fall_type",
    "Source",
    "name",
    "gnis_name_",
    "watercours",
    "Recon",
    "ManualReview",
    "BarrierSeverity",
    "Link",
    "Year_Removed",
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
    "Minor Barrier",  # NOTE: excluded from primary networks
]

UNRANKED_POTENTIAL_PROJECT = ["No Upstream Channel", "No Upstream Habitat"]
REMOVED_POTENTIAL_PROJECT = ["Past Project", "Completed Project", "Removed Crossing"]

# These are DROPPED from all analysis and mapping
# NA are modeled road / stream crossings from WDFW, drop them per direction from Kat (8/1/2024)
DROP_POTENTIAL_PROJECT = ["No Crossing", "NA"]

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
    13,  # Partial Breach
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
EXCLUDE_PASSABILITY = [7]  # No Barrier

INVASIVE_MANUALREVIEW = [
    10,  # invasive barriers; these break the network, but not included in prioritization
]

INVASIVE_RECON = [
    16  # invasive barriers; these break the network, but not included in prioritization
]

INVASIVE_FEASIBILITY = [
    9  # invasive barriers; these break the network, but not included in prioritization
]

# per instructions from Kat on 7/14/2023; drop all types except 3 and 9
# NOTE: category 3 has dedicated handling based on other fields
DROP_STRUCTURECATEGORY = [0, 1, 2, 4, 5, 6, 7, 8, 10, 11, 12]

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
#   # 14: 'Fish passage installed for conservation benefit'
#   # 15: 'Treatment completed (removal vs fishway unspecified)
#   # 16: 'Treatment planned'
# }

# NOTE: values with 10 are NOT shown in filters in the UI; 0 is reserved for missing values
# Domain is FeasibilityClass
FEASIBILITY_TO_FEASIBILITYCLASS_DOMAIN = {
    0: 1,  # not assessed
    1: 5,  # not feasible
    2: 4,  # likely infeasible
    3: 3,  # possibly feasible
    4: 2,  # likely feasible
    5: 6,  # no conservation benefit
    6: 1,  # unknown
    7: 11,  # error (filtered out)
    8: 11,  # dam removed for conservation benefit (filtered out)
    9: 11,  # invasive species barrier (filtered out)
    10: 11,  # proposed dam (filtered out, code no longer used)
    11: 9,  # fish passage installed (code no longer used, superseded by 14)
    12: 7,  # removal planned
    13: 8,  # breached - full flow
    14: 9,  # fish passage installed for conservation benefit
    15: 10,  # treatment complete
    16: 7,  # treatment planned
}


# recode domain values to be in better order
HAZARD_TO_DOMAIN = {
    0: 0,  # not provided in domain, is unknown
    1: 1,  # high
    2: 3,  # intermediate
    3: 4,  # low
    4: 0,  # unknown,
    5: 2,  # significant
    6: 0,  # unknown (not in domain / NID, recode to unknown per direction from Kat)
}


CROSSING_TYPE_TO_DOMAIN = {
    "bridge": 5,
    "bridge adequate": 5,
    "buried stream": 10,
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
    "tide gate": 9,
    "tidegate": 9,
    "failed culvert": 8,
    "removed": 0,
    # only for unassessed road crossings
    "assumed culvert": 99,
    # added per direction from Kat on 7/24/2025
    "temporary structure": 11,
}

CONSTRICTION_TO_DOMAIN = {
    "unknown": 0,
    "": 0,
    "no": 0,
    "no data": 0,
    "spans full channel & banks": 1,
    "spans only channel & banks": 1,  # TODO: verify with Kat
    "not constricted": 1,
    "spans only bankfull/active channel": 2,
    "spans only bankfull / active channel": 2,
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

# Dams, small barriers, and waterfalls are mapped to PASSABILITY_DOMAIN
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


FERCREGULATED_TO_DOMAIN = {
    0: 0,  # unknown
    1: 1,  # licensed
    3: 4,  # exemption
    4: 3,  # pending permit
    5: 2,  # preliminary permit
    2: 5,  # not a FERC dam
}

STATEREGULATED_TO_DOMAIN = {"": 0, "0": 0, "Yes": 1, "Y": 1, "1": 1, "No": 2, "N": 2, "2": 2}


# uses BarrierSeverity domain
# barriers with severity == 0 are excluded from analysis
POTENTIALPROJECT_TO_SEVERITY = {
    "": 0,
    "na": 0,
    "unknown": 0,
    "inaccessible": 0,
    "indeterminate": 3,
    "insignificant barrier": 5,
    "minor barrier": 4,  # remove from processing except for darter scenario
    "moderate barrier": 2,
    "no barrier": 8,  # removed from processing
    "no crossing": 8,
    "no upstream channel": 9,
    "no upstream habitat": 9,
    "buried stream": 8,
    "not scored": 0,
    "no": 8,
    "unassessed": 0,
    "completed project": 0,  # removed from processing
    "completed": 0,  # removed from processing
    "past project": 0,  # removed from processing
    # Potential / proposed project both get assigned as likely barrier if SARP_Score != -1
    "potential project": 7,
    "proposed project": 7,
    "severe barrier": 1,
    "significant barrier": 1,
    "small project": 0,
    "sri only": 0,
    "other": 0,
    "no score - missing data": 0,
    "error-delete": 0,
}


# Map small barrier BarrierSeverity to Passability domain used by dams / combined
SEVERITY_TO_PASSABILITY = {
    0: 0,
    1: 1,
    2: 2,
    3: 2,
    4: 2,
    5: 2,
    6: 2,
    7: 2,
    8: 7,
    9: 0,
}


# recoded to better align general order with OwnerType: Federal, State, ... Private
BARRIEROWNERTYPE_TO_DOMAIN = {
    0: 0,  # <missing>
    1: 1,  # "Federal",
    2: 3,  # "State",
    3: 4,  # "Local Government",
    4: 5,  # "Public Utility",
    5: 8,  # "Private",
    6: 0,  # "Not Listed",
    7: 0,  # "Unknown",
    8: 0,  # "Other",
    9: 7,  # "Tribe",
    10: 6,  # "Irrigation district",
    11: 2,  # USFS  TODO: implement everywhere
}

OWNERTYPE_TO_DOMAIN = {
    # Unknown types are not useful
    # "Unknown": 0,
    # "Designation": 0,
    "Bureau of Land Management": 1,
    "Bureau of Reclamation": 2,
    "Department of Defense": 3,
    "National Park Service": 4,
    "US Fish and Wildlife Service": 5,
    "USDA Forest Service (ownership boundary)": 6,
    "USDA Forest Service (admin boundary)": 7,
    "Federal Land": 8,
    "State Land": 9,
    "Local Land": 10,
    "Joint Ownership": 10,
    "Regional Agency Special Distribution": 10,
    "Native American Land": 11,
    "Easement": 12,
    "Private Conservation Land": 13,
    "NGO": 13,
}


# Map of owner type domain above to whether or not the land is
# considered public
OWNERTYPE_TO_PUBLIC_LAND = {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True, 8: True}


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
    42000: 5,  # underground connector
    42001: 5,  # underground connector
    42002: 5,  # underground connector
    42003: 5,  # underground connector
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


# map ESU layer names to 2-digit integer indexes
# these are based on data/species/source/ESU_DPS_CA_WA_OR_ID.gdb
# the inverse of this (with modifications) is the lookup used in frontend
SALMONID_ESU_LAYER_TO_CODE = {
    "Chinook_California_Coastal": 10,
    "Chinook_Central_Valley_Fall_LateFall_run": 11,
    "Chinook_Central_Valley_Spring_run": 12,
    "Chinook_Deschutes_River_Summer_Fall_run": 13,
    "Chinook_Lower_Columbia_River": 14,
    "Chinook_Mid_Columbia_River_Spring_run": 15,
    "Chinook_Oregon_Coast": 16,
    "Chinook_Puget_Sound": 17,
    "Chinook_Sacramento_River_Winter_run": 18,
    "Chinook_Snake_River_Fall_run": 19,
    "Chinook_Snake_River_Spring_Summer_run": 20,
    "Chinook_Southern_OR_Northern_CA_Coastal": 21,
    "Chinook_Upper_Columbia_River_Spring_run": 22,
    "Chinook_Upper_Columbia_River_Summer_Fall_run": 23,
    "Chinook_Upper_Klamath_Trinity_Rivers": 24,
    "Chinook_Upper_Willamette_River": 25,
    "Chinook_Washington_Coast": 26,
    "Chum_Columbia_River": 27,
    "Chum_Hood_Canal_Summer_run": 28,
    "Chum_Pacific_Coast": 29,
    "Chum_Puget_Sound_Strait_of_Georgia": 30,
    "Coho_Central_California_Coast": 31,
    "Coho_Lower_Columbia_River": 32,
    "Coho_Olympic_Peninsula": 33,
    "Coho_Oregon_Coast": 34,
    "Coho_Puget_Sound_Strait_of_Georgia": 35,
    "Coho_Southern_OR_Northern_CA_Coast": 36,
    "Coho_Southwest_Washington": 37,
    "Pink_even_year": 38,
    "Pink_odd_year": 39,
    "Sockeye_Baker_River": 40,
    "Sockeye_Lake_Pleasant": 41,
    "Sockeye_Lake_Wenatchee": 42,
    "Sockeye_Okanogan_River": 43,
    "Sockeye_Ozette_Lake": 44,
    "Sockeye_Quinalt_Lake": 45,
    "Sockeye_Snake_River": 46,
    "Steelhead_California_Central_Valley": 47,
    "Steelhead_Central_California_Coast": 48,
    "Steelhead_Klamath_Mountains_Province": 49,
    "Steelhead_Lower_Columbia_River": 50,
    "Steelhead_Middle_Columbia_River": 51,
    "Steelhead_Northern_California": 52,
    "Steelhead_Olympic_Peninsula": 53,
    "Steelhead_Oregon_Coast": 54,
    "Steelhead_Puget_Sound": 55,
    "Steelhead_Snake_River_Basin": 56,
    "Steelhead_South_Central_California_Coast": 57,
    "Steelhead_Southern_California": 58,
    "Steelhead_Southwest_Washington": 59,
    "Steelhead_Upper_Columbia_River": 60,
    "Steelhead_Upper_Willamette_River": 61,
}

# Note: not all FHPs are included here (Reservoir FHP specifically excluded)
FHP_LAYER_TO_CODE = {
    "FHP_Atlantic_Coast_Boundary_2013": "ACFHP",
    "FHP_CFPF_Boundary_2013": "CFPF",
    "FHP_DARE_Boundary_2013": "DARE",
    "FHP_Desert_Boundary_2013": "DFHP",
    "FHP_EBTJV_Boundary_2013": "EBTJV",
    "FHP_Fishers_Farmers_Boundary_2013": "FFP",
    "FHP_GLB_Boundary_2013": "GLBFHP",
    "FHP_Great_Plains_Boundary_2013": "GPFHP",
    "FHP_Hawaii_Boundary_2013": "HFHP",
    "FHP_Kenai_Peninsula_Boundary": "KPFHP",
    "FHP_MatSu_Basin_Boundary_2013": "MSBSHP",
    "FHP_Midwest_Glacial_Lakes_Boundary_2013": "MGLP",
    "FHP_Ohio_River_Basin_Boundary": "ORBFHP",
    "FHP_PMEP_Boundary_2013": "PMEP",
    # NOTE: intentionally exclude SARP since this layer is out of date; use SARP_STATES instead
    # "FHP_SARP_Boundary_2013": "SARP",
    "FHP_SEAK_Boundary_2013": "SEAFHP",
    "FHP_SW_AK_Salmon_Boundary_2013": "SWASHP",
    "FHP_Western_Native_Trout_Boundary_2013": "WNTI",
}

TNC_RESILIENCE_TO_DOMAIN = {
    "Far Below Average": 1,
    "Below Average": 2,
    "Slightly Below Average": 3,
    "Average": 4,
    "Slightly Above Average": 5,
    "Above Average": 6,
    "Far Above Average": 7,
}
# same as above but missing Far Below Average
TNC_COLDWATER_TO_DOMAIN = {
    "Below Average": 2,
    "Slightly Below Average": 3,
    "Average": 4,
    "Slightly Above Average": 5,
    "Above Average": 6,
    "Far Above Average": 7,
}


EPA_CAUSE_TO_CODE = {
    "temperature": "t",
    "cause_unknown_impaired_biota": "b",
    "oxygen_depletion": "o",
    "algal_growth": "a",
    "flow_alterations": "f",
    "habitat_alterations": "a",
    "hydrologic_alteration": "y",
    "cause_unknown_fish_kills": "f",
}

TU_BROOK_TROUT_PORTFOLIO_TO_DOMAIN = {
    "Other": 1,
    "Other populations": 1,
    "Other population": 1,
    "Persistent": 2,
    "Stronghold": 3,
}


# List of NHDPlusIDs to convert from loops to non-loops;
# they are coded incorrectly in NHD
# WARNING: you may need to remove the corresponding segments or joins that
# were previously identified as loops
CONVERT_TO_NONLOOP = {
    "01": [10000900029041, 10000900015420],
    "04": [60000800221705, 60000800211576, 60000800234160],
    "05": [
        # this is a loop at the junction of 05/06 that needs to be retained as a non-loop
        # for networks to be built correctly
        24000100384878,
    ],
    "07": [
        # junction of Wisconsin River into Mississippi River
        22000400022387
    ],
    "09": [65000200009866],
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
        50000900308920,
        50000900160000,
        # this preserves the join to the Middle Fork Eel river
        50000400146877,
        # This preserves the join to Indian Creek
        50000900432339,
        50000900017559,
        50000900432337,
        # This preserves the join to Kittredge Canal into main network
        # from Williamson river
        50000400211221,
        # this preserves an incoming tributary at Pyramid dam
        50000100088802,
        # preserves incoming triburary;
        50000100131551,
    ],
    "19": [
        75009800049435,
        75009800000058,
        75009800048972,
        75009800048710,
        75009800049981,
        75009800048342,
        75009800049483,
        75009800051579,
        75009800049998,
        75009800051156,
        75009900007041,
        75009900012804,
        75009900023996,
        75009900014179,
        75009800049470,
        75009900010772,
        75009800048820,
    ],
}

# List of NHDPlusIDs to convert from non-loops to loops based on inspection of
# the network topology
CONVERT_TO_LOOP = {
    "01": [10000900028934],
    "03": [15000600190797],
    "04": [60000800227820],
    "07": [22000200040459, 22000500077837, 22000500108669, 22000200040459],
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
        # fix non-loop segment immediately between other loops at Bonneville Dam
        55000300287268,
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
        # This feeds a very long pipeline (dropped) out of Pyramid dam and
        # should be dropped too
        50000100117028,
        # this is the counterpart to a loop converted to a non-loop
        50000100017093,
    ],
    "19": [75009800049027, 75009800049021, 75009900024438, 75009800049174],
}

# List of NHDPlusIDs to remove due to issues with NHD
REMOVE_IDS = {
    "01": [
        # flowlines around networks that are broken at dams; remove
        # them to prevent barriers from snapping to them
        5000701358265,
        5000701362304,
    ],
    "04": [60000800202273, 60000800265556],
    "09": [65000200080964],
    "17": [
        # Fix flowlines at Big Sheep Creek
        55000500251842
    ],
    "19": [
        # remove divergent downstream
        75000100004795,
        75009800049233,
        75009800000625,
        75009800050969,
        # remove duplicate flowline
        75009800048647,
    ],
}

# List of NHDPlusIDs that border the Great Lakes or are located at junctions
# between them and aren't picked up automatically via remove_great_lakes_flowlines()
CONVERT_TO_GREAT_LAKES = {
    "04": [
        60001900010183,
        60002500018160,
        60002700043312,
        60002100000007,
        60002100056060,
        60002100000016,
        60002100000021,
        60002100045841,
        60002100000015,
        60002800048624,
    ]
}

# List of NHDPlusIDs that flow into marine based on visual inspection
CONVERT_TO_MARINE = {
    "01": [
        # NOTE: this flowline terminates at edge of available HUC4s on the Saint John's River
        # about 75 miles from the ocean, but there appear to be no barriers downstream
        5000100086769,
        5000701377471,
        5000801717495,
        5000200801727,
        5000200805990,
        10000800011376,
        10000800061360,
        10000800071952,
        10000800003148,
        10000800073041,
        10000800002216,
        10000800068314,
        10000800073132,
        10000800061298,
        10000800003141,
        10000800002262,
        10000800069333,
        10000800007841,
        10000800007827,
        10000800007870,
        10000800039419,
        10000800066390,
        10000800065250,
        10000800059013,
        10000800066225,
        10000800030186,
        10000800064416,
        10000800065275,
        10000800066314,
        10000800044095,
        10000800068493,
        10000800068518,
        10000800068634,
        10000800043890,
        10000800068755,
        10000800072770,
        10000800032820,
        10000800062628,
        10000800068648,
        10000800068534,
        10000800044102,
        10000800056880,
        10000800037841,
        10000800026338,
        10000800072874,
        10000800055696,
        10000800034009,
        10000800034013,
        10000800034006,
        10000800055743,
        10000800034032,
        10000800056871,
        10000800056945,
        10000800055810,
        10000800034041,
        10000800072902,
        10000800065389,
        10000800072901,
        10000800055654,
        10000800034658,
        10000800057376,
        10000800065390,
        10000800034577,
        10000800034617,
        10000800034598,
        10000800072897,
        10000800034570,
        10000800034582,
        10000800034655,
        10000800034609,
        10000800072819,
        10000800034604,
        10000800065376,
        10000800072909,
        10000800072876,
        10000800065362,
        10000800072881,
        10000800034665,
        10000800034566,
        10000800057391,
        10000800055610,
        10000800034654,
        10000800065413,
        10000800055586,
        10000800065408,
        10000800034581,
        10000800072813,
        10000800034575,
        10000800034568,
        10000800034245,
        10000800066355,
        10000800065353,
        10000800031740,
        10000800065300,
        10000800064377,
        10000800064372,
        10000800030215,
        10000800069381,
        10000800060573,
        10000800067255,
        10000800067244,
        10000800048225,
        10000800028440,
        10000800034794,
        10000800000109,
        10000800020565,
        10000800072789,
        10000800070103,
        10000800047087,
        10000800069324,
        10000800060731,
        10000800034261,
        10000800038717,
        10000800057337,
        10000800060819,
        10000800056564,
        10000800038687,
        10000800000024,
        10000800034879,
        10000800033261,
        10000800033286,
        10000800024213,
        10000800061100,
        10000800071296,
        10000800070842,
        10000800071281,
        10000800035544,
        10000800011384,
        10000800011383,
        10000800035542,
        10000800067088,
        10000800067080,
        10000800061446,
        10000800001137,
        10000800001185,
        10000800061367,
        10000800068320,
        10000800068318,
        10000800002260,
        10000800002272,
        10000800071753,
        10000800073164,
        10000800073013,
        10000800073163,
        10000800068383,
        10000800072545,
        10000800007847,
        10000800012116,
        10000800012111,
        10000800039436,
        10000800069225,
        10000900000317,
        10000800035757,
        10000800000162,
        10000800071182,
        10000800071176,
        10000800043836,
        10000800067241,
        10000800065312,
        10000800000528,
        10000800027670,
        10000800031691,
        10000800055836,
        10000800033678,
        10000800056879,
        10000800033735,
        10000800000172,
        10000800000174,
        10000800040947,
        10000800000016,
        10000800061104,
        10000800024217,
        10000800061046,
        5000200806596,
        5000200811966,
    ],
    "02": [10000100039317, 10000200672603, 10000200653686, 10000200427232],
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
    "04": [
        # the following flow into the Saint Lawrence River and terminate at the edge of available HUC4s,
        # but connect downstream to marine with no apparent barriers
        60000100003951,
        60000200106923,
    ],
    "12": [30000800214326, 30000100041238, 30000100041306, 30000100041205],
    "13": [35000100017108],
    "15": [
        # not sure why Sea of Cortez is missing; only tried to get larger flowlines
        40000100000001,
        40000100000468,
        40000100000606,
        40000100000747,
        40000100000808,
        40000100001242,
        40000100001245,
        40000100001269,
        40000100001623,
        40000100001679,
        40000100001715,
        40000100015372,
        40000100015654,
        40000100016338,
        40000100016387,
        40000100016389,
        40000100016768,
        40000100016964,
        40000100016967,
        40000100016970,
        40000100017000,
        40000100017001,
        40000100030648,
        40000100030661,
        40000100030662,
        40000100031432,
        40000100031951,
        40000100032240,
        40000100032417,
        40000100045950,
        40000100046247,
        40000100046251,
        40000100046545,
        40000100046974,
        40000100047193,
        40000100047194,
        40000100047216,
        40000100047218,
        40000100047410,
        40000100047593,
        40000100047645,
        40000100047685,
        40000100047686,
        40000100061669,
        40000100061707,
        40000100061775,
        40000100062602,
        40000100063029,
        40000100063030,
        40000100063031,
        40000100063066,
        40000100063067,
        40000100063070,
        40000100076853,
        40000100076858,
        40000100077558,
        40000100078120,
        40000100078233,
        40000100078479,
        40000100092443,
        40000100092750,
        40000100093330,
        40000100093593,
        40000100107531,
        40000100107841,
        40000100107861,
        40000100107954,
        40000100108732,
        40000100108755,
        40000100108886,
        40000100109150,
        40000100109151,
        40000100109152,
        40000100109153,
        40000100109155,
        40000100109187,
        40000100109305,
        40000100122808,
        40000100122809,
        40000100122810,
        40000200001852,
        40000200002612,
        40000200003384,
        40000200003898,
        40000200004051,
        40000200010314,
        40000200011917,
        40000200019148,
        40000200020689,
        40000200021128,
        40000200021993,
        40000200029305,
        40000200030671,
        40000200037816,
        40000200038150,
        40000200038262,
        40000200038593,
        40000200045053,
        40000200046432,
        40000200046627,
        40000200046714,
        40000200047448,
        40000200056366,
        40000200064305,
        40000200064738,
        40000200069667,
        40000100087660,
        40000100069470,
        40000100069301,
        40000100069351,
        40000100069288,
        40000100069474,
        40000100069419,
        40000100071580,
        40000100072065,
        40000100072121,
        40000100070972,
        40000100070959,
        40000100072156,
        40000100070905,
        40000100072102,
        40000100072096,
        40000100072064,
        40000100072073,
        40000100072160,
        40000100072152,
        40000100015850,
        40000100023174,
        40000100015860,
        40000100015862,
        40000100072088,
        40000100072089,
        40000100101044,
        40000100013415,
        40000100013380,
        40000100013285,
        40000100013405,
        40000100013316,
        40000100077812,
        40000100077736,
        40000100077712,
        40000100077792,
        40000100077695,
        40000100077817,
        40000100077698,
        40000100077680,
        40000100077682,
        40000100077802,
        40000100077675,
        40000100077831,
        40000100077724,
        40000100028254,
        40000100028090,
        40000100028212,
        40000100028043,
        40000100028252,
        40000100028231,
        40000100033351,
        40000100033360,
        40000100037768,
        40000100037733,
        40000100033608,
        40000100033624,
        40000100032934,
        40000100032921,
        40000100032922,
        40000100075260,
        40000100075165,
        40000100075352,
        40000200052741,
        40000200052738,
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
        40000100075180,
        40000100028189,
        40000100033361,
        40000100013344,
        40000100069392,
    ],
    "18": [
        50000400299351,
        50000400256410,
        50000400001171,
        50000900133268,
        50000400000939,
        50000400000439,
        50000400214004,
        50000300031364,
        50000300025391,
        50000300025392,
        50000300010855,
        50000300037339,
        50000300037473,
    ],
    "19": [75009900028839, 75009900028171],
    "20": [
        80000800000017,
        80000800000401,
        80000800000063,
        80000700003326,
        80000700002795,
        80000600000338,
        80000600001051,
        80000600001052,
        80000500000904,
        80000500000035,
        80000500000190,
        80000500000912,
        80000500001082,
        80000500000259,
        80000500000856,
        80000200000403,
        80000200002683,
        80000100003233,
    ],
}


CONVERT_TO_FLOW_INTO_GREAT_LAKES = {"04": [60001500014272, 60002700006825, 60003700022372, 60003700005514]}


# List of NHDPlusIDs that are of pipeline type and greater than MAX_PIPELINE_LENGTH
# but must be kept as they flow through dams; removing them would break networks
KEEP_PIPELINES = {
    "01": [10000900032491, 10000900077592],
    "02": [
        10000200568875,
        10000200523449,
        10000200672603,
        10000200653686,
        10000200664162,
        10000200664187,
    ],
    "05": [24000900019974, 24000200040231],
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
    "14": [41000300090633, 41000300071358],
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
        50000400323321,
        50000400237762,
        50000400280625,
        50000900123418,
        50000900301457,
        50000800165535,
        50000200030140,
        # San Gabriel River at San Gabriel dam
        50000100180163,
        50000100067358,
        50000100010944,
        # Bouquet Reservoir dam
        50000100120191,
        # Littlerock dam
        50000700072234,
        # Seven oaks dam
        50000100136899,
        # short stretch in urban San Luis Obispo, keep per direction from Kat 4/11/2024
        50000200011605,
        # Anderson Lake dam
        50000300014446,
        # Fern Lake (looks like mostly overland flowline)
        50000300004005,
        # Wishon Reservoir
        50001000073809,
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
        # Following entries fix Governor Edmund G Brown West Branch California Aqueduct
        # flowlines in waterbody to feed tribs in waterbody to main network instead of pipeline
        # route 50000100088803=>50000100088802
        {"upstream": 50000100088803, "downstream": 50000100173491, "new_downstream": 50000100088802},
        # route 50000100088802=>50000100178204
        {"upstream": 50000100088802, "downstream": 50000100173491, "new_downstream": 50000100178204},
        # route 50000100004266=>50000100173491
        {"upstream": 50000100004266, "downstream": 50000100117028, "new_downstream": 50000100173491},
        # route 50000100173491=>50000100088802
        {"upstream": 50000100173491, "downstream": 50000100117028, "new_downstream": 50000100088802},
        # fix incoming trib to Lake Elisnore
        # route 50000100017094=>50000100131551
        {"upstream": 50000100017094, "downstream": 50000100017093, "new_downstream": 50000100131551},
        # route 50000100131551=>50000100045184 (flip direction)
        {
            "upstream": 50000100101106,
            "downstream": 50000100131551,
            "new_upstream": 50000100131551,
            "new_downstream": 50000100045184,
        },
    ],
}

### data structure of NHDPlusIDs where upstream, downstream are the original values (used to join into data)
# to be removed; they are likely replaced by other fixes
REMOVE_JOINS = {
    "01": [
        # incorrect terminal + downstream value, remove the terminal
        {"upstream": 5000701364039, "downstream": 0}
    ],
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
        # fix at Governor Edmund G Brown West Branch California Aqueduct
        {"upstream": 50000100004266, "downstream": 50000100117028},
        {"upstream": 50000100173491, "downstream": 50000100117028},
        {"upstream": 50000100173270, "downstream": 50000100088802},
    ],
}

# set of HUC2s that touch the coast
COASTAL_HUC2 = {"01", "02", "03", "08", "12", "13", "15", "17", "18", "19", "21"}


# List of NHDPlusIDs that are exit points draining a given HUC2
# NOTE: these are only applicable for HUC2s that drain into other HUCS2s outside the analysis region
# they are not specified for HUC2s that can be traversed to the ocean
HUC2_EXITS = {
    "01": [
        # eventually connects to the ocean through Canada
        5000100086769
    ],
    "04": [
        # there are several networks that flow into Canada
        60003500015245,
        60000200097957,
        60000100003951,
        60000200106923,
        60000200005463,
        60000200088973,
        60000200111331,
        60000200088449,
        60000200025568,
        60000200103466,
        60000300003409,
        60000300002879,
        60000300002274,
        60000300003840,
        60000300005212,
        60000300007591,
        60000300038536,
    ],
    "09": [65000200059360, 65000100013652, 65000300094466],
    "14": [41000100046769, 41000100047124],
    "15": [
        # NOTE: the first two are irrigation ditches
        40000200002291,
        40000200063130,
        40000100060519,
        40000100121143,
    ],
    # Note: 16 is internally draining and omitted here
    "19": [
        75027600014367,
        75027600007693,
        75027600013820,
        75027600027495,
        75025400001071,
    ],
}
