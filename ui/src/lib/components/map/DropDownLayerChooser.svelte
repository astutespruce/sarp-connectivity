<script lang="ts">
	import CloseIcon from '@lucide/svelte/icons/circle-x'
	import LayersIcon from '@lucide/svelte/icons/layers'

	import { Button } from '$lib/components/ui/button'
	import { Checkbox } from '$lib/components/ui/checkbox'
	import { Label } from '$lib/components/ui/label'

	type Option = {
		id: string
		label: string
	}

	const { options, onChange } = $props()
	let isOpen = $state(false)
	let checkboxState = $derived(Object.fromEntries(options.map(({ id }: Option) => [id, false])))

	const handleToggleOpen = () => {
		isOpen = !isOpen
	}
</script>

{#if isOpen}
	<div
		class="absolute leading-none bg-white z-2000 top-30 right-2.5 rounded-lg p-1.75 border border-[#AAA] shadow-lg"
	>
		<div class="flex items-center justify-between gap-4">
			<div class="flex flex-auto gap-1 items-center">
				<LayersIcon class="size-6" />
				Show / hide map layers
			</div>
			<Button
				variant="ghost"
				class="flex-none p-0"
				onclick={handleToggleOpen}
				aria-label="Close popup"
			>
				<CloseIcon />
			</Button>
		</div>

		<div class="mt-4 max-w-[16rem]">
			{#each options as option (option.id)}
				<div>
					<Checkbox
						bind:checked={checkboxState[option.id]}
						onchange={() => onChange(option.id)}
						id={`layer-toggle-${option.id}`}
					/>
					<Label for={`layer-toggle-${option.id}`}>
						{option.label}
					</Label>
				</div>
			{/each}
		</div>
	</div>
{:else}
	<Button
		variant="outline"
		class="absolute leading-none bg-white z-2000 top-30 right-2.5 rounded-lg p-1.75 size-7.25 hover:grey-0"
		title="Show / hide map layers"
		aria-label="Show / hide map layers"
		onclick={handleToggleOpen}
	>
		<LayersIcon class="size-6" />
	</Button>
{/if}
