/* cannot call this constants.js because it collides with constants module in NodeJS */

export { siteMetadata } from '../gatsby-config'

export const barrierTypeLabels = {
  dams: 'dams',
  small_barriers: 'road-related barriers',
  road_crossings: 'road/stream crossings',
  waterfalls: 'waterfalls',
  combined_barriers: 'dams & road-related barriers',
}

export const barrierTypeLabelSingular = {
  dams: 'dam',
  small_barriers: 'road-related barrier',
  road_crossings: 'road/stream crossing',
  waterfalls: 'waterfall',
  // FIXME: is this used?
  // combined_barriers: 'dam or road-related barrier',
  combined_barriers: 'FIXME: is this showing up anywhere?',
}

export const barrierNameWhenUnknown = {
  dams: 'Dam (unknown name)',
  small_barriers: 'Road-related barrier (unknown name)',
  road_crossings: 'Road / stream crossing',
  waterfalls: 'Waterfall (unknown name)',
}

// some colors are derived from: https://xdgov.github.io/data-design-standards/components/colors
export const pointColors = {
  highlight: {
    color: '#fd8d3c',
    strokeColor: '#f03b20',
  },
  included: {
    color: '#c51b8a',
    strokeColor: '#FFFFFF',
    // combined scenario:
    smallBarriersColor: '#E645A7',
    damsStrokeColor: '#333333',
  },
  // outside selected areas or filters
  excluded: {
    color: '#E9B4D0',
    strokeColor: '#c51b8a',
    // combined scenario:
    smallBarriersColor: '#f7e3ee',
    smallBarriersStrokeColor: '#f08fce',
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
    color: '#c20a38',
    strokeColor: '#FFFFFF',
  },
  removed: {
    color: '#6BEFF9',
    strokeColor: '#000000',
    // combined scenario:
    damsColor: '#09cad7',
  },
  minorBarrier: {
    color: '#fec44f',
    strokeColor: '#b27701',
  },
  nonBarrier: {
    color: '#00D46A',
    strokeColor: '#037424',
    // combined scenario:
    damsColor: '#00994d',
  },
  invasive: {
    color: '#FFBEA9',
    strokeColor: '#000000',
    // combined scenario:
    damsColor: '#ff8c66',
  },
  waterfalls: {
    color: '#6DA1E0',
    strokeColor: '#000000',
  },
  // only used in prioritize
  topRank: {
    color: '#7916BD',
    // combined scenario:
    smallBarriersColor: '#a948ea',
  },
  lowerRank: {
    color: '#c51b8a',
    // combined scenario:
    smallBarriersColor: '#E645A7',
  },
}

