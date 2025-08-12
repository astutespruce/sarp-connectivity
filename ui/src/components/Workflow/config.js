import { siteMetadata } from 'config'

const { tileHost } = siteMetadata

export const unitLayerConfig = {
  HUC6: {
    title: 'Basin',
    minzoom: 0,
    maxzoom: 24,
  },
  HUC8: {
    minzoom: 0,
    maxzoom: 24,
    parent: {
      id: 'HUC6',
      minzoom: 4,
    },
  },
  HUC10: {
    minzoom: 6,
    maxzoom: 24,
    parent: {
      id: 'HUC8',
      minzoom: 7,
    },
  },
  HUC12: {
    minzoom: 8,
    maxzoom: 24,
    parent: {
      id: 'HUC10',
      minzoom: 9,
    },
  },
  State: {
    minzoom: 0,
    maxzoom: 24,
  },
  County: {
    minzoom: 3,
    maxzoom: 24,
    parent: {
      id: 'State',
      minzoom: 0,
    },
  },
  CongressionalDistrict: {
    minzoom: 1,
    maxzoom: 24,
  },
  StateWRA: {
    minzoom: 1,
    maxzoom: 24,
  },
}

export const sources = {
  priority_areas: {
    type: 'vector',
    maxzoom: 12,
    tiles: [`${tileHost}/services/priority_areas/tiles/{z}/{x}/{y}.pbf`],
  },
}

export const priorityAreasLegend = {
  color: '#3182bd99',
  entries: [
    {
      id: 'hifhp_gfa',
      label: 'Hawaii Fish Habitat Partnership geographic focus areas',
      showName: true,
    },

    {
      id: 'sarp_coa',
      label: 'SARP conservation opportunity areas',
      showName: true,
    },
    {
      id: 'wsr_designated_corridor',
      label: 'Designated Wild & Scenic River corridor',
    },
    {
      id: 'wsr_eligible_suitable_corridor',
      label: 'Eligible / suitable Wild & Scenic River corridor',
    },
    {
      id: 'wsr_designated_buffer',
      label: 'Near designated Wild & Scenic River (outside corridor)',
    },
    {
      id: 'wsr_eligible_suitable_buffer',
      label: 'Near eligible / suitable Wild & Scenic River (outside corridor)',
    },
  ],
}
