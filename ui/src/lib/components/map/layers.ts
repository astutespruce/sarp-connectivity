import { getHighlightExpr } from './util'

const flowlinesLayer = {
	id: 'flowlines',
	source: 'networks',
	'source-layer': 'networks',
	filter: ['any', ['==', 'mapcode', 0], ['==', 'mapcode', 2]],
	layout: {
		'line-cap': 'round'
	},
	minzoom: 5,
	type: 'line',
	paint: {
		'line-opacity': {
			base: 0,
			stops: [
				[5, 0.5],
				[7, 0.75],
				[9, 1]
			]
		},
		// NOTE: size classes are 0-10
		'line-width': [
			'interpolate',
			['linear'],
			['zoom'],
			6,
			['*', ['-', ['get', 'sizeclass'], 10], 0.1],
			9,
			['*', ['-', ['get', 'sizeclass'], 5], 0.1],
			11,
			['*', ['+', ['get', 'sizeclass'], 0.25], 0.1],
			12,
			['*', ['+', ['get', 'sizeclass'], 0.5], 0.25],
			14,
			['*', ['+', ['get', 'sizeclass'], 0.75], 1]
		],
		'line-color': ['case', ['<', ['get', 'mapcode'], 2], '#1891ac', '#9370db']
	}
}

const intermittentFlowlinesLayer = {
	...flowlinesLayer,
	id: 'flowlines-intermittent',
	filter: ['any', ['==', 'mapcode', 1], ['==', 'mapcode', 3]],
	paint: {
		...flowlinesLayer.paint,
		'line-dasharray': [3, 2]
	}
}

const networkHighlightLayer = {
	...flowlinesLayer,
	id: 'network-highlight',
	filter: ['==', 'dams', Infinity],
	layout: {
		'line-cap': 'butt'
	},
	paint: {
		...flowlinesLayer.paint,
		'line-opacity': 1,
		'line-color': '#fd8d3c',
		'line-width': [
			'interpolate',
			['linear'],
			['zoom'],
			6,
			['*', ['-', ['get', 'sizeclass'], 10], 0.1],
			9,
			['*', ['-', ['get', 'sizeclass'], 3], 0.25],
			11,
			['*', ['+', ['get', 'sizeclass'], 0.25], 0.15],
			12,
			['*', ['+', ['get', 'sizeclass'], 0.5], 0.25],
			14,
			['*', ['+', ['get', 'sizeclass'], 1], 0.5]
		],
		'line-gap-width': [
			'interpolate',
			['linear'],
			['zoom'],
			6,
			['*', ['-', ['get', 'sizeclass'], 10], 0.1],
			9,
			['*', ['-', ['get', 'sizeclass'], 3], 0.5],
			12,
			['*', ['+', ['get', 'sizeclass'], 0.5], 0.75],
			14,
			['*', ['+', ['get', 'sizeclass'], 0.75], 1.5]
		]
	}
}

const intermittentNetworkHighlightLayer = {
	...networkHighlightLayer,
	id: 'network-intermittent-highlight',
	paint: {
		...networkHighlightLayer.paint
	}
}

const removedNetworkHighlightLayer = {
	...networkHighlightLayer,
	id: 'removed-network-highlight',
	'source-layer': 'removed_networks',
	filter: ['==', 'id', Infinity],
	paint: {
		...networkHighlightLayer.paint
	}
}

const removedIntermittentNetworkHighlightLayer = {
	...removedNetworkHighlightLayer,
	id: 'removed-network-intermittent-highlight',
	paint: {
		...networkHighlightLayer.paint
	}
}

export const networkLayers = [
	networkHighlightLayer,
	intermittentNetworkHighlightLayer,
	removedNetworkHighlightLayer,
	removedIntermittentNetworkHighlightLayer,
	flowlinesLayer,
	intermittentFlowlinesLayer
]

const priorityAreasLayer = {
	// id: // provided by specific layer
	source: 'priority_areas',
	'source-layer': 'priority_areas',
	minzoom: 0,
	maxzoom: 24,
	layout: {
		visibility: 'none'
	}
	// filter: // provided based on toggle of specific subsets
}

const priorityAreasFillLayer = {
	...priorityAreasLayer,
	id: 'priority_areas-fill',
	type: 'fill',
	paint: {
		'fill-opacity': 0.4,
		'fill-color': '#3182bd'
	}
}

const priorityAreasOutlineLayer = {
	...priorityAreasLayer,
	id: 'priority_areas-outline',
	type: 'line',
	paint: {
		'line-opacity': getHighlightExpr(0.2, 1),
		'line-width': [
			'interpolate',
			['linear'],
			['zoom'],
			4,
			getHighlightExpr(0.1, 2),
			8,
			getHighlightExpr(0.5, 3)
		],
		'line-color': getHighlightExpr('#AAAAAA', '#000000')
	}
}

export const priorityAreaLayers = [priorityAreasFillLayer, priorityAreasOutlineLayer]
