import {
  RARESPP,
  TROUT,
  INTERMITTENT,
  GAINMILES,
  BARRIER_SEVERITY,
  CROSSING_TYPE,
  CONSTRICTION,
  ROAD_TYPE,
  STREAMORDER,
  PERCENT_ALTERED,
  BARRIER_CONDITION,
  OWNERTYPE,
  BARRIEROWNERTYPE,
} from 'constants'

import { getEntries, priorityAreaFilters } from './common'

export const smallBarriers = [
  {
    id: 'benefits',
    title: 'Conservation benefits',
    filters: [
      {
        field: 'severityclass',
        title: 'Barrier Severity',
        sort: true,
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
        help: 'Note: altered stream channels are those that are assigned in the underlying NHD data as canals and ditches or that overlap with altered riverine areas in the National Wetlands Inventory; this status is not consistently available for all stream reaches.',
        ...getEntries(PERCENT_ALTERED),
      },
    ],
  },
  {
    id: 'structure',
    title: 'Road-related barrier characteristics',
    filters: [
      {
        field: 'crossingtypeclass',
        title: 'Crossing type',
        sort: true,
        ...getEntries(CROSSING_TYPE),
      },
      {
        field: 'roadtypeclass',
        title: 'Road type',
        sort: true,
        ...getEntries(ROAD_TYPE),
      },
      {
        field: 'constriction',
        title: 'Type of constriction',
        ...getEntries(CONSTRICTION),
      },
      {
        field: 'conditionclass',
        title: 'Barrier condition',
        sort: true,
        ...getEntries(BARRIER_CONDITION),
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
        title: 'Located on an Intermittent / Ephemeral Stream',
        help: 'Note: intermittent / ephemeral status is assigned in the underlying NHD data and is not consistently assigned for all stream reaches.  Non-intermittent reaches may have perennial flow or be assigned to a different stream reach type which precludes intermittent / ephemeral status.',
        ...getEntries(INTERMITTENT),
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
    ],
  },

  ...priorityAreaFilters,
]
