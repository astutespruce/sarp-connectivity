import {
  HEIGHT,
  PURPOSE,
  FEASIBILITY,
  RARESPP,
  TROUT,
  STREAMORDER,
  INTERMITTENT,
  GAINMILES,
  BARRIER_SEVERITY,
  CROSSING_TYPE,
  CONSTRICTION,
  ROAD_TYPE,
  DAM_CONDITION,
  DAM_BARRIER_SEVERITY,
  LOWHEAD_DAM,
  WATERBODY_SIZECLASS,
  PERCENT_ALTERED,
  BARRIER_CONDITION,
  PASSAGEFACILITY_CLASS,
  OWNERTYPE,
  HUC8_COA,
  HUC8_SGCN,
} from 'constants'

const getIntKeys = (obj) =>
  Object.keys(obj)
    .map((k) => parseInt(k, 10))
    .sort()

/**
 * Get sorted integer keys and labels for each entry in a keyed object
 * @param {Object} obj
 */
const getEntries = (obj) => {
  const values = getIntKeys(obj)
  return {
    values,
    labels: values.map((key) => obj[key]),
  }
}

const priorityFilters = [
  {
    field: 'huc8_coa',
    title: 'SARP conservation opportunity areas',
    sort: false,
    hideEmpty: true,
    help: "These areas were designated by each state and approved by SARP's steering committee for funding through SARP-NFHP-USFWS each year.",
    url: 'https://southeastaquatics.net/sarps-programs/usfws-nfhap-aquatic-habitat-restoration-program/conservation-opportunity-areas',
    ...getEntries(HUC8_COA),
  },
  {
    field: 'huc8_sgcn',
    title: 'Watersheds with most Species of Greatest Conservation Need (SGCN)',
    sort: false,
    hideEmpty: true,
    help: 'These watersheds are among the top 10 per state based on number of State-listed Species of Greatest Conservation Need.',
    url: '/sgcn',
    ...getEntries(HUC8_SGCN),
  },
]

// Each filter needs to have a dimension above that matches the key here
const dams = [
  {
    field: 'feasibility',
    title: 'Feasibility & Conservation Benefit',
    help: 'Note: feasibility is based on further reconnaissance to evaluate individual barriers. Values are provided only for those that have been evaluated. There may be more feasible or infeasible dams than are indicated above.',
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
    help: 'Note: height information is only available for a small number of dams.  Not all data sources recorded this information.',
    ...getEntries(HEIGHT),
  },
  {
    field: 'tesppclass',
    title: 'Number of Federally-Listed Threatened & Endangered Species',
    hideEmpty: true,
    help: 'Note: This information is based on occurrences of one or more federally- threatened or endangered aquatic species within the same subwatershed as the dam.  These species may or may not be impacted by this dam.  Information on these species is limited and comprehensive information has not been provided for all states at this time.',
    url: '/sgcn',
    ...getEntries(RARESPP),
  },
  {
    field: 'statesgcnsppclass',
    title: 'Number of State-listed Species of Greatest Conservation Need',
    hideEmpty: true,
    help: 'Note: This information is based on occurrences within the same subwatershed as the dam.  These species may or may not be impacted by this dam.  Information on these species is limited and comprehensive information has not been provided for all states at this time.',
    url: '/sgcn',
    ...getEntries(RARESPP),
  },
  {
    field: 'trout',
    title: 'Trout presence / absence',
    help: 'Note: This information is based on occurrences within the same subwatershed as the dam.  These species may or may not be impacted by this dam.  Information on these species is limited and comprehensive information has not been provided for all states at this time.',
    sort: false,
    hideEmpty: false,
    ...getEntries(TROUT),
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
    help: 'Note: condition information is only available for a small number of dams.  Not all data sources recorded this information.',
    ...getEntries(DAM_CONDITION),
  },
  {
    field: 'purpose',
    title: 'Purpose',
    sort: true,
    hideEmpty: true,
    help: 'Note: purpose information is only available for a small number of dams.  Not all data sources recorded this information.',
    ...getEntries(PURPOSE),
  },
  {
    field: 'barrierseverity',
    title: 'Barrier Passability',
    sort: false,
    hideEmpty: true,
    help: 'Note: barrier passability information is only available for a small number of dams.  Not all data sources recorded this information.',
    ...getEntries(DAM_BARRIER_SEVERITY),
  },
  {
    field: 'lowheaddam',
    title: 'Lowhead Dams',
    sort: false,
    hideEmpty: false,
    help: 'Note: lowhead dam status is only available for a small number of dams.  Not all data sources recorded this information.  Likely lowhead dams are those specifically marked as run-of-river dams with a height <= 15 ft.',
    ...getEntries(LOWHEAD_DAM),
  },
  {
    field: 'passagefacilityclass',
    title: 'Fish Passage Facility Present',
    sort: false,
    hideEmpty: false,
    help: 'Note: fish passage facility information is only available for a small number of dams.  Not all data sources recorded this information.',
    ...getEntries(PASSAGEFACILITY_CLASS),
  },
  {
    field: 'ownertype',
    title: 'Land Ownership Type',
    sort: true,
    hideEmpty: true,
    help: 'This information is derived from the CBI Protected Areas Database and TNC Secured Lands Database, to highlight ownership types of particular importance to partners.  NOTE: this does not include most private land.',
    ...getEntries(OWNERTYPE),
  },
  {
    field: 'intermittent',
    title: 'Located on an Intermittent / Ephemeral Stream',
    sort: false,
    hideEmpty: false,
    help: 'Note: intermittent / ephemeral status is assigned in the underlying NHD data and is not consistently assigned for all stream reaches.  Non-intermittent reaches may have perennial flow or be assigned to a different stream reach type which precludes intermittent / ephemeral status.',
    ...getEntries(INTERMITTENT),
  },
  {
    field: 'percentalteredclass',
    title: 'Percent of upstream network in altered stream channels',
    sort: false,
    hideEmpty: false,
    help: 'Note: altered stream channels are those that are assigned in the underlying NHD data as canals and ditches and is not consistently assigned for all stream reaches.',
    ...getEntries(PERCENT_ALTERED),
  },
  {
    field: 'waterbodysizeclass',
    title: 'Size of associated pond or lake',
    sort: false,
    hideEmpty: false,
    help: 'Note: dams are associated with ponds or lakes extracted from NHD and the National Wetlands Inventory (NWI) if they spatially overlap; the associated pond or lake is not necessarily a result of an impoundment created by the dam.  Many small lakes and ponds are not present in NHD and NWI.',
    ...getEntries(WATERBODY_SIZECLASS),
  },
  ...priorityFilters,
]

