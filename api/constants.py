from pathlib import Path

from enum import Enum


LOGO_PATH = Path("ui/src/images/sarp_logo_highres.png").resolve()


### Enums for validating incoming request values
class PublicAPIBarrierTypes(str, Enum):
    dams = "dams"
    # NOTE: small_barriers is referred to as barriers for public API
    barriers = "barriers"


# road crossings and waterfalls cannot be ranked
class RankedBarrierTypes(str, Enum):
    dams = "dams"
    small_barriers = "small_barriers"
    combined_barriers = "combined_barriers"
    largefish_barriers = "largefish_barriers"
    smallfish_barriers = "smallfish_barriers"


# types that support query (filtering) and download; includes all ranked types
# plus road crossings; waterfalls cannot be filtered or downloaded via API
class FullySupportedBarrierTypes(str, Enum):
    dams = "dams"
    small_barriers = "small_barriers"
    combined_barriers = "combined_barriers"
    largefish_barriers = "largefish_barriers"
    smallfish_barriers = "smallfish_barriers"
    road_crossings = "road_crossings"


class NationalDownloadBarrierTypes(str, Enum):
    dams = "dams"
    small_barriers = "small_barriers"
    combined_barriers = "combined_barriers"
    road_crossings = "road_crossings"


# must match the subset of analysis/constants.py::NETWORK_TYPES keys
# that are available for use in the tool
class NetworkTypes(str, Enum):
    dams = "dams"
    combined_barriers = "combined_barriers"
    largefish_barriers = "largefish_barriers"
    smallfish_barriers = "smallfish_barriers"


class Layers(str, Enum):
    HUC2 = "HUC2"
    HUC6 = "HUC6"
    HUC8 = "HUC8"
    HUC10 = "HUC10"
    HUC12 = "HUC12"
    State = "State"
    County = "County"
    CongressionalDistrict = "CongressionalDistrict"
    FishHabitatPartnership = "FishHabitatPartnership"
    Region = "Region"


class Formats(str, Enum):
    csv = "csv"


class Scenarios(str, Enum):
    NC = "NC"
    WC = "WC"
    NCWC = "NCWC"
    PNC = "PNC"
    PWC = "PWC"
    PNCWC = "PNCWC"
    MNC = "MNC"
    MWC = "MWC"
    MNCWC = "MNCWC"


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
        if item not in s:
            result.append(item)
            s.add(item)

    return result


# Fields that have multiple values present, encoded as comma-delimited string
MULTIPLE_VALUE_FIELDS = ["Trout", "SalmonidESU", "DisadvantagedCommunity", "FishHabitatPartnership"]
BOOLEAN_FILTER_FIELDS = ["Removed"]


# Summary unit fields
UNIT_FIELDS = ["HUC2", "HUC6", "HUC8", "HUC10", "HUC12", "State", "County", "CongressionalDistrict"]


# metric fields that are only valid for barriers with networks
METRIC_FIELDS = [
    "HasNetwork",
    "Ranked",
    "Intermittent",
    "Canal",
    "StreamOrder",
    "Landcover",
    "SizeClasses",
    "PerennialSizeClasses",
    "MainstemSizeClasses",
    # full upstream functional network
    "TotalUpstreamMiles",
    "PerennialUpstreamMiles",
    "IntermittentUpstreamMiles",
    "AlteredUpstreamMiles",
    "UnalteredUpstreamMiles",
    "PercentUnaltered",
    "PerennialUnalteredUpstreamMiles",
    "PercentPerennialUnaltered",
    "ResilientUpstreamMiles",
    "ColdUpstreamMiles",
    "PercentResilient",
    "PercentCold",
    "UpstreamDrainageAcres",
    "UpstreamUnalteredWaterbodyAcres",
    "UpstreamUnalteredWetlandAcres",
    # downstream functional network
    "TotalDownstreamMiles",
    "FreeDownstreamMiles",
    "FreePerennialDownstreamMiles",
    "FreeIntermittentDownstreamMiles",
    "FreeAlteredDownstreamMiles",
    "FreeUnalteredDownstreamMiles",
    "FreeResilientDownstreamMiles",
    "FreeColdDownstreamMiles",
    # upstream / downstream functional network
    "GainMiles",
    "PerennialGainMiles",
    "TotalNetworkMiles",
    "TotalPerennialNetworkMiles",
    # mainstem upstream network
    "TotalUpstreamMainstemMiles",
    "PerennialUpstreamMainstemMiles",
    "IntermittentUpstreamMainstemMiles",
    "AlteredUpstreamMainstemMiles",
    "UnalteredUpstreamMainstemMiles",
    "PerennialUnalteredUpstreamMainstemMiles",
    "PercentMainstemUnaltered",
    # downstream linear networks (to next barrier or outlet)
    "FreeLinearDownstreamMiles",
    "FreePerennialLinearDownstreamMiles",
    "FreeIntermittentLinearDownstreamMiles",
    "FreeAlteredLinearDownstreamMiles",
    "FreeUnalteredLinearDownstreamMiles",
    # mainstem / downstream linear network
    "MainstemGainMiles",
    "PerennialMainstemGainMiles",
    "TotalMainstemNetworkMiles",
    "TotalMainstemPerennialNetworkMiles",
]

# Per guidance from SARP, only expose upstream functional network counts
# and total upstream crossings (but not other total upstream counts),
# and exclude count of downstream crossings
UPSTREAM_COUNT_FIELDS = [
    "UpstreamWaterfalls",
    "UpstreamDams",
    "UpstreamSmallBarriers",
    "UpstreamRoadCrossings",
    "UpstreamHeadwaters",
    "TotalUpstreamRoadCrossings",
    # remaining total upstream metrics are not used
    # "TotalUpstreamWaterfalls",
    "TotalUpstreamDams",
    # "TotalUpstreamSmallBarriers",
    # "TotalUpstreamHeadwaters",
]

# Downstream linear networks (to outlet)
# these fields remain constant regardless of network type
DOWNSTREAM_LINEAR_NETWORK_FIELDS = [
    "TotalDownstreamWaterfalls",
    "TotalDownstreamDams",
    "TotalDownstreamSmallBarriers",
    # "TotalDownstreamRoadCrossings", # not used
    "MilesToOutlet",
    "InvasiveNetwork",
]

# Only present when custom prioritization is performed
CUSTOM_TIER_FIELDS = [
    "NC_tier",
    "WC_tier",
    "NCWC_tier",
    "PNC_tier",
    "PWC_tier",
    "PNCWC_tier",
    "MNC_tier",
    "MWC_tier",
    "MNCWC_tier",
]

# Only present for dams
STATE_TIER_FIELDS = [f"State_{c}" for c in CUSTOM_TIER_FIELDS]

SPECIES_HABITAT_FIELDS = [
    # species upstream / downstream habitat
    "AlewifeHabitatUpstreamMiles",
    "FreeAlewifeHabitatDownstreamMiles",
    "AmericanEelHabitatUpstreamMiles",
    "FreeAmericanEelHabitatDownstreamMiles",
    "AmericanShadHabitatUpstreamMiles",
    "FreeAmericanShadHabitatDownstreamMiles",
    "AtlanticSturgeonHabitatUpstreamMiles",
    "FreeAtlanticSturgeonHabitatDownstreamMiles",
    "BluebackHerringHabitatUpstreamMiles",
    "FreeBluebackHerringHabitatDownstreamMiles",
    "BonnevilleCutthroatTroutHabitatUpstreamMiles",
    "FreeBonnevilleCutthroatTroutHabitatDownstreamMiles",
    "BullTroutHabitatUpstreamMiles",
    "FreeBullTroutHabitatDownstreamMiles",
    "CaBaselineFishHabitatUpstreamMiles",
    "FreeCaBaselineFishHabitatDownstreamMiles",
    "ChesapeakeDiadromousHabitatUpstreamMiles",
    "FreeChesapeakeDiadromousHabitatDownstreamMiles",
    "ChinookSalmonHabitatUpstreamMiles",
    "FreeChinookSalmonHabitatDownstreamMiles",
    "ChumSalmonHabitatUpstreamMiles",
    "FreeChumSalmonHabitatDownstreamMiles",
    "CoastalCutthroatTroutHabitatUpstreamMiles",
    "FreeCoastalCutthroatTroutHabitatDownstreamMiles",
    "CohoSalmonHabitatUpstreamMiles",
    "FreeCohoSalmonHabitatDownstreamMiles",
    "EasternBrookTroutHabitatUpstreamMiles",
    "FreeEasternBrookTroutHabitatDownstreamMiles",
    "GreenSturgeonHabitatUpstreamMiles",
    "FreeGreenSturgeonHabitatDownstreamMiles",
    "HickoryShadHabitatUpstreamMiles",
    "FreeHickoryShadHabitatDownstreamMiles",
    "KokaneeHabitatUpstreamMiles",
    "FreeKokaneeHabitatDownstreamMiles",
    "PacificLampreyHabitatUpstreamMiles",
    "FreePacificLampreyHabitatDownstreamMiles",
    "PinkSalmonHabitatUpstreamMiles",
    "FreePinkSalmonHabitatDownstreamMiles",
    "RainbowTroutHabitatUpstreamMiles",
    "FreeRainbowTroutHabitatDownstreamMiles",
    "RedbandTroutHabitatUpstreamMiles",
    "FreeRedbandTroutHabitatDownstreamMiles",
    "ShortnoseSturgeonHabitatUpstreamMiles",
    "FreeShortnoseSturgeonHabitatDownstreamMiles",
    "SockeyeSalmonHabitatUpstreamMiles",
    "FreeSockeyeSalmonHabitatDownstreamMiles",
    "SouthAtlanticAnadromousHabitatUpstreamMiles",
    "FreeSouthAtlanticAnadromousHabitatDownstreamMiles",
    "SteelheadHabitatUpstreamMiles",
    "FreeSteelheadHabitatDownstreamMiles",
    "StreamnetAnadromousHabitatUpstreamMiles",
    "FreeStreamnetAnadromousHabitatDownstreamMiles",
    "StripedBassHabitatUpstreamMiles",
    "FreeStripedBassHabitatDownstreamMiles",
    "WestslopeCutthroatTroutHabitatUpstreamMiles",
    "FreeWestslopeCutthroatTroutHabitatDownstreamMiles",
    "WhiteSturgeonHabitatUpstreamMiles",
    "FreeWhiteSturgeonHabitatDownstreamMiles",
    "YellowstoneCutthroatTroutHabitatUpstreamMiles",
    "FreeYellowstoneCutthroatTroutHabitatDownstreamMiles",
]