export const pointLegends = {
  // included for ranking based on filters / primary barrier in summary view

  included: {
    getSymbol: (barrierType) => {
      if (barrierType === 'combined_barriers') {
        return {
          symbols: [
            {
              radius: 6,
              color: pointColors.included.color,
              borderColor: pointColors.included.damsStrokeColor,
              borderWidth: 1,
            },
            {
              radius: 4,
              color: pointColors.included.smallBarriersColor,
              borderColor: pointColors.included.color,
              borderWidth: 1,
            },
          ],
        }
      }
      return {
        radius: 6,
        color: pointColors.included.color,
        // border is actually white, but this makes it bigger in legend
        borderColor: pointColors.included.color,
        borderWidth: 1,
      }
    },
    getLabel: (barrierTypeLabel) =>
      `${barrierTypeLabel} included in prioritization`,
  },

  // excluded from ranking based on filters
  excluded: {
    getSymbol: (barrierType) => {
      if (barrierType === 'combined_barriers') {
        return {
          symbols: [
            {
              radius: 6,
              color: `${pointColors.excluded.color}99`,
              borderColor: `${pointColors.excluded.strokeColor}99`,
              borderWidth: 1,
            },
            {
              radius: 4,
              color: `${pointColors.excluded.smallBarriersColor}99`,
              borderColor: `${pointColors.excluded.smallBarriersStrokeColor}99`,
              borderWidth: 1,
            },
          ],
        }
      }

      return {
        radius: 6,
        color: `${pointColors.excluded.color}99`,
        borderColor: `${pointColors.excluded.strokeColor}99`,
        borderWidth: 1,
      }
    },
    getLabel: (barrierTypeLabel) =>
      `${barrierTypeLabel} not included in prioritization`,
  },
  topRank: {
    getSymbol: (barrierType) => {
      if (barrierType === 'combined_barriers') {
        return {
          symbols: [
            {
              radius: 6,
              color: pointColors.topRank.color,
              borderColor: pointColors.topRank.color,
              borderWidth: 1,
            },
            {
              radius: 4,
              color: pointColors.topRank.smallBarriersColor,
              borderColor: pointColors.topRank.color,
              borderWidth: 1,
            },
          ],
        }
      }
      return {
        radius: 6,
        color: pointColors.topRank.color,
        borderColor: pointColors.topRank.color,
        borderWidth: 1,
      }
    },
    getLabel: (barrierTypeLabel, tierLabel) =>
      `top-ranked ${barrierTypeLabel} (${tierLabel})`,
  },
  lowerRank: {
    getSymbol: (barrierType) => {
      if (barrierType === 'combined_barriers') {
        return {
          symbols: [
            {
              radius: 6,
              color: pointColors.lowerRank.color,
              // intentionally using top rank for outline color
              borderColor: pointColors.topRank.color,
              borderWidth: 1,
            },
            {
              radius: 4,
              color: pointColors.lowerRank.smallBarriersColor,
              borderColor: pointColors.topRank.color,
              borderWidth: 1,
            },
          ],
        }
      }
      return {
        radius: 6,
        color: pointColors.lowerRank.color,
        // borderColor: pointColors.lowerRank.color,
        borderColor: pointColors.topRank.color,
        borderWidth: 1,
      }
    },
    getLabel: (barrierTypeLabel, tierLabel) =>
      `lower-ranked ${barrierTypeLabel} (${tierLabel})`,
  },

  // only show >= minZoom for layers
  unrankedBarriers: [
    {
      id: 'removed',
      getSymbol: (barrierType) => {
        if (barrierType === 'combined_barriers') {
          return {
            symbols: [
              {
                radius: 5,
                color: pointColors.removed.damsColor,
                borderColor: pointColors.removed.strokeColor,
                borderWidth: 0.5,
              },
              {
                radius: 3,
                color: pointColors.removed.color,
                borderColor: pointColors.removed.strokeColor,
                borderWidth: 0.5,
              },
            ],
          }
        }
        return {
          radius: 5,
          color: pointColors.removed.color,
          borderColor: pointColors.removed.strokeColor,
          borderWidth: 0.5,
        }
      },
      getLabel: (barrierTypeLabel) =>
        `${barrierTypeLabel} removed for conservation`,
    },
    {
      id: 'minorBarrier',
      getSymbol: () => ({
        radius: 5,
        color: pointColors.minorBarrier.color,
        borderColor: pointColors.minorBarrier.strokeColor,
        borderWidth: 0.5,
      }),
      getLabel: () => 'minor barrier based on field assessment',
    },
    {
      id: 'nonBarrier',
      getSymbol: (barrierType) => {
        if (barrierType === 'combined_barriers') {
          return {
            symbols: [
              {
                radius: 5,
                color: pointColors.nonBarrier.damsColor,
                borderColor: pointColors.nonBarrier.strokeColor,
                borderWidth: 0.5,
              },
              {
                radius: 3,
                color: pointColors.nonBarrier.color,
                borderColor: pointColors.nonBarrier.strokeColor,
                borderWidth: 0.5,
              },
            ],
          }
        }
        return {
          radius: 5,
          color: pointColors.nonBarrier.color,
          borderColor: pointColors.nonBarrier.strokeColor,
          borderWidth: 0.5,
        }
      },
      getLabel: () => 'not a barrier based on field assessment',
    },
    {
      id: 'invasive',
      getSymbol: (barrierType) => {
        if (barrierType === 'combined_barriers') {
          return {
            symbols: [
              {
                radius: 5,
                color: pointColors.invasive.damsColor,
                borderColor: pointColors.invasive.strokeColor,
                borderWidth: 0.5,
              },
              {
                radius: 3,
                color: pointColors.invasive.color,
                borderColor: pointColors.invasive.strokeColor,
                borderWidth: 0.5,
              },
            ],
          }
        }
        return {
          radius: 5,
          color: pointColors.invasive.color,
          borderColor: pointColors.invasive.strokeColor,
          borderWidth: 0.5,
        }
      },
      getLabel: (barrierTypeLabel) =>
        `${barrierTypeLabel} that prevent movement of invasive species`,
    },
    {
      id: 'default',
      getSymbol: (barrierType) => {
        if (barrierType === 'combined_barriers') {
          return {
            symbols: [
              {
                radius: 5,
                color: pointColors.offNetwork.color,
                borderColor: pointColors.offNetwork.strokeColor,
                borderWidth: 1,
              },
              {
                radius: 3,
                color: pointColors.offNetwork.color,
                borderColor: pointColors.offNetwork.strokeColor,
                borderWidth: 1,
              },
            ],
          }
        }
        return {
          radius: 5,
          color: pointColors.offNetwork.color,
          borderColor: pointColors.offNetwork.strokeColor,
          borderWidth: 1,
        }
      },
      getLabel: (barrierTypeLabel) =>
        `${barrierTypeLabel} not available for prioritization`,
    },
  ],

  other: [
    {
      id: 'dams-secondary',
      getSymbol: () => ({
        radius: 5,
        color: pointColors.damsSecondary.color,
        borderColor: pointColors.damsSecondary.strokeColor,
        borderWidth: 0.5,
      }),
      getLabel: () => 'dams analyzed for impacts to aquatic connectivity',
    },
    {
      id: 'waterfalls',
      getSymbol: () => ({
        radius: 5,
        color: pointColors.waterfalls.color,
        borderColor: `${pointColors.waterfalls.strokeColor}`,
        borderWidth: 0.5,
      }),
      getLabel: () => 'waterfalls',
    },
  ],
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
  VI: 'U.S. Virgin Islands',
  VT: 'Vermont',
  WA: 'Washington',
  WI: 'Wisconsin',
  WV: 'West Virginia',
  WY: 'Wyoming',
}

