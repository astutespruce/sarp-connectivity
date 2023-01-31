/* cannot call this constants.js because it collides with constants module in NodeJS */

export { siteMetadata } from '../gatsby-config'

export const barrierTypeLabels = {
  dams: 'dams',
  small_barriers: 'road-related barriers',
  road_crossings: 'road/stream crossings',
  waterfalls: 'waterfalls',
}

export const barrierTypeLabelSingular = {
  dams: 'dam',
  small_barriers: 'road-related barrier',
  road_crossings: 'road/stream crossing',
  waterfalls: 'waterfall',
}

export const barrierNameWhenUnknown = {
  dams: 'Dam (unknown name)',
  small_barriers: 'Road-related barrier (unknown name)',
  road_crossings: 'Road / stream crossing',
  waterfalls: 'Waterfall (unknown name)',
}

export const REGIONS = {
  gpiw: 'Great Plains & Intermountain West',
  pnw: 'Pacific Northwest',
  se: 'Southeast',
  sw: 'Southwest',
}

export const pointColors = {
  highlight: {
    color: '#fd8d3c',
    strokeColor: '#f03b20',
  },
  included: {
    color: '#c51b8a',
    strokeColor: '#FFFFFF',
  },
  // outside selected areas or filters
  excluded: {
    color: '#E9B4D0',
    strokeColor: '#c51b8a',
  },
  offNetwork: {
    color: '#999',
    strokeColor: '#666',
  },
  roadCrossings: {
    color: '#999',
    strokeColor: '#666',
  },
  damsSecondary: {
    color: '#fec44f',
    strokeColor: '#FFFFFF',
  },
  removed: {
    color: '#00F8FB',
    strokeColor: '#FFFFFF',
  },
  nonBarrier: {
    color: '#00D46A',
    strokeColor: '#037424',
  },
  // TODO: use 1px stroke at all zooms
  invasive: {
    color: '#F9DAEA',
    strokeColor: '#DB8CB7',
  },
  waterfalls: {
    color: '#007DC5',
    strokeColor: '#000000',
  },

  // only used in prioritize
  ranked: {
    strokeColor: '#FFFFFF',
  },
  topRank: {
    color: '#7916BD',
  },
  lowerRank: {
    color: '#DB8CB7',
  },
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

export const BOOLEAN_FIELD = {
  0: 'no',
  1: 'yes',
}

export const RECON = {
  '-1': 'not applicable',
  0: 'feasibility not yet evaluated',
  1: 'good candidate for removal. Move forward with landowner contact',
  2: 'dam needs follow-up with landowner',
  3: 'removal is unlikely.  Social conditions unfavorable',
  4: 'removal is extremely infeasible.  Large reservoirs, etc.',
  5: 'dam may be removed or error',
  6: 'infeasible in short term via landowner contact',
  7: 'dam was deliberately removed',
  8: 'dam location is incorrect and needs to be moved',
  9: 'dam is breached and no impoundment visible',
  10: 'dam was once considered, need to revisit',
  11: 'removal planned',
  13: 'unsure, need second opinion',
  14: 'take immediate action, abandoned-looking dam in poor condition',
  15: 'no conservation benefit',
  16: 'invasive species barrier',
  17: 'risky for mussels',
  18: 'dam failed',
  19: 'proposed dam',
  20: 'farm pond - no conservation benefit',
  21: 'potential thermal issues',
  22: 'removal unlikely; fish passage installed',
  23: 'duplicate fish passage project structure',
}

export const PURPOSE = {
  '-1': 'not applicable',
  0: 'unknown',
  1: 'agriculture',
  2: 'flood control',
  3: 'water supply',
  4: 'navigation',
  5: 'recreation',
  6: 'hydropower',
  7: 'aquatic resource management',
  8: 'other',
  9: 'tailings',
  10: 'not rated',
  13: 'mine or industrial waste',
  11: 'grade stabilization',
}

export const CONSTRUCTION = {
  '-1': 'not applicable',
  0: 'unknown',
  1: 'cement',
  2: 'concrete/roller-compacted concrete',
  3: 'masonry/stone',
  4: 'steel',
  5: 'timber',
  6: 'earthfill (gravel, sand, silt, clay)',
  7: 'rockfill (rock, composite)',
  8: 'corrugated metal',
  9: 'polyvinyl chloride (PVC)',
  10: 'cast iron',
  11: 'other',
}

export const CONDITION = {
  0: 'unknown',
  1: 'satisfactory',
  2: 'fair',
  3: 'poor',
  4: 'unsatisfactory',
  5: 'dam failed',
  6: 'dam breached',
}

export const FEASIBILITYCLASS = {
  0: 'not applicable', // only when merged with small barriers
  1: 'unknown',
  2: 'likely feasible',
  3: 'possibly feasible',
  4: 'likely infeasible',
  5: 'not feasible',
  6: 'no conservation benefit',
  7: 'removal planned',
  8: 'breached with full flow',
  9: 'fish passage installed',
  // not shown to user
  // 10: (multiple values lumped to prevent showing in filter)
}

export const HEIGHT = {
  0: 'Not applicable',
  1: 'Unknown',
  2: '< 5 feet',
  3: '5 - 10 feet',
  4: '10 - 25 feet',
  5: '25 - 50 feet',
  6: '50 - 100 feet',
  7: '>= 100 feet',
}

export const GAINMILES = {
  0: '< 1 miles',
  1: '1 - 5 miles',
  2: '5 - 10 miles',
  3: '10 - 25 miles',
  4: '25 - 100 miles',
  5: '>= 100 miles',
}

export const DOWNSTREAM_OCEAN_MILES = {
  0: 'not on an aquatic network known to flow into the ocean',
  1: '< 1 miles',
  2: '1 - 5 miles',
  3: '5 - 10 miles',
  4: '10 - 25 miles',
  5: '25 - 100 miles',
  6: '100 - 250 miles',
  7: '250 - 500 miles',
  8: '500 - 1,000 miles',
  9: '>= 1,000 miles',
}

export const RARESPP = { 0: '0', 1: '1', 2: '2 - 4', 3: '5 - 9', 4: '>= 10' }

export const TROUT = {
  0: 'absent or not recorded',
  1: 'one or more trout species present',
}

export const STREAMORDER = {
  // 0: 'not on aquatic network', # filtered out
  1: '1',
  2: '2',
  3: '3',
  4: '4',
  5: '5',
  6: '>= 6',
}

export const DOWNSTREAM_OCEAN_DAMS_DOMAIN = {
  0: 'not on an aquatic network known to flow into the ocean',
  1: 'no dams',
  2: '1 dam',
  3: '2-4 dams',
  4: '5-9 dams',
  5: '>= 10 dams',
}

export const DOWNSTREAM_OCEAN_SMALL_BARRIERS_DOMAIN = {
  0: 'not on an aquatic network known to flow into the ocean',
  1: 'no dams / road-related barriers',
  2: '1 dams / road-related barrier',
  3: '2-4 dams / road-related barriers',
  4: '5-9 dams / road-related barriers',
  5: '>= 10 dams / road-related barriers',
}

export const CROSSING_TYPE = {
  '-1': 'not applicable',
  0: 'unknown',
  1: 'inaccessible',
  2: 'no crossing',
  3: 'no upstream habitat',
  4: 'not a barrier',
  5: 'bridge',
  6: 'ford / low water crossing',
  7: 'natural ford',
  8: 'culvert',
  9: 'assumed culvert',
  10: 'tide gate',
  11: 'buried stream',
}

export const CONSTRICTION = {
  '-1': 'not applicable',
  0: 'unknown',
  1: 'spans full channel & banks',
  2: 'spans only bankfull/active channel',
  3: 'constricted to some degree',
  4: 'minor',
  5: 'moderate',
  6: 'severe',
}

export const ROAD_TYPE = {
  '-1': 'Not applicable',
  0: 'unknown',
  1: 'unpaved',
  2: 'paved',
  3: 'railroad',
}

export const OWNERTYPE = {
  0: 'unknown (likely privately owned)',
  1: 'US Fish and Wildlife Service land',
  2: 'USDA Forest Service land',
  3: 'federal land',
  4: 'state land',
  5: 'joint ownership or regional land',
  6: 'Native American land',
  7: 'private easement',
  8: 'other private conservation land',
}

export const BARRIEROWNERTYPE = {
  0: 'unknown (possibly privately owned)',
  1: 'USDA Forest Service',
  2: 'federal',
  3: 'state',
  4: 'local government',
  5: 'public utility',
  6: 'tribal',
}

export const PASSAGEFACILITY_CLASS = {
  0: 'not applicable',
  1: 'no known fish passage structure',
  2: 'fish passage structure present',
}

export const PASSAGEFACILITY = {
  '-1': 'not applicable',
  0: 'unknown or none',
  1: 'trap & truck',
  2: 'fish ladder - unspecified',
  3: 'locking',
  4: 'rock rapids',
  5: 'eelway',
  6: 'Alaskan steeppass',
  7: 'herring passage',
  8: 'reservation',
  9: 'exemption',
  10: 'notch',
  11: 'denil fishway',
  12: 'fish lift',
  13: 'partial breach',
  14: 'removal',
  15: 'pool and weir fishway',
  16: 'vertical slot fishway',
  17: 'nature-like fishway',
  18: 'bypass channel fishway',
}

export const INTERMITTENT = {
  // -1: 'off network', // filtered out
  0: 'no',
  1: 'yes',
}

// barrier passability
export const PASSABILITY = {
  0: 'unknown',
  1: 'complete barrier',
  2: 'partial passability - unspecified',
  3: 'partial passability - non salmonid',
  4: 'partial passability - salmonid',
  5: 'seasonbly passable - non salmonid',
  6: 'seasonably passable - salmonid',
  7: 'no barrier',
}

// severity is limited to small barriers
export const SMALL_BARRIER_SEVERITY = {
  0: 'unknown',
  1: 'complete barrier',
  2: 'moderate barrier',
  3: 'indeterminate barrier',
  4: 'minor barrier',
  5: 'barrier - unknown severity',
  6: 'no barrier',
}

export const LOWHEAD_DAM = {
  '-1': 'not applicable',
  0: 'unknown',
  1: 'lowhead dam',
  2: 'likely lowhead dam',
  3: 'not a lowhead dam',
}

export const PERCENT_ALTERED = {
  // 0: no network // filtered out
  1: '0 - 9%',
  2: '10 - 49%',
  3: '50 - 89%',
  4: '90 - 100%',
}

export const STREAM_SIZECLASS = {
  '1a': 'headwaters',
  '1b': 'creek',
  2: 'small river',
  '3a': 'medium tributary river',
  '3b': 'medium mainstem river',
  4: 'large river',
  5: 'great river',
}

// in km2
export const STREAM_SIZECLASS_DRAINAGE_AREA = {
  '1a': '< 10',
  '1b': '10 - 99',
  2: '100 - 517',
  '3a': '518 - 2,589',
  '3b': '2,590 - 9,999',
  4: '10,000 - 24,999',
  5: '>= 25,000',
}

export const WATERBODY_SIZECLASS = {
  0: 'not associated with a pond or lake',
  1: 'pond (< 0.01 km2)',
  2: 'very small lake (0.01 - 0.09 km2)',
  3: 'small lake (0.1 - 0.9 km2)',
  4: 'medium lake (1 - 9.9 km2)',
  5: 'large lake (>= 10 km2)',
}

// NOTE: these are encoded into a comma-delimited field
export const SALMONID_ESU = {
  CKNR: 'Chinook ESU',
  CKSP: 'Spring-run Chinook ESU',
  CKSS: 'Spring/summer-run Chinook ESU',
  CKSF: 'Summer/fall-run Chinook ESU',
  CKFA: 'Fall-run Chinook ESU',
  CKWI: 'Winter-run Chinook ESU',
  CMNR: 'Chum ESU',
  CMSU: 'Summer-run Chum ESU',
  CMSF: 'Summer/fall-run Chum ESU',
  CONR: 'Coho ESU',
  PKO: 'Odd year Pink ESU',
  PKE: 'Even year Pink ESU',
  SENR: 'Sockeye ESU',
  SDNR: 'Steelhead trout DPS',
}

export const SALMONID_ESU_COUNT = {
  0: 'none present',
  1: '1',
  2: '2',
  3: '3',
  4: '4',
  5: '5',
  6: '6',
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
}

export const SYSTEM_UNITS = {
  ADM: ['State', 'County'],
  HUC: ['HUC2', 'HUC6', 'HUC8', 'HUC10', 'HUC12'],
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
}

// Ideal zoom level for each layer, e.g., when fitting bounds to a selected feature
export const LAYER_ZOOM = {
  State: 5,
  County: 9,
  HUC6: 5,
  HUC8: 8,
  HUC10: 9,
  HUC12: 10,
}

// Bounds around all selected HUC6s
export const SARP_BOUNDS = [
  -107.87000919, 17.62370026, -64.5126611, 44.26093852,
]

// Note: all pack_bits fields are lowercase in UI but uppercase on backend

// tiers use just the scenario as the key here
export const TIER_PACK_BITS = [
  { field: 'nc', bits: 5, value_shift: 1 },
  { field: 'pnc', bits: 5, value_shift: 1 },
  { field: 'wc', bits: 5, value_shift: 1 },
  { field: 'pwc', bits: 5, value_shift: 1 },
  { field: 'ncwc', bits: 5, value_shift: 1 },
  { field: 'pncwc', bits: 5, value_shift: 1 },
]

export const DAM_PACK_BITS = [
  { field: 'streamorder', bits: 4 },
  { field: 'recon', bits: 5 },
  { field: 'passagefacility', bits: 5 },
  { field: 'diversion', bits: 2 },
  { field: 'nostructure', bits: 1 },
  { field: 'estimated', bits: 1 },
  { field: 'hasnetwork', bits: 1 },
  { field: 'excluded', bits: 1 },
  { field: 'onloop', bits: 1 },
  { field: 'unsnapped', bits: 1 },
  { field: 'unranked', bits: 1 },
  { field: 'invasive', bits: 1 },
]

export const SB_PACK_BITS = [
  { field: 'streamorder', bits: 4 },
  { field: 'recon', bits: 5 },
  { field: 'hasnetwork', bits: 1 },
  { field: 'excluded', bits: 1 },
  { field: 'onloop', bits: 1 },
  { field: 'unsnapped', bits: 1 },
  { field: 'unranked', bits: 1 },
  { field: 'invasive', bits: 1 },
]

export const RC_PACK_BITS = [
  { field: 'streamorder', bits: 4 },
  { field: 'ownertype', bits: 4 },
  { field: 'crossingtype', bits: 4 },
  { field: 'trout', bits: 1 },
  { field: 'intermittent', bits: 1 },
]

export const WF_PACK_BITS = [
  { field: 'streamorder', bits: 4 },
  { field: 'hasnetwork', bits: 1 },
  { field: 'intermittent', bits: 1 },
  { field: 'excluded', bits: 1 },
  { field: 'onloop', bits: 1 },
  { field: 'unsnapped', bits: 1 },
]
