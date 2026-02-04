<script lang="ts">
	import ResetIcon from '@lucide/svelte/icons/circle-x'
	import ChevronRightIcon from '@lucide/svelte/icons/chevron-right'
	import ChevronDownIcon from '@lucide/svelte/icons/chevron-down'

	import { Button } from '$lib/components/ui/button'
	import { pluralize } from '$lib/util/format'
	import { cn } from '$lib/utils'

	import type { Dimension } from './types'
	import Filter from './Filter.svelte'

	const { id, title, filters: dimensions, crossfilter } = $props()

	// all filters initially closed
	let isOpen: boolean = $state(false)
	let openFilters: Record<string, boolean> = $state({})

	const hasFilters = $derived(
		dimensions.filter(({ field }: Dimension) =>
			crossfilter.filters[field] ? crossfilter.filters[field].size : 0
		).length > 0
	)

	const availableDimensions = $derived(
		dimensions.filter(
			({ field, hideIfEmpty }: Dimension) =>
				!(hideIfEmpty && crossfilter.emptyDimensions.has(field))
		)
	)

	const handleReset = () => {
		crossfilter.resetGroupFilters(id)
	}
</script>

{#if availableDimensions.length > 0}
	<div class="not-last:border-b not-last:border-b-grey-2">
		<div class="grid grid-cols-[1fr_2rem] gap-2 py-2 w-full">
			<div>
				<Button
					variant="ghost"
					class="block text-left justify-start items-start h-auto rounded-none gap-1 pl-0! pr-2 py-1 w-full overflow-hidden"
					onclick={() => {
						isOpen = !isOpen
					}}
				>
					<div class="flex gap-1">
						{#if isOpen}
							<ChevronDownIcon class="size-6 flex-none" />
						{:else}
							<ChevronRightIcon class="size-6 flex-none" />
						{/if}
						<div class="flex-auto text-wrap">
							<div class="font-bold text-lg -mt-1 leading-snug">{title}</div>
							<div class="text-xs text-muted-foreground">
								{availableDimensions.length}
								{pluralize('filter', availableDimensions.length)} available
							</div>
						</div>
					</div>
				</Button>
			</div>

			<div>
				<Button
					variant="ghost"
					class={cn(
						'flex items-start mt-1 h-auto! rounded-full p-0! flex-none text-accent invisible',
						{
							visible: hasFilters
						}
					)}
					title={`Reset all filters in ${title.toLowerCase()}`}
					onclick={handleReset}
				>
					<ResetIcon class="size-5" />
				</Button>
			</div>
		</div>

		{#if isOpen}
			<div class="border-l-8 border-l-blue-1">
				{#each availableDimensions as dimension (dimension.field)}
					<Filter
						{crossfilter}
						{...dimension}
						bind:isOpen={
							() => !!openFilters[dimension.field],
							(v) => {
								openFilters[dimension.field] = v
							}
						}
					/>
				{/each}
			</div>
		{/if}
	</div>
{/if}