FILTER_FIELDS = [
    "GainMilesClass",
    "MainstemGainMilesClass",
    "Condition",
    "TESppClass",
    "StateSGCNSppClass",
    "Trout",
    "SalmonidESU",
    "SalmonidESUCount",
    "StreamOrderClass",
    "AnnualFlowClass",
    "PercentUnalteredClass",
    "PercentResilientClass",
    "PercentColdClass",
    "OwnerType",
    "BarrierOwnerType",
    "Intermittent",
    "Canal",
    "FlowsToOcean",
    "DownstreamOceanMilesClass",
    "DownstreamOceanBarriersClass",
    "FlowsToGreatLakes",
    "DownstreamGreatLakesMilesClass",
    "DownstreamGreatLakesBarriersClass",
    "InvasiveNetwork",
    "CoastalHUC8",
    "PassageFacilityClass",
    "DisadvantagedCommunity",
    "WildScenicRiver",
    "Wilderness",
    "FishHabitatPartnership",
    "UpstreamUnalteredWaterbodyClass",
    "UpstreamUnalteredWetlandClass",
    "DiadromousHabitat",
]

DAM_FILTER_FIELDS = FILTER_FIELDS + [
    "Hazard",
    "FERCRegulated",
    "StateRegulated",
    "NRCSDam",
    "WaterRight",
    "Passability",
    "FeasibilityClass",
    "Purpose",
    "HeightClass",
    "YearCompletedClass",
    "LowheadDam",
    "WaterbodySizeClass",
    "Removed",
    "CostClass",
    "IsPriority",
]
DAM_FILTER_FIELD_MAP = {f.lower(): f for f in DAM_FILTER_FIELDS}

SB_FILTER_FIELDS = FILTER_FIELDS + [
    "BarrierSeverity",
    "Constriction",
    "RoadType",
    "CrossingType",
    "Removed",
    "IsPriority",
]
SB_FILTER_FIELD_MAP = {f.lower(): f for f in SB_FILTER_FIELDS}

# BarrierSeverity included for API but not filtering
COMBINED_FILTER_FIELDS = [c for c in unique(DAM_FILTER_FIELDS + SB_FILTER_FIELDS) if not c == "BarrierSeverity"]
COMBINED_FILTER_FIELD_MAP = {f.lower(): f for f in COMBINED_FILTER_FIELDS}

ROAD_CROSSING_FILTER_FIELDS = [
    "StreamOrderClass",
    "AnnualFlowClass",
    "Intermittent",
    "Canal",
    "CrossingType",
    "OwnerType",
    "BarrierOwnerType",
    "TESppClass",
    "StateSGCNSppClass",
    "Trout",
    "SalmonidESU",
    "SalmonidESUCount",
    "DisadvantagedCommunity",
    "FishHabitatPartnership",
    "Surveyed",
    "OnNetwork",
    "WildScenicRiver",
    "Wilderness",
    "CoastalHUC8",
    "DiadromousHabitat",
    "FlowsToOcean",
    "FlowsToGreatLakes",
    # "SlopeClass",
]
ROAD_CROSSING_FILTER_FIELD_MAP = {f.lower(): f for f in ROAD_CROSSING_FILTER_FIELDS}


### Fields used for export
# common API fields
GENERAL_API_FIELDS1 = [
    "lat",
    "lon",
    "Name",
    "SARPID",
    "Source",
    "SourceID",
    "Snapped",
    "NHDPlusID",
    "River",
    "StreamSizeClass",
    "FlowsToOcean",
    "FlowsToGreatLakes",
]

GENERAL_API_FIELDS2 = (
    [
        "Removed",
        "YearRemoved",
        "Condition",
        "PassageFacility",
        "TESpp",
        "StateSGCNSpp",
        "RegionalSGCNSpp",
        "Trout",
        "DiadromousHabitat",
        "OwnerType",
        "BarrierOwnerType",
        "ProtectedLand",
        "SourceLink",
        "EJTract",
        "EJTribal",
        "NativeTerritories",
        "WildScenicRiver",
        "Wilderness",
        "FishHabitatPartnership",
        # Watershed names
        "Basin",
        "Subbasin",
        "Subwatershed",
    ]
    + UNIT_FIELDS
    + ["Excluded", "Invasive", "OnLoop"]
    + METRIC_FIELDS
    + UPSTREAM_COUNT_FIELDS
    + DOWNSTREAM_LINEAR_NETWORK_FIELDS
    + SPECIES_HABITAT_FIELDS
)

# This order should mostly match FIELD_DEFINITIONS below
# NOTE: make sure the resultant set is unique!
DAM_CORE_FIELDS = (
    GENERAL_API_FIELDS1
    + [
        "NIDID",
        "NIDFederalID",
        "PartnerID",
        "Estimated",
        "AnnualVelocity",
        "AnnualFlow",
        "TotDASqKm",
        "YearCompleted",
        "FERCRegulated",
        "StateRegulated",
        "NRCSDam",
        "FedRegulatoryAgency",
        "WaterRight",
        "IsPriority",
        "Height",
        "Length",
        "Width",
        "Hazard",
        "Construction",
        "Purpose",
        "Passability",
        "FishScreen",
        "ScreenType",
        "Feasibility",
        "Recon",
        "Diversion",
        "LowheadDam",
        "StorageVolume",
        "WaterbodyAcres",
        "Fatality",
    ]
    + GENERAL_API_FIELDS2
)

DAM_CORE_FIELDS = unique(DAM_CORE_FIELDS)

# Internal API includes tiers

DAM_EXPORT_FIELDS = unique(DAM_CORE_FIELDS + STATE_TIER_FIELDS + CUSTOM_TIER_FIELDS + ["URL"])

DAM_API_FIELDS = unique(
    DAM_CORE_FIELDS
    + STATE_TIER_FIELDS
    + DAM_FILTER_FIELDS
    + [
        "upNetID",
        "downNetID",
        "COUNTYFIPS",
        "Unranked",
        "in_network_type",
        # NOTE: cost columns are excluded from download
        "CostLower",
        "CostMean",
        "CostUpper",
        # Size class is used for display
        "WaterbodySizeClass",
    ]
)

# Public API does not include tier or filter fields
DAM_PUBLIC_EXPORT_FIELDS = DAM_CORE_FIELDS + ["URL"]


DAM_TILE_FILTER_FIELDS = unique(
    DAM_FILTER_FIELDS
    + [
        f
        for f in UNIT_FIELDS
        if f
        not in {
            "HUC2",
            "HUC6",
            "HUC8",
            "HUC10",
        }
    ]
)


SB_CORE_FIELDS = (
    GENERAL_API_FIELDS1
    + [
        "CrossingCode",
        "PartnerID",
        "NearestCrossingID",
        "NearestUSGSCrossingID",
        "AnnualVelocity",
        "AnnualFlow",
        "TotDASqKm",
        "Road",
        "RoadType",
        "CrossingType",
        "Constriction",
        "PotentialProject",
        "BarrierSeverity",
        "SARP_Score",
        "ProtocolUsed",
        "Recon",
        "IsPriority",
    ]
    + GENERAL_API_FIELDS2
)

SB_CORE_FIELDS = unique(SB_CORE_FIELDS)

# NOTE: state tiers are excluded based on SARP direction
SB_EXPORT_FIELDS = unique(SB_CORE_FIELDS + CUSTOM_TIER_FIELDS + ["URL"])

SB_API_FIELDS = unique(
    SB_CORE_FIELDS
    + SB_FILTER_FIELDS
    + ["upNetID", "downNetID", "COUNTYFIPS", "Unranked", "in_network_type", "attachments"]
)

# Public API does not include tier fields
SB_PUBLIC_EXPORT_FIELDS = SB_CORE_FIELDS + ["URL"]


SB_TILE_FILTER_FIELDS = unique(
    SB_FILTER_FIELDS
    + [
        f
        for f in UNIT_FIELDS
        if f
        not in {
            "HUC2",
            "HUC6",
            "HUC8",
            "HUC10",
        }
    ]
)


COMBINED_API_FIELDS = [
    c for c in unique(["BarrierType"] + DAM_API_FIELDS + SB_API_FIELDS) if c not in STATE_TIER_FIELDS
]

COMBINED_EXPORT_FIELDS = [
    c for c in unique(["BarrierType"] + DAM_EXPORT_FIELDS + SB_EXPORT_FIELDS) if c not in STATE_TIER_FIELDS
]

COMBINED_TILE_FILTER_FIELDS = [
    c for c in unique(DAM_TILE_FILTER_FIELDS + SB_TILE_FILTER_FIELDS) if not c == "BarrierSeverity"
]


ROAD_CROSSING_CORE_FIELDS = (
    GENERAL_API_FIELDS1
    + [
        "CrossingCode",
        "USGSCrossingID",  # original USGS ID, blank for USFS crossings
        # for parity with small barriers
        "Removed",
        "YearRemoved",
        "Constriction",
        "PotentialProject",
        "BarrierSeverity",
        "SARP_Score",
        "ProtocolUsed",
        "Excluded",
        "Invasive",
        "OnLoop",
        # other standard fields
        "AnnualVelocity",
        "AnnualFlow",
        "TotDASqKm",
        "TESpp",
        "StateSGCNSpp",
        "RegionalSGCNSpp",
        "DiadromousHabitat",
        "Trout",
        "OwnerType",
        "BarrierOwnerType",
        "ProtectedLand",
        "EJTract",
        "EJTribal",
        "NativeTerritories",
        "WildScenicRiver",
        "Wilderness",
        "SalmonidESU",
        "FishHabitatPartnership",
        # Watershed names
        "Basin",
        "Subbasin",
        "Subwatershed",
        "CrossingType",
        "Intermittent",
        "Canal",
        "StreamOrder",
        # specific to crossings
        "Surveyed",
        "OnNetwork",
    ]
    + UNIT_FIELDS
)

