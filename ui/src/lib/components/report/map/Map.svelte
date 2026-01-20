<script lang="ts">
	import { onMount, onDestroy } from 'svelte'
	import { Map as MapboxGLMap, NavigationControl, ScaleControl } from 'mapbox-gl'
	import type { Map as MapboxGLMapType, SourceSpecification, LayerSpecification } from 'mapbox-gl'
	import 'mapbox-gl/dist/mapbox-gl.css'

	import MapboxLogo from '$lib/assets/images/mapbox-logo.png'

	import { MAPBOX_TOKEN } from '$lib/env'
	import {
		rankedPointLayer,
		damsSecondaryLayer,
		roadCrossingsLayer,
		waterfallsLayer,
		removedBarrierPointLayer,
		otherBarrierPointLayer,
		unrankedPointLayer
	} from '$lib/components/explore/layers'
	import {
		BasemapSelector,
		networkLayers,
		mapConfig,
		sources,
		basemapLayers,
		basemapAttribution
	} from '$lib/components/map'
	import { pointHighlightLayer } from './layers'
	import Legend from './Legend.svelte'

	const { networkType, id: barrierID, name, upnetid, lat, lon, removed } = $props()

	const networkID = $derived(removed ? barrierID : upnetid)

	let mapNode: HTMLElement
	let locatorMapNode: HTMLElement
	let imageNode: HTMLImageElement
	let locatorImageNode: HTMLImageElement
	let scalebarWidth: number | undefined = $state()
	let scalebarLabel: string | undefined = $state()
	let map: MapboxGLMapType | undefined = $state()
	let locatorMap: MapboxGLMapType | undefined = $state()
	let isLoaded = $state(false)
	let basemapId = $state(mapConfig.styleID)
	let visibleLayers: Set<string> = $state(new Set())

	onMount(() => {
		map = new MapboxGLMap({
			container: mapNode,
			accessToken: MAPBOX_TOKEN,
			style: `mapbox://styles/mapbox/${mapConfig.styleID}`,
			center: [lon, lat],
			zoom: 13.5,
			minZoom: 7,
			maxZoom: 18,
			preserveDrawingBuffer: true
		})
		window.map = map

		map.addControl(new NavigationControl(), 'top-right')
		map.addControl(new ScaleControl({ unit: 'imperial' }), 'bottom-right')

		locatorMap = new MapboxGLMap({
			container: locatorMapNode,
			accessToken: MAPBOX_TOKEN,
			style: `mapbox://styles/mapbox/${mapConfig.styleID}`,
			center: [lon, lat],
			zoom: 5,
			preserveDrawingBuffer: true,
			interactive: false,
			attributionControl: false
		})

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

			// Add network layers
			networkLayers.forEach((layer) => {
				if (layer.id.endsWith('-highlight')) {
					let filterExpr = null
					if (removed) {
						filterExpr = ['all', ['==', 'network_type', networkType], ['==', 'id', networkID]]
					} else {
						filterExpr = ['==', networkType, networkID]
					}

					map!.addLayer({
						...layer,
						minzoom: 6,
						filter: filterExpr
					} as LayerSpecification)
				} else {
					map!.addLayer(layer as LayerSpecification)
				}
			})

			// Add barrier point layers
			map.addLayer(waterfallsLayer as LayerSpecification)

			if (networkType === 'small_barriers') {
				map.addLayer({
					...damsSecondaryLayer,
					layout: { visibility: 'visible' }
				} as LayerSpecification)
			}
			if (networkType !== 'dams') {
				map.addLayer({
					...roadCrossingsLayer,
					layout: { visibility: 'visible' }
				} as LayerSpecification)
			}

			map.addLayer({
				id: networkType,
				source: networkType,
				'source-layer': `ranked_${networkType}`,
				...rankedPointLayer
			} as LayerSpecification)

			map.addLayer({
				id: `unranked_${networkType}`,
				source: networkType,
				'source-layer': `unranked_${networkType}`,
				...unrankedPointLayer
			} as LayerSpecification)

			map.addLayer({
				id: `other_${networkType}`,
				source: networkType,
				'source-layer': `other_${networkType}`,
				...otherBarrierPointLayer
			} as LayerSpecification)

			map.addLayer({
				id: `removed_${networkType}`,
				source: networkType,
				'source-layer': `removed_${networkType}`,
				...removedBarrierPointLayer
			} as LayerSpecification)

			// Add barrier highlight layer for on and off-network barriers.
			map.addLayer({
				...pointHighlightLayer,
				source: networkType,
				'source-layer': `ranked_${networkType}`,
				minzoom: 6,
				filter: ['==', ['get', 'id'], barrierID]
			} as LayerSpecification)

			map.addLayer({
				...pointHighlightLayer,
				id: 'unranked-point-highlight',
				source: networkType,
				'source-layer': `unranked_${networkType}`,
				minzoom: 6,
				filter: ['==', ['get', 'id'], barrierID]
			} as LayerSpecification)

			map.addLayer({
				...pointHighlightLayer,
				id: 'other-point-highlight',
				source: networkType,
				'source-layer': `other_${networkType}`,
				minzoom: 6,
				filter: ['==', ['get', 'id'], barrierID]
			} as LayerSpecification)

			map.addLayer({
				...pointHighlightLayer,
				id: 'removed-point-highlight',
				source: networkType,
				'source-layer': `removed_${networkType}`,
				minzoom: 6,
				filter: ['==', ['get', 'id'], barrierID]
			} as LayerSpecification)

			map.once('idle', handleVisibleLayerUpdate)
			map.on('zoomend', handleVisibleLayerUpdate)
			map.on('moveend', handleVisibleLayerUpdate)

			isLoaded = true
		})

		map.on('idle', () => {
			// capture map image for printing
			imageNode.src = map!.getCanvas().toDataURL('image/png')

			// keep the scalebar in sync
			const scaleNode = document.querySelector('.mapboxgl-ctrl-scale') as HTMLElement
			if (scaleNode) {
				scalebarWidth = scaleNode.offsetWidth
				scalebarLabel = scaleNode.innerText
			}
		})

		locatorMap.on('load', () => {
			locatorMap!.addLayer({
				id: 'marker',
				source: {
					type: 'geojson',
					data: {
						type: 'Point',
						coordinates: [lon, lat]
					}
				},
				type: 'circle',
				paint: {
					'circle-color': '#fd8d3c',
					'circle-radius': 8,
					'circle-stroke-width': 2,
					'circle-stroke-color': '#f03b20'
				}
			})
		})

		locatorMap.on('idle', () => {
			locatorImageNode.src = locatorMap!.getCanvas().toDataURL('image/png')
		})
	})

	onDestroy(() => {
		if (map) {
			map.remove()
		}
		if (locatorMap) {
			locatorMap.remove()
		}
	})

	const handleVisibleLayerUpdate = () => {
		if (!(map && isLoaded)) {
			return
		}

		const flowlineLayers = networkLayers
			.filter(({ id }) => !id.endsWith('-highlight'))
			.map(({ id }) => id)

		// @ts-expect-error undefined is valid
		const flowlines = map.queryRenderedFeatures(undefined, {
			layers: flowlineLayers
		})

		const flowlineTypes = flowlines
			// @ts-expect-error mapcode is defined
			.map(({ properties: { mapcode } }) =>
				mapcode === 2 || mapcode === 3 ? 'alteredFlowline' : 'flowline'
			)
			.concat(
				// @ts-expect-error mapcode is defined, valid concat
				flowlines.map(({ properties: { mapcode } }) =>
					mapcode === 1 || mapcode === 3 ? 'intermittentFlowline' : 'flowline'
				)
			)

		const barrierLayers = [waterfallsLayer.id]
		if (networkType === 'small_barriers') {
			barrierLayers.push(damsSecondaryLayer.id)
			barrierLayers.push(roadCrossingsLayer.id)
		}
		// @ts-expect-error undefined is valid
		const barriers = map.queryRenderedFeatures(undefined, {
			layers: barrierLayers
		})

		visibleLayers = new Set(
			// @ts-expect-error id is actually defined
			flowlineTypes.concat(barriers.map(({ layer: { id } }) => id))
		)
	}

	const handleUpdateBasemap = (newBasemapId: string) => {
		basemapId = newBasemapId
	}