const smallBarriers = [
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
    field: 'constriction',
    title: 'Type of Constriction',
    hideEmpty: true,
    ...getEntries(CONSTRICTION),
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
    field: 'tesppclass',
    title: 'Number of Federally-Listed Threatened and Endangered Species',
    hideEmpty: true,
    help: 'Note: This information is based on occurrences of one or more federally-listed threatened or endangered aquatic species within the same subwatershed as the barrier.  These species may or may not be impacted by this dam.  Information on these species is limited and comprehensive information has not been provided for all states at this time.',
    url: '/sgcn',
    ...getEntries(RARESPP),
  },
  {
    field: 'statesgcnsppclass',
    title:
      'Number of State-listed Species of Greatest Conservation Need (SGCN)',
    hideEmpty: true,
    help: 'Note: This information is based on occurrences within the same subwatershed as the barrier.  These species may or may not be impacted by this barrier.  Information on these species is limited and comprehensive information has not been provided for all states at this time.',
    url: '/sgcn',
    ...getEntries(RARESPP),
  },
  {
    field: 'trout',
    title: 'Trout presence / absence',
    help: 'Note: This information is based on occurrences within the same subwatershed as the dam.  These species may or may not be impacted by this dam.  Information on these species is limited and comprehensive information has not been provided for all states at this time.',
    sort: false,
    hideEmpty: false,
    ...getEntries(TROUT),
  },
  {
    field: 'ownertype',
    title: 'Land Ownership Type',
    sort: true,
    hideEmpty: true,
    help: 'This information is derived from the CBI Protected Areas Database and TNC Secured Lands Database, to highlight ownership types of particular importance to partners.  NOTE: does not include most private land.',
    ...getEntries(OWNERTYPE),
  },
  {
    field: 'intermittent',
    title: 'Located on an Intermittent / Ephemeral Stream',
    sort: false,
    hideEmpty: false,
    help: 'Note: intermittent / ephemeral status is assigned in the underlying NHD data and is not consistently assigned for all stream reaches.  Non-intermittent reaches may have perennial flow or be assigned to a different stream reach type which precludes intermittent / ephemeral status.',
    ...getEntries(INTERMITTENT),
  },
  {
    field: 'percentalteredclass',
    title: 'Percent of upstream network in altered stream channels',
    sort: false,
    hideEmpty: false,
    help: 'Note: altered stream channels are those that are assigned in the underlying NHD data as canals and ditches and is not consistently assigned for all stream reaches.',
    ...getEntries(PERCENT_ALTERED),
  },
  ...priorityFilters,
]

export const FILTERS = {
  dams,
  smallBarriers,
}
