import {
  RARESPP,
  TROUT,
  SALMONID_ESU,
  SALMONID_ESU_COUNT,
  INTERMITTENT,
  GAINMILES,
  SMALL_BARRIER_SEVERITY_FILTER_BINS,
  CROSSING_TYPE,
  CONSTRICTION,
  ROAD_TYPE,
  STREAMORDER,
  PERCENT_ALTERED,
  PASSAGEFACILITY_CLASS,
  CONDITION,
  OWNERTYPE,
  BARRIEROWNERTYPE,
  BOOLEAN_FIELD,
  DOWNSTREAM_OCEAN_MILES,
  DOWNSTREAM_OCEAN_SMALL_BARRIERS_DOMAIN,
  DISADVANTAGED_COMMUNITY,
} from 'config'

import { getEntries, hasDiadromousData } from './common'

export const smallBarriers = [
  {
    id: 'social_benefits',
    title: 'Social Benefits',
    filters: [
      {
        field: 'disadvantagedcommunity',
        title: 'Climate and environmental justice',
        help: 'Within a disadvantaged community as defined by the Climate and Environmental Justice Screening tool.  These include overburdened and underserved Census tracts and American Indian and Alaska Native areas as defined by the Census.', // TODO:,
        sort: false,
        hideIfEmpty: true,
        isArray: true,
        labels: Object.values(DISADVANTAGED_COMMUNITY),
        values: Object.keys(DISADVANTAGED_COMMUNITY),
      },
    ],
  },
  {
    id: 'conservation_benefits',
    title: 'Conservation benefits',
    filters: [
      {
        field: 'barrierseverity',
        title: 'Barrier Severity',
        sort: true,
        ...getEntries(SMALL_BARRIER_SEVERITY_FILTER_BINS),
      },

      {
        field: 'gainmilesclass',
        title: 'Miles gained',
        ...getEntries(GAINMILES),
      },
      {
        field: 'percentalteredclass',
        title: 'Percent of upstream network in altered stream channels',
        sort: false,
        help: 'Note: altered reaches are those specifically identified in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other channel alteration); this status is not consistently available for all stream reaches.',
        ...getEntries(PERCENT_ALTERED),
      },
    ],
  },
  {
    id: 'structure',
    title: 'Road-related barrier characteristics',
    filters: [
      {
        field: 'crossingtype',
        title: 'Crossing type',
        sort: true,
        ...getEntries(CROSSING_TYPE, (v) => v >= 0),
      },
      {
        field: 'roadtype',
        title: 'Road type',
        sort: true,
        ...getEntries(ROAD_TYPE, (v) => v >= 0),
      },
      {
        field: 'constriction',
        title: 'Type of constriction',
        ...getEntries(CONSTRICTION, (v) => v >= 0),
      },
      {
        field: 'condition',
        title: 'Barrier condition',
        sort: true,
        ...getEntries(CONDITION),
      },
      {
        field: 'passagefacilityclass',
        title: 'Does it have a fish passage facility?',
        sort: false,
        hideMissingValues: false,
        help: 'Note: fish passage facility information is only available for a small number of road-related barriers.  Not all data sources recorded this information.',
        ...getEntries(PASSAGEFACILITY_CLASS, (v) => v > 0),
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
    id: 'marine',
    title: 'Marine connectivity',
    hasData: hasDiadromousData,
    filters: [
      {
        field: 'flowstoocean',
        title: 'On a network that flows to ocean',
        sort: false,
        help: 'Note: this is limited to networks that are known to connect to marine areas identified by NHD for NHD regions included in this tool, and may not be set correctly for networks that flow through other NHD regions not included in the analysis or outside the U.S. before connecting to marine areas.',
        ...getEntries(BOOLEAN_FIELD),
      },
      {
        field: 'coastalhuc8',
        title: 'Within a coastal subbasin',
        sort: false,
        // help: '',
        ...getEntries(BOOLEAN_FIELD),
      },
      {
        field: 'downstreamoceanmilesclass',
        title: 'Miles downstream to the ocean',
        sort: false,
        help: 'This value is based on linear miles downstream along aquatic network to the ocean.  Note: distances close to the coast may not be accurate due to inaccuracies in how marine areas are identified with respect to the aquatic network downstream termination points.',
        ...getEntries(DOWNSTREAM_OCEAN_MILES),
      },
      {
        field: 'downstreamoceanbarriersclass',
        title:
          'Number of dams / assessed road-related barriers between this dam and the ocean',
        sort: false,
        help: 'This value is based on any dams or assessed road-related barriers that occur on the downstream path between this dam and the ocean.  Note: this does not include any road crossings that have not been evaluated for barrier severity.',
        ...getEntries(DOWNSTREAM_OCEAN_SMALL_BARRIERS_DOMAIN),
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
        sort: false,
        hideMissingValues: true,
        help: 'This information is derived from the BLM Surface Management Agency dataset for federal lands and CBI Protected Areas Database and TNC Secured Lands Database for non-federal lands, to highlight ownership types of particular importance to partners.  NOTE: this does not include most private land.',
        ...getEntries(OWNERTYPE),
      },
      {
        field: 'barrierownertype',
        title: 'Barrier ownership type',
        sort: true,
        hideMissingValues: true,
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
        hideMissingValues: true,
        help: 'Note: This information is based on occurrences of one or more federally-listed threatened or endangered aquatic species within the same subwatershed as the barrier.  These species may or may not be impacted by this barrier.  Information on these species is limited and comprehensive information has not been provided for all states at this time.',
        url: '/sgcn',
        ...getEntries(RARESPP),
      },
      {
        field: 'statesgcnsppclass',
        title:
          'Number of State-listed Species of Greatest Conservation Need (SGCN)',
        hideMissingValues: true,
        help: 'Note: This information is based on occurrences within the same subwatershed as the barrier.  These species may or may not be impacted by this barrier.  Information on these species is limited and comprehensive information has not been provided for all states at this time.',
        url: '/sgcn',
        ...getEntries(RARESPP),
      },
      {
        field: 'trout',
        title: 'Interior and eastern native trout presence / absence',
        help: 'Note: This information is based on occurrences of Apache, brook, bull, cutthroat, Gila, lake, and redband trout species within the same subwatershed as the barrier.  These species may or may not be impacted by this barrier.  Information on these species is limited and comprehensive information has not been provided for all states at this time.',
        sort: false,
        hideMissingValues: false,
        ...getEntries(TROUT),
      },
      {
        field: 'salmonidesucount',
        title:
          'Number of salmon Evolutionarily Significant Units / Steelhead trout Discrete Population Segments',
        help: 'This information is based on the presence of salmon Evolutionarily Significant Units (ESU) or steelhead trout Discrete Population Segments (DPS) within the same watershed as the barrier, as provided by NOAA at the subwatershed level. These species may or may not be impacted by this barrier.',
        sort: false,
        hideMissingValues: true,
        hideIfEmpty: true,
        ...getEntries(SALMONID_ESU_COUNT),
      },
      {
        field: 'salmonidesu',
        title:
          'Salmon Evolutionarily Significant Units / Steelhead trout Discrete Population Segments',
        help: 'This information is based on the presence of salmon Evolutionarily Significant Units (ESU) or steelhead trout Discrete Population Segments (DPS) within the same watershed as the dam, as provided by NOAA at the subwatershed level. These species may or may not be impacted by this dam.',
        sort: false,
        hideMissingValues: true,
        hideIfEmpty: true,
        isArray: true,
        labels: Object.values(SALMONID_ESU),
        values: Object.keys(SALMONID_ESU),
      },
    ],
  },
]
