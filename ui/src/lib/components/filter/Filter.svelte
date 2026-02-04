<script lang="ts">
	import ResetIcon from '@lucide/svelte/icons/circle-x'
	import ChevronRightIcon from '@lucide/svelte/icons/chevron-right'
	import ChevronDownIcon from '@lucide/svelte/icons/chevron-down'
	import { SvelteSet } from 'svelte/reactivity'

	import { resolve } from '$app/paths'
	import { Button } from '$lib/components/ui/button'
	import { cn } from '$lib/utils'
	import FilterBars from './FilterBars.svelte'

	type Datum = {
		value: number | string
		label: string | number
		quantity: number
		isFiltered: boolean
		isExcluded: boolean
		isMissing: boolean
	}

	let {
		crossfilter,
		field,
		title,
		values,
		labels,
		help,
		url,
		isOpen = $bindable(false),
		hideMissingValues,
		sort
	} = $props()

	const filterValues = $derived(crossfilter.filters[field] || new SvelteSet())
	const hasFilter = $derived(
		crossfilter.filters[field] ? crossfilter.filters[field].size > 0 : false
	)
	const counts: Record<string, number> = $derived(crossfilter.dimensionCounts[field])
	const unfilteredCounts: Record<string, number> = $derived(crossfilter.totalDimensionCounts[field])
	const max = $derived(Math.max(0, ...Object.values(counts)))

	const data: Datum[] = $derived.by(() => {
		// if not isOpen, we can bypass processing the data
		if (!isOpen) {
			return []
		}

		// splice together label, value, and count so that we can filter and sort
		let newData = values.map((value: number | string, i: number) => ({
			value,
			label: labels ? labels[i] : value,
			quantity: counts[value] || 0,
			isFiltered: filterValues.has(value),
			isExcluded: filterValues.size > 0 && !filterValues.has(value),
			// value is not present in the original data
			isMissing: (unfilteredCounts[value] || 0) === 0
		}))

		if (hideMissingValues) {
			newData = newData.filter(({ isMissing }: Datum) => !isMissing)
		}

		if (sort) {
			newData = newData.sort((a: Datum, b: Datum) => {
				if (a.quantity === b.quantity) {
					return a.label < b.label ? -1 : 1
				}
				return a.quantity < b.quantity ? 1 : -1
			})
		}
		return newData
	})

	const handleToggleValue = (value: number | string) => {
		crossfilter.toggleFilterValue(field, value)
	}

	const handleReset = () => {
		crossfilter.resetFilter(field)
	}
</script>

<div class="pb-4 not-first:border-t not-first:border-t-grey-1 not-first:pt-4">
	<div class="grid grid-cols-[1fr_1.5rem] gap-2 pr-2">
		<div>
			<Button
				variant="ghost"
				class="flex text-left justify-start items-start h-auto rounded-none gap-1 pl-0! pr-2 py-1 w-full overflow-hidden"
				onclick={() => {
					isOpen = !isOpen
				}}
			>
				{#if isOpen}
					<ChevronDownIcon class="size-5 flex-none" />
				{:else}
					<ChevronRightIcon class="size-5 flex-none" />
				{/if}

				<div class="flex-auto text-base font-bold text-wrap leading-snug">{title}</div>
			</Button>
		</div>
		<div>
			<Button
				variant="ghost"
				class={cn(
					'flex items-start mt-1 h-auto! rounded-full p-0! flex-none text-accent invisible',
					{
						visible: hasFilter
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
		{#if data.length > 0}
			<div class="pt-2 px-4">
				<FilterBars bars={data} {max} onValueClick={handleToggleValue} />

				{#if help}
					<div class="text-xs text-muted-foreground">
						{help}

						{#if url}
							<a href={resolve(url)} target="_blank" class="block">Read more.</a>
						{/if}
					</div>
				{/if}
			</div>
		{:else}
			<div class="text-sm text-muted-foreground italic text-center">No data available</div>
		{/if}
	{/if}
</div>
