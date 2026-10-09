import { TILES_URL } from '#lib/env.js'

export const mapConfig = {
	bounds: [-187.65, 17.62, -64.51, 71.44],
	styleID: 'light-v10',
	minZoom: 2,
	maxZoom: 22,
	projection: 'mercator'
}

export const sources = {
	map_units: {
		type: 'vector',
		url: `${TILES_URL}/map_units_summary.pmtiles`,
		provider: 'pmtiles',
		maxzoom: 12
	},
	// same actual source as map_units, but using maxzoom 6 to allow overzooming lowres mask
	mask_lowres: {
		type: 'vector',
		url: `${TILES_URL}/map_units_summary.pmtiles`,
		provider: 'pmtiles',
		maxzoom: 6
	},
	dams: {
		type: 'vector',
		url: `${TILES_URL}/dams.pmtiles`,
		provider: 'pmtiles',
		minzoom: 2,
		maxzoom: 16,
		promoteId: 'id'
	},
	small_barriers: {
		type: 'vector',
		url: `${TILES_URL}/small_barriers.pmtiles`,
		provider: 'pmtiles',
		minzoom: 2,
		maxzoom: 16,
		promoteId: 'id'
	},
	combined_barriers: {
		type: 'vector',
		url: `${TILES_URL}/combined_barriers.pmtiles`,
		provider: 'pmtiles',
		minzoom: 2,
		maxzoom: 16,
		promoteId: 'id'
	},
	largefish_barriers: {
		type: 'vector',
		url: `${TILES_URL}/largefish_barriers.pmtiles`,
		provider: 'pmtiles',
		minzoom: 2,
		maxzoom: 16,
		promoteId: 'id'
	},
	smallfish_barriers: {
		type: 'vector',
		url: `${TILES_URL}/smallfish_barriers.pmtiles`,
		provider: 'pmtiles',
		minzoom: 2,
		maxzoom: 16,
		promoteId: 'id'
	},
	road_crossings: {
		type: 'vector',
		url: `${TILES_URL}/road_crossings.pmtiles`,
		provider: 'pmtiles',
		minzoom: 3,
		maxzoom: 16
	},
	waterfalls: {
		type: 'vector',
		url: `${TILES_URL}/waterfalls.pmtiles`,
		provider: 'pmtiles',
		minzoom: 9,
		maxzoom: 16,
		promoteId: 'id'
	},
	networks: {
		type: 'vector',
		url: `${TILES_URL}/networks.pmtiles`,
		provider: 'pmtiles',
		minzoom: 3,
		maxzoom: 16
	},
	priority_areas: {
		type: 'vector',
		url: `${TILES_URL}/priority_areas.pmtiles`,
		provider: 'pmtiles',
		maxzoom: 12
	}
}

export const basemapLayers = {
	imagery: [
		{
			id: 'imagery',
			source: {
				type: 'raster',
				tiles: [
					'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
				],
				attribution: 'Esri, DigitalGlobe. ...',
				tileSize: 256
			},
			type: 'raster',
			layout: {
				visibility: 'none'
			}
		},
		{
			id: 'imagery-ref',
			source: {
				type: 'raster',
				tiles: [
					'https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}'
				],
				tileSize: 256
			},
			type: 'raster',
			layout: {
				visibility: 'none'
			}
		},
		{
			id: 'imagery-streets',
			source: {
				type: 'raster',
				tiles: [
					'https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}'
				],
				tileSize: 256
			},
			type: 'raster',
			minzoom: 10,
			layout: {
				visibility: 'none'
			},
			paint: {
				'raster-opacity': {
					stops: [
						[10, 0.1],
						[12, 0.5],
						[14, 1]
					]
				}
			}
		}
	],
	topo: [
		{
			id: 'topo',
			source: {
				type: 'raster',
				tiles: [
					'https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}'
				],
				attribution: 'Esri, HERE, Garmin, ...',
				tileSize: 256
			},
			type: 'raster',
			layout: {
				visibility: 'none'
			}
		}
	],
	streets: [
		{
			id: 'streets',
			source: {
				type: 'raster',
				tiles: [
					'https://services.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}'
				],
				attribution: 'Esri, HERE, Garmin, ...',
				tileSize: 256
			},
			type: 'raster',
			layout: {
				visibility: 'none'
			}
		}
	]
}

// used for downloadable reports
export const basemapAttribution = {
	imagery: '© Mapbox, © OpenStreetMap',
	'light-v10': '© Mapbox, © OpenStreetMap',
	topo: 'Esri, HERE, Garmin, Intermap, increment P Corp., GEBCO, USGS, FAO, NPS, NRCAN, GeoBase, IGN, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), © OpenStreetMap contributors, and the GIS User Community',
	streets:
		'Esri, HERE, Garmin, USGS, Intermap, INCREMENT P, NRCan, Esri Japan, METI, Esri China (Hong Kong), Esri Korea, Esri (Thailand), NGCC, © OpenStreetMap contributors, and the GIS User Community'
}
