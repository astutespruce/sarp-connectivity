export const barrierTypeLabels = {
  dams: 'dams',
  small_barriers: 'road-related barriers',
  waterfalls: 'waterfalls',
}

export const barrierTypeLabelSingular = {
  dams: 'dam',
  small_barriers: 'road-related barrier',
  waterfalls: 'waterfall',
}

export const REGIONS = {
  gpiw: 'Great Plains & Intermountain West',
  pnw: 'Pacific Northwest',
  se: 'Southeast',
  sw: 'Southwest',
}

export const STATE_FIPS = {
  '01': 'Alabama',
  '04': 'Arizona',
  '05': 'Arkansas',
  '06': 'California',
  '08': 'Colorado',
  '09': 'Connecticut',
  10: 'Delaware',
  11: 'District of Columbia',
  12: 'Florida',
  13: 'Georgia',
  16: 'Idaho',
  17: 'Illinois',
  18: 'Indiana',
  19: 'Iowa',
  20: 'Kansas',
  21: 'Kentucky',
  22: 'Louisiana',
  23: 'Maine',
  24: 'Maryland',
  25: 'Massachusetts',
  26: 'Michigan',
  27: 'Minnesota',
  28: 'Mississippi',
  29: 'Missouri',
  30: 'Montana',
  31: 'Nebraska',
  32: 'Nevada',
  33: 'New Hampshire',
  34: 'New Jersey',
  35: 'New Mexico',
  36: 'New York',
  37: 'North Carolina',
  38: 'North Dakota',
  39: 'Ohio',
  40: 'Oklahoma',
  41: 'Oregon',
  42: 'Pennsylvania',
  44: 'Rhode Island',
  45: 'South Carolina',
  46: 'South Dakota',
  47: 'Tennessee',
  48: 'Texas',
  49: 'Utah',
  50: 'Vermont',
  51: 'Virginia',
  53: 'Washington',
  54: 'West Virginia',
  55: 'Wisconsin',
  56: 'Wyoming',
  72: 'Puerto Rico',
}

export const STATES = {
  AK: 'Alaska',
  AL: 'Alabama',
  AR: 'Arkansas',
  AS: 'American Samoa',
  AZ: 'Arizona',
  CA: 'California',
  CO: 'Colorado',
  CT: 'Connecticut',
  DC: 'District of Columbia',
  DE: 'Delaware',
  FL: 'Florida',
  GA: 'Georgia',
  GU: 'Guam',
  HI: 'Hawaii',
  IA: 'Iowa',
  ID: 'Idaho',
  IL: 'Illinois',
  IN: 'Indiana',
  KS: 'Kansas',
  KY: 'Kentucky',
  LA: 'Louisiana',
  MA: 'Massachusetts',
  MD: 'Maryland',
  ME: 'Maine',
  MI: 'Michigan',
  MN: 'Minnesota',
  MO: 'Missouri',
  MS: 'Mississippi',
  MT: 'Montana',
  NC: 'North Carolina',
  ND: 'North Dakota',
  NE: 'Nebraska',
  NH: 'New Hampshire',
  NJ: 'New Jersey',
  NM: 'New Mexico',
  NV: 'Nevada',
  NY: 'New York',
  OH: 'Ohio',
  OK: 'Oklahoma',
  OR: 'Oregon',
  PA: 'Pennsylvania',
  PR: 'Puerto Rico',
  RI: 'Rhode Island',
  SC: 'South Carolina',
  SD: 'South Dakota',
  TN: 'Tennessee',
  TX: 'Texas',
  UT: 'Utah',
  VA: 'Virginia',
  VT: 'Vermont',
  WA: 'Washington',
  WI: 'Wisconsin',
  WV: 'West Virginia',
  WY: 'Wyoming',
}

export const REGION_STATES = {
  se: [
    'AL',
    'AR',
    'FL',
    'GA',
    'KY',
    'LA',
    'MO',
    'MS',
    'NC',
    'OK',
    'PR',
    'SC',
    'TN',
    'TX',
    'VA',
    'WV', // TEMP
  ],
  gpiw: [
    'CO',
    'IA', // TEMP:
    'KS',
    'MT',
    'ND',
    'NE',
    'SD',
    'WY',
    'UT',
  ],
  pnw: ['ID', 'OR', 'WA'],
  sw: ['AZ', 'NM', 'OK', 'TX'],
}
REGION_STATES.total = [
  ...new Set(
    Object.values(REGION_STATES).reduce((prev, cur) => {
      prev.push(...cur)
      return prev
    }, [])
  ),
].sort()