ROAD_CROSSING_CORE_FIELDS = unique(ROAD_CROSSING_CORE_FIELDS)

# include COUNTYFIPS, for download of road crossings by county
ROAD_CROSSING_API_FIELDS = unique(ROAD_CROSSING_CORE_FIELDS + ["COUNTYFIPS"] + ROAD_CROSSING_FILTER_FIELDS)

ROAD_CROSSING_EXPORT_FIELDS = ROAD_CROSSING_CORE_FIELDS

# only need HUC12 for filtering
ROAD_CROSSING_TILE_FILTER_FIELDS = unique(
    ROAD_CROSSING_FILTER_FIELDS
    + [
        f
        for f in UNIT_FIELDS
        if f
        not in {
            "HUC2",
            "HUC6",
            "HUC8",
            "HUC10",
        }
    ]
)


WF_CORE_FIELDS = (
    GENERAL_API_FIELDS1
    + [
        "PartnerID",
        "FallType",
        "AnnualVelocity",
        "AnnualFlow",
        "TotDASqKm",
        "Passability",
        # from GENERAL_API_FIELDS2
        "TESpp",
        "StateSGCNSpp",
        "RegionalSGCNSpp",
        "DiadromousHabitat",
        "Trout",
        "SalmonidESU",
        "FishHabitatPartnership",
        "OwnerType",
        "ProtectedLand",
        "WildScenicRiver",
        "Wilderness",
        # Watershed names
        "Basin",
        "Subbasin",
        "Subwatershed",
        "Excluded",
        "OnLoop",
        "Invasive",
    ]
    + UNIT_FIELDS
    + METRIC_FIELDS
    + UPSTREAM_COUNT_FIELDS
    + DOWNSTREAM_LINEAR_NETWORK_FIELDS
    + SPECIES_HABITAT_FIELDS
)
WF_CORE_FIELDS = unique(WF_CORE_FIELDS)

# network_type resolves to a single row; API has one row per waterfall per network type
WF_API_FIELDS = unique(WF_CORE_FIELDS + ["network_type", "in_network_type"])


BARRIER_SEARCH_RESULT_FIELDS = [
    "SARPID",
    "Name",
    "River",
    "State",
    "BarrierType",
    "lat",
    "lon",
]


# fields returned by map unit search / details APIs
SUMMARY_UNIT_FIELDS = [
    "layer",
    "id",
    "name",
    "bbox",
    "state",
    "dams",
    "ranked_dams",
    "recon_dams",
    "removed_dams",
    "removed_dams_gain_miles",
    "removed_dams_by_year",
    "small_barriers",
    "ranked_small_barriers",
    "total_small_barriers",
    "removed_small_barriers",
    "removed_small_barriers_gain_miles",
    "removed_small_barriers_by_year",
    "ranked_largefish_barriers_dams",
    "ranked_largefish_barriers_small_barriers",
    "ranked_smallfish_barriers_dams",
    "ranked_smallfish_barriers_small_barriers",
    "total_road_crossings",
    "unsurveyed_road_crossings",
]


### Domains for coded values in exported data
BARRIERTYPE_DOMAIN = {
    "dams": "Dam",
    "small_barriers": "Assessed road-related barrier",
}


# typos fixed and trailing periods removed
RECON_DOMAIN = {
    0: "Not yet evaluated",  # added
    1: "Good candidate for removal. Move forward with landowner contact",  # expanded acronym
    2: "Dam needs follow-up with landowner",
    3: "Removal is unlikely.  Social conditions unfavorable",
    4: "Removal is extremely infeasible.  Large reservoirs, etc.",
    5: "Barrier may be removed or error",
    6: "Infeasible in short term via landowner contact",
    7: "Barrier was deliberately removed",
    8: "Location is incorrect and needs to be moved",  # fixed phrasing
    9: "Breached and no impoundment visible",
    10: "Was once considered, need to revisit",
    11: "Removal planned",
    13: "Unsure, need second opinion",
    14: "Good candidate for further exploration - dam appears to be in poor condition",  # new phrasing from Kat
    15: "No conservation benefit",
    16: "Invasive species barrier",
    17: "Risky for mussels",
    18: "Barrier failed",
    19: "Proposed dam",
    20: "Farm pond - no conservation benefit",
    21: "Potential thermal issues",
    22: "Removal unlikely; fish passage installed",
    23: "Duplicate fish passage project structure",
    24: "Treatment completed (removal vs fishway unspecified)",
    25: "Treatment planned",
}

# Created here to capture values below
FEASIBILITY_DOMAIN = {
    -1: "Not applicable (road-related barrier)",
    0: "Not assessed",
    1: "Not feasible",
    2: "Likely infeasible",
    3: "Possibly feasible",
    4: "Likely feasible",
    5: "No conservation benefit",
    11: "Fish passage installed",  # code no longer used
    12: "Removal planned",  # code no longer used; superseded by 16
    13: "Breached with full flow",
    14: "Fish passage installed for conservation benefit",
    15: "Treatment complete (removal vs fishway unspecified)",
    16: "Removal or fish passage planned",
    # not shown to user (filtered out for other reasons)S
    6: "Unknown",
    7: "Error",
    8: "Dam removed for conservation benefit",
    9: "Invasive species barrier",
    10: "Proposed dam",  # code no longer used
}


PURPOSE_DOMAIN = {
    -1: "Not applicable (road-related barrier)",
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
    -1: "Not applicable  (road-related barrier)",
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
    0: "Unknown",
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
    0: "Not applicable (road-related barrier)",
    1: "Unknown",
    2: "< 5",
    3: "5 - 10",
    4: "10 - 25",
    5: "25 - 50",
    6: "50 - 100",
    7: ">= 100",
}

