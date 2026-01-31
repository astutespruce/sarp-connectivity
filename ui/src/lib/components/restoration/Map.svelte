<script lang="ts">
	import { Popup } from 'mapbox-gl'
	import type { FeatureSelector, GeoJSONFeature, Point } from 'mapbox-gl'
	import { untrack } from 'svelte'

	import {
		Map,
		Legend,
		interpolateExpr,
		networkLayers,
		highlightNetwork,
		setBarrierHighlight,
		getBarrierTooltip,
		runOnceOnIdle
	} from '$lib/components/map'
	import { shortBarrierTypeLabels, pointLegends, SUMMARY_UNIT_COLORS } from '$lib/config/constants'
	import type { BarrierTypePlural, FocalBarrierType } from '$lib/config/types'
	import { isEqual } from '$lib/util/data'
	import { summaryUnitLayers, removedBarrierPointLayer, regionMask, regionBoundary } from './layers'

	const barrierTypes: FocalBarrierType[] = ['dams', 'small_barriers', 'combined_barriers']

	let {
		map = $bindable(),
		region: regionProp,
		system,
		focalBarrierType,
		summaryUnits = [],
		selectedBarrier = null,
		onSelectUnit,
		onSelectBarrier,
		children
	} = $props()

	// only use initial value of region when setting up layers (it is a route variable and does not change after mount)
	const region = $state.snapshot(untrack(() => regionProp))

	const barrierTypeLabel = $derived(shortBarrierTypeLabels[focalBarrierType as BarrierTypePlural])

	let zoom = $state(0)
	let hoverFeature: (FeatureSelector & GeoJSONFeature) | null = $state(null)
	let selectedFeature: (FeatureSelector & GeoJSONFeature) | null = $state(null)

	// @ts-expect-error layers is constructed dynamically
	const layers = []

	// add layers to map
	// set all layers as invisible to start; these will be set via an effect
	summaryUnitLayers.forEach(({ id, fill, outline }) => {
		// base config for each layer
		const config = {
			source: 'map_units',
			'source-layer': id
		}

		// fill layer
		const fillID = `${id}-fill`
		layers.push({
			...config,
			...fill,
			id: fillID,
			type: 'fill',
			layout: {
				visibility: 'none'
			},
			paint: {
				'fill-opacity': fill.paint['fill-opacity']
			}
		})

		// outline layer
		layers.push({
			...config,
			...outline,
			id: `${id}-outline`,
			type: 'line',
			maxzoom: 24,
			layout: {
				visibility: 'none',
				'line-cap': 'round',
				'line-join': 'round'
			},
			paint: {
				'line-opacity': 1,
				'line-width': outline.paint['line-width'],
				'line-color': SUMMARY_UNIT_COLORS.Greens[7][3]
			}
		})

		// highlight layer
		layers.push({
			...config,
			id: `${id}-highlight`,
			type: 'line',
			minzoom: 0,
			maxzoom: 21,
			layout: {
				visibility: 'none',
				'line-cap': 'round',
				'line-join': 'round'
			},
			paint: {
				'line-opacity': 1,
				'line-width': 3,
				'line-color': '#333'
			},
			filter: ['==', 'id', Infinity]
		})
	})

	// Add network layers
	layers.push(...networkLayers)

	barrierTypes.forEach((t) => {
		layers.push({
			id: `removed_${t}`,
			source: t,
			'source-layer': `removed_${t}`,
			...removedBarrierPointLayer,
			layout: {
				visibility: 'none'
			}
		})
	})

	// Add region mask / boundary layers
	// NOTE: we intentionally use the first value of region here; it does not change after mounting
	layers.push({
		...regionMask,
		filter: ['==', 'id', `${region.id}_mask`]
	})
	layers.push({
		...regionBoundary,
		'source-layer': region.boundaryLayer,
		filter: ['==', 'id', region.id]
	})

	const clearNetworkHighlight = () => {
		map.setFilter('network-highlight', ['==', 'dams', Infinity])
		map.setFilter('network-intermittent-highlight', ['==', 'dams', Infinity])
		map.setFilter('removed-network-highlight', ['==', 'id', Infinity])
		map.setFilter('removed-network-intermittent-highlight', ['==', 'id', Infinity])
	}

	/**
	 * Setup click and hover handlers
	 */
	const handleCreateMap = () => {
		// keep track of zoom for legend
		zoom = map.getZoom()
		map.on('zoomend', () => {
			zoom = map.getZoom()
		})

		const pointLayers = barrierTypes.map((t) => `removed_${t}`)
		const clickLayers = pointLayers.concat(summaryUnitLayers.map(({ id }) => `${id}-fill`))

		// add hover and tooltip to point layers
		const tooltip = new Popup({
			closeButton: false,
			closeOnClick: false,
			anchor: 'left',
			offset: 20
		})
		pointLayers.forEach((id) => {
			map.on(
				'mousemove',
				id,
				({ features: [feature] }: { features: ((FeatureSelector & GeoJSONFeature) | null)[] }) => {
					if (map.getZoom() < 9) {
						return
					}
					const {
						// @ts-expect-error coordinates is valid
						geometry: { coordinates }
					} = feature
					setBarrierHighlight(map, hoverFeature, false)
					hoverFeature = feature
					setBarrierHighlight(map, feature, true)
					map.getCanvas().style.cursor = 'pointer'
					tooltip
						.setLngLat(coordinates)
						.setHTML(
							getBarrierTooltip(
								feature?.source === 'combined_barriers'
									? feature?.properties?.barriertype
									: feature?.source,
								feature?.properties as { sarpidname: string | undefined }
							)
						)
						.addTo(map)
				}
			)
			map.on('mouseleave', id, () => {
				// only unhighlight if not the same as currently selected feature
				const prevFeature = hoverFeature
				if (prevFeature) {
					if (
						!selectedFeature ||
						prevFeature.id !== selectedFeature.id ||
						prevFeature?.layer?.id !== selectedFeature?.layer?.id
					) {
						setBarrierHighlight(map, prevFeature, false)
					}
				}
				hoverFeature = null
				map.getCanvas().style.cursor = ''
				tooltip.remove()
			})
		})
		map.on('click', ({ point }: { point: Point }) => {
			const [feature] = map.queryRenderedFeatures(point, {
				layers: clickLayers
			})
			// always clear out prior feature
			if (selectedFeature) {
				setBarrierHighlight(map, selectedFeature, false)
				selectedFeature = null
				if (isEqual(selectedFeature, hoverFeature, ['id', 'layer'])) {
					setBarrierHighlight(map, hoverFeature, false)
					hoverFeature = null
				}
			}
			if (!feature) {
				// clear out any selected barriers
				onSelectBarrier(null)
				return
			}
			const { source, sourceLayer, properties } = feature

			if (source === 'map_units') {
				// map unit layer
				const { id } = properties
				onSelectUnit({ layer: sourceLayer, id })
				return
			}
			const {
				geometry: {
					coordinates: [lon, lat]
				}
			} = feature
			setBarrierHighlight(map, feature, true)
			selectedFeature = feature
			const removed = sourceLayer.startsWith('removed_')
			const thisBarrierType = source === 'combined_barriers' ? properties.barriertype : source
			// promote network fields if clicking on a waterfall
			let networkIDField = 'upnetid'
			if (removed) {
				networkIDField = 'id'
			} else if (thisBarrierType === 'waterfalls') {
				networkIDField = `${focalBarrierType}_upnetid`
			}

			// dam, barrier, waterfall
			onSelectBarrier({
				...properties,
				upnetid: properties[networkIDField] || Infinity,
				barrierType: thisBarrierType,
				// use combined barrier networks unless we are looking at only
				// dams
				networkType: focalBarrierType === 'dams' ? 'dams' : 'combined_barriers',
				lat,
				lon,
				ranked: sourceLayer.startsWith('ranked_'),
				removed,
				layer: {
					source,
					sourceLayer
				}
			})
		})
	}

	/**
	 * Update summary unit layer visibility and rendering on change of system
	 * and focalBarrierType
	 */
	const updateSummaryUnitLayers = () => {
		const subLayers = ['fill', 'outline', 'highlight']

		// update renderer and filter on all layers
		const fieldExpr =
			focalBarrierType === 'combined_barriers'
				? ['+', ['get', 'removed_dams'], ['get', 'removed_small_barriers']]
				: ['get', `removed_${focalBarrierType}`]

		// update layer visibility and rendering

		// @ts-expect-error focalBarrierType is a valid key
		summaryUnitLayers.forEach(({ id, system: lyrSystem, bins: { [focalBarrierType]: bins } }) => {
			const visibility = lyrSystem === system ? 'visible' : 'none'
			subLayers.forEach((suffix) => {
				map.setLayoutProperty(`${id}-${suffix}`, 'visibility', visibility)

				if (lyrSystem === system) {
					// NOTE: only update the visible layers, otherwise map gets hung up and doesn't return to idle
					const colors =
						SUMMARY_UNIT_COLORS.Greens[bins.length as keyof typeof SUMMARY_UNIT_COLORS.Greens]
					map.setPaintProperty(`${id}-fill`, 'fill-color', [
						'match',
						fieldExpr,
						0,
						SUMMARY_UNIT_COLORS.empty,
						interpolateExpr(fieldExpr, bins, colors)
					])
				}
			})
		})
	}

	/**
	 * Update barrier layer visibility based on focalBarrierType
	 */
	const updateBarrierTypeVisibility = () => {
		barrierTypes.forEach((t) => {
			const visibility = focalBarrierType === t ? 'visible' : 'none'
			map.setLayoutProperty(`removed_${t}`, 'visibility', visibility)
		})

		clearNetworkHighlight()
	}

	/**
	 * Update highlight of selected barrier's network
	 */
	const updateSelectedBarrierNetwork = () => {
		clearNetworkHighlight()

		if (selectedBarrier) {
			const { upnetid: networkID = Infinity } = selectedBarrier
			highlightNetwork(
				map,
				focalBarrierType === 'dams' ? 'dams' : 'combined_barriers',
				networkID,
				selectedBarrier.removed
			)
		} else {
			if (selectedFeature) {
				setBarrierHighlight(map, selectedFeature, false)
				hoverFeature = null

				if (isEqual(selectedFeature, hoverFeature, ['id', 'layer'])) {
					setBarrierHighlight(map, hoverFeature, false)
					hoverFeature = null
				}
			}
		}
	}

	const updateSelectedSummaryUnits = () => {
		const ids = summaryUnits.map(({ id }: { id: string }) => id)

		summaryUnitLayers.forEach(({ id: lyrId, system: lyrSystem }) => {
			map.setFilter(
				`${lyrId}-highlight`,
				lyrSystem === system && ids.length > 0 ? ['in', 'id', ...ids] : ['==', 'id', Infinity]
			)
		})
	}

	// update summary unit layers on change of system, focalBarrierType
	$effect.pre(() => {
		system
		focalBarrierType

		if (!map) {
			return
		}

		runOnceOnIdle(map, updateSummaryUnitLayers)
	})

	// update barrier layers on change of focalBarrierType
	$effect.pre(() => {
		focalBarrierType

		if (!map) {
			return
		}

		runOnceOnIdle(map, updateBarrierTypeVisibility)
	})

	// update highlight of selected barrier network on change of selected barrier
	$effect.pre(() => {
		selectedBarrier

		if (!map) {
			return
		}

		runOnceOnIdle(map, updateSelectedBarrierNetwork)
	})

	/**
	 * Update filters on summary unit layers to highlight selected summary units
	 */
	$effect.pre(() => {
		summaryUnits

		runOnceOnIdle(map, updateSelectedSummaryUnits)
	})

	const { layerTitle = '', legendEntries = [] } = $derived.by(() => {
		if (!map) {
			return {}
		}

		const [layer] = summaryUnitLayers.filter(
			({ system: lyrSystem, fill: { minzoom, maxzoom } }) =>
				lyrSystem === system && zoom >= minzoom && zoom <= maxzoom
		)

		if (layer === undefined) {
			return {}
		}

		const {
			title,
			// @ts-expect-error focalBarrierType is a valid key
			bins: { [focalBarrierType]: bins }
		} = layer
		// flip the order of colors and bins since we are displaying from top to bottom
		// add opacity to color
		const colors = SUMMARY_UNIT_COLORS.Greens[
			bins.length as keyof typeof SUMMARY_UNIT_COLORS.Greens
		]
			.map((c) => `${c}4d`)
			.reverse()

		const labels = bins
			.map((bin: number, i: number) => {
				if (i === 0) {
					return `≤ ${Math.round(bin).toLocaleString()}`
				}
				if (i === bins.length - 1) {
					return `≥ ${Math.round(bin).toLocaleString()}`
				}
				// Use midpoint value
				return Math.round(bin).toLocaleString()
			})
			.reverse()

		const patchEntries = colors.map((color, i) => ({
			color,
			label: labels[i]
		}))

		patchEntries.push({
			color: 'rgba(0,0,0,0.15)',
			label: `no inventoried ${barrierTypeLabel}`
		})

		const circles = []
		if (map && map.getZoom() >= 8) {
			const { unrankedBarriers } = pointLegends
			const removedLegend = unrankedBarriers.filter(({ id }) => id === 'removed')[0]
			circles.push({
				...removedLegend.getSymbol(focalBarrierType),
				label: removedLegend.getLabel(barrierTypeLabel)
			})
		}

		let lines = null
		if (zoom >= 11) {
			lines = [
				{
					id: 'normal',
					label: 'stream reach',
					color: '#1891ac',
					lineWidth: '2px'
				},
				{
					id: 'altered',
					label: 'altered stream reach (canal / ditch / reservoir)',
					color: '#9370db',
					lineWidth: '2px'
				},
				{
					id: 'intermittent',
					label: 'intermittent / ephemeral stream reach',
					color: '#1891ac',
					lineStyle: 'dashed',
					lineWidth: '2px'
				}
			]
		}

		return {
			layerTitle: title,
			legendEntries: {
				patches: [{ id: 'summaryAreas', entries: patchEntries }],
				circles,
				lines
			}
		}
	})
</script>

<Map bind:map bounds={region.bbox} {layers} onCreateMap={handleCreateMap}>
	<Legend title={layerTitle} subtitle={`number of ${barrierTypeLabel}`} {...legendEntries} />

	{@render children()}
</Map>
