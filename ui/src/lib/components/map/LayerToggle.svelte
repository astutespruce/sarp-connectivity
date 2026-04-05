<script lang="ts">
	import CloseIcon from '@lucide/svelte/icons/circle-x'
	import LayersIcon from '@lucide/svelte/icons/layers'

	import { priorityAreasLegend } from '$lib/config/constants'
	import { Button } from '$lib/components/ui/button'
	import { Checkbox } from '$lib/components/ui/checkbox'
	import { ScrollArea } from '$lib/components/ui/scroll-area'
	import { Label } from '$lib/components/ui/label'

	let { visibleLayers = $bindable({}) } = $props()
	let isOpen = $state(false)

	const handleToggleOpen = () => {
		isOpen = !isOpen
	}
</script>

{#if isOpen}
	<div
		class="layer-toggle absolute leading-none bg-white z-2000 top-32 right-2.5 rounded-lg pt-2 px-1 pb-4 border-none max-w-[16rem]"
		style="box-shadow:0 0 0 2px #0000001a"
	>
		<div class="flex items-center justify-between gap-4 px-1">
			<div class="flex flex-auto gap-2 items-center font-bold">
				<LayersIcon class="size-5" />
				Show / hide map layers
			</div>
			<Button variant="close" onclick={handleToggleOpen} aria-label="Close popup">
				<CloseIcon class="size-5" />
			</Button>
		</div>

		<ScrollArea type="always" orientation="vertical" class="mt-4 h-72 px-1">
			{#each priorityAreasLegend.entries as layer (layer.id)}
				<div class="flex gap-2 items-start not-first:mt-2">
					<Checkbox bind:checked={visibleLayers[layer.id]} id={`layer-toggle-${layer.id}`} />
					<Label for={`layer-toggle-${layer.id}`} class="leading-tight text-xs">
						{layer.label}
					</Label>
				</div>
			{/each}
			<div class="text-xs text-muted-foreground mt-4">
				Data derived from PAD-US 4.0, USDA Forest Service ownership boundaries, and USDA Wild &
				Scenic River information.
			</div>
		</ScrollArea>
	</div>
{:else}
	<Button
		variant="outline"
		class="layer-toggle absolute leading-none bg-white z-2000 top-32 right-2.5 rounded-sm p-1.75 size-7.25 border-none hover:grey-0"
		style="box-shadow:0 0 0 2px #0000001a"
		title="Show / hide map layers"
		aria-label="Show / hide map layers"
		onclick={handleToggleOpen}
	>
		<LayersIcon class="size-5" />
	</Button>
{/if}
