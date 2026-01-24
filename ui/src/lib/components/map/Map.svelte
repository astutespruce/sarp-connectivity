<script lang="ts">
	import { onMount, onDestroy } from 'svelte'
	import { Map as MapboxGLMap, NavigationControl, ScaleControl } from 'mapbox-gl'
	import type { Map as MapboxGLMapType, SourceSpecification, LayerSpecification } from 'mapbox-gl'
	import 'mapbox-gl/dist/mapbox-gl.css'

	import { MAPBOX_TOKEN } from '$lib/env'

	import { mapConfig, sources, basemapLayers } from './config'
	import { getCenterAndZoom } from './util'
	import BasemapSelector from './BasemapSelector.svelte'
	import Coords from './Coords.svelte'
	import { GoToLocation } from './gotolocation'

	const { bounds = mapConfig.bounds, children, onCreateMap, children = null } = $props()

	let mapNode: HTMLElement
	let map: MapboxGLMapType | undefined = $state()
	let basemapId = $state(mapConfig.styleID)
	let isLoaded = $state(false)

	onMount(() => {
		const { center, zoom } = getCenterAndZoom(mapNode, bounds, 0.1)
		const { styleID, minZoom, maxZoom, projection } = mapConfig

		map = new MapboxGLMap({
			container: mapNode,
			accessToken: MAPBOX_TOKEN,
			style: `mapbox://styles/mapbox/${styleID}`,
			center,
			zoom: zoom || 0,
			minZoom,
			maxZoom,
			projection
		})
		window.map = map

		map.addControl(new NavigationControl({ showCompass: false }), 'top-right')
		map.dragRotate.disable()

		map.on('load', () => {
			if (!map) {
				return
			}

			// add sources
			Object.entries(sources).forEach(([id, source]) => {
				map!.addSource(id, source as SourceSpecification)
			})

			// add basemap sources and layers
			Object.values(basemapLayers).forEach((layers) => {
				layers.forEach(({ id, source, ...rest }) => {
					map!.addSource(id, source as SourceSpecification)
					map!.addLayer({
						...rest,
						id,
						source: id
					} as LayerSpecification)
				})
			})

			onCreateMap(map)

			isLoaded = true
		})
	})

	onDestroy(() => {
		if (map) {
			map.remove()
		}
	})
</script>

<div class="relative flex-auto h-full z-1 [&_.mapboxgl-ctrl-top-right]:t-[46px]">
	<div bind:this={mapNode} class="h-full w-full"></div>

	{#if map}
		<BasemapSelector {map} />
		<Coords {map} />
		<GoToLocation {map} />
		{#if children}
			{@render children()}
		{/if}
	{/if}
</div>
