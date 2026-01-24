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

	const { map, size = '50px', bottom = '32px', left = '10px', onUpdate = null } = $props()

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

{#snippet basemapButton(basemap: Basemap, isCurrent = false, isNext = false)}
	<div
		class={cn(
			'flex-none flex-col gap-1 items-center cursor-pointer hidden group-hover/basemaps:flex group-focus-within/basemaps:flex group/basemap',
			{
				flex: isNext
			}
		)}
		style="flex-basis:calc({size} + 0.5rem);"
	>
		<div
			class={cn(
				'invisible text-[0.65rem] text-center p-1 group-hover/basemaps:visible group-focus-within/basemaps:visible',
				{ 'font-bold': isCurrent }
			)}
		>
			{basemap.id.split('-')[0]}
		</div>
		<Button
			class={cn(
				'rounded-full overflow-hidden border-white shadow-lg shadow-grey-8 ring-1 focus-visible:ring-2 hover:ring-2 ring-grey-4 p-0 focus-visible:ring-accent hover:ring-accent',
				{ 'ring-2 ring-grey-9': isCurrent }
			)}
			style="width:{size};height:{size};"
			onclick={() => {
				handleBasemapClick(basemap)
			}}
			tabindex={0}
		>
			<img src={basemap.src} class="w-full h-full" alt={`${basemap.id} basemap button`} />
		</Button>
	</div>
{/snippet}

<div
	class="absolute z-10000 flex gap-2 items-center group/basemaps print:hidden hover:bg-white focus-within:bg-white focus-within:border-grey-5 p p-2 -m-2 border border-transparent hover:border-grey-5 rounded"
	style="bottom:{bottom};left:{left}"
>
	{#each options as option (option.id)}
		{@render basemapButton(option, option.id === basemap.id, option.id === nextBasemap.id)}
	{/each}
</div>
