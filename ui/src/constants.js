export const STATE_FIPS = {
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
    "51": "Virginia"
}

export const RECON = {
    0: "Not yet evaluated",
    2: "Dam needs follow-up with landowner",
    3: "Removal is unlikely.  Social conditions unfavorable",
    4: "Removal is extremely infeasible.  Large reservoirs, etc.",
    5: "Dam may be removed or error",
    7: "Dam was deliberately removed",
    8: "Dam location is incorrect and needs to be moved",
    9: "Dam is breached and no impoundment visible",
    10: "Dam was once considered, need to revisit",
    11: "Removal planned",
    13: "Unsure, need second opinion",
    1: "Good candidate for removal. Move forward with landowner contact",
    14: "Take immediate action, abandoned-looking dam in poor condition",
    15: "No conservation benefit",
    16: "Invasive species barrier",
    6: "Infeasible in short term via landowner contact",
    18: "Dam failed",
    19: "Proposed dam",
    17: "Risky for mussels"
}

export const PURPOSE = {
    0: "Unknown",
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
    11: "Grade Stabilization"
}

export const CONSTRUCTION = {
    0: "Unknown",
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
    11: "Other"
}

export const DAM_CONDITION = {
    0: "Not Rated",
    1: "Satisfactory",
    2: "Fair",
    3: "Poor",
    4: "Unsatisfactory"
}

export const FEASIBILITY = {
    0: "Unknown",
    1: "Not feasible",
    2: "Likely infeasible",
    3: "Possibly feasible",
    4: "Likely feasible",
    5: "No conservation benefit"
}

export const HEIGHT = {
    0: "Unknown",
    1: "< 5 feet",
    2: "5 - 10 feet",
    3: "10 - 25 feet",
    4: "25 - 50 feet",
    5: "50 - 100 feet",
    6: ">= 100 feet"
}

export const GAINMILES = {
    0: "< 1 miles",
    1: "1 - 5 miles",
    2: "5 - 10 miles",
    3: "10 - 25 miles",
    4: "25 - 100 miles",
    5: ">= 100 miles"
}

export const RARESPP = { 0: "0", 1: "1", 2: "1 - 4", 3: "5 - 9", 4: ">= 10" }

export const STREAMORDER = {
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: ">= 6"
}

export const SINUOSITY = {
    0: "low",
    1: "moderate",
    2: "high"
}

export const BARRIER_SEVERITY = {
    0: "Unknown",
    // 1: "Not a barrier",
    2: "Moderate barrier",
    3: "Major barrier"
}

export const CROSSING_TYPE = {
    0: "Unknown",
    1: "Not a barrier",
    2: "Bridge",
    3: "Culvert",
    4: "Ford",
    5: "Dam",
    6: "Buried stream"
}

export const ROAD_TYPE = { 0: "Unknown", 1: "Unpaved", 2: "Paved", 3: "Railroad" }

export const BARRIER_CONDITION = { 0: "Unknown", 1: "Failing", 2: "Poor", 3: "OK", 4: "New" }

export const CONNECTIVITY_TEAMS = {
    Georgia: {
        description:
            "Georgia has a state-based Aquatic Connectivity Team (ACT) that is co-lead by SARP and The Nature Conservancy (TNC) and includes members from all sectors including various state, federal, NGO, and private corporations/companies that are all interested in addressing aquatic connectivity. This team has been instrumental in increasing the knowledge of barriers through reconnaissance and field assessments since inception.",
        contact: {
            name: "Kat Hoenke",
            email: "kat@southeastaquatics.net"
        }
    },
    Arkansas: {
        description:
            "Arkansas kicked off a state-based Aquatic Connectivity Team (ACT) in early 2018 currently led by the Arkansas Natural Heritage Commission. The group, officially titled the Arkansas Stream Heritage Partnership, consists of over 50 members from all sectors including various state, federal, NGO, and private corporations/companies working to address aquatic connectivity in the state. This team has been working with SARP to consolidate data held by individual entities as well as those that are not readily available in an effort to be accurately reflect the number of barriers across the state. This team has been active in identifying and securing funding for various projects.",
        contact: {
            name: "Darrell Bowman",
            email: "darrell.bowman@agfc.ar.gov"
        }
    },
    Tennessee: {
        description:
            "Tennessee has had an active Aquatic Connectivity Team (ACT) since 2010 and led by The Nature Conservancy with support from American Rivers and the Tennessee Wildlife Resources Agency. Annual in person meetings and quarterly teleconferences support the coordinations and collaboration among team members across all sectors. Numerous projects have been identified and executed by various members as well as assessments conducted to better understand the level of aquatic fragmentation.",
        contact: {
            name: "Rob Bullard",
            email: "ebullard@tnc.org"
        }
    },
    "North Carolina": {
        description:
            "The North Carolina Aquatic Connectivity Team was initiated in 2011, and is led by American Rivers. This ACT holds yearly in person meetings as well as quarterly webinars. Over the years, this Team has had much success through the removal of multiple dams, and is currently working with SARP to perform feasibility reconnaissance on all of the dams in the SARP inventory.",
        contact: {
            name: "Erin McCombs",
            email: "emccombs@americanrivers.org"
        }
    }
}

export const SYSTEMS = {
    ADM: "State / County",
    HUC: "Hydrologic unit",
    ECO: "Ecoregion"
}

export const SYSTEM_UNITS = {
    ADM: ["State", "County"],
    HUC: ["HUC6", "HUC8", "HUC12"],
    ECO: ["ECO3", "ECO4"]
}

export const SCENARIOS = {
    nc: "Network Connectivity",
    wc: "Watershed Condition",
    ncwc: "Combined"
}

export const LAYER_NAMES = {
    "State": "State",
    "County": "County",
    "HUC6": "Basin",
    "HUC8": "Subbasin",
    "HUC12": "Subwatershed",
    "ECO3": "Level 3",
    "ECO4": "Level 4"
}

// Bounds around all selected HUC6s
export const SARP_BOUNDS = [-107.87000919, 17.62370026, -64.5126611, 44.26093852]