export const RECON = {
  0: 'Feasibility not yet evaluated',
  2: 'Dam needs follow-up with landowner',
  3: 'Removal is unlikely.  Social conditions unfavorable',
  4: 'Removal is extremely infeasible.  Large reservoirs, etc.',
  5: 'Dam may be removed or error',
  7: 'Dam was deliberately removed',
  8: 'Dam location is incorrect and needs to be moved',
  9: 'Dam is breached and no impoundment visible',
  10: 'Dam was once considered, need to revisit',
  11: 'Removal planned',
  13: 'Unsure, need second opinion',
  1: 'Good candidate for removal. Move forward with landowner contact',
  14: 'Take immediate action, abandoned-looking dam in poor condition',
  15: 'No conservation benefit',
  16: 'Invasive species barrier',
  6: 'Infeasible in short term via landowner contact',
  18: 'Dam failed',
  19: 'Proposed dam',
  17: 'Risky for mussels',
  20: 'Farm pond - no conservation benefit',
  21: 'Potential thermal issues',
  22: 'Removal unlikely; fish passage installed',
  23: 'Duplicate fish passage project structure',
}

export const PURPOSE = {
  0: 'Unknown',
  1: 'Agriculture',
  2: 'Flood Control',
  3: 'Water Supply',
  4: 'Navigation',
  5: 'Recreation',
  6: 'Hydropower',
  7: 'Aquatic Resource Management',
  8: 'Other',
  9: 'Tailings',
  10: 'Not Rated',
  13: 'Mine or Industrial Waste',
  11: 'Grade Stabilization',
}

export const CONSTRUCTION = {
  0: 'Unknown',
  1: 'Cement',
  2: 'Concrete/Roller-compacted Concrete',
  3: 'Masonry/Stone',
  4: 'Steel',
  5: 'Timber',
  6: 'Earthfill (Gravel, Sand, Silt, Clay)',
  7: 'Rockfill (Rock, Composite)',
  8: 'Corrugated Metal',
  9: 'Polyvinyl chloride (PVC)',
  10: 'Cast Iron',
  11: 'Other',
}

export const DAM_CONDITION = {
  0: 'Not Rated',
  1: 'Satisfactory',
  2: 'Fair',
  3: 'Poor',
  4: 'Unsatisfactory',
  5: 'Dam failed',
  6: 'Dam breached',
}

export const FEASIBILITY = {
  0: 'Not assessed',
  1: 'Not feasible',
  2: 'Likely infeasible',
  3: 'Possibly feasible',
  4: 'Likely feasible',
  12: 'Removal planned',
  5: 'No conservation benefit',
  6: 'Unknown',
  // not shown to user
  // 7: 'Error',
  // 8: 'Dam removed for conservation benefit'
  // 9: 'Invasive species barrier',
  // 10: 'Proposed dam',
  // 11: 'Fish passage installed'
}

export const HEIGHT = {
  0: 'Unknown',
  1: '< 5 feet',
  2: '5 - 10 feet',
  3: '10 - 25 feet',
  4: '25 - 50 feet',
  5: '50 - 100 feet',
  6: '>= 100 feet',
}

export const GAINMILES = {
  0: '< 1 miles',
  1: '1 - 5 miles',
  2: '5 - 10 miles',
  3: '10 - 25 miles',
  4: '25 - 100 miles',
  5: '>= 100 miles',
}

export const RARESPP = { 0: '0', 1: '1', 2: '2 - 4', 3: '5 - 9', 4: '>= 10' }

export const TROUT = {
  0: 'absent or not recorded',
  1: 'one or more trout species present',
}

export const STREAMORDER = {
  1: '1',
  2: '2',
  3: '3',
  4: '4',
  5: '5',
  6: '>= 6',
}

export const BARRIER_SEVERITY = {
  0: 'Unknown',
  1: 'Not a barrier',
  2: 'Moderate barrier',
  3: 'Major barrier',
}

export const CROSSING_TYPE = {
  0: 'Unknown',
  1: 'Not a barrier',
  2: 'Bridge',
  3: 'Culvert',
  4: 'Ford',
  5: 'Dam',
  6: 'Buried stream',
}

export const CONSTRICTION = {
  0: 'Unknown',
  1: 'Spans full channel & banks',
  2: 'Spans only bankfull/active channel',
  3: 'Moderate',
  4: 'Severe',
}