YEARCOMPLETED_DOMAIN = {
    0: "Not applicable (road-related barrier)",
    1: "Unknown",
    2: "< 10 years",
    3: "10 - 29 years",
    4: "30 - 49 years",
    5: "50 - 69 years",
    6: "70 - 99 years",
    7: ">= 100 years",
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

DOWNSTREAM_OCEAN_MILES_DOMAIN = {
    0: "not on aquatic network known to flow into the ocean",
    1: "< 1 miles",
    2: "1 - 5 miles",
    3: "5 - 10 miles",
    4: "10 - 25 miles",
    5: "25 - 100 miles",
    6: "100 - 250 miles",
    7: "250 - 500 miles",
    8: "500 - 1,000 miles",
    9: ">= 1,000 miles",
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

# NOTE: barrier count depends on network type
DOWNSTREAM_OCEAN_BARRIERS_DOMAIN = {
    0: "not on aquatic network known to flow into the ocean",
    1: "0",
    2: "1",
    3: "2-4",
    4: "5-9",
    5: ">= 10",
}


WATERBODY_SIZECLASS_DOMAIN = {
    0: "Not associated with a pond or lake",
    1: "Pond (< 2.5 acres)",
    2: "Very small lake (2.5 - 24.9 acres)",
    3: "Small lake (25 - 249 acres)",
    4: "Medium lake (250 - 2,499 acres)",
    5: "Large lake (>= 2,500 acres)",
}


CROSSING_TYPE_DOMAIN = {
    -1: "Not applicable (dam)",
    0: "Unknown",
    1: "Inaccessible",
    2: "No crossing",
    3: "No upstream habitat",
    4: "Not a barrier",
    5: "Bridge",
    6: "Ford / low water crossing",
    7: "Natural ford",
    8: "Culvert",
    9: "Tide gate",
    10: "Buried stream",
    98: "Assumed bridge",  # only for road crossings
    99: "Assumed culvert",  # only for road crossings
}


CONSTRICTION_DOMAIN = {
    -1: "Not applicable (dam)",
    0: "Unknown",
    1: "Spans full channel & banks",
    2: "Spans only bankfull/active channel",
    3: "Constricted to some degree",
    4: "Minor",
    5: "Moderate",
    6: "Severe",
}

DIVERSION_DOMAIN = {
    -1: "Not applicable (road-related barrier)",
    0: "Unknown",
    1: "Yes",
    2: "No",
}

# NOTE: values do not match original domain; they are recoded
LOWHEADDAM_DOMAIN = {
    -1: "Not applicable (road-related barrier)",
    0: "Unknown",
    1: "Yes",
    2: "Likely",
    3: "No",
}

FISHSCREEN_DOMAIN = {
    -1: "Not applicable (road-related barrier)",
    0: "Unknown",
    1: "Yes",
    2: "No",
}

SCREENTYPE_DOMAIN = {
    -1: "Not applicable (road-related barrier)",
    0: "Unknown",
    1: "Horizontal",
    2: "Vertical",
    3: "Cone",
    4: "Pipe",
    5: "Drum",
    6: "Other",
    7: "No screen",
}


BARRIER_SEVERITY_DOMAIN = {
    -1: "Not applicable (dam)",
    0: "Unknown",
    1: "Complete barrier",
    2: "Moderate barrier",
    3: "Indeterminate barrier",
    4: "Minor barrier",
    5: "Insignificant barrier",
    6: "Likely barrier",
    7: "Barrier - unknown severity",
    8: "No barrier",
    9: "No upstream habitat",
}

PASSABILITY_DOMAIN = {
    0: "Unknown",
    1: "Complete barrier",
    2: "Partial passability",
    3: "Partial passability - non salmonid",
    4: "Partial passability - salmonid",
    5: "Seasonably passable - non salmonid",
    6: "Seasonably passable - salmonid",
    7: "No barrier",
}

FERCREGULATED_DOMAIN = {
    -1: "Not applicable",  # small barriers only
    0: "Unknown",
    1: "Yes",
    2: "Preliminary permit",
    3: "Pending permit",
    4: "Exempt",
    5: "No",
}

STATE_REGULATED_DOMAIN = {
    -1: "Not applicable",  # small barriers only
    0: "Unknown",
    1: "Yes",
    2: "No",
}

NRCSDAM_DOMAIN = {
    -1: "Not applicable",  # small barriers only
    0: "Unknown",  # not used
    1: "Yes",
    2: "No",
}


WATER_RIGHT_DOMAIN = {
    -1: "Not applicable",  # small barriers only
    0: "Unknown",
    1: "Yes",
    2: "No",
}

HAZARD_DOMAIN = {
    -1: "Not applicable",
    0: "Unknown",
    1: "High",
    2: "Significant",
    3: "Intermediate",
    4: "Low",
}


ROAD_TYPE_DOMAIN = {
    -1: "Not applicable (dam)",
    0: "Unknown",
    1: "Unpaved",
    2: "Paved",
    3: "Railroad",
}


OWNERTYPE_DOMAIN = {
    0: "",  # most likely private land, but just don't say anything
    1: "Bureau of Land Management",
    2: "Bureau of Reclamation",
    3: "Department of Defense",
    4: "National Park Service",
    5: "US Fish and Wildlife Service land",
    6: "USDA Forest Service (ownership boundary)",
    7: "USDA Forest Service (admin boundary)",
    8: "Other Federal land",
    9: "State land",
    10: "Joint Ownership or Regional land",
    11: "Native American land",
    12: "Private easement",
    13: "Other private conservation land",
}


BARRIEROWNERTYPE_DOMAIN = {
    0: "Unknown",
    1: "Federal",
    2: "USDA Forest Service",
    3: "State",
    4: "Local government",
    5: "Public utility",
    6: "Irrigation district",
    7: "Tribal",
    8: "Private",
}

WILD_SCENIC_RIVER_DOMAIN = {
    0: "",  # indicates not a wild & scenic river
    1: "Designated corridor",  # "within a designated Wild & Scenic River corridor",
    2: "Eligible / suitable corridor",  # "within an eligible / suitable Wild & Scenic River corridor",
    3: "Near designated river",  # "within a 250 meter buffer around designated Wild & Scenic Rivers outside a designated or eligible / suitable corridor",
    4: "Near eligible / suitable river",  # "within a 250 meter buffer around eligible / suitable Wild & Scenic Rivers outside a designated or eligible / suitable corridor",
}

BOOLEAN_DOMAIN = {False: "no", True: "yes"}

PASSAGEFACILITY_CLASS_DOMAIN = {
    0: "No known fish passage structure",
    1: "Fish passage structure present",
}

PASSAGEFACILITY_DOMAIN = {
    0: "Unknown or none",
    1: "Trap & truck",
    2: "Fish ladder - unspecified",
    3: "Locking",
    4: "Rock rapids",
    5: "Eelway",
    6: "Alaskan steeppass",
    7: "Herring passage",
    8: "Reservation",
    9: "Exemption",
    10: "Notch",
    11: "Denil fishway",
    12: "Fish lift",
    13: "Partial breach",
    14: "Removal",
    15: "Pool and weir fishway",
    16: "Vertical slot fishway",
    17: "Nature-like fishway",
    18: "Bypass channel fishway",
    19: "Crossvane",
    20: "Screen bypass",
    21: "Fishway unspecified",
    22: "Roughened channel",
    23: "Hybrid / multiple",
    24: "None (confirmed)",
    25: "Submerged orifice",
    26: "Other",
}

MANUALREVIEW_DOMAIN = {
    0: "",
    1: "",
    2: "NABD Dams",
    4: "Onstream checked by SARP",
    5: "Offstream checked by SARP - do not snap",
    6: "Delete - Error, checked by SARP",
    7: "Assumed offstream, >100 meters from flowline",
    8: "Removed for conservation",
    9: "Assumed offstream, >200 meters from flowline",
    10: "Invasive barriers, do not prioritize",
    11: "Delete (Duplicate)",
    13: "Onstream checked by SARP - Did not have to move",
    14: "Delete (No Dam)",
    15: "Onstream - moved to correct location",
    20: "Estimated dam",
    21: "Dam likely off network (source from Amber Ignatius ACF project)",
}


STREAMTYPE_DOMAIN = {
    0: "Not on a stream / river",  # not snapped to flowline,
    1: "Perennial stream / river",
    2: "Intermittent stream / river",
    3: "Artificial path / unspecified connector",
    4: "Canal / ditch",
    5: "Pipeline / underground connector",
}

BOOLEAN_OFFNETWORK_DOMAIN = {-1: "off network", 0: "no", 1: "yes"}

INTERMITTENT_DOMAIN = {
    -1: "off network",
    0: "stream is not likely intermittent / ephemeral",
    1: "stream is likely intermittent / ephemeral",
}

CANAL_DOMAIN = {
    -1: "off network",
    0: "stream is not identified by NHD as a canal/ditch",
    1: "stream is identified by NHD as a canal/ditch",
}


# this domain is created dynamically in calculate_spp_stats and needs to be updated
# whenever species data are reprocessed
# IMPORTANT: the UI uses a domain for individual values
TROUT_DOMAIN = {
    "1": "Apache trout",
    "1,3": "Apache trout, Gila trout",
    "2": "cutthroat trout",
    "2,4": "cutthroat trout, redband trout",
    "2,4,5": "bull trout, cutthroat trout, redband trout",
    "2,5": "bull trout, cutthroat trout",
    "2,5,7": "bull trout, cutthroat trout, lake trout",
    "2,7": "cutthroat trout, lake trout",
    "3": "Gila trout",
    "4": "redband trout",
    "4,5": "bull trout, redband trout",
    "5": "bull trout",
    "6": "brook trout",
    "": "not recorded",
}

DIADROMOUS_HABITAT_DOMAIN = {
    -1: "off network",
    0: "not located on a reach associated with anadromous / catadromous species habitat",
    1: "located on a reach associated with anadromous / catadromous species habitat",
}

SURVEYED_CROSSING_DOMAIN = {0: "not likely", 1: "yes", 2: "likely"}

IS_PRIORITY_DOMAIN = {
    0: "not identified as a priority by resource managers",
    1: "identified as a priority by resource managers",
}

# NOTE: this is not available in the public download
ACTIVE_LIST_DOMAIN = {0: "Not reviewed", 1: "Yes", 2: "No - dropped", 3: "In queue", 5: "Unsure"}


# symbol domain - not used but included here as a reference for the codes used
# SYMBOL_DOMAIN = {
#     0: "regular barrier",
#     1: "unsnapped",
#     2: "assessed and not a barrier (fully passable)",
#     3: "invasive barrier",
#     4: "no-structure diversion",
# }


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


FISH_HABITAT_PARTNERSHIPS = {
    "ACFHP": "Atlantic Coastal Fish Habitat Partnership",
    "CFPF": "California Fish Passage Forum",
    "DARE": "Driftless Area Restoration Effort",
    "DFHP": "Desert Fish Habitat Partnership",
    "EBTJV": "Eastern Brook Trout Joint Venture",
    "FFP": "Farmers & Fishers Partnership",
    "GLBFHP": "Great Lakes Basin Fish Habitat Partnership",
    "GPFHP": "Great Plains Fish Habitat Partnership",
    "HFHP": "Hawaii Fish Habitat Partnership",
    "KPFHP": "Kenai Peninsula Fish Habitat Partnership",
    "MSBSHP": "Mat-Su Basin Salmon Habitat Partnership",
    "MGLP": "Midwest Glacial Lakes Partnership",
    "ORBFHP": "Ohio River Basin Fish Habitat Partnership",
    "PMEP": "Pacific Marine & Estuarine Fish Habitat Partnership",
    "SARP": "Southeast Aquatic Resources Partnership",
    "SEAFHP": "Southeast Alaska Fish Habitat Partnership",
    "SWASHP": "Southwest Alaska Salmon Habitat Partnership",
    "WNTI": "Western Native Trout Initiative",
}


# mapping of field name to domains
DOMAINS = {
    "BarrierType": BARRIERTYPE_DOMAIN,
    "State": STATES,
    "HasNetwork": BOOLEAN_DOMAIN,
    "OnLoop": BOOLEAN_DOMAIN,
    "Excluded": BOOLEAN_DOMAIN,
    "Ranked": BOOLEAN_DOMAIN,
    "Invasive": BOOLEAN_DOMAIN,
    "Intermittent": INTERMITTENT_DOMAIN,
    "Canal": CANAL_DOMAIN,
    "FlowsToOcean": BOOLEAN_OFFNETWORK_DOMAIN,
    "FlowsToGreatLakes": BOOLEAN_OFFNETWORK_DOMAIN,
    "InvasiveNetwork": BOOLEAN_OFFNETWORK_DOMAIN,
    "OwnerType": OWNERTYPE_DOMAIN,
    "BarrierOwnerType": BARRIEROWNERTYPE_DOMAIN,
    "ProtectedLand": BOOLEAN_DOMAIN,
    "ManualReview": MANUALREVIEW_DOMAIN,
    "Recon": RECON_DOMAIN,
    "Condition": CONDITION_DOMAIN,
    "Trout": TROUT_DOMAIN,
    "Removed": BOOLEAN_DOMAIN,
    "EJTract": BOOLEAN_DOMAIN,
    "EJTribal": BOOLEAN_DOMAIN,
    "DiadromousHabitat": DIADROMOUS_HABITAT_DOMAIN,
    "WildScenicRiver": WILD_SCENIC_RIVER_DOMAIN,
    "Wilderness": BOOLEAN_DOMAIN,
    # dam fields
    "FERCRegulated": FERCREGULATED_DOMAIN,
    "StateRegulated": STATE_REGULATED_DOMAIN,
    "NRCSDam": NRCSDAM_DOMAIN,
    "WaterRight": WATER_RIGHT_DOMAIN,
    "Hazard": HAZARD_DOMAIN,
    "Construction": CONSTRUCTION_DOMAIN,
    "Purpose": PURPOSE_DOMAIN,
    "Feasibility": FEASIBILITY_DOMAIN,
    "Passability": PASSABILITY_DOMAIN,
    "PassageFacility": PASSAGEFACILITY_DOMAIN,
    "Diversion": DIVERSION_DOMAIN,
    "LowheadDam": LOWHEADDAM_DOMAIN,
    "FishScreen": FISHSCREEN_DOMAIN,
    "ScreenType": SCREENTYPE_DOMAIN,
    "WaterbodySizeClass": WATERBODY_SIZECLASS_DOMAIN,
    "Estimated": BOOLEAN_DOMAIN,
    "IsPriority": IS_PRIORITY_DOMAIN,
    # barrier fields
    "BarrierSeverity": BARRIER_SEVERITY_DOMAIN,
    "Constriction": CONSTRICTION_DOMAIN,
    "CrossingType": CROSSING_TYPE_DOMAIN,
    "RoadType": ROAD_TYPE_DOMAIN,
    # crossing fields
    "Surveyed": SURVEYED_CROSSING_DOMAIN,
    "OnNetwork": BOOLEAN_DOMAIN,
    # extra fields added for export for Kat
    "ActiveList": ACTIVE_LIST_DOMAIN,
    "KeepOnActiveList": BOOLEAN_DOMAIN,
}

# domain values are stored as comma-delimited values in a string field
MULTI_VALUE_DOMAINS = {"FishHabitatPartnership": FISH_HABITAT_PARTNERSHIPS}


def verify_domains(df):
    failed = False
    for col in df.columns.intersection(DOMAINS.keys()):
        diff = set(df[col].unique()).difference(DOMAINS[col].keys())
        if diff:
            print(f"Missing values from domain lookup: {col}: {diff}")
            failed = True

    for col in df.columns.intersection(MULTI_VALUE_DOMAINS.keys()):
        diff = set(",".join(df.loc[df[col] != "", col].unique()).split(",")).difference(MULTI_VALUE_DOMAINS[col].keys())
        if diff:
            print(f"Missing values from multi-value domain lookup: {col}: {diff}")
            failed = True

    if failed:
        raise ValueError("ERROR: stopping; one or more domain fields includes values not present in domain lookup")


# Lookup of field to description, for download / APIs
# Note: replace {type} with appropriate type when rendering
FIELD_DEFINITIONS = {
    # general fields
    "BarrierType": "Type of barrier",
    "lat": "Latitude in WGS84 geographic coordinates.",
    "lon": "Longitude in WGS84 geographic coordinates.",
    "Name": "{type} name, if available.",
    "SARPID": "SARP Identifier.",
    "River": "River or stream name where {type} occurs, if available.",
    "Source": "Source of this record in the inventory.",
    "SourceID": "Identifier of this {type} in the source database",
    "PartnerID": "Identifier used by local partners for this {type}",
    # dam-specific fields
    "NIDID": "National Inventory of Dams Identifier (legacy ID); this value was provided in earlier versions of NID or partner databases and may no longer match the latest ID, and may also have duplicate IDs or incorrectly-associated IDs.",
    "NIDFederalID": "National Inventory of Dams Federal Identifier (new ID) that can be used to join to the latest version of NID.",
    "SourceLink": "Link to additional information about this {type} provided by the data source.",
    "FERCRegulated": "Identifies if the {type} is regulated by the Federal Energy Regulatory Commission, if known.",
    "StateRegulated": "Identifies if the {type} is regulated at the state level, if known.",
    "NRCSDam": "Identifies if the {type} is a flood control dam constructed in partnership with the USDA Natural Resources Conservation Service.",
    "FedRegulatoryAgency": "Identifies the federal regulatory agency for this {type}, if known",
    "WaterRight": "Identifies if the {type} has an associated water right, if known.",
    "IsPriority": "Indicates if the {type} has been identified as a priority by resource managers, if known.",
    "Estimated": "Dam represents an estimated dam location based on NHD high resolution waterbodies or other information.",
    "YearCompleted": "year that construction was completed, if available.  0 = data not available.",
    "Removed": "Identifies if the {type} has been removed for conservation, if known.  Removed barriers will not have values present for all fields.",
    "YearRemoved": "year that barrier was removed or mitigated, if available.  All barriers removed prior to 2000 or where YearRemoved is unknown were lumped together for the network analysis.  0 = data not available or not removed / mitigated.",
    "Height": "{type} height in feet, if available.  0 = data not available.",
    "Length": "{type} length in feet, if available.  0 = data not available.",
    "Width": "{type} width in feet, if available.  0 = data not available.",
    "Hazard": "Hazard rating of this {type}, if known.",
    "Construction": "material used in {type} construction, if known.",
    "Purpose": "primary purpose of {type}, if known.",
    "PassageFacility": "type of fish passage facility, if known.",
    "FishScreen": "Whether or not a fish screen is present, if known.",
    "ScreenType": "Type of fish screen, if known.",
    "Feasibility": "feasibility of {type} removal, based on reconnaissance.  Note: reconnaissance information is available only for a small number of {type}s.",
    "Diversion": "Identifies if dam is known to be a diversion.  Note: diversion information is available only for a small number of dams.",
    "LowheadDam": "Identifies if dam is known or estimated to be a lowhead dam.  Note: lowhead dam information is available only for a small number of dams.",
    "StorageVolume": "Identifies the reported normal storage volume (acre/feet) of the impounded waterbody, from NID NormStor attribute, if known.  ",
    "WaterbodyAcres": "area in acres of waterbody associated with dam.  -1 = no associated waterbody",
    "Fatality": "number of fatalities recorded at this location from Locations of Fatalities at Submerged Hydraulic Jumps (https://krcproject.groups.et.byu.net/browse.php)",
    # barrier-specific fields
    "CrossingCode": "crossing identifier.",
    "NearestCrossingID": "The SARPID of the nearest road/stream crossing point, if any are found within 50 meters",
    "NearestUSGSCrossingID": "The ID of the nearest road/stream crossing point in the USGS Database of Stream Crossings in the United States (2022), if any are found within 50 meters.  Will be blank for crossings from other sources",
    "Road": "road name, if available.",
    "RoadType": "type of road, if available.",
    "CrossingType": "type of road / stream crossing, if known.",
    "Constriction": "type of constriction at road / stream crossing, if known.",
    "PotentialProject": "reconnaissance information about the crossing, including severity of the barrier and / or potential for removal project.",
    "BarrierSeverity": "barrier severity of the {type}, if known.   Note: assessment dates are not known.",
    "SARP_Score": "The best way to consider the aquatic passability scores is that they represent the degree to which crossings deviate from an ideal crossing. We assume that those crossings that are very close to the ideal (scores > 0.6) will present only a minor or insignificant barrier to aquatic organisms. Those structures that are farthest from the ideal (scores < 0.4) are likely to be either significant or severe barriers. These are, however, arbitrary distinctions imposed on a continuous scoring system and should be used with that in mind. -1 = not available.",
    "ProtocolUsed": "Name of survey protocol used",
    # crossing-specific fields
    "Surveyed": "Indicates if the crossing has likely been surveyed according to assessed road/stream crossing data.  'yes': inventoried barrier was linked to crossing at time of survey, 'likely': inventoried barrier within 50m, 'not likely': no inventoried barrier within 50m.",
    "OnNetwork": "if yes, this {type} was snapped to the aquatic network and does not occur on a loop within the NHD High Resolution aquatic network and is not snapped to an off-network canal or ditch; if no, this {type} is either on a loop or an off-network canal or ditch considered off-network for purposes of network analysis and ranking",
    "USGSCrossingID": "The ID of the road/stream crossing point in the USGS Database of Stream Crossings in the United States (2022); will be blank for crossings from other sources.",
    # other general fields
    "Recon": "Field reconnaissance notes, if available.",
    "Passability": "passability of the {type}, if known.   Note: assessment dates are not known.",
    "Condition": "Condition of the {type} as of last assessment, if known. Note: assessment dates are not known.",
    "Snapped": "Indicates if the {type} was snapped to a flowline.  Note: not all barriers snapped to flowlines are used in the network connectivity analysis.",
    "NHDPlusID": "Unique NHD Plus High Resolution flowline identifier to which this {type} is snapped.  -1 = not snapped to a flowline.  Note: not all barriers snapped to flowlines are used in the network connectivity analysis.",
    "StreamSizeClass": "Stream size class based on total catchment drainage area in acres.  1a: <2,471 acres, 1b: 2,471-24,709 acres, 2: 24,710-127,999 acres, 3a: 128,000-640,001 acres, 3b: 640,002-2,471,049 acres, 4: 2,471,050-6,177,624 acres, 5: >= 6,177,625 acres.",
    "TotDASqKm": "Total drainage area in square kilometers at the downstream end of the NHD Plus High Resolution flowline to which this {type} has been snapped, as reported by NHD.  -1 if not snapped to flowline or otherwise not available",
    "AnnualFlow": "Annual flow at the downstream end of the NHD Plus High Resolution flowline to which this {type} has been snapped, in cubic feet per second.  -1 if not snapped to flowline or otherwise not available",
    "AnnualVelocity": "Annual velocity at the downstream end of the NHD Plus High Resolution flowline to which this {type} has been snapped, in square feet per second.  -1 if not snapped to flowline or otherwise not available",
    "TESpp": "Number of federally-listed threatened or endangered aquatic species, compiled from element occurrence data within the same subwatershed (HUC12) as the {type}. Note: rare species information is based on occurrences within the same subwatershed as the barrier.  These species may or may not be impacted by this {type}.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.",
    "StateSGCNSpp": "Number of state-listed Species of Greatest Conservation Need (SGCN), compiled from element occurrence data within the same subwatershed (HUC12) as the {type}.  Note: rare species information is based on occurrences within the same subwatershed as the {type}.  These species may or may not be impacted by this {type}.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.",
    "RegionalSGCNSpp": "Number of regionally-listed Species of Greatest Conservation Need (SGCN), compiled from element occurrence data within the same subwatershed (HUC12) as the {type}.  Note: rare species information is based on occurrences within the same subwatershed as the {type}.  These species may or may not be impacted by this {type}.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.",
    "Trout": "Identifies one or more interior or eastern native trout species (Apache, brook, bull, cutthroat, Gila, lake, and redband) that are present within the same subwatershed (HUC12) as the {type} based on in available natural heritage data and other data sources.  Note: absence means that occurrences were not present in the available natural heritage data and should not be interpreted as true absences.",
    "DiadromousHabitat": "Indicates if the {type} occurs on a stream reach associated with the habitat of one or more anadromous or catadromous species, based on multiple data sources.  Please see https://aquaticbarriers.org/habitat_methods for more information.  -1 = not available.",
    "OwnerType": "Land ownership type. This information is derived from the USFS ownership parcels dataset and Protected Areas Database (PAD-US v4) to highlight ownership types of particular importance to partners.  NOTE: this does not include most private land.",
    "BarrierOwnerType": "Barrier ownership type, if available.  For unsurveyed road / stream crossings, this information is derived from the National Bridge Inventory, US Census TIGER Roads route type, and USFS National Forest road / stream crossings database ownership information, and may not be fully accurate.",
    "ProtectedLand": "Indicates if the {type} occurs on public land as represented within the USFS ownership parcels dataset and Protected Areas Database (PAD-US v4).",
    "WildScenicRiver": "Indicates if the {type} occurs within a designated or eligible / suitable Wild & Scenic River corridor in the Protected Areas Database of the United States (v4), or within 250 meters of a designated or eligible / suitable Wild & Scenic River.",
    "Wilderness": "Within a designated wilderness area in the Protected Areas Database of the United States (v4).",
    "EJTract": "Within an overburdened and underserved Census tracts a defined by the Climate and Environmental Justice Screening tool.",
    "EJTribal": "Within a disadvantaged tribal community as defined by the Climate and Environmental Justice Screening tool based on American Indian and Alaska Native areas as defined by the US Census Bureau.  Note: all tribal communities considered disadvantaged by the Climate and Environmental Justice Screening tool.",
    "NativeTerritories": "Native / indigenous people's territories as mapped by Native Land Digital (https://native-land.ca/",
    "FishHabitatPartnership": "Fish Habitat Partnerships working in the area where the {type} occurs.  See https://www.fishhabitat.org/the-partnerships for more information.",
    "Basin": "Name of the hydrologic basin (HUC6) where the {type} occurs.",
    "Subbasin": "Name of the hydrologic subbasin (HUC8) where the {type} occurs.",
    "Subwatershed": "Name of the hydrologic subwatershed (HUC12) where the {type} occurs.",
    "HUC2": "Hydrologic region identifier where the {type} occurs",
    "HUC6": "Hydrologic basin identifier where the {type} occurs.",
    "HUC8": "Hydrologic subbasin identifier where the {type} occurs.",
    "HUC10": "Hydrologic watershed identifier where the {type} occurs.",
    "HUC12": "Hydrologic subwatershed identifier where the {type} occurs.",
    "County": "County where {type} occurs.",
    "State": "State where {type} occurs.",
    "CongressionalDistrict": "Congressional District where {type} occurs (118th Congressional Districts).",
    "HasNetwork": "indicates if this {type} was snapped to the aquatic network for analysis.  1 = on network, 0 = off network.  Note: network metrics and scores are not available for {type}s that are off network.",
    "Excluded": "this {type} was excluded from the connectivity analysis based on field reconnaissance or manual review of aerial imagery.",
    "Ranked": "this {type} was included for prioritization.  Some barriers that are beneficial to restricting the movement of invasive species or that are water diversions without associated barriers are excluded from ranking.",
    "Invasive": "this {type} is identified as a beneficial to restricting the movement of invasive species and is not ranked",
    "OnLoop": "this {type} occurs on a loop within the NHD High Resolution aquatic network and is considered off-network for purposes of network analysis and ranking",
    "Intermittent": "indicates if this {type} was snapped to a a stream or river reach coded by NHDPlusHR as an intermittent or ephemeral. -1 = not available.",
    "Canal": "indicates if this {type} was snapped to a a stream or river reach coded by NHDPlusHR as a canal or ditch. -1 = not available.",
    "StreamOrder": "NHDPlus Modified Strahler stream order. -1 = not available.",
    "Landcover": "average amount of the river floodplain in the upstream network that is in natural landcover types.  -1 = not available.",
    "SizeClasses": "number of unique upstream size classes that could be gained by removal of this {type}. -1 = not available.",
    "PerennialSizeClasses": "number of unique upstream size classes of perennial stream reaches that could be gained by removal of this {type}. -1 = not available.",
    "MainstemSizeClasses": "number of unique upstream size classes within mainstem networks that could be gained by removal of this {type}. -1 = not available.",
    # upstream and downstream functional network stats
    "TotalUpstreamMiles": "number of miles in the upstream functional river network from this {type}, including miles in waterbodies. -1 = not available.",
    "PerennialUpstreamMiles": "number of perennial miles in the upstream functional river network from this {type}, including miles in waterbodies.  Perennial reaches are all those not specifically coded by NHD as ephemeral or intermittent, and include other types, such as canals and ditches that may not actually be perennial.  Networks are constructed using all flowlines, not just perennial reaches. -1 = not available.",
    "IntermittentUpstreamMiles": "number of ephemeral and intermittent miles in the upstream functional river network from this {type}, including miles in waterbodies.  Ephemeral and intermittent reaches are all those that are specifically coded by NHD as ephemeral or intermittent, and specifically excludes other types, such as canals and ditches that may actually be ephemeral or intermittent in their flow frequency.  -1 = not available.",
    "AlteredUpstreamMiles": "number of altered miles in the upstream functional river network from this {type}, including miles in waterbodies.  Altered reaches are those specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration). -1 = not available.",
    "UnalteredUpstreamMiles": "number of unaltered miles in the upstream functional river network from this {type}, including miles in waterbodies.  Unaltered miles exclude reaches specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration). -1 = not available.",
    "PerennialUnalteredUpstreamMiles": "number of unaltered perennial miles in the upstream functional river network from this {type}, including miles in waterbodies.  Unaltered miles exclude reaches specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration). -1 = not available.",
    "PercentUnaltered": "percent of the total upstream functional river network length from this {type} that is not specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration).  -1 = not available.",
    "PercentPerennialUnaltered": "percent of the perennial upstream functional river network length from this {type} that is not specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration).  See PerennialUpstreamMiles.  -1 = not available.",
    "ResilientUpstreamMiles": "number of miles in the upstream functional river network from this {type} that are within watersheds identified by The Nature Conservancy with above average or greater freshwater resilience (v0.44), including miles in waterbodies.  -1 = not available.  See https://www.maps.tnc.org/resilientrivers/#/explore for more information.",
    "ColdUpstreamMiles": "number of miles in the upstream functional river network from this {type} that are within watersheds identified by The Nature Conservancy with above average or greater freshwater resilience (v0.44), including miles in waterbodies.  -1 = not available.  See https://www.maps.tnc.org/resilientrivers/#/explore for more information.",
    "PercentResilient": "percent of the the upstream functional river network length from this {type} that is within watersheds identified by The Nature Conservancy with slightly above average or greater cold water temperature scores (March 2024), including miles in waterbodies.  -1 = not available.  See https://www.maps.tnc.org/resilientrivers/#/explore for more information.",
    "PercentCold": "percent of the the upstream functional river network length from this {type} that is within watersheds identified by The Nature Conservancy with above average or greater cold water temperature scores (March 2024), including miles in waterbodies.  -1 = not available.  See https://www.maps.tnc.org/resilientrivers/#/explore for more information.",
    "UpstreamDrainageAcres": "approximate drainage area in acres of all NHD High Resolution catchments within upstream functional network of {type}.  Includes the total catchment area of any NHD High Resolution flowlines that are cut by barriers in the analysis, which may overrepresent total drainage area of the network. -1 = not available.",
    "TotalDownstreamMiles": "number of miles in the complete downstream functional river network from this {type}, including miles in waterbodies.  Note: this measures the length of the complete downstream network including all tributaries, and is not limited to the shortest downstream path.  -1 = not available.",
    "FreeDownstreamMiles": "number of free-flowing miles in the downstream functional river network.  Excludes miles in altered reaches in waterbodies.  -1 = not available.",
    "FreePerennialDownstreamMiles": "number of free-flowing perennial miles in the downstream functional river network.  Excludes miles in altered reaches in waterbodies.  See PerennialUpstreamMiles for definition of perennial reaches. -1 = not available.",
    "FreeIntermittentDownstreamMiles": "number of free-flowing ephemeral and intermittent miles in the downstream functional river network.  Excludes miles altered reaches in waterbodies.  See IntermittentUpstreamMiles for definition of intermittent reaches. -1 = not available.",
    "FreeAlteredDownstreamMiles": "number of free-flowing altered miles in the downstream functional river network from this {type}.  Excludes miles in altered reaches in waterbodies.  See AlteredUpstreaMiles for definition of altered reaches.  -1 = not available.",
    "FreeUnalteredDownstreamMiles": "number of free-flowing altered miles in the downstream functional river network from this {type}.  Excludes miles in altered reaches in waterbodies.  See UnalteredUpstreamMiles for definition of unaltered reaches.  -1 = not available.",
    "FreeResilientDownstreamMiles": "number of free-flowing miles in the downstream functional river network length from this {type} that is within watersheds identified by The Nature Conservancy with slightly above average or greater cold water temperature scores (March 2024).  Excludes miles in altered reaches in waterbodies.  -1 = not available.  See https://www.maps.tnc.org/resilientrivers/#/explore for more information.",
    "FreeColdDownstreamMiles": "number of free-flowing miles in the downstream functional river network length from this {type} that is within watersheds identified by The Nature Conservancy with above average or greater freshwater resilience (v0.44).  Excludes miles in altered reaches in waterbodies.  -1 = not available.  See https://www.maps.tnc.org/resilientrivers/#/explore for more information.",
    "UpstreamUnalteredWaterbodyAcres": "area in acres of all unaltered lakes and ponds that intersect any reach in upstream functional network; these waterbodies are not specifically marked by data sources as altered and are not associated with dams in this inventory.  Use with caution because waterbodies may not be correctly subdivided by dams in the data sources, and altered waterbodies may not be marked as such. -1 = not available.",
    "UpstreamUnalteredWetlandAcres": "area in acres of all unaltered freshwater wetlands that intersect any reach in the upstream functional network. Wetlands are derived from specific wetland types in the National Wetlands Inventory (freshwater scrub-shrub, freshwater forested, freshwater emergent) and NHD (swamp/marsh) and exclude any specifically marked by the data provider as altered.  Use with caution because wetlands may not be correctly subdivided by dams or dikes in the data sources, and altered wetlands may not be marked as such. -1 = not available.",
    # functional network gain / total
    "GainMiles": "absolute number of miles that could be gained by removal of this {type}.  Calculated as the minimum of the TotalUpstreamMiles and FreeDownstreamMiles unless the downstream network flows into the Great Lakes or the Ocean and has no downstream barriers, in which case this is based only on TotalUpstreamMiles. For removed barriers, this is based on the barriers present at the time this barrier was removed, with the exception of those that are immediately upstream and removed in the same year.  -1 = not available.",
    "PerennialGainMiles": "absolute number of perennial miles that could be gained by removal of this {type}.  Calculated as the minimum of the PerennialUpstreamMiles and FreePerennialDownstreamMiles unless the downstream network flows into the Great Lakes or the Ocean and has no downstream barriers, in which case this is based only on PerennialUpstreamMiles.  For removed barriers, this is based on the barriers present at the time this barrier was removed, with the exception of those that are immediately upstream and removed in the same year.  -1 = not available.",
    "TotalNetworkMiles": "sum of TotalUpstreamMiles and FreeDownstreamMiles. -1 = not available.",
    "TotalPerennialNetworkMiles": "sum of PerennialUpstreamMiles and FreePerennialDownstreamMiles. -1 = not available.",
    # mainstem upstream network
    "TotalUpstreamMainstemMiles": "number of miles in the upstream mainstem river network from this {type}, including miles in waterbodies.  Mainstems are defined as having >= 1 square mile drainage area and on the same stream order as the reach where the dam is located. -1 = not available.",
    "PerennialUpstreamMainstemMiles": "number of perennial miles in the upstream mainstem river network from this {type}, including miles in waterbodies.  See TotalUpstreamMainstemMiles for definition of mainstem and PerennialUpstreamMiles for definition of perennial reaches.  Networks are constructed using all flowlines, not just perennial reaches. -1 = not available.",
    "IntermittentUpstreamMainstemMiles": "number of ephemeral and intermittent miles in the upstream mainstem river network from this {type}, including miles in waterbodies.  See TotalUpstreamMainstemMiles for definition of mainstem and IntermittentUpstreamMiles for definition of intermittent reaches.  -1 = not available.",
    "AlteredUpstreamMainstemMiles": "number of altered miles in the upstream mainstem river network from this {type}, including miles in waterbodies.  See TotalUpstreamMainstemMiles for definition of mainstem and AlteredUpstreamMiles for definition of altered reaches.  -1 = not available.",
    "UnalteredUpstreamMainstemMiles": "number of unaltered miles in the upstream mainstem river network from this {type}, including miles in waterbodies.  See TotalUpstreamMainstemMiles for definition of mainstem and UnalteredUpstreamMiles for definition of unaltered reaches.  -1 = not available.",
    "PerennialUnalteredUpstreamMainstemMiles": "number of unaltered perennial miles in the upstream mainstem river network from this {type}, including miles in waterbodies.  See TotalUpstreamMainstemMiles for definition of mainstem and PerennialUnalteredUpstreamMiles for definition of perennial unaltered reaches.   -1 = not available.",
    "PercentMainstemUnaltered": "percent of the upstream mainstem river network length from this {type} that is not specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration).  -1 = not available.",
    # downstream linear networks (to next barrier or outlet)
    "FreeLinearDownstreamMiles": "number of miles in the linear downstream flow direction between this {type} and the next barrier downstream (if any) or downstream-most point (e.g., ocean, river outlet, interior basin, etc) on the full aquatic network on which it occurs. Excludes miles in altered reaches in waterbodies.  -1 = not available.",
    "FreePerennialLinearDownstreamMiles": "number of perennial miles in the linear downstream flow direction between this {type} and the next barrier downstream or downstream-most point on the full aquatic network on which it occurs.  Excludes miles in altered reaches in waterbodies.  See PerennialUpstreamMiles for definition of perennial reaches. -1 = not available.",
    "FreeIntermittentLinearDownstreamMiles": "number of ephemeral and intermittent miles in the linear downstream flow direction between this {type} and the next barrier downstream or downstream-most point on the full aquatic network on which it occurs.  Excludes miles in altered reaches in waterbodies.  See IntermittentUpstreamMiles for definition of intermittent reaches. -1 = not available.",
    "FreeAlteredLinearDownstreamMiles": "number of altered miles in the linear downstream flow direction between this {type} and the next barrier downstream or downstream-most point on the full aquatic network on which it occurs.  Excludes miles in altered reaches in waterbodies.  See AlteredUpstreamMiles for definition of altered reaches. -1 = not available.",
    "FreeUnalteredLinearDownstreamMiles": "number of unaltered miles in the linear downstream flow direction between this {type} and the next barrier downstream or downstream-most point on the full aquatic network on which it occurs.  Excludes miles in unaltered reaches in waterbodies.  See UnalteredUpstreamMiles for definition of unaltered reaches. -1 = not available.",
    # mainstem network gain / total
    "MainstemGainMiles": "absolute number of mainstem miles that could be gained by removal of this {type}.  Calculated as the minimum of the TotalUpstreamMainstemMiles and FreeLinearDownstreamMiles unless the downstream network flows into the Great Lakes or the Ocean and has no downstream barriers, in which case this is based only on TotalUpstreamMainstemMiles.  -1 = not available.",
    "PerennialMainstemGainMiles": "absolute number of perennial mainstem miles that could be gained by removal of this {type}.  Calculated as the minimum of the PerennialUpstreamMainstemMiles and FreePerennialLinearDownstreamMiles unless the downstream network flows into the Great Lakes or the Ocean and has no downstream barriers, in which case this is based only on TotalUpstreamMainstemMiles.  -1 = not available.",
    "TotalMainstemNetworkMiles": "sum of TotalUpstreamMainstemMiles and FreeLinearDownstreamMiles. -1 = not available.",
    "TotalMainstemPerennialNetworkMiles": "sum of PerennialUpstreamMainstemMiles and FreePerennialLinearDownstreamMiles. -1 = not available.",
    # barrier counts upstream / downstream
    "UpstreamWaterfalls": "number of waterfalls at the upstream ends of the functional network for this {type}. -1 = not available.",
    "UpstreamDams": "number of dams at the upstream ends of the functional network for this {type}.",
    "UpstreamSmallBarriers": "number of assessed road/stream crossings within the functional network if this barrier is a dam or at the upstream ends of the functional network if this barrier is a road/stream crossing. -1 = not available.",
    "UpstreamRoadCrossings": "number of uninventoried estimated road crossings within the functional network for this {type}. -1 = not available.",
    "UpstreamHeadwaters": "number of headwaters within the functional network for this {type}. -1 = not available.",
    "TotalUpstreamWaterfalls": "total number of waterfalls upstream of this {type}; includes in all functional networks above this {type}. -1 = not available.",
    "TotalUpstreamDams": "total number of dams upstream of this {type}; includes in all functional networks above this {type}. -1 = not available.",
    "TotalUpstreamSmallBarriers": "total number of assessed road/stream crossings upstream of this {type}; includes in all functional networks above this {type}. -1 = not available.",
    "TotalUpstreamRoadCrossings": "total number of uninventoried estimated road crossings upstream of this {type}; includes in all functional networks above this {type}. -1 = not available.",
    "TotalUpstreamHeadwaters": "total number of headwaters upstream of this {type}; includes in all functional networks above this {type}. -1 = not available.",
    "TotalDownstreamWaterfalls": "total number of waterfalls between this {type} and the downstream-most point the full aquatic network on which it occurs. -1 = not available.",
    "TotalDownstreamDams": "total number of dams between this {type} and the downstream-most point the full aquatic network on which it occurs (e.g., river mouth). -1 = not available.",
    "TotalDownstreamSmallBarriers": "total number of assessed road/stream crossings between this {type} and the downstream-most point the full aquatic network on which it occurs. -1 = not available.",
    "TotalDownstreamRoadCrossings": "total number of uninventoried estimated road crossings between this {type} and the downstream-most point the full aquatic network on which it occurs. -1 = not available.",
    # properties of downstream linear network (to outlet)
    "MilesToOutlet": "miles between this {type} and the downstream-most point (e.g., ocean, river outlet, interior basin, etc) on the full aquatic network on which it occurs. -1 = not available.",
    "FlowsToOcean": "indicates if this {type} was snapped to a stream or river that is known to flow into the ocean.  Note: this underrepresents any networks that traverse regions outside the analysis region that would ultimately connect the networks to the ocean.",
    "FlowsToGreatLakes": "indicates if this {type} was snapped to a stream or river that is known to flow into the Great Lakes.  Note: this underrepresents any networks that traverse regions outside the analysis region that would ultimately connect the networks to the Great Lakes.",
    "InvasiveNetwork": "indicates if there is an invasive species barrier at or downstream of this {type}.",
    # Species upstream habitat
    "AlewifeHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for Alewife.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeAlewifeHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for Alewife.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "AmericanEelHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for American eel.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeAmericanEelHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for American eel.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "AmericanShadHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for American shad.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeAmericanShadHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for American shad.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "AtlanticSturgeonHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for Atlantic sturgeon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeAtlanticSturgeonHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for Atlantic sturgeon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "BluebackHerringHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for blueback herring.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeBluebackHerringHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for blueback herring.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "BonnevilleCutthroatTroutHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for Bonneville cutthroat trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeBonnevilleCutthroatTroutHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for Bonneville cutthroat trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "BullTroutHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for bull trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeBullTroutHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for bull trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "CaBaselineFishHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat based on the California Baseline Fish Habitat dataset.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the California Fish Passage Forum; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeCaBaselineFishHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat based on the California Baseline Fish Habitat dataset.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the California Fish Passage Forum; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "ChesapeakeDiadromousHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for diadromous species in the Chesapeake Bay watershed.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeChesapeakeDiadromousHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for diadromous species in the Chesapeake Bay watershed.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "ChinookSalmonHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for Chinook salmon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeChinookSalmonHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for Chinook salmon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "ChumSalmonHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for chum salmon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeChumSalmonHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for chum salmon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "CoastalCutthroatTroutHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for coastal cutthroat trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeCoastalCutthroatTroutHabitatDOwnstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for coastal cutthroat trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "CohoSalmonHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for coho salmon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeCohoSalmonHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for coho salmon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "EasternBrookTroutHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for eastern brook trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by Trout Unlimited and the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeEasternBrookTroutHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for eastern brook trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by Trout Unlimited and the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "GreenSturgeonHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for green sturgeon (limited to Oregon).  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet (limited to Oregon); please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeGreenSturgeonHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for green sturgeon (limited to Oregon).  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet (limited to Oregon); please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "HickoryShadHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for hickory shad.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeHickoryShadHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for hickory shad.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "KokaneeHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for Kokanee salmon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeKokaneeHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for Kokanee salmon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "PacificLampreyHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for Pacific lamprey (limited to Oregon).  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet (limited to Oregon); please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreePacificLampreyHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for Pacific lamprey (limited to Oregon).  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet (limited to Oregon); please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "PinkSalmonHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for pink salmon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreePinkSalmonHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for pink salmon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "RainbowTroutHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for resident rainbow trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeRainbowTroutHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for resident rainbow trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "RedbandTroutHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for redband trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeRedbandTroutHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for redband trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "ShortnoseSturgeonHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for shortnose sturgeon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeShortnoseSturgeonHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for shortnose sturgeon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "SockeyeSalmonHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for sockeye salmon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeSockeyeSalmonHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for sockeye salmon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "SouthAtlanticAnadromousHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for South Atlantic and Gulf diadromous fish species.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by SEACAP; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeSouthAtlanticAnadromousHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for South Atlantic and Gulf diadromous fish species.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by SEACAP; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "SteelheadHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for steelhead trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeSteelheadHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for steelhead trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "StreamnetAnadromousHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for anadromous species identified by StreamNet.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeStreamnetAnadromousHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for anadromous species identified by StreamNet.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "StripedBassHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for striped bass.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeStripedBassHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for striped bass.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by the Chesapeake Fish Passage Workgroup; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "WestslopeCutthroatTroutHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for westslope cutthroat trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeWestslopeCutthroatTroutHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for westslope cutthroat trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "WhiteSturgeonHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for white sturgeon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeWhiteSturgeonHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for white sturgeon.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "YellowstoneCutthroatTroutHabitatUpstreamMiles": "number of miles in the upstream river network from this {type} that are attributed as habitat for Yellowstone cutthroat trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "FreeYellowstoneCutthroatTroutHabitatDownstreamMiles": "number of free-flowing miles in the downstream river network from this {type} that are attributed as habitat for Yellowstone cutthroat trout.  Habitat reaches are not necessarily contiguous.  Habitat is estimated at the NHDPlusHR flowline level based on best available habitat data provided by StreamNet; please see https://aquaticbarriers.org/habitat_methods for more information. -1 = not available.",
    "State_NC_tier": "network connectivity tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_WC_tier": "watershed condition tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_NCWC_tier": "combined network connectivity and watershed condition tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_PNC_tier": "perennial network connectivity tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_PWC_tier": "perennial watershed condition tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_PNCWC_tier": "combined perennial network connectivity and watershed condition tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_MNC_tier": "mainstem network connectivity tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_MWC_tier": "mainstem watershed condition tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "State_MNCWC_tier": "combined mainstem network connectivity and watershed condition tier for the state that contains this {type}.  Tier 1 represents the {type}s within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "NC_tier": "network connectivity tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "WC_tier": "watershed condition tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "NCWC_tier": "combined network connectivity and watershed condition tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "PNC_tier": "perennial network connectivity tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "PWC_tier": "perennial watershed condition tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "PNCWC_tier": "combined perennial network connectivity and watershed condition tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "MNC_tier": "mainstem network connectivity tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "MWC_tier": "mainstem watershed condition tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
    "MNCWC_tier": "mainstem combined network connectivity and watershed condition tier for your selected subset.  Tier 1 represents the {type}s within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.",
}

DAM_FIELD_DEFINITIONS = {k: v.replace("{type}", "dam") for k, v in FIELD_DEFINITIONS.items()}
SB_FIELD_DEFINITIONS = {k: v.replace("{type}", "assessed road/stream crossing") for k, v in FIELD_DEFINITIONS.items()}
COMBINED_FIELD_DEFINITIONS = {
    k: v.replace("{type}", "dam or assessed road/stream crossing") for k, v in FIELD_DEFINITIONS.items()
}
ROAD_CROSSING_FIELD_DEFINITIONS = {k: v.replace("{type}", "road/stream crossing") for k, v in FIELD_DEFINITIONS.items()}


### Domains not currently used

# Not used directly
# BARRIERSTATUS_DOMAIN = {
#     -1: "Not applicable",
#     0: "Unknown",
#     1: "Impounding",
#     2: "Full breach",
#     3: "Partial breach",
#     4: "Drained",
#     5: "Dry detention",
#     6: "Functions limited"
# }


### Not exported
# IMPOUNDMENTTYPE_DOMAIN = {1: "Run of river", 2: "Lake-like", 3: "Large reservoir"}


# STRUCTURECATEGORY_DOMAIN = {
#     -1: "Not applicable",
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
#     10: "Channel",
#     11: "Gravel/borrow pits",
#     12: "Utility crossing"
# }


# NOTE: structureclass is original name and not used as a class for filtering
# STRUCTURECLASS_DOMAIN = {
#     11: "Fish Mgnt: Fishway",
#     12: "Fish Mgnt: Fish Ladder",
#     13: "Fish Mgnt: Fish Trap",
#     14: "Fish Mgnt: Fish Lock",
#     15: "Fish Mgnt: Rock-Ramp",
#     16: "Fish Mgnt: Vertical-Slot",
#     17: "Fish Mgnt: Baffle",
#     21: "Road Crossing: Railroad",
#     22: "Road Crossing: Bridge-Free Span",
#     23: "Road Crossing: Instream Crossing",
#     24: "Road Crossing: Road Crosses Stream",
#     25: "Road Crossing: Bridge",
#     26: "Road Crossing: Low Water Crossing",
#     31: "Diversion: Unscreened",
#     32: "Diversion: Screened",
#     33: "Diversion: Canal",
#     34: "Diversion: Channel",
#     35: "Diversion: Pump",
#     36: "Diversion: Ditch",
#     37: "Diversion: Vertical",
#     38: "Diversion: Centrifugal",
#     39: "Diversion: Slant",
#     310: "Diversion: Floodgate",
#     311: "Diversion: Siphon",
#     312: "Diversion: Submersible",
#     41: "Culvert: Corrugated metal",
#     43: "Culvert: Circular",
#     44: "Culvert: Open Bottom",
#     45: "Culvert: Pipe Arch",
#     46: "Culvert: Arch",
#     47: "Culvert: Bottomless",
#     49: "Culvert: Pipe-multiple",
#     411: "Culvert: Box",
#     51: "Natural: Waterfall",
#     511: "Natural: Cascade",
#     52: "Natural: Beaver Dam",
#     53: "Natural: Rocks Blockage",
#     61: "Non-structural: High Velocity",
#     62: "Non-structural: Temperature",
#     63: "Non-structural: Low Flow",
#     64: "Non-structural: Chemical",
#     65: "Non-structural: Steep Gradient",
#     66: "Non-structural: Oxygen Depleted",
#     67: "Non-structural: Salinity",
#     68: "Non-structural: Low Light",
#     71: "Debris: Log Jam",
#     72: "Debris: Trash (non-natural)",
#     73: "Debris: Landslide",
#     74: "Debris: Boulders-Rocks (man-made)",
#     75: "Debris: Debris Jam",
#     81: "Other: Levee",
#     82: "Other: Gabion",
#     83: "Other: Locks",
#     84: "Other: Tailing",
#     85: "Other: Waterfall (man-made)",
#     86: "Other: Dike",
#     97: "Dam: Buttress",
#     98: "Dam: Arch",
#     99: "Dam: Multi-Arch",
#     910: "Dam: Embankment",
#     911: "Dam: Grade",
#     916: "Dam: Lowhead or Weir",
#     917: "Dam: Dam Other",
#     918: "Dam: Gravity",
# }
