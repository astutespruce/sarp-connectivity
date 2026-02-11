<script lang="ts">
	import { Popup } from 'mapbox-gl'
	import type { FeatureSelector, GeoJSONFeature, Point } from 'mapbox-gl'
	import { untrack } from 'svelte'

	import { shortBarrierTypeLabels, pointLegends } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import {
		Map,
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
	import { otherBarrierPointLayer } from '$lib/components/priority/layers'
	import { unitLayers, unitHighlightLayers, parentOutline } from '$lib/components/workflow/layers'

	import { excludedPointLayer, includedPointLayer, waterfallsLayer } from './layers'

	let {
		map = $bindable(),
		networkType: networkTypeProp,
		crossfilter,
		activeLayer,
		summaryUnits,
		allowUnitSelect,
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

	// all points are initially excluded from analysis until their
	// units are selected
	layers.push(excludedPointLayer)
	layers.push(includedPointLayer)

	// prioritized points are not initially visible

	const pointLayers = [
		waterfallsLayer.id,
		excludedPointLayer.id,
		includedPointLayer.id
		// NOTE: other barrier types not added because they are already
		// present in road crossings tiles
	]

	const clickLayers = pointLayers.concat(
		Object.keys(unitLayerConfig).map((id) => `${id}-unit-fill`)
	)

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
							properties.sarpidname && properties.sarpidname.startsWith('sm')
								? 'small_barriers'
								: source,
							feature.properties
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

			if (isEqual(feature, selectedFeature, ['id', 'layer'])) {
				// no change
				return
			}

			// always ; out prior feature
			clearSelectedBarrier()

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

			const thisBarrierType =
				properties.sarpidname && properties.sarpidname.startsWith('sm') ? 'small_barriers' : source

			const network =
				networkType === 'small_barriers' || networkType === 'road_crossings'
					? 'combined_barriers'
					: networkType

			// promote network fields if clicking on a waterfall
			let networkIDField = 'upnetid'
			if (thisBarrierType === 'waterfalls') {
				networkIDField = `${network}_upnetid`
			}

			const networkID = properties[networkIDField] || Infinity

			selectedFeature = feature
			setBarrierHighlight(map, feature, true)

			onSelectBarrier({
				upnetid: networkID,
				...properties,
				barrierType: thisBarrierType,
				networkType,
				lat,
				lon,
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
	 * reset selected barrier highlight and network highlight
	 * NOTE: this is called from the parent component when the sidebar barrier entry is closed
	 */
	export const clearSelectedBarrier = () => {
		if (selectedFeature) {
			setBarrierHighlight(map, selectedFeature, false)

			if (isEqual(selectedFeature, hoverFeature, ['id', 'layer'])) {
				setBarrierHighlight(map, hoverFeature, false)
				hoverFeature = null
			}

			selectedFeature = null
		}
	}

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

		const hasActiveUnits = ids && ids.length > 0
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

	const { legendEntries, footnote: legendFootnote } = $derived.by(() => {
		const pointLayers = [includedPointLayer, excludedPointLayer, otherBarrierPointLayer]

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
			unrankedBarriers,
			other
		} = pointLegends

		const circles: Circle[] = []
		const patches: Patch[] = []

		let footnote = null

		if (!isWithinZoom[includedPointLayer.id as keyof typeof isWithinZoom]) {
			footnote = 'zoom in to see crossings available for download'
		} else {
			circles.push({
				id: includedPointLayer.id,
				...includedLegend.getSymbol(networkType),
				label: 'surveyed/unsurveyed crossings selected for download'
			} as Circle)
		}

		if (activeLayer !== null) {
			if (isWithinZoom[excludedPointLayer.id as keyof typeof isWithinZoom]) {
				circles.push({
					id: `${networkType}-excluded`,
					...excludedLegend.getSymbol(networkType),
					label: 'surveyed/unsurveyed crossings not selected for download'
				} as Circle)
			}

			if (isWithinZoom[otherBarrierPointLayer.id as keyof typeof isWithinZoom]) {
				unrankedBarriers.forEach(({ id, getSymbol, getLabel }) => {
					let label =
						id === 'default'
							? 'surveyed crossings not located on aquatic network'
							: getLabel(shortBarrierTypeLabels.small_barriers)
					if (id === 'nonBarrier') {
						label = `surveyed crossings that are ${label}`
					} else if (id === 'minorBarrier') {
						label = `surveyed crossings that are a ${label}`
					}

					circles.push({
						id,
						...getSymbol(networkType),
						label
					} as Circle)
				})

				other
					.filter(({ id }) => id !== 'dams-secondary')
					.forEach(({ id, getSymbol, getLabel }) => {
						circles.push({
							id,
							...getSymbol(),
							label: getLabel()
						})
					})
			}

			if (allowUnitSelect) {
				patches.push({
					id: 'summaryAreas',
					entries: [
						{
							color: 'rgba(0,0,0,0.15)',
							label: 'area with no inventoried crossings'
						}
					]
				})
			}
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
	{layers}
	{bounds}
	region={{ id: 'total', boundaryLayer: 'boundary' }}
	legend={{ legendEntries, footnote: legendFootnote }}
	onCreateMap={handleCreateMap}
	class={className}
>
	{@render children()}
</Map>