export const REGIONS = {
  ak: {
    name: 'Alaska',
    order: 6,
    url: '/regions/alaska',
    states: ['AK'],
    inDevelopment: true,
  },
  gl: {
    name: 'Great Lakes',
    order: 4,
    url: '/regions/great_lakes',
    states: ['IA', 'IL', 'IN', 'MI', 'MN', 'OH', 'WI'],
    inDevelopment: true,
  },
  gpiw: {
    name: 'Great Plains & Intermountain West',
    url: '/regions/great_plains_intermountain_west',
    order: 1,
    states: ['CO', 'IA', 'KS', 'MT', 'ND', 'NE', 'SD', 'WY', 'UT'],
  },
  ne: {
    name: 'Northeast',
    order: 7,
    url: '/regions/northeast',
    states: [
      'CT',
      'DC',
      'DE',
      'MA',
      'MD',
      'ME',
      'NH',
      'NJ',
      'NY',
      'PA',
      'RI',
      'VT',
    ],
    inDevelopment: true,
  },
  pnw: {
    name: 'Pacific Northwest',
    order: 3,
    url: '/regions/northwest',
    states: ['ID', 'OR', 'WA'],
  },
  psw: {
    name: 'Pacific Southwest',
    order: 5,
    url: '/regions/pacific_southwest',
    states: ['CA', 'NV'],
    inDevelopment: true,
  },
  se: {
    name: 'Southeast',
    order: 0,
    url: '/regions/southeast',
    states: [
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
      'VI',
      'WV',
    ],
  },
  sw: {
    name: 'Southwest',
    order: 2,
    url: '/regions/southwest',
    states: ['AZ', 'NM', 'OK', 'TX'],
  },
}