export const ROAD_TYPE = {
  0: 'Unknown',
  1: 'Unpaved',
  2: 'Paved',
  3: 'Railroad',
}

export const BARRIER_CONDITION = {
  0: 'Unknown',
  1: 'Failing',
  2: 'Poor',
  3: 'OK',
  4: 'New',
}

export const OWNERTYPE = {
  1: 'US Fish and Wildlife Service land',
  2: 'USDA Forest Service land',
  3: 'Federal land',
  4: 'State land',
  5: 'Joint Ownership or Regional land',
  6: 'Native American land',
  7: 'Private easement',
  8: 'Other private conservation land',
}

export const PASSAGEFACILITY_CLASS = {
  0: 'No known fish passage structure',
  1: 'Fish passage structure present',
}

export const PASSAGEFACILITY = {
  0: 'Unknown or None',
  1: 'Trap & Truck',
  2: 'Fish Ladder - unspecified',
  3: 'Locking',
  4: 'Rock Rapids',
  5: 'Eelway',
  6: 'Alaskan Steeppass',
  7: 'Herring Passage',
  8: 'Reservation',
  9: 'Exemption',
  10: 'Notch',
  11: 'Denil Fishway',
  12: 'Fish Lift',
  13: 'Partial Breach',
  14: 'Removal',
  15: 'Pool and Weir Fishway',
  16: 'Vertical Slot Fishway',
  17: 'Nature-like Fishway',
  18: 'Bypass Channel Fishway',
}

export const INTERMITTENT = {
  0: 'No',
  1: 'Yes',
}

export const DAM_BARRIER_SEVERITY = {
  0: 'Unknown',
  1: 'Complete',
  2: 'Partial',
  3: 'Partial Passability - Non Salmonid',
  4: 'Partial Passability - Salmonid',
  5: 'Seasonbly Passable - Non Salmonid',
  6: 'Seasonably Passable - Salmonid',
  7: 'No Barrier',
}

export const LOWHEAD_DAM = {
  '-1': 'Unknown',
  0: 'Not a lowhead dam',
  1: 'Lowhead dam',
  2: 'Likely lowhead dam',
}

export const PERCENT_ALTERED = {
  // -1: no network
  0: '0 - 9%',
  1: '10 - 49%',
  2: '50 - 89%',
  3: '90 - 100%',
}

export const WATERBODY_SIZECLASS = {
  '-1': 'Not associated with a pond or lake',
  0: 'Pond (< 0.01 km2)',
  1: 'Very small lake (0.01 - 0.09 km2)',
  2: 'Small lake (0.1 - 0.9 km2)',
  3: 'Medium lake (1 - 9.9 km2)',
  4: 'Large lake (>= 10 km2)',
}