</script>

<div class="relative z-1 border border-grey-4 mt-2 overflow-hidden">
	<div
		bind:this={mapNode}
		class="w-full sm:w-188 h-132 print:hidden [&_.mapboxgl-ctrl-logo]:hidden! [&_.mapboxgl-ctrl-attrib]:hidden!"
	></div>
	{#if isLoaded}
		<BasemapSelector {map} bottom="10px" size="40px" onUpdate={handleUpdateBasemap} />
	{/if}

	<img bind:this={imageNode} class="hidden print:block relative z-1 h-132" alt="map" />

	{#if scalebarLabel}
		<div
			class="hidden print:block absolute z-2 h-5 bg-white/75 bottom-2.5 right-2.5 border-2 border-t-0 border-black px-1.25 py-1 overflow-hidden text-[10px] leading-none"
			style="width: {scalebarWidth}px"
		>
			{scalebarLabel}
		</div>
	{/if}
</div>

<div class="flex items-start mt-1 gap-4 leading-none text-muted-foreground text-[10px]">
	<img src={MapboxLogo} alt="MapBox logo" class="h-4 flex-none" />
	<div class="mt-0.5">
		Basemap credits: {basemapAttribution[basemapId as keyof typeof basemapAttribution]}
	</div>
</div>

<div class="flex flex-wrap sm:flex-nowrap gap-8 mt-2">
	<div class="size-50 relative border border-grey-4 mt-2 flex-none">
		<div
			bind:this={locatorMapNode}
			class="w-full h-full print:hidden [&_.mapboxgl-ctrl-logo]:hidden!"
		></div>

		<img bind:this={locatorImageNode} class="hidden print:block z-1" alt="locator map" />
	</div>

	<Legend {networkType} {name} {visibleLayers} />
</div>
