<script lang="ts">
	import { Button } from '$lib/components/ui/button'
	import { Root as ButtonGroup } from '$lib/components/ui/button-group'

	type LayerOption = { value: string; label: string; sublabel?: string }

	const adminLayerOptions: LayerOption[] = [
		{ value: 'State', label: 'State' },
		{ value: 'County', label: 'County' },
		{ value: 'CongressionalDistrict', label: 'Congressional Districts' }
	]

	const hucLayerOptions: LayerOption[] = [
		{ value: 'HUC6', label: 'Basin', sublabel: '(HUC6)' },
		{ value: 'HUC8', label: 'Subbasin', sublabel: '(HUC8)' },
		{ value: 'HUC10', label: 'Watershed', sublabel: '(HUC10)' },
		{ value: 'HUC12', label: 'Subwatershed', sublabel: '(HUC12)' }
	]

	const otherLayerOptions: LayerOption[] = [
		{ value: 'StateWRA', label: 'State Water Resource Areas' }
	]

	const { onSetLayer } = $props()
</script>

<div class="flex-auto overflow-y-auto overflow-x-auto p-4">
	<h2 class="text-2xl">What type of area do you want to select?</h2>
	<div class="text-muted-foreground text-base leading-snug mt-4">
		Choose from one of the following types of areas that will best capture your area of interest.
		You will select specific areas on the next screen.
	</div>

	<div class="mt-8">
		<h3 class="text-lg">Administrative / political unit</h3>

		<ButtonGroup class="mt-1 w-full">
			{#each adminLayerOptions as option (option.value)}
				<Button
					class="px-4.75 h-auto not-first:ml-px bg-blue-1 text-foreground hover:bg-blue-2"
					onclick={() => {
						onSetLayer(option.value)
					}}
				>
					{option.label}
				</Button>
			{/each}
		</ButtonGroup>
	</div>

	<div class="mt-12">
		<h3 class="text-lg">Hydrologic unit</h3>

		<ButtonGroup class="mt-1 w-full">
			{#each hucLayerOptions as option (option.value)}
				<Button
					class="px-2.5 h-auto not-first:ml-px bg-blue-1 text-foreground  hover:bg-blue-2"
					onclick={() => {
						onSetLayer(option.value)
					}}
				>
					{option.label}
				</Button>
			{/each}
		</ButtonGroup>
	</div>

	<div class="mt-12">
		<h3 class="text-lg">Other units</h3>
		<ButtonGroup class="mt-1 w-full">
			{#each otherLayerOptions as option (option.value)}
				<Button
					class="h-auto not-first:ml-px bg-blue-1 text-foreground  hover:bg-blue-2"
					onclick={() => {
						onSetLayer(option.value)
					}}
				>
					{option.label}
				</Button>
			{/each}
		</ButtonGroup>
		<div class="text-xs text-muted-foreground mt-2">
			State water resource areas currently include Washington State Water Resource Inventory Areas.
		</div>
	</div>
</div>
