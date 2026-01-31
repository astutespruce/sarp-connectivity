<script lang="ts">
	import CloseIcon from '@lucide/svelte/icons/circle-x'
	import LayersIcon from '@lucide/svelte/icons/layers'

	import { Button } from '$lib/components/ui/button'
	import { Checkbox } from '$lib/components/ui/checkbox'
	import { Label } from '$lib/components/ui/label'

	const { options = $bindable([]) } = $props()
	let isOpen = $state(false)

	const handleToggleOpen = () => {
		isOpen = !isOpen
	}
</script>

{#if isOpen}
	<div
		class="layer-toggle absolute leading-none bg-white z-2000 top-32 right-2.5 rounded-lg pt-2 px-2 pb-4 border-none"
		style="box-shadow:0 0 0 2px #0000001a"
	>
		<div class="flex items-center justify-between gap-4">
			<div class="flex flex-auto gap-2 items-center font-bold">
				<LayersIcon class="size-5" />
				Show / hide map layers
			</div>
			<Button variant="close" onclick={handleToggleOpen} aria-label="Close popup">
				<CloseIcon class="size-5" />
			</Button>
		</div>

		<div class="mt-4 max-w-[16rem]">
			{#each options as option (option.id)}
				<div class="flex gap-2 items-start not-first:mt-4">
					<Checkbox bind:checked={option.visible} id={`layer-toggle-${option.id}`} />
					<Label for={`layer-toggle-${option.id}`} class="leading-tight text-sm">
						{option.label}
					</Label>
				</div>
			{/each}
		</div>
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
