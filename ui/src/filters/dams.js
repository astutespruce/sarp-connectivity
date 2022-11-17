import {
  HEIGHT,
  PURPOSE,
  FEASIBILITY,
  RARESPP,
  TROUT,
  STREAMORDER,
  INTERMITTENT,
  GAINMILES,
  CONDITION,
  BARRIER_SEVERITY,
  LOWHEAD_DAM,
  WATERBODY_SIZECLASS,
  PERCENT_ALTERED,
  PASSAGEFACILITY_CLASS,
  OWNERTYPE,
  BARRIEROWNERTYPE,
} from 'config'

import { getEntries, priorityAreaFilters } from './common'

// Each filter needs to have a dimension above that matches the key here
export const dams = [
  {
    id: 'benefits',
    title: 'Conservation benefits',
    filters: [
      {
        field: 'feasibility',
        title: 'Feasibility & conservation benefit',
        help: 'Note: feasibility is based on further reconnaissance to evaluate individual barriers. Values are provided only for those that have been evaluated. There may be more feasible or infeasible dams than are indicated above.',
        ...getEntries(FEASIBILITY),
      },
      {
        field: 'barrierseverity',
        title: 'Passability',
        sort: false,
        hideEmpty: true,
        help: 'Note: passability information is only available for a small number of dams.  Not all data sources recorded this information.',
        ...getEntries(BARRIER_SEVERITY),
      },
      {
        field: 'gainmilesclass',
        title: 'Miles Gained',
        ...getEntries(GAINMILES),
      },
      {
        field: 'percentalteredclass',
        title: 'Percent of upstream network in altered stream channels',
        sort: false,
        help: 'Note: altered reaches are those specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration); this status is not consistently available for all stream reaches.',
        ...getEntries(PERCENT_ALTERED),
      },
      ...priorityAreaFilters,
    ],
  },
  {
    id: 'structure',
    title: 'Dam characteristics',
    filters: [
      {
        field: 'heightclass',
        title: 'Height',
        // hideEmpty: true,
        help: 'Note: height information is only available for a small number of dams.  Not all data sources recorded this information.',
        ...getEntries(HEIGHT),
      },
      {
        field: 'condition',
        title: 'Condition',
        sort: true,
        hideEmpty: true,
        help: 'Note: condition information is only available for a small number of dams.  Not all data sources recorded this information.',
        ...getEntries(CONDITION),
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
        field: 'lowheaddam',
        title: 'Is it a lowhead dam?',
        sort: false,
        help: 'Note: lowhead dam status is only available for a small number of dams.  Not all data sources recorded this information.  Likely lowhead dams are those specifically marked as run-of-river dams with a height <= 15 ft.',
        ...getEntries(LOWHEAD_DAM),
      },
      {
        field: 'passagefacilityclass',
        title: 'Does it have a fish passage facility?',
        sort: false,
        hideEmpty: false,
        help: 'Note: fish passage facility information is only available for a small number of dams.  Not all data sources recorded this information.',
        ...getEntries(PASSAGEFACILITY_CLASS),
      },
    ],
  },
  {
    id: 'network',
    title: 'Aquatic network characteristics',
    filters: [
      {
        field: 'streamorderclass',
        title: 'Stream order (NHD modified Strahler)',
        ...getEntries(STREAMORDER),
      },
      {
        field: 'intermittent',
        title: 'Located on an intermittent / ephemeral stream',
        sort: false,
        help: 'Note: intermittent / ephemeral status is assigned in the underlying NHD data and is not consistently assigned for all stream reaches.  Non-intermittent reaches may have perennial flow or be assigned to a different stream reach type which precludes intermittent / ephemeral status.',
        ...getEntries(INTERMITTENT),
      },
      {
        field: 'waterbodysizeclass',
        title: 'Size of associated pond or lake',
        sort: false,
        help: 'Note: dams are associated with ponds or lakes extracted from NHD and the National Wetlands Inventory (NWI) if they spatially overlap; the associated pond or lake is not necessarily a result of an impoundment created by the dam.  Many small lakes and ponds are not present in NHD and NWI.',
        ...getEntries(WATERBODY_SIZECLASS),
      },
    ],
  },
  {
    id: 'ownership',
    title: 'Land and barrier ownership',
    filters: [
      {
        field: 'ownertype',
        title: 'Land ownership type',
        sort: true,
        hideEmpty: true,
        help: 'This information is derived from the CBI Protected Areas Database and TNC Secured Lands Database, to highlight ownership types of particular importance to partners.  NOTE: this does not include most private land.',
        ...getEntries(OWNERTYPE),
      },
      {
        field: 'barrierownertype',
        title: 'Barrier ownership type',
        sort: true,
        hideEmpty: true,
        // help: '', // TODO:
        ...getEntries(BARRIEROWNERTYPE),
      },
    ],
  },

  {
    id: 'species',
    title: 'Presence of key species',
    filters: [
      {
        field: 'tesppclass',
        title: 'Number of federally-listed Threatened & Endangered Species',
        hideEmpty: true,
        help: 'Note: This information is based on occurrences of one or more federally- threatened or endangered aquatic species within the same subwatershed as the dam.  These species may or may not be impacted by this dam.  Information on these species is limited and comprehensive information has not been provided for all states at this time.',
        url: '/sgcn',
        ...getEntries(RARESPP),
      },
      {
        field: 'statesgcnsppclass',
        title: 'Number of state-listed Species of Greatest Conservation Need',
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
    ],
  },
]
