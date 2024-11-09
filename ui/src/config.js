/* cannot call this constants.js because it collides with constants module in NodeJS */

export { siteMetadata } from '../gatsby-config'

export const barrierTypeLabels = {
  dams: 'dams',
  small_barriers: 'road-related barriers',
  road_crossings: 'road/stream crossings',
  waterfalls: 'waterfalls',
  combined_barriers: 'dams & road-related barriers',
  largefish_barriers: 'dams & road-related barriers',
  smallfish_barriers: 'dams & road-related barriers',
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
  // majorBarrier only used for surveyed barriers in survey view
  majorBarrier: {
    color: '#ef3b2c',
    strokeColor: '#FFFFFF',
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
      if (
        barrierType === 'combined_barriers' ||
        barrierType === 'largefish_barriers' ||
        barrierType === 'smallfish_barriers'
      ) {
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
      if (
        barrierType === 'combined_barriers' ||
        barrierType === 'largefish_barriers' ||
        barrierType === 'smallfish_barriers'
      ) {
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
      if (
        barrierType === 'combined_barriers' ||
        barrierType === 'largefish_barriers' ||
        barrierType === 'smallfish_barriers'
      ) {
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
      if (
        barrierType === 'combined_barriers' ||
        barrierType === 'largefish_barriers' ||
        barrierType === 'smallfish_barriers'
      ) {
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
        if (
          barrierType === 'combined_barriers' ||
          barrierType === 'largefish_barriers' ||
          barrierType === 'smallfish_barriers'
        ) {
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
        if (
          barrierType === 'combined_barriers' ||
          barrierType === 'largefish_barriers' ||
          barrierType === 'smallfish_barriers'
        ) {
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
        if (
          barrierType === 'combined_barriers' ||
          barrierType === 'largefish_barriers' ||
          barrierType === 'smallfish_barriers'
        ) {
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
        if (
          barrierType === 'combined_barriers' ||
          barrierType === 'largefish_barriers' ||
          barrierType === 'smallfish_barriers'
        ) {
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

export const SUMMARY_UNIT_COLORS = {
  YlOrRed: {
    // http://colorbrewer2.org/#type=sequential&scheme=YlOrRd&n=8
    8: [
      '#ffffcc',
      '#ffeda0',
      '#fed976',
      '#feb24c',
      '#fd8d3c',
      '#fc4e2a',
      '#e31a1c',
      '#b10026',
    ],
    7: [
      '#ffffb2',
      '#fed976',
      '#feb24c',
      '#fd8d3c',
      '#fc4e2a',
      '#e31a1c',
      '#b10026',
    ],
    6: ['#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026'],
    5: ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026'],
  },
  Greens: {
    // https://colorbrewer2.org/?type=sequential&scheme=Greens&n=7
    7: [
      '#edf8e9',
      '#c7e9c0',
      '#a1d99b',
      '#74c476',
      '#41ab5d',
      '#238b45',
      '#005a32',
    ],
    6: ['#edf8e9', '#c7e9c0', '#a1d99b', '#74c476', '#31a354', '#006d2c'],
    5: ['#edf8e9', '#bae4b3', '#74c476', '#31a354', '#006d2c'],
  },

  empty: '#BBB',
}

export const STATE_FIPS = {
  '01': 'Alabama',
  '02': 'Alaska',
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
  78: 'United States Virgin Islands',
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
  alaska: {
    name: 'Alaska',
    order: 7,
    url: '/regions/alaska',
    states: ['AK'],
    inDevelopment: true,
  },
  great_lakes: {
    name: 'Great Lakes',
    order: 4,
    url: '/regions/great_lakes',
    states: ['IA', 'IL', 'IN', 'MI', 'MN', 'OH', 'WI'],
  },
  great_plains_intermountain_west: {
    name: 'Great Plains & Intermountain West',
    url: '/regions/great_plains_intermountain_west',
    order: 1,
    states: ['CO', 'IA', 'KS', 'MT', 'ND', 'NE', 'SD', 'WY', 'UT'],
  },
  hawaii: {
    name: 'Hawaii',
    url: '/regions/hawaii',
    order: 8,
    states: ['HI'],
    inDevelopment: true,
  },
  northeast: {
    name: 'Northeast',
    order: 6,
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
  },
  northwest: {
    name: 'Pacific Northwest',
    order: 3,
    url: '/regions/northwest',
    states: ['ID', 'OR', 'WA'],
  },
  pacific_southwest: {
    name: 'Pacific Southwest',
    order: 5,
    url: '/regions/pacific_southwest',
    states: ['CA', 'NV'],
  },
  southeast: {
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
  southwest: {
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

export const STATE_DATA_PROVIDERS = {
  CA: [
    {
      key: 'ca',
      description:
        'The <a href="https://www.cafishpassageforum.org/" target="_blank">California Fish Passage Forum </a>and the <a href="https://www.psmfc.org/" target="_blank">Pacific States Marine Fisheries Commission</a> have developed and maintain a barrier inventory for the state of California, called the <a href="https://www.calfish.org/ProgramsData/HabitatandBarriers/CaliforniaFishPassageAssessmentDatabase.aspx">California Fish Passage Assessment Database</a> (PAD). The PAD is an ongoing map-based inventory of known and potential barriers to anadromous fish in California, compiled and maintained through a cooperative interagency agreement. It compiles currently available fish passage information from many different sources, allows past and future barrier assessments to be standardized and stored in one place, and enables the analysis of cumulative effects of passage barriers in the context of overall watershed health.  This dataset is the primary dataset used within this tool for the state of California.',
      logo: 'cfpf_logo.png',
      logoWidth: '180px',
    },
  ],
  HI: [
    {
      key: 'cwrm',
      description:
        'Points of Diversion Data provided by the <a href="https://dlnr.hawaii.gov/cwrm/" target="_blank">Commission on Water Resource Management</a>, Department of Land and Natural Resources, State of Hawaii',
      logo: 'hi_cwrm_logo.png',
      logoWidth: '130px',
    },
  ],
  ID: [
    {
      key: 'idfg',
      description:
        'Records describing dams and road-related barriers within Idaho include those maintained by the <a href="https://idfg.idaho.gov/data/fisheries/resources" target="_blank">Idaho Department of Fish and Game</a>.',
      logo: 'idfg_logo.png',
      logoWidth: '64px',
    },
  ],
  MT: [
    {
      key: 'mtfwp',
      description:
        'Records describing dams and road-related barriers within Montana include those maintained by the <a href="https://fwp.mt.gov/" target="_blank">Montana Department of Fish, Wildlife, and Parks</a>.',
      logo: 'mtfwp_logo.svg',
      logoWidth: '80px',
    },
  ],
  OR: [
    {
      key: 'odfw',
      description:
        'Records describing dams and road-related barriers within Oregon include those maintained by the <a href="https://www.dfw.state.or.us/fish/passage/inventories.asp" target="_blank"> Oregon Department of Fish and Wildlife</a>.',
      logo: 'odfw_logo.svg',
      logoWidth: '240px',
    },
  ],
  UT: [
    {
      key: 'utdwr',
      description:
        'Records describing dams and road-related barriers within Utah include those maintained by the <a href="https://wildlifemigration.utah.gov/fish-and-amphibians/barriers/" target="_blank">Utah Barrier Assessment Inventory Tool</a>.',
      logo: 'utdwr_logo.svg',
      logoWidth: '300px',
    },
  ],
  WA: [
    {
      key: 'wdfw',
      description:
        'Records describing dams and road-related barriers within Washington State include those maintained by the <a href="https://wdfw.wa.gov/species-habitats/habitat-recovery/fish-passage" target="_blank">Washington State Department of Fish and Wildlife, Fish Passage Division</a>. For more information about specific structures, please visit the <a href="https://geodataservices.wdfw.wa.gov/hp/fishpassage/index.html" target="_blank">fish passage web map</a>.',
      logo: 'wdfw_logo.svg',
      logoWidth: '240px',
    },
  ],
  WY: [
    {
      key: 'wygfd',
      description:
        'Information on aquatic barriers in Wyoming is a product of the <a href="https://wgfd.wyo.gov/habitat/aquatic-habitat" target="_blank">Wyoming Game & Fish Department</a>, including field data collection in coordination with the Southeast Aquatic Resources Partnership.',
      logo: 'wygfd_logo.png',
      logoWidth: '80px',
    },
  ],
}

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

export const YEARCOMPLETED = {
  0: 'Not applicable (road-related barrier)',
  1: 'Unknown',
  2: '< 10 years',
  3: '10 - 29 years',
  4: '30 - 49 years',
  5: '50 - 69 years',
  6: '70 - 99 years',
  7: '>= 100 years',
}

export const GAINMILES = {
  0: '< 1 miles',
  1: '1 - 5 miles',
  2: '5 - 10 miles',
  3: '10 - 25 miles',
  4: '25 - 100 miles',
  5: '>= 100 miles',
}

export const MAINSTEM_GAINMILES = {
  '-1': 'not on a mainstem network',
  0: '< 1 miles',
  1: '1 - 2 miles',
  2: '2 - 5 miles',
  3: '5 - 10 miles',
  4: '10 - 25 miles',
  5: '>= 25 miles',
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

// blank means that trout were not recorded
export const TROUT = {
  1: 'Apache trout',
  2: 'cutthroat trout',
  3: 'Gila trout',
  4: 'redband trout',
  5: 'bull trout',
  6: 'brook trout',
  7: 'lake trout',
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

export const ANNUAL_FLOW = {
  0: 'unknown',
  1: '< 1 cubic feet per second',
  2: '1 - 3 cubic feet per second',
  3: '3 - 5 cubic feet per second',
  4: '5 - 10 cubic feet per second',
  5: '10 - 50 cubic feet per second',
  6: '50 - 100 cubic feet per second',
  7: '>= 100 cubic feet per second',
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
  9: 'tide gate',
  10: 'buried stream',
  98: 'assumed bridge', // not shown in filters for small barriers, only for road crossings
  99: 'assumed culvert', // not shown in filters for small barriers, only for road crossings
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
  6: 'USDA Forest Service (ownership boundary)',
  7: 'USDA Forest Service (admin boundary)',
  8: 'Other Federal land',
  9: 'State land',
  10: 'Joint Ownership or Regional land',
  11: 'Native American land',
  12: 'Private easement',
  13: 'Other private conservation land',
}

export const BARRIEROWNERTYPE = {
  0: 'Unknown',
  1: 'Federal',
  2: 'State',
  3: 'Local government',
  4: 'Public utility',
  5: 'Irrigation district',
  6: 'Tribal',
  7: 'Private',
}

export const FERC_REGULATED = {
  '-1': 'Not applicable (road-related barrier)', // small barriers only
  0: 'Unknown',
  1: 'Yes',
  2: 'Preliminary permit',
  3: 'Pending permit',
  4: 'Exempt',
  5: 'No',
}

export const STATE_REGULATED = {
  '-1': 'Not applicable (road-related barrier)', // small barriers only
  0: 'Unknown',
  1: 'Yes',
  2: 'No',
}

export const NRCSDAM = {
  '-1': 'Not applicable (road-related barrier)', // small barriers only
  // 0: 'Unknown', // not used
  1: 'Yes',
  2: 'No',
}

export const WATER_RIGHT = {
  '-1': 'Not applicable (road-related barrier)', // small barriers only
  0: 'Unknown',
  1: 'Yes',
  2: 'No',
}

export const HAZARD = {
  '-1': 'Not applicable (road-related barrier)',
  0: 'Unknown',
  1: 'High',
  2: 'Significant',
  3: 'Intermediate',
  4: 'Low',
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
  23: 'Hybrid / multiple',
  24: 'None (confirmed)',
  25: 'Submerged orifice',
  26: 'Other',
}

export const INTERMITTENT = {
  // -1: 'off network', // filtered out
  0: 'stream is not likely intermittent / ephemeral',
  1: 'stream is likely intermittent / ephemeral',
}

export const CANAL = {
  // -1: "off network", // filtered out
  0: 'stream is not identified by NHD as a canal/ditch',
  1: 'stream is identified by NHD as a canal/ditch',
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
// minor barrier because these are never ranked (in small barriers scenario;
// other combined scenarios use PASSABILITY)
export const SMALL_BARRIER_SEVERITY_FILTER_BINS = {
  1: 'complete barrier',
  2: 'moderate barrier',
  3: 'indeterminate barrier',
  6: 'likely barrier',
  7: 'barrier with unknown severity',
}
export const SMALL_BARRIER_SEVERITY = {
  0: 'unknown',
  ...SMALL_BARRIER_SEVERITY_FILTER_BINS,
  4: 'minor barrier',
  5: 'insignificant barrier',
  8: 'no barrier',
  9: 'no upstream habitat',
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

export const PERCENT_RESILIENT = {
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

export const STREAM_SIZECLASS_DRAINAGE_AREA = {
  '1a': '< 2,471 acres',
  '1b': '2,471 - 24,709 acres',
  2: '24,710 - 127,999 acres',
  '3a': '128,000 - 640,001 acres',
  '3b': '640,002 - 2,471,049 acres',
  4: '2,471,050 - 6,177,624 acres',
  5: '>= 6,177,625 acres',
}

export const WATERBODY_SIZECLASS = {
  0: 'Not associated with a pond or lake',
  1: 'Pond (< 2.5 acres)',
  2: 'Very small lake (2.5 - 24.9 acres)',
  3: 'Small lake (25 - 249 acres)',
  4: 'Medium lake (250 - 2,499 acres)',
  5: 'Large lake (>= 2,500 acres)',
}

export const UNALTERED_WATERBODY_CLASS = {
  0: '0 acres',
  1: '< 2.5 acres',
  2: '2.5 - 24.9 acres',
  3: '25 - 249 acres',
  4: '250 - 2,499 acres',
  5: '>= 2,500 acres',
}

export const UNALTERED_WETLAND_CLASS = {
  0: '0 acres',
  1: '< 2.5 acres',
  2: '2.5 - 24.9 acres',
  3: '25 - 249 acres',
  4: '250 - 2,499 acres',
  5: '>= 2,500 acres',
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

export const COST_CLASS = {
  0: 'not applicable (road-related barrier)',
  1: 'Unknown',
  2: '<$100,000',
  3: '$100,000 - $250,000',
  4: '$250,000 - $500,000',
  5: '$500,000 - $750,000',
  6: '$750,000 - $1M',
  7: '$1M - $2M',
  8: '>=$2M',
}

// NOTE: these are encoded into a comma-delimited field
export const FISH_HABITAT_PARTNERSHIPS = {
  ACFHP: {
    name: 'Atlantic Coastal Fish Habitat Partnership',
    description:
      'The Atlantic Coastal Fish Habitat Partnership (ACFHP) mission is to accelerate the conservation, protection, restoration, and enhancement of habitat for native Atlantic coastal, estuarine-dependent, and diadromous fishes through partnerships between federal, tribal, state, local, and other entities. The Partnership works from the headwaters of coastally draining rivers to the edge of the continental shelf, with a focus on estuarine habitats.',
    url: 'https://www.atlanticfishhabitat.org/',
    logo: 'acfhp_logo.png',
    logoWidth: '140px',
  },
  CFPF: {
    name: 'California Fish Passage Forum',
    description:
      'The mission of the California Fish Passage Forum is to protect and restore listed anadromous salmonid species, and other aquatic organisms, in California by promoting collaboration among public and private sectors for fish passage improvement projects and programs. Species of concern include (but are not limited to): coho and chinook salmon, steelhead trout, and Pacific lamprey.',
    url: 'https://www.cafishpassageforum.org/',
    logo: 'cfpf_logo.png',
    logoWidth: '100px',
  },
  DARE: {
    name: 'Driftless Area Restoration Effort',
    description:
      'The Driftless Area is a 24,000 square-mile area that encompasses portions of southeast Minnesota, northeast Iowa, southwest Wisconsin and northwest Illinois bypassed by the last continental glacier. The region has a high concentration of spring-fed coldwater streams and is recognized for its high diversity of plants, animals, and habitats. The Driftless Area Restoration Effort (DARE) partnership formed to address habitat degradation, loss, and alteration that are the primary factors contributing to the decline of fish populations in this unique region.',
    url: 'https://www.tu.org/conservation/conservation-areas/watershed-restoration/driftless-area-restoration-effort/',
  },
  DFHP: {
    name: 'Desert Fish Habitat Partnership',
    description:
      'Desert fish have declined across these arid lands as a result of habitat loss and alteration and the widespread introduction and establishment of nonnative aquatic species. Despite numerous federal and state laws, regulations, and policies to protect and recover native desert fishes and their habitats, most of them remain imperiled.Current habitat conditions and threats require specific management actions and focused consideration of desert fishes if these species and their habitats are to be protected and remain viable into the future.',
    url: 'https://www.desertfhp.org/',
    logo: 'dfhp_logo.png',
    logoWidth: '200px',
  },
  EBTJV: {
    name: 'Eastern Brook Trout Joint Venture',
    description:
      'In 2005, in recognition of the need to address regional and range-wide threats to brook trout, a group of public and private entities formed the Eastern Brook Trout Joint Venture (EBTJV) to halt the decline of brook trout and restore fishable populations of this iconic species. The EBTJV directs locally-driven efforts that build partnerships to improve fish habitat, working to ensure healthy, fishable brook trout populations throughout their historic eastern United States range.',
    url: 'https://easternbrooktrout.org/',
    logo: 'ebtjv_logo.png',
    logoWidth: '200px',
  },
  FFP: {
    name: 'Farmers & Fishers Partnership',
    description:
      'Our vision rests on a belief that the combined experience, knowledge and skills of fishers and farmers can measurably improve the health of land and streams in the altered landscape of the Upper Mississippi River Basin. To advance this purpose, rural landowners voluntarily develop and implement science-based solutions to local fish habitat and water quality issues with the support of conservationists and community partners. As landowners achieve their own goals for conservation and sustainable prosperity, successful practices are demonstrated and effects measured, lessons are learned and shared with neighbors and throughout the Basin, and ultimately a globally significant landscape is renewed.',
    url: 'https://fishersandfarmers.org/',
    logo: 'ffp_logo.png',
    logoWidth: '100px',
  },
  GLBFHP: {
    name: 'Great Lakes Basin Fish Habitat Partnership',
    description:
      'The international Great Lakes Basin is a unique and biologically diverse region containing the largest surface freshwater system in the world, with sport and commercial fisheries valued at over $7 billion annually. The fishery and aquatic resources of the Great Lakes have suffered detrimental effects of invasive species, loss of biodiversity, poor water quality, contaminants, loss or degradation of coastal wetlands, land use changes, and other factors.  The Basin includes all of Michigan; portions of New York, Pennsylvania, Ohio, Indiana, Illinois, Wisconsin, and Minnesota in the U.S. and Ontario and Quebec in Canada. It covers 295,710 square miles, including 94,250 square miles of surface water and 201,460 square miles of land in the U.S. and Canada. The Great Lakes and connecting waters have over 11,000 miles of coastline.',
    url: 'https://www.fishhabitat.org/the-partnerships/great-lakes-basin-fish-habitat-partnership',
    logo: 'glbfhp_logo.jpg',
    logoWidth: '100px',
  },
  GPFHP: {
    name: 'Great Plains Fish Habitat Partnership',
    description:
      'Streams of the Great Plains are home to a wide diversity of aquatic fauna adapted to harsh changes in temperature and water availability. Low human population density has enabled many Great Plains streams to remain relatively unimpaired, yet aquatic species have experienced a slow but steady decline in abundance and diversity during the 20th Century and continue to face challenges that threaten their viability.  Existing habitat loss are attributed to numerous factors including the conversion of native prairie to land uses for agriculture, energy development, and urbanization, which are reflected in degraded water quality, water quantity, fragmentation, and isolation of rivers from their floodplains. Climate change and invasive species are also factors affecting Great Plains stream habitat.',
    url: 'https://www.prairiefish.org/',
    logo: 'gpfhp_logo.jpg',
    logoWidth: '160px',
  },
  HFHP: {
    name: 'Hawaii Fish Habitat Partnership',
    url: 'https://www.fishhabitat.org/the-partnerships/hawaii-fish-habitat-partnership',
    logo: 'hifhp_logo.png',
    logoWidth: '180px',
  },
  KPFHP: {
    name: 'Kenai Peninsula Fish Habitat Partnership',
    description:
      'The Kenai Peninsula Borough covers approximately 25,000 square miles with over 20,000 miles of in-stream habitat and 350,000 acres of wetland habitat in southcentral Alaska. The Peninsula sustains populations of coho, sockeye, chinook, pink, and chum salmon, as well as rainbow and steelhead trout that make it a premier destination for Alaskans, Americans, and people from all over the world. The Kenai Peninsula Fish Habitat Partnership helps foster responsible stewardship to combat threats such as increased development, a warming climate, and invasive species as well as increase awareness for the species that have deep cultural roots in this area.',
    url: 'http://www.kenaifishpartnership.org/',
    logo: 'kpfhp_logo.png',
    logoWidth: '100px',
  },
  MSBSHP: {
    name: 'Mat-Su Basin Salmon Habitat Partnership',
    description:
      'The Matanuska-Susitna Basin, or Mat-Su, covers 24,500 square miles in southcentral Alaska, roughly the combined size of Vermont, New Hampshire, and Massachusetts. The basin supports populations of chinook, coho, sockeye, pink and chum salmon as well as world-class rainbow trout, char, and grayling, making it one of the country’s premier sportfishing and wildlife viewing destinations. Salmon and other fish are at the heart of Alaskan ecosystems, economy, and culture.',
    url: 'https://matsusalmon.org/',
    logo: 'msbshp_logo.png',
    logoWidth: '400px',
  },
  MGLP: {
    name: 'Midwest Glacial Lakes Partnership',
    description:
      'Each year, millions of anglers fish on over 40,000 inland lakes across the Upper Midwest, seeking recreation, food, and the opportunity to catch “the big one”. These lakes, which were naturally formed by glaciers, are essential in supporting biodiversity, including the many threatened and endangered species that live in them. Fish populations in Midwest glacial lakes are dependent upon the healthy habitats that lakes provide, allowing them to grow, reproduce, and thrive. Stress from human development along lake shorelines, water quality decline driven by development and agriculture in watersheds, changing climate, invasive species, and many other factors threaten these fish populations. The Midwest Glacial Lakes Partnership was created in 2009 to coordinate and improve the conservation of fish habitat in the over 40,000 lakes across the Upper Midwest. ',
    url: 'https://midwestglaciallakes.org/',
  },
  ORBFHP: {
    name: 'Ohio River Basin Fish Habitat Partnership',
    description:
      'The Ohio River Basin Fish Habitat Partnership was formed to protect, restore, and enhance priority habitat for fish and mussels in the watersheds of the Ohio River Basin. We pursue this mission for the benefit of the public, but what brings us to the table is as diverse as the basin itself. Whether it is sport fish, mussels, imperiled fish, water quality, or one of many other drivers, what bonds us is the Basin and our desire to work together to protect, restore, and enhance her aquatic resources.  The partnership encompasses the entire 981 miles of the Ohio River mainstem (the second largest river in the U.S. as measured by annual discharge) and 143,550 square miles of the watershed. A decision was made to exclude the Tennessee-Cumberland sub-basin to limit overlap with SARP.',
    url: 'https://orbfhp.org/',
    logo: 'orbfhp_logo.png',
    logoWidth: '300px',
  },
  PMEP: {
    name: 'Pacific Marine & Estuarine Fish Habitat Partnership',
    description:
      "The Pacific Marine and Estuarine Fish Habitat Partnership's (PMEP) mission is to protect, enhance, and restore ecological habitats within estuaries and nearshore marine environments to sustain healthy native fish communities and support sustainable human uses that depend on healthy fish populations.  The PMEP originated in 2009 when representatives from Oregon, Washington and California agencies and non-governmental entities met to discuss the need to protect and restore habitat for fish species that use estuaries and nearshore marine areas.",
    url: 'https://www.pacificfishhabitat.org/',
    logo: 'pmep_logo.png',
    logoWidth: '180px',
  },
  SARP: {
    name: 'Southeast Aquatic Resources Partnership',
    description:
      'The Southeast Aquatic Resources Partnership (SARP) was formed by the Southeastern Association of Fish and Wildlife Agencies (SEAFWA) to protect aquatic resources across political boundaries as many of our river systems cross multiple jurisdictional boundaries. SARP works with partners to protect, conserve, and restore aquatic resources including habitats throughout the Southeast for the continuing benefit, use, and enjoyment of the American people.',
    url: 'https://southeastaquatics.net/',
    logo: 'sarp_logo.png',
    logoWidth: '140px',
  },
  SEAFHP: {
    name: 'Southeast Alaska Fish Habitat Partnership',
    description:
      'The Southeast Alaska Fish Habitat Partnership works to foster cooperative fish habitat conservation in freshwater, estuarine and marine ecosystems across the southern panhandle of Alaska including the dynamic watersheds and waterways that make up the Alexander Archipelago. Covering nearly 17 million acres of this region is the Tongass National Forest, the largest national forest in the United States and a key producer of salmon. The Partnership’s mission is to support cooperative fish habitat conservation, restoration, and management across the region with consideration of economic, social, and cultural interests of local communities in its efforts.',
    url: 'http://www.seakfhp.org/',
    logo: 'seafhp_logo.png',
    logoWidth: '200px',
  },
  SWASHP: {
    name: 'Southwest Alaska Salmon Habitat Partnership',
    description:
      'The Southwest Alaska Salmon Habitat Partnership is a made up of local communities, Native organizations, subsistence users, anglers, hunters, commercial fishing interests, lodge owners, hunting and fishing guides, tourism interests, non-profit organizations, federal, state, and local agencies and corporations and foundations working cooperatively to conserve fish, wildlife and habitat and perpetuate the uses they support through voluntary habitat conservation in Southwest Alaska.',
    url: 'https://www.fishhabitat.org/the-partnerships/southwest-alaska-salmon-habitat-partnership',
    logo: 'swash_logo.png',
    logoWidth: '100px',
  },
  WNTI: {
    name: 'Western Native Trout Initiative',
    description:
      'The Western Native Trout Initiative (WNTI) works collaboratively across 12 western states to conserve (protect, restore, and enhance) 21 native trout and char species. Formed in 2006 under the Western Association of Fish and Wildlife Agencies, WNTI provides a new perspective and impetus to improve the return on investment of the time, money, and workforce dedicated to native trout conservation. WNTI is a collaborative, multi-state approach that requires the involvement of a wide range of partners – from public agencies to private individuals to conservation-minded organizations and corporations. WNTI provides a forum for partners to coordinate and invest their collective assets and capacity toward completing the highest-priority, native trout conservation efforts across the West. Proposed and led by local communities and resource agencies, these projects are funded and supported through WNTI’s grant programs and in-kind contributions by our partners. WNTI is governed by a steering committee representing 12 western state fish and wildlife agencies, 3 federal natural resource agencies, Native American Tribes, Canadian provincial fish and wildlife agencies, and Trout Unlimited and has partnered with over 350 organizations, nonprofits, and businesses to date.',
    url: 'https://westernnativetrout.org/',
    logo: 'wnti_logo.png',
    logoWidth: '60px',
  },
}

export const INVASIVE_NETWORK = {
  // -1: 'off network', // filtered out
  0: 'not upstream of an invasive species barrier',
  1: 'upstream of an invasive species barrier',
}

export const SURVEYED = {
  0: 'not likely surveyed',
  1: 'likely surveyed',
}

export const SLOPE_CLASS = {
  0: 'slope not available',
  1: '0 - 9%',
  2: '10 - 19%',
  3: '20 - 29%',
  4: '30 - 39%',
  5: '40 - 49%',
  6: '>50%',
}

export const CONNECTIVITY_TEAMS = {
  AL: {
    name: 'Alabama Rivers and Streams Network including Connectivity',
    url: 'https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act/act/alabama-act',
  },
  AR: {
    name: 'Arkansas Stream Heritage Partnership',
    url: 'https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act/act/ashp',
  },
  CA: {
    name: 'California Fish Passage Forum',
    url: 'https://www.cafishpassageforum.org/',
  },
  CO: {
    name: 'Colorado Aquatic Connectivity Team',
  },
  FL: {
    name: 'Florida Aquatic Connectivity Team',
    url: 'https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act/act/florida-act-1',
  },
  GA: {
    name: 'Georgia Aquatic Connectivity Team',
    url: 'https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act/act/georgia-act',
  },
  LA: { name: 'Louisiana Aquatic Connectivity Team' },
  ME: { name: 'Maine Stream Aquatic Connectivity Team' },
  MO: { name: 'Missouri Aquatic Connectivity Team' },
  MS: { name: 'Mississippi Aquatic Connectivity Team' },
  NC: {
    name: 'North Carolina Aquatic Connectivity Team',
    url: 'https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act/act/north-carolina-act',
  },
  NH: { name: 'New Hampshire River Restoration Task Force' },
  NJ: {
    name: 'NJ Statwide Dam Removal Partnership',
    url: 'https://njdams.org/',
  },
  NM: { name: 'New Mexico Aquatic Connectivity Team' },
  NY: { name: 'New York Dam Removal Working Group' },
  OK: { name: 'Oklahoma Aquatic Connectivity Team' },
  OR: {
    name: 'Oregon Fish Passage Task Force',
    url: 'https://www.dfw.state.or.us/fish/passage/task_force.asp',
  },
  PA: { name: 'Pennsylvania Aquatic Connectivity Team' },
  SC: {
    name: 'South Carolina Aquatic Connectivity Team',
    url: 'https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act/act/south-carolina-act',
  },
  TN: {
    name: 'Tennessee Aquatic Connectivity Team',
    url: 'https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act/act/tennessee-act',
  },
  TX: {
    name: 'Texas Aquatic Connectivity Team',
    url: 'https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act/act/texas-act',
  },
  VA: {
    name: 'Virginia Stream Barrier Removal Task Force',
    url: 'https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act/act/virginia-act',
  },
  VT: {
    name: 'Vermont Dam Removal Partnership',
    url: 'https://freevermontrivers.org/',
  },
  WY: {
    name: 'Wyoming Interagency Fish Passage Task Force',
  },
}

export const MAP_SERVICES = {
  dams: 'https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Aquatic_Barrier_Prioritization_Dams_v360/FeatureServer',
  small_barriers:
    'https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Aquatic_Barrier_Prioritization_RoadBarriers_v360/FeatureServer',
  combined_barriers:
    'https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/Aquatic_Barrier_Prioritization_Dams_Crossings_Indicators_05242024/FeatureServer',
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
  mnc: 'Mainstem Network Connectivity',
  mwc: 'Mainstem Watershed Condition',
  mncwc: 'Mainstem Combined',
}

export const LAYER_NAMES = {
  State: 'State',
  County: 'County',
  CongressionalDistrict: 'Congressional district',
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
export const TIER_FIELDS = ['nc', 'wc', 'ncwc']
export const TIER_PACK_INFO = { bits: 5, value_shift: 1 }
// export const FULL_TIER_PACK_BITS = [
//   { field: 'nc', bits: 5, value_shift: 1 },
//   { field: 'pnc', bits: 5, value_shift: 1 },
//   { field: 'mnc', bits: 5, value_shift: 1 },
//   { field: 'wc', bits: 5, value_shift: 1 },
//   { field: 'pwc', bits: 5, value_shift: 1 },
//   { field: 'mwc', bits: 5, value_shift: 1 },
//   { field: 'ncwc', bits: 5, value_shift: 1 },
//   { field: 'pncwc', bits: 5, value_shift: 1 },
//   { field: 'mncwc', bits: 5, value_shift: 1 },
// ]

export const YEAR_REMOVED_BINS = {
  0: 'unknown',
  1: 'before 2000',
  2: '2000-2009',
  3: '2010-2019',
  4: '2020',
  5: '2021',
  6: '2022',
  7: '2023',
  8: '2024',
  9: '2025',
}

export const SPECIES_HABITAT_FIELDS = {
  // StreamNet
  bonnevillecutthroattrouthabitat: {
    label: 'Bonneville cutthroat trout',
    source: 'StreamNet',
  },
  bulltrouthabitat: { label: 'bull trout', source: 'StreamNet' },
  chinooksalmonhabitat: { label: 'Chinook salmon', source: 'StreamNet' },
  chumsalmonhabitat: { label: 'chum salmon', source: 'StreamNet' },
  coastalcutthroattrouthabitat: {
    label: 'coastal cutthroat trout',
    source: 'StreamNet',
  },
  cohosalmonhabitat: { label: 'coho salmon', source: 'StreamNet' },
  greensturgeonhabitat: {
    label: 'green sturgeon',
    source: 'StreamNet',
    limit: 'Oregon',
  },
  kokaneehabitat: { label: 'kokanee', source: '' },
  pacificlampreyhabitat: {
    label: 'Pacific lamprey',
    source: 'StreamNet',
    limit: 'Oregon',
  },
  pinksalmonhabitat: { label: 'pink salmon', source: 'StreamNet' },
  rainbowtrouthabitat: { label: 'rainbow trout', source: 'StreamNet' },
  redbandtrouthabitat: { label: 'redband trout', source: 'StreamNet' },
  sockeyesalmonhabitat: { label: 'sockeye salmon', source: 'StreamNet' },
  steelheadhabitat: { label: 'steelhead', source: 'StreamNet' },
  streamnetanadromoushabitat: {
    label: 'StreamNet anadromous species (combined)',
    source: 'StreamNet',
  },

  // CA Baseline
  cabaselinefishhabitat: {
    label: 'California Baseline fish habitat',
    source: 'California Fish Passage Forum',
  },

  // Eastern Brook Trout / Chesapeake
  easternbrooktrouthabitat: {
    label: 'eastern brook trout',
    source: 'Trout Unlimited / Chesapeake Fish Passage Workgroup',
  },

  // South Atlantic / Gulf
  southatlanticanadromoushabitat: {
    label: 'South Atlantic and Gulf anadromous fish habitat (combined)',
    source: 'SEACAP',
  },

  // Chesapeake
  alewifehabitat: {
    label: 'alewife',
    source: 'Chesapeake Fish Passage Workgroup',
  },
  americaneelhabitat: {
    label: 'American eel',
    source: 'Chesapeake Fish Passage Workgroup',
  },
  americanshadhabitat: {
    label: 'American shad',
    source: 'Chesapeake Fish Passage Workgroup',
  },
  atlanticsturgeonhabitat: {
    label: 'Atlantic sturgeon',
    source: 'Chesapeake Fish Passage Workgroup',
  },
  bluebackherringhabitat: {
    label: 'BluebackHerring',
    source: 'Chesapeake Fish Passage Workgroup',
  },
  hickoryshadhabitat: {
    label: 'hickory shad',
    source: 'Chesapeake Fish Passage Workgroup',
  },
  shortnosesturgeonhabitat: {
    label: 'shortnose sturgeon',
    source: 'Chesapeake Fish Passage Workgroup',
  },
  stripedbasshabitat: {
    label: 'striped bass',
    source: 'Chesapeake Fish Passage Workgroup',
  },
  chesapeakediadromoushabitat: {
    label: 'Chesapeake diadromous fish habitat (combined)',
    source: 'Chesapeake Fish Passage Workgroup',
  },
}

export const getSingularUnitLabel = (layer) => {
  switch (layer) {
    case 'State':
      return 'state'
    case 'County':
      return 'county'
    case 'HUC6':
      return 'basin'
    case 'HUC8':
      return 'subbasin'
    case 'HUC10':
      return 'watershed'
    case 'HUC12':
      return 'subwatershed'
    default:
      return 'area'
  }
}

// ordered array of attachment keywords for sorting attached photos
export const attachmentKeywords = [
  'inlet',
  'outlet',
  'upstream',
  'downstream',
  'optional1',
  'optional2',
]
