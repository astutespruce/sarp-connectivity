<script lang="ts">
	import { onMount, onDestroy } from 'svelte'
	import { Map as MapboxGLMap, NavigationControl, Popup } from 'mapbox-gl'
	import type { Map as MapboxGLMapType, SourceSpecification, LayerSpecification } from 'mapbox-gl'
	import 'mapbox-gl/dist/mapbox-gl.css'
	import { untrack } from 'svelte'

	import { MAPBOX_TOKEN } from '$lib/env'
	import { cn } from '$lib/utils'

	import { priorityAreasLegend } from '$lib/config/constants'
	import { mapConfig, sources as initSources, basemapLayers } from './config'
	import { priorityAreaLayers, networkLayers, regionBoundary, regionMask } from './layers'
	import { getCenterAndZoom, runOnceOnIdle } from './util'
	import BasemapSelector from './BasemapSelector.svelte'
	import Coords from './Coords.svelte'
	import { GoToLocation } from './gotolocation'
	import LayerToggle from './LayerToggle.svelte'
	import { Legend } from './legend'
	import type { Circle, Line, Patch } from './legend/types'

	let {
		map: mapRef = $bindable(),
		bounds = mapConfig.bounds,
		sources = {},
		layers = [],
		legend = {},
		region = {},
		onCreateMap = null,
		children = null,
		class: className = null
	} = $props()

	let map: MapboxGLMapType | undefined = $state.raw()
	let mapNode: HTMLElement
	let isLoaded = $state(false)
	let zoom = $state(0)

	let hoverPriorityAreaId: string | number | null = $state(null)
	// all priority layers are not visible by default
	let visiblePriorityAreaLayers = $state(
		Object.fromEntries(priorityAreasLegend.entries.map(({ id }) => [id, false]))
	)

	onMount(() => {
		const { center, zoom: initZoom } = getCenterAndZoom(mapNode, bounds, 0.05)
		const { styleID, minZoom, maxZoom, projection } = mapConfig

		map = new MapboxGLMap({
			container: mapNode,
			accessToken: MAPBOX_TOKEN,
			style: `mapbox://styles/mapbox/${styleID}`,
			center,
			zoom: initZoom || 0,
			minZoom,
			maxZoom,
			projection
		})
		window.map = map

		map.addControl(new NavigationControl({ showCompass: false }), 'top-right')
		map.dragRotate.disable()

		const tooltip = new Popup({
			closeButton: false,
			closeOnClick: false,
			anchor: 'left',
			offset: 20
		})

		// bind to map instance so that downstream users use the same one
		// @ts-expect-error tooltip defined dynamically
		map.tooltip = tooltip

		map.on('zoomend', () => {
			zoom = map!.getZoom()
		})

		map.on('load', () => {
			zoom = map!.getZoom()

			// add sources
			Object.entries(initSources).forEach(([id, source]) => {
				map!.addSource(id, source as SourceSpecification)
			})

			if (sources) {
				Object.entries(sources).forEach(([id, source]) => {
					map!.addSource(id, source as SourceSpecification)
				})
			}

			// add basemap sources and layers
			Object.values(basemapLayers).forEach((layersInBasemap) => {
				layersInBasemap.forEach(({ id, source, ...rest }) => {
					map!.addSource(id, source as SourceSpecification)
					map!.addLayer({
						...rest,
						id,
						source: id
					} as LayerSpecification)
				})
			})

			// Add the priority areas under everything else
			priorityAreaLayers.forEach((layer) => {
				map!.addLayer(layer as LayerSpecification)
			})

			// Add network layers
			networkLayers.forEach((layer) => {
				map!.addLayer(layer as LayerSpecification)
			})

			if (layers) {
				layers.forEach((layer) => {
					map!.addLayer(layer)
				})
			}

			// Add region mask / boundary layers
			// only use initial value of region when setting up layers (it is a route variable and does not change after mount)
			const { id: regionId, boundaryLayer: regionBoundaryLayer } = $state.snapshot(
				untrack(() => region)
			)
			map!.addLayer({
				...regionMask,
				filter: ['==', 'id', regionId && regionId !== 'total' ? `${regionId}_mask` : 'total']
			} as LayerSpecification)
			map!.addLayer({
				...regionBoundary,
				'source-layer': regionBoundaryLayer || 'boundary',
				filter: ['==', 'id', regionId || 'total']
			} as LayerSpecification)

			// hook up mouse events for priority layer hover / unhover
			// index 0 is the fill layer, index 1 is the outline
			// @ts-expect-error ignore typing on feature and lngLat
			map!.on('mousemove', priorityAreaLayers[0].id, ({ features: [feature], lngLat }) => {
				const {
					id: featureId,
					properties: { type, name }
				} = feature

				// only show tooltips for broad priority areas at lower zooms, but
				// always show for Wild & Scenic Rivers
				if ((type === 'hifhp_gfa' || type === 'sarp_coa') && map!.getZoom() > 10) {
					if (hoverPriorityAreaId !== null) {
						map!.removeFeatureState({
							id: hoverPriorityAreaId,
							source: priorityAreaLayers[1].source,
							sourceLayer: priorityAreaLayers[1]['source-layer']
						})
						hoverPriorityAreaId = null
					}
					return
				}

				if (hoverPriorityAreaId !== featureId) {
					map!.removeFeatureState({
						// @ts-expect-error ignore typing error
						id: hoverPriorityAreaId,
						source: priorityAreaLayers[1].source,
						sourceLayer: priorityAreaLayers[1]['source-layer']
					})
				}

				const { label: priorityLabel, showName } = priorityAreasLegend.entries.filter(
					({ id }) => id === type
				)[0]
				const prefix = `${priorityLabel}`
				const suffix = showName ? `: ${name}` : ''

				map!.getCanvas().style.cursor = 'pointer'
				tooltip.setLngLat(lngLat).setHTML(`<b>${prefix}${suffix}</b>`).addTo(map!)

				map!.setFeatureState(
					{
						id: featureId,
						source: priorityAreaLayers[1].source,
						sourceLayer: priorityAreaLayers[1]['source-layer']
					},
					{ highlight: true }
				)

				hoverPriorityAreaId = featureId
			})
			map!.on('mouseleave', priorityAreaLayers[0].id, () => {
				map!.getCanvas().style.cursor = ''
				tooltip.remove()

				map!.removeFeatureState({
					// @ts-expect-error ignore typing error
					id: hoverPriorityAreaId,
					source: priorityAreaLayers[1].source,
					sourceLayer: priorityAreaLayers[1]['source-layer']
				})

				hoverPriorityAreaId = null
			})

			isLoaded = true

			// only set the reference when map is fully loaded
			mapRef = map

			if (onCreateMap) {
				onCreateMap(map)
			}
		})
	})

	onDestroy(() => {
		if (map) {
			map.remove()
		}
	})

	const updatePriorityLayerVisibility = () => {
		// visibility here means that the priority layer types are filtered IN
		const visibleIds = Object.entries(visiblePriorityAreaLayers)
			// eslint-disable-next-line @typescript-eslint/no-unused-vars
			.filter(([_, visible]) => visible)
			.map(([id]) => id)

		priorityAreaLayers.forEach(({ id }) => {
			map!.setLayoutProperty(id, 'visibility', visibleIds.length > 0 ? 'visible' : 'none')
			map!.setFilter(id, ['in', ['get', 'type'], ['literal', visibleIds]])
		})
	}

	$effect(() => {
		// use snapshot to force monitoring of object values
		$state.snapshot(visiblePriorityAreaLayers)

		if (!map) {
			return
		}

		runOnceOnIdle(map, updatePriorityLayerVisibility)
	})

	/**
	 * Update map bounds on change
	 */
	$effect.pre(() => {
		bounds

		if (!(map && bounds)) {
			return
		}

		runOnceOnIdle(map, () => {
			map!.fitBounds(bounds, { padding: 100, maxZoom: 14, duration: 500 })
		})
	})

	const legendEntries = $derived.by(() => {
		const circles: Circle[] = [...(legend?.legendEntries?.circles || [])]
		const patches: Patch[] = [...(legend?.legendEntries?.patches || [])]
		const lines: Line[] = [...(legend?.legendEntries?.lines || [])]

		if (zoom > 6) {
			lines.push(
				...[
					{
						id: 'normal',
						label: 'stream reach',
						color: '#1891ac',
						lineWidth: 2
					},
					{
						id: 'altered',
						label: 'altered stream reach (canal / ditch / reservoir)',
						color: '#9370db',
						lineWidth: 2
					},
					{
						id: 'intermittent',
						label: 'intermittent / ephemeral stream reach',
						color: '#1891ac',
						lineStyle: 'dashed',
						lineWidth: 2
					}
				]
			)
		}

		priorityAreasLegend.entries
			.filter(({ id }: { id: string }) => visiblePriorityAreaLayers[id])
			.forEach(({ id, label }) => {
				patches.push({
					id,
					entries: [{ id, label, color: priorityAreasLegend.color }]
				})
			})

		return {
			patches,
			circles,
			lines
		}
	})
</script>

<div class={cn('map-container relative flex-auto h-full z-1 overflow-hidden', className)}>
	<div bind:this={mapNode} class="h-full w-full"></div>

	{#if isLoaded}
		{#if children}
			{@render children()}
		{/if}

		<GoToLocation {map} />
		<LayerToggle bind:visibleLayers={visiblePriorityAreaLayers} />
		<BasemapSelector {map} />
		<Coords {map} />
		<Legend {...legendEntries} title={legend.title} footnote={legend.footnote} />
	{/if}
</div>
