<script lang="ts">
	import { onMount, onDestroy } from 'svelte'
	import { Map as MapboxGLMap, NavigationControl } from 'mapbox-gl'
	import type { Map as SourceSpecification, LayerSpecification } from 'mapbox-gl'
	import 'mapbox-gl/dist/mapbox-gl.css'

	import { MAPBOX_TOKEN } from '$lib/env'

	import { mapConfig, sources, basemapLayers } from './config'
	import { getCenterAndZoom } from './util'
	import BasemapSelector from './BasemapSelector.svelte'
	import Coords from './Coords.svelte'
	import { GoToLocation } from './gotolocation'

	let {
		map = $bindable(),
		bounds = mapConfig.bounds,
		onCreateMap = null,
		children = null
	} = $props()

	let mapNode: HTMLElement
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

			if (onCreateMap) {
				onCreateMap(map)
			}

			isLoaded = true
		})
	})

	onDestroy(() => {
		if (map) {
			map.remove()
		}
	})
</script>

<div class="relative flex-auto h-full z-1 [&_.mapboxgl-ctrl-top-right]:mt-12!">
	<div bind:this={mapNode} class="h-full w-full"></div>

	{#if isLoaded}
		<GoToLocation {map} />
		<BasemapSelector {map} />

		{#if children}
			{@render children()}
		{/if}
		<Coords {map} />
	{/if}
</div>