export const CONNECTIVITY_TEAMS = {
  southeast: {
    AR: {
      description:
        'Arkansas kicked off a state-based Aquatic Connectivity Team (ACT) in early 2018 currently led by the Arkansas Natural Heritage Commission. The group, officially titled the Arkansas Stream Heritage Partnership, consists of over 50 members from all sectors including various state, federal, NGO, and private corporations/companies working to address aquatic connectivity in the state. This team has been working with SARP to consolidate data held by individual entities as well as those that are not readily available in an effort to be accurately reflect the number of barriers across the state. This team has been active in identifying and securing funding for various projects.',
      contact: {
        name: 'Darrell Bowman',
        org: 'Arkansas Natural Heritage Commission',
        email: 'darrell.bowman@agfc.ar.gov',
      },
    },
    FL: {
      description:
        'The Florida Aquatic Connectivity Team initiated in 2018, following efforts to improve the inventory of dams and road stream crossings within the State through Florida State Wildlife Grant funding. Following the completion of this assessment project, the team began with an in person dam removal workshop held in Tallahassee, and two in person webinars for the southern portion of the State. The FL ACT seeks to improve aquatic connectivity through dam removal, road stream crossing barrier remediation and floodplain restoration. The FL ACT is led by the Florida Fish and Wildlife Commission (Florida FWC) and SARP.',
      contact: {
        name: 'B.J. Jamison',
        org: 'Florida Fish and Wildlife Commission',
        email: 'bj.jamison@myfwc.com',
      },
    },
    GA: {
      description:
        'Georgia has a state-based Aquatic Connectivity Team (ACT) that is co-lead by SARP and The Nature Conservancy (TNC) and includes members from all sectors including various state, federal, NGO, and private corporations/companies that are all interested in addressing aquatic connectivity. This team has been instrumental in increasing the knowledge of barriers through reconnaissance and field assessments since inception.',
      contact: {
        name: 'Kat Hoenke',
        org: 'Southeast Aquatic Resources Partnership',
        email: 'kat@southeastaquatics.net',
      },
      url: 'https://www.ga-act.org/',
    },
    NC: {
      description:
        'The North Carolina Aquatic Connectivity Team was initiated in 2011, and is led by American Rivers. This ACT holds yearly in person meetings as well as quarterly webinars. Over the years, this Team has had much success through the removal of multiple dams, and is currently working with SARP to perform feasibility reconnaissance on all of the dams in the SARP inventory.',
      contact: {
        name: 'Erin McCombs',
        org: 'American Rivers',
        email: 'emccombs@americanrivers.org',
      },
    },
    SC: {
      description:
        'The South Carolina Aquatic Connectivity Team was initiated in the Spring of 2019. It is a collaborative group consisting of multiple partners who hope to work together to remove and remediate barriers to aquatic organism passage throughout the state. The SC ACT held a kickoff workshop and several subcommittee calls to discuss current projects, identification of new projects, and culvert assessments. The SC ACT is co-led by American Rivers and SARP.',
      contact: {
        name: 'Gerrit Jobsis',
        org: 'American Rivers',
        email: 'gjobsis@americanrivers.org',
      },
    },
    TN: {
      description:
        'Tennessee has had an active Aquatic Connectivity Team (ACT) since 2010 and led by The Nature Conservancy with support from American Rivers and the Tennessee Wildlife Resources Agency. Annual in person meetings and quarterly teleconferences support the coordinations and collaboration among team members across all sectors. Numerous projects have been identified and executed by various members as well as assessments conducted to better understand the level of aquatic fragmentation.',
      contact: {
        name: 'Rob Bullard',
        org: 'The Nature Conservancy',
        email: 'ebullard@tnc.org',
      },
    },
    VA: {
      description:
        'The Virginia Dam Removal Task Force is an Aquatic Connectivity Team in the State of Virginia. It has members from many different organizations that have been collaborating to identify and implement high priority projects. Many partnerships have been built from this team, including the Virginia DOT Who has been working with the Team to replace culverts.',
      contact: {
        name: 'Jessie Thomas-Blate',
        org: 'American Rivers',
        email: 'jthomas@americanrivers.org',
      },
    },
  },
}

export const SYSTEMS = {
  ADM: 'State / County',
  HUC: 'Hydrologic unit',
  ECO: 'Ecoregion',
}

export const SYSTEM_UNITS = {
  ADM: ['State', 'County'],
  HUC: ['HUC2', 'HUC6', 'HUC8', 'HUC10', 'HUC12'],
  ECO: ['ECO3', 'ECO4'],
}

export const SCENARIOS = {
  nc: 'Network Connectivity',
  wc: 'Watershed Condition',
  ncwc: 'Combined',
  pnc: 'Perennial Network Connectivity',
  pwc: 'Perennial Watershed Condition',
  pncwc: 'Perennial Combined',
}

export const LAYER_NAMES = {
  State: 'State',
  County: 'County',
  HUC6: 'Basin',
  HUC8: 'Subbasin',
  HUC10: 'Watershed',
  HUC12: 'Subwatershed',
  ECO3: 'Level 3',
  ECO4: 'Level 4',
}

// Ideal zoom level for each layer, e.g., when fitting bounds to a selected feature
export const LAYER_ZOOM = {
  State: 5,
  County: 9,
  HUC6: 5,
  HUC8: 8,
  HUC10: 9,
  HUC12: 10,
  ECO3: 4,
  ECO4: 8,
}

// Bounds around all selected HUC6s
export const SARP_BOUNDS = [
  -107.87000919, 17.62370026, -64.5126611, 44.26093852,
]

export const HUC8_USFS = {
  1: 'highest',
  2: 'moderate',
  3: 'lowest',
  0: 'not a priority / not assessed',
}

export const HUC8_COA = {
  1: 'conservation opportunity area',
  0: 'not a conservation opportunity area',
}

export const HUC8_SGCN = {
  1: 'within top 10 watersheds per state',
  0: 'not within top 10 watersheds per state',
}