export const ANALYSIS_STATES = [
  ...new Set(
    Object.values(REGIONS).reduce((prev, { states: cur }) => {
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
  14: 'good candidate for further exploration - dam appears to be in poor condition',
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
  '-1': 'not applicable (road-related barrier)',
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
  '-1': 'not applicable (road-related barrier)',
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
  0: 'not applicable (road-related barrier)', // only when merged with small barriers
  1: 'unknown',
  2: 'likely feasible',
  3: 'possibly feasible',
  4: 'likely infeasible',
  5: 'not feasible',
  6: 'no conservation benefit',
  7: 'project planned',
  8: 'breached with full flow',
  9: 'fish passage installed',
  10: 'treatment complete (removal vs fishway unspecified)',
  // not shown to user
  // 11: (multiple values lumped to prevent showing in filter)
}

export const HEIGHT = {
  0: 'Not applicable (road-related barrier)',
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
  1: 'no dams or road-related barriers',
  2: '1 dam or road-related barrier',
  3: '2-4 dams or road-related barriers',
  4: '5-9 dams or road-related barriers',
  5: '>= 10 dams or road-related barriers',
}

export const CROSSING_TYPE = {
  '-1': 'not applicable (dam)',
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
  '-1': 'not applicable (dam)',
  0: 'unknown',
  1: 'spans full channel & banks',
  2: 'spans only bankfull/active channel',
  3: 'constricted to some degree',
  4: 'minor',
  5: 'moderate',
  6: 'severe',
}

export const ROAD_TYPE = {
  '-1': 'Not applicable (dam)',
  0: 'unknown',
  1: 'unpaved',
  2: 'paved',
  3: 'railroad',
}

export const OWNERTYPE = {
  0: 'unknown (likely privately owned)',
  1: 'Bureau of Land Management',
  2: 'Bureau of Reclamation',
  3: 'Department of Defense',
  4: 'National Park Service',
  5: 'US Fish and Wildlife Service land',
  6: 'USDA Forest Service land',
  7: 'Other Federal land',
  8: 'State land',
  9: 'Joint Ownership or Regional land',
  10: 'Native American land',
  11: 'Private easement',
  12: 'Other private conservation land',
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

export const FERC_REGULATED = {
  '-1': 'Not applicable', // small barriers only
  0: 'Unknown',
  1: 'Yes',
  2: 'Preliminary permit',
  3: 'Pending permit',
  4: 'Exemption',
  5: 'No',
}

export const STATE_REGULATED = {
  '-1': 'Not applicable', // small barriers only
  0: 'Unknown',
  1: 'Yes',
  2: 'No',
}

export const PASSAGEFACILITY_CLASS = {
  0: 'no known fish passage structure',
  1: 'fish passage structure present',
}

export const PASSAGEFACILITY = {
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
  19: 'crossvane',
  20: 'screen bypass',
  21: 'fishway unspecified',
  22: 'other',
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
  2: 'partial passability',
  3: 'partial passability - non salmonid',
  4: 'partial passability - salmonid',
  5: 'seasonbly passable - non salmonid',
  6: 'seasonably passable - salmonid',
  7: 'no barrier',
}

// severity is limited to small barriers
// filter bins do not include unknown, no barrier, no upstream habitat,
// minor barrier because these are never ranked
export const SMALL_BARRIER_SEVERITY_FILTER_BINS = {
  1: 'complete barrier',
  2: 'moderate barrier',
  3: 'indeterminate barrier',
  5: 'likely barrier',
  6: 'barrier - unknown severity',
}
export const SMALL_BARRIER_SEVERITY = {
  0: 'unknown',
  ...SMALL_BARRIER_SEVERITY_FILTER_BINS,
  4: 'minor barrier',
  7: 'no barrier',
  8: 'no upstream habitat',
}

export const LOWHEAD_DAM = {
  '-1': 'not applicable (road-related barrier)',
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
  10: 'Chinook (California Coastal)',
  11: 'Chinook (Central Valley Fall Late Fall run)',
  12: 'Chinook (Central Valley Spring run)',
  13: 'Chinook (Deschutes River Summer Fall run)',
  14: 'Chinook (Lower Columbia River)',
  15: 'Chinook (Mid Columbia River Spring run)',
  16: 'Chinook (Oregon Coast)',
  17: 'Chinook (Puget Sound)',
  18: 'Chinook (Sacramento River Winter run)',
  19: 'Chinook (Snake River Fall run)',
  20: 'Chinook (Snake River Spring Summer run)',
  21: 'Chinook (Southern OR Northern CA Coastal)',
  22: 'Chinook (Upper Columbia River Spring run)',
  23: 'Chinook (Upper Columbia River Summer Fall run)',
  24: 'Chinook (Upper Klamath Trinity Rivers)',
  25: 'Chinook (Upper Willamette River)',
  26: 'Chinook (Washington Coast)',
  27: 'Chum (Columbia River)',
  28: 'Chum (Hood Canal Summer run)',
  29: 'Chum (Pacific Coast)',
  30: 'Chum (Puget Sound Strait of Georgia)',
  31: 'Coho (Central California Coast)',
  32: 'Coho (Lower Columbia River)',
  33: 'Coho (Olympic Peninsula)',
  34: 'Coho (Oregon Coast)',
  35: 'Coho (Puget Sound Strait of Georgia)',
  36: 'Coho (Southern OR Northern CA Coast)',
  37: 'Coho (Southwest Washington)',
  38: 'Pink (even year)',
  39: 'Pink (odd year)',
  40: 'Sockeye (Baker River)',
  41: 'Sockeye (Lake Pleasant)',
  42: 'Sockeye (Lake Wenatchee)',
  43: 'Sockeye (Okanogan River)',
  44: 'Sockeye (Ozette Lake)',
  45: 'Sockeye (Quinalt Lake)',
  46: 'Sockeye (Snake River)',
  47: 'Steelhead (California Central Valley)',
  48: 'Steelhead (Central California Coast)',
  49: 'Steelhead (Klamath Mountains Province)',
  50: 'Steelhead (Lower Columbia River)',
  51: 'Steelhead (Middle Columbia River)',
  52: 'Steelhead (Northern California)',
  53: 'Steelhead (Olympic Peninsula)',
  54: 'Steelhead (Oregon Coast)',
  55: 'Steelhead (Puget Sound)',
  56: 'Steelhead (Snake River Basin)',
  57: 'Steelhead (South Central California Coast)',
  58: 'Steelhead (Southern California)',
  59: 'Steelhead (Southwest Washington)',
  60: 'Steelhead (Upper Columbia River)',
  61: 'Steelhead (Upper Willamette River)',
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

export const DISADVANTAGED_COMMUNITY = {
  tract: 'Within a disadvantaged census tract',
  tribal: 'Within a tribal community',
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
  { field: 'passagefacility', bits: 5 },
  { field: 'hasnetwork', bits: 1 },
  { field: 'excluded', bits: 1 },
  { field: 'onloop', bits: 1 },
  { field: 'unsnapped', bits: 1 },
  { field: 'unranked', bits: 1 },
  { field: 'invasive', bits: 1 },
]

export const RC_PACK_BITS = [
  { field: 'StreamOrder', bits: 4 },
  { field: 'OnLoop', bits: 1 },
  { field: 'OwnerType', bits: 4 },
  { field: 'crossingtype', bits: 4 },
  { field: 'Trout', bits: 1 },
  { field: 'Intermittent', bits: 1 },
  { field: 'ProtectedLand', bits: 1 },
  { field: 'EJTract', bits: 1 },
  { field: 'EJTribal', bits: 1 },
]

export const WF_PACK_BITS = [
  { field: 'streamorder', bits: 4 },
  { field: 'hasnetwork', bits: 1 },
  { field: 'intermittent', bits: 1 },
  { field: 'excluded', bits: 1 },
  { field: 'onloop', bits: 1 },
  { field: 'unsnapped', bits: 1 },
]
