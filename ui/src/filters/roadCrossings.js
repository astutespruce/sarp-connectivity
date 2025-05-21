import {
  BOOLEAN_FIELD,
  RARESPP,
  TROUT,
  SALMONID_ESU,
  SALMONID_ESU_COUNT,
  INTERMITTENT,
  CANAL,
  CROSSING_TYPE,
  STREAMORDER,
  ANNUAL_FLOW,
  OWNERTYPE,
  BARRIEROWNERTYPE,
  DISADVANTAGED_COMMUNITY,
  SURVEYED,
  FISH_HABITAT_PARTNERSHIPS,
  DIADROMOUS_HABITAT,
  WILDSCENIC_RIVER,
  YEAR_SURVEYED_BINS,
} from 'config'

import { getEntries } from './common'

export const roadCrossings = [
  {
    id: 'surveyed',
    title: 'Surveyed status',
    filters: [
      {
        field: 'surveyed',
        title: 'Has crossing been surveyed?',
        help: 'Road/stream crossings are likely surveyed if there is an inventoried road-related barrier within 50-100m (depends on data source)',
        sort: false,
        hideIfEmpty: false,
        ...getEntries(SURVEYED),
      },
      {
        field: 'yearsurveyedclass',
        title: 'Year surveyed',
        sort: false,
        hideMissingValues: false,
        ...getEntries(YEAR_SURVEYED_BINS),
      },
      {
        field: 'resurveyed',
        title: 'Has the crossing been resurveyed?',
        sort: false,
        hideMissingValues: false,
        ...getEntries(BOOLEAN_FIELD),
      },
    ],
  },
  {
    id: 'social_benefits',
    title: 'Social Benefits & Partners',
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
      {
        field: 'fishhabitatpartnership',
        title: 'Fish Habitat Partnerships working in area',
        help: '',
        sort: false,
        hideMissingValues: true,
        hideIfEmpty: true,
        isArray: true,
        labels: Object.values(FISH_HABITAT_PARTNERSHIPS).map(
          ({ name }) => name
        ),
        values: Object.keys(FISH_HABITAT_PARTNERSHIPS),
      },
    ],
  },
  {
    id: 'conservation_benefits',
    title: 'Conservation benefits',
    filters: [
      {
        field: 'wildscenicriver',
        title: 'Near a Wild & Scenic River',
        sort: false,
        help: 'Note: Wild & Scenic river corridors are extracted from the Protected Areas Database of the U.S. (v4).  Barriers are considered near a Wild & Scenic River if they are within 250 meters but outside a corridor.',
        ...getEntries(WILDSCENIC_RIVER),
      },
      {
        field: 'wilderness',
        title: 'Within a designated wilderness area',
        sort: false,
        help: 'Note: wilderness areas are extracted from the Protected Areas Database of the U.S. (v4).',
        ...getEntries(BOOLEAN_FIELD),
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
      {
        field: 'canal',
        title: 'Located on a canal or ditch',
        sort: false,
        help: 'Note: canal / ditch status is assigned in the underlying NHD data and is not necessarily assigned for all stream reaches.',
        ...getEntries(CANAL),
      },
      {
        field: 'annualflowclass',
        title: 'Stream reach annual flow rate',
        sort: false,
        help: 'Note: annual flow rate is estimated at the downstream endpoint of the stream reach to which this barrier snapped and is not available for all reaches within the underlying NHD data.',
        ...getEntries(ANNUAL_FLOW),
      },
    ],
  },
  {
    id: 'marine',
    title: 'Marine connectivity & diadromous species information',
    hasData: (data) =>
      data &&
      data.numRows() > 0 &&
      data.filter((d) => d.diadromoushabitat === 1).numRows() > 0,
    filters: [
      {
        field: 'flowstoocean',
        title: 'On a network that flows to ocean',
        sort: false,
        help: 'Note: this is limited to networks that are known to connect to marine areas identified by NHD for NHD regions included in this tool, and may not be set correctly for networks that flow through other NHD regions not included in the analysis or outside the U.S. before connecting to marine areas.',
        ...getEntries(BOOLEAN_FIELD),
      },
      {
        field: 'diadromoushabitat',
        title:
          'Located on a reach with anadromous / catadromous species habitat',
        sort: false,
        help: 'Note: information on habitat of anadromous / catadromous species is quite limited, is compiled from multiple data sources, and may include a mix of current versus potential habitat for those species.',
        ...getEntries(DIADROMOUS_HABITAT),
      },
      {
        field: 'coastalhuc8',
        title: 'Within a coastal subbasin',
        sort: false,
        ...getEntries(BOOLEAN_FIELD),
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
        help: 'This information is derived from the USFS ownership parcels dataset and Protected Areas Database (PAD-US v4) to highlight ownership types of particular importance to partners.  NOTE: this does not include most private land.',
        ...getEntries(OWNERTYPE),
      },
      {
        field: 'barrierownertype',
        title: 'Barrier ownership type',
        sort: true,
        hideMissingValues: true,
        help: 'This information is derived from the National Bridge Inventory, US Census TIGER Roads route type, and USFS National Forest road / stream crossings database ownership information, and may not be fully accurate.',
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
        title: 'Native trout present',
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
