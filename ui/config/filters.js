import {
  HEIGHT,
  CONSTRUCTION,
  PURPOSE,
  FEASIBILITY,
  RARESPP,
  STREAMORDER,
  GAINMILES,
  BARRIER_SEVERITY,
  CROSSING_TYPE,
  ROAD_TYPE,
  DAM_CONDITION,
  BARRIER_CONDITION,
} from './constants'

const getIntKeys = obj =>
  Object.keys(obj)
    .map(k => parseInt(k, 10))
    .sort()

/**
 * Get sorted integer keys and labels for each entry in a keyed object
 * @param {Object} obj
 */
const getEntries = obj => {
  const values = getIntKeys(obj)
  return {
    values,
    labels: values.map(key => obj[key]),
  }
}

const sizeclassValues = [0, 1, 2, 3, 4, 5, 6, 7]

// Each filter needs to have a dimension above that matches the key here
const dams = [
  {
    field: 'feasibility',
    title: 'Feasibility & Conservation Benefit',
    sort: true,
    hideEmpty: true,
    help:
      'Note: feasibility is based on further reconnaissance to evaluate individual barriers. Values are provided only for those that have been evaluated. There may be more feasible or infeasible dams than are indicated above.',
    ...getEntries(FEASIBILITY),
  },
  {
    field: 'gainmilesclass',
    title: 'Miles Gained',
    ...getEntries(GAINMILES),
  },
  {
    field: 'heightclass',
    title: 'Dam Height',
    hideEmpty: true,
    help:
      'Note: height information is only available for a small number of dams.  Not all data sources recorded this information.',
    ...getEntries(HEIGHT),
  },
  {
    field: 'sizeclasses',
    title: 'Upstream Size Classes',
    values: sizeclassValues,
    labels: sizeclassValues,
  },
  {
    field: 'raresppclass',
    title: 'Number of Threatened & Endangered Species',
    hideEmpty: true,
    help:
      'Note: This information is based on occurrences of one or more federally threatened or endangered aquatic species within the same subwatershed as the dam.  These species may or may not be impacted by this dam.  Information on these species is limited and comprehensive information has not been provided for all states at this time.',
    ...getEntries(RARESPP),
  },
  {
    field: 'streamorderclass',
    title: 'Stream Order (NHD modified Strahler)',
    ...getEntries(STREAMORDER),
  },
  {
    field: 'condition',
    title: 'Dam Condition',
    sort: true,
    hideEmpty: true,
    help:
      'Note: condition information is only available for a small number of dams.  Not all data sources recorded this information.',
    ...getEntries(DAM_CONDITION),
  },
  {
    field: 'construction',
    title: 'Dam Construction Materials',
    sort: true,
    hideEmpty: true,
    help:
      'Note: construction information is only available for a small number of dams.  Not all data sources recorded this information.',
    ...getEntries(CONSTRUCTION),
  },
  {
    field: 'purpose',
    title: 'Purpose',
    sort: true,
    hideEmpty: true,
    help:
      'Note: purpose information is only available for a small number of dams.  Not all data sources recorded this information.',
    ...getEntries(PURPOSE),
  },
]

const barriers = [
  {
    field: 'severityclass',
    title: 'Barrier Severity',
    sort: true,
    hideEmpty: true,
    ...getEntries(BARRIER_SEVERITY),
  },
  {
    field: 'crossingtypeclass',
    title: 'Crossing Type',
    sort: true,
    hideEmpty: true,
    ...getEntries(CROSSING_TYPE),
  },
  {
    field: 'roadtypeclass',
    title: 'Road Type',
    sort: true,
    hideEmpty: true,
    ...getEntries(ROAD_TYPE),
  },
  {
    field: 'gainmilesclass',
    title: 'Miles Gained',
    ...getEntries(GAINMILES),
  },
  {
    field: 'conditionclass',
    title: 'Barrier Condition',
    sort: true,
    hideEmpty: true,
    ...getEntries(BARRIER_CONDITION),
  },
  {
    field: 'sizeclasses',
    title: 'Upstream Size Classes',
    values: sizeclassValues,
    labels: sizeclassValues,
  },
  {
    field: 'raresppclass',
    title: 'Number of Threatened and Endangered Species',
    hideEmpty: true,
    help:
      'Note: This information is based on occurrences of one or more federally threatened or endangered aquatic species within the same subwatershed as the dam.  These species may or may not be impacted by this dam.  Information on these species is limited and comprehensive information has not been provided for all states at this time.',
    ...getEntries(RARESPP),
  },
]

export const FILTERS = {
  dams,
  barriers,
}
