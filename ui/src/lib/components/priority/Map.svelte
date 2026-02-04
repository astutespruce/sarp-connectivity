<script lang="ts">
	import { Popup } from 'mapbox-gl'
	import type { FeatureSelector, GeoJSONFeature, Point } from 'mapbox-gl'
	import { untrack } from 'svelte'

	import { shortBarrierTypeLabels, pointLegends } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import {
		Map,
		highlightNetwork,
		setBarrierHighlight,
		getInArrayExpr,
		getInStringExpr,
		getInMapUnitsExpr,
		getBarrierTooltip,
		getBitFromBitsetExpr,
		runOnceOnIdle
	} from '$lib/components/map'
	import type { Circle, Patch } from '$lib/components/map/legend/types'

	import { isEqual } from '$lib/util/data'

	import { unitLayerConfig } from '$lib/components/workflow/config'
	import { unitLayers, unitHighlightLayers, parentOutline } from '$lib/components/workflow/layers'

	import {
		prioritizedPointLayer,
		unrankedPointLayer,
		removedBarrierPointLayer,
		otherBarrierPointLayer,
		excludedPointLayer,
		includedPointLayer,
		roadCrossingsLayer,
		damsSecondaryLayer,
		waterfallsLayer,
		getTierPointColor,
		getTierPointSize
	} from './layers'

	let {
		map = $bindable(),
		networkType: networkTypeProp,
		crossfilter,
		activeLayer,
		summaryUnits,
		allowUnitSelect,
		selectedBarrier = null,
		rankedBarriers,
		tierThreshold,
		scenario,
		bounds,
		onSelectUnit,
		onSelectBarrier,
		onCreateMap,
		children,
		class: className = null
	} = $props()

	// only use initial value of network type when setting up layers (it is a route variable and does not change after mount)
	const networkType = $state.snapshot(untrack(() => networkTypeProp))

	const barrierTypeLabel = $derived(shortBarrierTypeLabels[networkType as BarrierTypePlural])

	let zoom = $state(0)
	let hoverFeature: (FeatureSelector & GeoJSONFeature) | null = $state.raw(null)
	let selectedFeature: (FeatureSelector & GeoJSONFeature) | null = $state.raw(null)

	// we keep a cached copy of the ranked barriers so we can unset their feature state on change of ranked barriers
	let prevRankedBarrierIds: number[] = $state.raw([])
	let rankedBarriersIndex = $state.raw({})
	let timeout = $state()

	const tooltip = new Popup({
		closeButton: false,
		closeOnClick: false,
		anchor: 'left',
		offset: 20
	})

	// @ts-expect-error layers is constructed dynamically
	const layers = []

	// Add summary unit layers
	// @ts-expect-error parent is valid
	Object.entries(unitLayerConfig).forEach(([layer, { minzoom = 0, maxzoom = 24, parent }]) => {
		const config = {
			'source-layer': layer,
			minzoom,
			maxzoom
		}

		if (parent) {
			layers.push({
				'source-layer': parent.id,
				minzoom: parent.minzoom || minzoom,
				maxzoom: parent.maxzoom || maxzoom,
				...parentOutline,
				id: `${layer}-${parentOutline.id}`
			})
		}

		// Each layer has 2 display layers: outline, fill
		// show grey fill when the map unit cannot be ranked
		let bitPos = 0

		switch (networkType) {
			case 'dams': {
				bitPos = 0
				break
			}
			case 'small_barriers': {
				bitPos = 1
				break
			}
			case 'combined_barriers': {
				bitPos = 2
				break
			}
			case 'largefish_barriers': {
				bitPos = 3
				break
			}
			case 'smallfish_barriers': {
				bitPos = 4
				break
			}
		}

		const fillExpr = ['case', ['==', getBitFromBitsetExpr('has_data', bitPos), 0], 0.25, 0]

		// make all layers initially hidden; these are shown via an effect below
		unitLayers.forEach(({ id, ...rest }) => {
			const unitLayer = { ...config, ...rest, id: `${layer}-${id}`, layout: { visibility: 'none' } }

			if (id === 'unit-fill') {
				// @ts-expect-error fill-opacity is valid key
				unitLayer.paint['fill-opacity'] = fillExpr
			}

			layers.push(unitLayer)
		})

		// Each layer has 2 highlight layers: highlight fill, highlight outline
		unitHighlightLayers.forEach(({ id, ...rest }) => {
			layers.push({ ...config, ...rest, id: `${layer}-${id}` })
		})
	})

	// add waterfalls
	layers.push(waterfallsLayer)

	// add road crossings layer
	layers.push({
		...roadCrossingsLayer,
		layout: {
			visibility: networkType !== 'dams' ? 'visible' : 'none'
		}
	})

	// add secondary dams layer (only applicable for small barriers)
	layers.push({
		...damsSecondaryLayer,
		layout: {
			visibility: networkType === 'small_barriers' ? 'visible' : 'none'
		}
	})

	layers.push({
		source: networkType,
		'source-layer': `other_${networkType}`,
		...otherBarrierPointLayer
	})

	layers.push({
		source: networkType,
		'source-layer': `removed_${networkType}`,
		...removedBarrierPointLayer
	})

	layers.push({
		source: networkType,
		'source-layer': `unranked_${networkType}`,
		...unrankedPointLayer
	})

	// add primary barrier-type point layers
	const pointConfig = {
		source: networkType,
		'source-layer': `ranked_${networkType}`
	}

	// all points are initially excluded from analysis until their
	// units are selected
	layers.push({ ...pointConfig, ...excludedPointLayer })
	layers.push({
		...pointConfig,
		...includedPointLayer
	})

	// prioritized points are not initially visible
	layers.push({
		...pointConfig,
		...prioritizedPointLayer,

		paint: {
			...prioritizedPointLayer.paint
		}
	})

	const pointLayers = [
		roadCrossingsLayer.id,
		damsSecondaryLayer.id,
		waterfallsLayer.id,
		removedBarrierPointLayer.id,
		otherBarrierPointLayer.id,
		unrankedPointLayer.id,
		excludedPointLayer.id,
		includedPointLayer.id,
		prioritizedPointLayer.id
	]

	const clickLayers = pointLayers.concat(
		Object.keys(unitLayerConfig).map((id) => `${id}-unit-fill`)
	)

	const clearNetworkHighlight = () => {
		map.setFilter('network-highlight', ['==', 'dams', Infinity])
		map.setFilter('network-intermittent-highlight', ['==', 'dams', Infinity])
		map.setFilter('removed-network-highlight', ['==', 'id', Infinity])
		map.setFilter('removed-network-intermittent-highlight', ['==', 'id', Infinity])
	}

	const handleCreateMap = () => {
		// keep track of zoom for legend
		zoom = map.getZoom()
		map.on('zoomend', () => {
			zoom = map.getZoom()
		})

		pointLayers.forEach((id) => {
			// @ts-expect-error ignore typing on feature
			map.on('mousemove', id, ({ features: [feature] }) => {
				if (map.getZoom() < 8) {
					return
				}

				const {
					geometry: { coordinates },
					properties,
					source
				} = feature

				setBarrierHighlight(map, hoverFeature, false)
				hoverFeature = feature
				setBarrierHighlight(map, feature, true)

				map.getCanvas().style.cursor = 'pointer'

				tooltip
					.setLngLat(coordinates)
					.setHTML(
						getBarrierTooltip(
							source === 'combined_barriers' ||
								source === 'largefish_barriers' ||
								source === 'smallfish_barriers'
								? properties.barriertype
								: source,
							properties
						)
					)
					.addTo(map)
			})
			map.on('mouseleave', id, () => {
				// only unhighlight if not the same as currently selected feature
				const prevFeature = hoverFeature

				if (prevFeature) {
					if (
						!selectedFeature ||
						prevFeature.id !== selectedFeature.id ||
						prevFeature.layer?.id !== selectedFeature.layer?.id
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
			const features = map.queryRenderedFeatures(point, {
				layers: clickLayers
			})

			const [feature] = features

			// always clear out prior feature
			const prevFeature = selectedFeature
			if (prevFeature) {
				setBarrierHighlight(map, prevFeature, false)

				selectedFeature = null

				if (isEqual(prevFeature, hoverFeature, ['id', 'layer'])) {
					setBarrierHighlight(map, hoverFeature, false)
					hoverFeature = null
				}
			}

			// only call handler if there was a feature
			if (!feature) {
				onSelectBarrier(null)
				return
			}

			const {
				source,
				sourceLayer,
				properties,
				geometry: {
					coordinates: [lon, lat]
				}
			} = feature

			if (source === 'map_units') {
				onSelectUnit({ layer: sourceLayer, id: properties.id })
				return
			}

			if (map.getZoom() < 8) {
				// don't allow selection of points below zoom 8
				const [unitLayerFeature] = features.filter(
					({ source: lyrSource }: { source: string }) => lyrSource === 'map_units'
				)
				if (unitLayerFeature) {
					onSelectUnit({
						layer: unitLayerFeature.sourceLayer,
						id: unitLayerFeature.properties.id
					})
				}
				return
			}

			const removed = sourceLayer.startsWith('removed_')

			const thisBarrierType =
				source === 'combined_barriers' ||
				source === 'largefish_barriers' ||
				source === 'smallfish_barriers'
					? properties.barriertype
					: source

			const network = networkType === 'small_barriers' ? 'combined_barriers' : networkType

			// promote network fields if clicking on a waterfall
			let networkIDField = 'upnetid'
			if (removed) {
				networkIDField = 'id'
			} else if (thisBarrierType === 'waterfalls') {
				networkIDField = `${network}_upnetid`
			}

			setBarrierHighlight(map, feature, true)
			selectedFeature = feature

			onSelectBarrier({
				upnetid: properties[networkIDField] || Infinity,
				...properties,
				tiers: rankedBarriersIndex[properties.id as keyof typeof rankedBarriersIndex] || null,
				barrierType: thisBarrierType,
				networkType,
				lat,
				lon,
				// note: ranked layers are those that can be ranked, not necessarily those that have custom ranks
				ranked: sourceLayer.startsWith('ranked_'),
				removed,
				layer: {
					source,
					sourceLayer
				}
			})
		})

		onCreateMap()
	}

	/**
	 * Update layers depending on whether they allow selection, or just show
	 * currently selected layers
	 */
	const updateSummaryUnitVisibility = () => {
		// make sure to update filters before toggling visibility
		if (activeLayer) {
			updateSelectedSummaryUnits()
		}

		// toggle visibility of layers so that we only show those layers for the activeLayer
		Object.keys(unitLayerConfig).forEach((layer) => {
			// only show the unit fill and boundary if we allow selection
			const visibility = layer === activeLayer && allowUnitSelect ? 'visible' : 'none'
			unitLayers.forEach(({ id }) => {
				map.setLayoutProperty(`${layer}-${id}`, 'visibility', visibility)
			})

			// @ts-expect-error parent is valid
			const { parent } = unitLayerConfig[layer as keyof typeof unitLayerConfig]
			if (parent) {
				map.setLayoutProperty(`${layer}-unit-parent-outline`, 'visibility', visibility)
			}

			// only show highlight fill when selecting units
			map.setLayoutProperty(`${layer}-${unitHighlightLayers[0].id}`, 'visibility', visibility)

			// show boundary highlight in all cases
			map.setLayoutProperty(
				`${layer}-${unitHighlightLayers[1].id}`,
				'visibility',
				layer === activeLayer ? 'visible' : 'none'
			)
		})
	}

	$effect.pre(() => {
		activeLayer
		allowUnitSelect

		if (!map) {
			return
		}

		runOnceOnIdle(map, updateSummaryUnitVisibility)
	})

	/**
	 * Update highlight of selected summary units in the active layer
	 */
	const updateSelectedSummaryUnits = () => {
		const ids = summaryUnits.ids
		const filterExpr = ids.length > 0 ? ['in', 'id', ...ids] : ['==', 'id', Infinity]

		unitHighlightLayers.forEach(({ id }) => {
			map.setFilter(`${activeLayer}-${id}`, filterExpr)
		})
	}

	// Highlight currently selected summaryUnits
	$effect.pre(() => {
		activeLayer
		summaryUnits.items

		if (!(map && activeLayer)) return

		runOnceOnIdle(map, updateSelectedSummaryUnits)
	})

	/**
	 * Update barrier and network highlight on change of selectedBarrier
	 */
	const updateNetworkHighlight = () => {
		clearNetworkHighlight()

		const removed = selectedBarrier && selectedBarrier.removed
		if (selectedBarrier) {
			const networkIDField = removed ? 'id' : 'upnetid'
			const { [networkIDField]: networkID = Infinity } = selectedBarrier

			highlightNetwork(
				map,
				networkType === 'small_barriers' ? 'combined_barriers' : networkType,
				networkID,
				removed
			)
		} else {
			const prevFeature = selectedFeature
			if (prevFeature) {
				setBarrierHighlight(map, prevFeature, false)
				hoverFeature = null

				if (isEqual(prevFeature, hoverFeature, ['id', 'layer'])) {
					setBarrierHighlight(map, hoverFeature, false)
					hoverFeature = null
				}
			}
		}
	}

	$effect.pre(() => {
		selectedBarrier
		networkType

		if (!map) return

		runOnceOnIdle(map, updateNetworkHighlight)
	})

	/**
	 * if map allows filter, show selected vs unselected points, and make those without networks
	 * background points
	 */
	const updateBarrierVisibility = () => {
		const ids = summaryUnits.ids

		if (!activeLayer || ids.length === 0) {
			// if no summary units are selected, reset filters on barriers
			map.setFilter(includedPointLayer.id, ['==', 'id', Infinity])
			map.setFilter(excludedPointLayer.id, null)
			return
		}

		// Construct filter expressions for each active filter
		// @ts-expect-error v.size is valid
		const filterEntries = Object.entries(crossfilter.filters).filter(([, v]) => v && v.size > 0)

		const hasActiveUnits = ids.length > 0
		const insideActiveUnitsExpr = hasActiveUnits ? getInMapUnitsExpr(activeLayer, ids) : false

		const outsideActiveUnitsExpr = hasActiveUnits ? ['!', insideActiveUnitsExpr] : true

		const includedByFilters = filterEntries.map(([field, values]) =>
			crossfilter.filterConfigIndex[field].isArray
				? getInStringExpr(field, values as string[] | number[])
				: getInArrayExpr(field, values as string[] | number[])
		)

		const excludedByFilters = includedByFilters.map((f) => ['!', f])

		// update barrier layers to select those that are in selected units
		map.setFilter(includedPointLayer.id, ['all', insideActiveUnitsExpr, ...includedByFilters])
		map.setFilter(excludedPointLayer.id, [
			'any', // should this be any?
			outsideActiveUnitsExpr,
			...excludedByFilters
		])
	}

	$effect.pre(() => {
		activeLayer
		summaryUnits.items
		// NOTE: have to take snapshot to force effect to detect deep change in filters
		$state.snapshot(crossfilter.filters)

		if (!map) return

		runOnceOnIdle(map, updateBarrierVisibility)
	})

	/**
	 * Update feature state of ranked barriers.  If ranked barriers are set,
	 * that means we were in priority results mode, and we show only prioritized
	 * vs excluded points, whereas in regular mode we show included vs excluded points
	 */
	const updateRankedBarriers = () => {
		const showRanks = rankedBarriers.length > 0
		map.setLayoutProperty(includedPointLayer.id, 'visibility', showRanks ? 'none' : 'visible')
		map.setLayoutProperty(prioritizedPointLayer.id, 'visibility', showRanks ? 'visible' : 'none')

		const { source, 'source-layer': sourceLayer } = map.getLayer(prioritizedPointLayer.id)

		// unset feature state for all ranked points
		if (prevRankedBarrierIds && prevRankedBarrierIds.length) {
			prevRankedBarrierIds.forEach((id: number) => {
				// NOTE: this removes all feature state including selected and hover
				// but neither of those should be active on transition to showing
				// ranked barriers
				map.removeFeatureState({ source, sourceLayer, id })
			})
		}
		if (showRanks) {
			// apply initial rendering of prioritized points to avoid initial flash of unstyled poitns
			map.setPaintProperty(
				prioritizedPointLayer.id,
				'circle-color',
				getTierPointColor(scenario, tierThreshold)
			)
			map.setPaintProperty(
				prioritizedPointLayer.id,
				'circle-radius',
				getTierPointSize(scenario, tierThreshold)
			)

			// copy filters to ranked layers
			map.setFilter(prioritizedPointLayer.id, map.getFilter(includedPointLayer.id))
			rankedBarriers.forEach(({ id, ...rest }: { id: string }) => {
				map.setFeatureState({ source, sourceLayer, id }, rest)
			})
			rankedBarriersIndex = Object.fromEntries(rankedBarriers.map((b: { id: string }) => [b.id, b]))
		} else {
			rankedBarriersIndex = {}
		}

		// cache ranked barrier ids
		prevRankedBarrierIds = $state.snapshot(
			untrack(() => rankedBarriers.map(({ id }: { id: number }) => id))
		)
	}

	$effect.pre(() => {
		rankedBarriers

		if (!map) {
			return
		}

		runOnceOnIdle(map, updateRankedBarriers)
	})

	/**
	 * Update rank filtering of barriers
	 * Note: this is debounced to prevent frequent redraws
	 * which have bad performance with high numbers of barriers
	 */
	const updateRankedBarrierRendering = () => {
		untrack(() => {
			// @ts-expect-error ignore typing error here
			clearTimeout(timeout)

			// use shorter timeout if fewer points
			const timeoutDuration = rankedBarriers && rankedBarriers.length > 5000 ? 300 : 100

			timeout = setTimeout(() => {
				// do not set paint properties on layers that are not visible
				if (map.getLayoutProperty('point-prioritized', 'visibility') === 'none') {
					return
				}

				map.setPaintProperty(
					prioritizedPointLayer.id,
					'circle-color',
					getTierPointColor(scenario, tierThreshold)
				)
				map.setPaintProperty(
					prioritizedPointLayer.id,
					'circle-radius',
					getTierPointSize(scenario, tierThreshold)
				)
			}, timeoutDuration)
		})
	}

	$effect.pre(() => {
		tierThreshold
		scenario
		rankedBarriers

		if (!(map && rankedBarriers)) {
			return
		}

		runOnceOnIdle(map, updateRankedBarrierRendering)
	})

	const { legendEntries, footnote: legendFootnote } = $derived.by(() => {
		const pointLayers = [
			includedPointLayer,
			excludedPointLayer,
			otherBarrierPointLayer,
			prioritizedPointLayer
		]

		const isWithinZoom = pointLayers.reduce(
			(prev, { id, minzoom, maxzoom }) =>
				Object.assign(prev, {
					[id]: zoom >= minzoom && zoom <= maxzoom
				}),
			{}
		)

		const {
			included: includedLegend,
			excluded: excludedLegend,
			topRank: topRankLegend,
			lowerRank: lowerRankLegend,
			unrankedBarriers,
			other
		} = pointLegends

		const circles: Circle[] = []
		const patches: Patch[] = []

		let footnote = null

		// if no layer is selected for choosing summary areas
		if (activeLayer === null) {
			if (!isWithinZoom[includedPointLayer.id as keyof typeof isWithinZoom]) {
				footnote = `zoom in to see ${barrierTypeLabel} available for prioritization`
			} else {
				circles.push({
					id: includedPointLayer.id,
					...includedLegend.getSymbol(networkType),
					label: `${barrierTypeLabel} available for prioritization`
				} as Circle)
			}
		}

		// may need to be mutually exclusive of above
		else if (rankedBarriers.length > 0) {
			const tierLabel = tierThreshold === 1 ? 'tier 1' : `tiers 1 - ${tierThreshold}`
			circles.push({
				id: `${networkType}-top-rank`,
				...topRankLegend.getSymbol(networkType),
				label: topRankLegend.getLabel(barrierTypeLabel, tierLabel)
			} as Circle)

			circles.push({
				id: `${networkType}-lower-rank`,
				...lowerRankLegend.getSymbol(networkType),
				label: lowerRankLegend.getLabel(barrierTypeLabel, tierLabel)
			} as Circle)

			if (isWithinZoom[excludedPointLayer.id as keyof typeof isWithinZoom]) {
				circles.push({
					id: excludedPointLayer.id,
					...excludedLegend.getSymbol(networkType),
					label: excludedLegend.getLabel(barrierTypeLabel)
				} as Circle)
			}
		} else {
			// either in select units or filter step
			if (isWithinZoom[includedPointLayer.id as keyof typeof isWithinZoom]) {
				circles.push({
					id: includedPointLayer.id,
					...includedLegend.getSymbol(networkType),
					label: includedLegend.getLabel(barrierTypeLabel)
				} as Circle)
			} else {
				footnote = `zoom in to see ${barrierTypeLabel} included in prioritization`
			}

			if (isWithinZoom[excludedPointLayer.id as keyof typeof isWithinZoom]) {
				circles.push({
					id: `${networkType}-excluded`,
					...excludedLegend.getSymbol(networkType),
					label: excludedLegend.getLabel(barrierTypeLabel)
				} as Circle)
			}

			if (allowUnitSelect) {
				patches.push({
					id: 'summaryAreas',
					entries: [
						{
							color: 'rgba(0,0,0,0.15)',
							label: `area with no inventoried ${barrierTypeLabel}`
						}
					]
				})
			}
		}

		if (isWithinZoom[otherBarrierPointLayer.id as keyof typeof isWithinZoom]) {
			unrankedBarriers
				.filter(
					({ id }) =>
						// don't show minor barriers legend entry for dams view
						id !== 'minorBarrier' || networkType !== 'dams'
				)
				.forEach(({ id, getSymbol, getLabel }) => {
					circles.push({
						id,
						...getSymbol(networkType),
						label: getLabel(barrierTypeLabel)
					} as Circle)
				})

			other.forEach(({ id, getSymbol, getLabel }) => {
				if (id === 'dams-secondary' && networkType !== 'small_barriers') {
					return
				}

				circles.push({
					id,
					...getSymbol(),
					label: getLabel()
				})
			})
		}

		return {
			legendEntries: {
				patches,
				circles
			},
			footnote
		}
	})
</script>

<Map
	bind:map
	{bounds}
	{layers}
	region={{ id: 'total', boundaryLayer: 'boundary' }}
	legend={{ legendEntries, footnote: legendFootnote }}
	onCreateMap={handleCreateMap}
	class={className}
>
	{@render children()}
</Map>
