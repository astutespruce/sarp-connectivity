<script lang="ts">
	import LightIcon from '$lib/assets/images/light-v10.png'
	import StreetsIcon from '$lib/assets/images/esri-streets.jpg'
	import TopoIcon from '$lib/assets/images/esri-topo.jpg'
	import ImageryIcon from '$lib/assets/images/esri-imagery.jpg'

	import { Button } from '$lib/components/ui/button'
	import { cn } from '$lib/utils'

	import { basemapLayers as basemaps } from './config'

	type Basemap = {
		id: string
		src: string
		layers: any[]
	}

	const icons = {
		'light-v10': LightIcon,
		imagery: ImageryIcon,
		streets: StreetsIcon,
		topo: TopoIcon
	}

	// add light-v10 to front of list since it is the default style and not
	// expressed as a basemap layer
	const options = [
		{
			id: 'light-v10',
			src: icons['light-v10'],
			layers: []
		} as Basemap
	].concat(
		Object.values(basemaps).map((layers) => {
			const { id } = layers[0]
			return {
				id,
				src: icons[id as keyof typeof icons],
				layers: layers.map(({ id: layerId }) => layerId)
			} as Basemap
		})
	)

	const { map, size = '64px', bottom = '24px', left = '10px', onUpdate = null } = $props()

	let basemap = $state(options[0])

	$effect(() => {
		if (!map) return

		Object.values(basemaps).forEach((layers) => {
			layers.forEach(({ id, source, ...rest }) => {
				if (!map.getSource(id)) {
					map.addSource(id, source)
				}
				if (!map.getLayer(id)) {
					map.addLayer({
						...rest,
						id,
						source: id
					})
				}
			})
		})
	})

	const handleBasemapClick = (newBasemap: Basemap) => {
		if (newBasemap.id === basemap.id) return

		basemap.layers.forEach((layer) => {
			map.setLayoutProperty(layer, 'visibility', 'none')
		})
		newBasemap.layers.forEach((layer) => {
			map.setLayoutProperty(layer, 'visibility', 'visible')
		})
		basemap = newBasemap

		if (onUpdate) {
			onUpdate(newBasemap.id)
		}
	}

	const nextBasemap = $derived(options.filter(({ id }) => id !== basemap.id)[0])
</script>

{#snippet basemapButton(basemap: Basemap, secondary = false)}
	<div
		class="flex-none flex flex-col gap-1 items-center cursor-pointer"
		style="flex-basis:calc({size} + 0.5rem);"
	>
		<div
			class="text-[0.65rem] text-center bg-white/50 text-shadow-sm invisible group-hover:visible group-focus-within:visible p-1"
		>
			{basemap.id.split('-')[0]}
		</div>
		<Button
			class={cn(
				'rounded-full overflow-hidden border-white shadow-lg shadow-grey-8 ring-1 ring-grey-4 p-0 focus-visible:ring-accent hover:ring-accent',
				{ 'hidden group-hover:block group-focus-within:block': secondary }
			)}
			style="width:{size};height:{size};"
			onclick={() => {
				handleBasemapClick(basemap)
			}}
		>
			<img src={basemap.src} class="w-full h-full" alt={`${basemap.id} basemap button`} />
		</Button>
	</div>
{/snippet}

<div class="absolute z-1 flex gap-2 items-center group" style="bottom:{bottom};left:{left}">
	{@render basemapButton(nextBasemap)}

	{#each options.filter(({ id }) => id !== nextBasemap.id) as altBasemap (altBasemap.id)}
		{@render basemapButton(altBasemap, true)}
	{/each}
</div>
