<script lang="ts">
	import WarningIcon from '@lucide/svelte/icons/triangle-alert'
	import { untrack } from 'svelte'
	import { createQuery } from '@tanstack/svelte-query'

	import { searchUnits } from '$lib/api'
	import { SearchField } from '$lib/components/search'
	import { LAYER_NAMES, SYSTEMS, SYSTEM_UNITS } from '$lib/config/constants'
	import { formatNumber } from '$lib/util/format'

	import SearchResult from './SearchResult.svelte'

	const TIMEOUT = 300 // ms

	type SearchResult = {
		layer: string
		id: string
		name: string
		bbox: string
		state: string
	}
	type ResponseData = { results: SearchResult[]; remaining: number }

	const {
		barrierType,
		system = null,
		layer = null,
		ignoreIds = null,
		showCount = false,
		onSelect,
		minQueryLength = 3,
		class: className = null
	} = $props()

	let query = $state('')
	let debouncedQuery = $state('')
	let activeIndex: number | null = $state(null)
	let timeout = $state()

	$effect(() => {
		query

		untrack(() => {
			clearTimeout(timeout)
			activeIndex = null
		})

		if (!query) {
			debouncedQuery = ''
			return
		}

		timeout = setTimeout(() => {
			debouncedQuery = query
		}, TIMEOUT)
	})

	const showID = $derived(layer ? layer.startsWith('HUC') : system !== 'ADM')

	const searchLabel = $derived(
		layer
			? LAYER_NAMES[layer as keyof typeof LAYER_NAMES].toLowerCase()
			: SYSTEMS[system as keyof typeof SYSTEMS].toLowerCase()
	)

	const suffix = $derived(
		` name${(system && system !== 'ADM') || (layer && layer.startsWith('HUC')) ? ' or ID' : ''}`
	)

	const searchRequest = createQuery(() => ({
		queryKey: ['search-units', system, layer, debouncedQuery],
		queryFn: async () => {
			if (!(debouncedQuery && debouncedQuery.length >= minQueryLength)) {
				return {}
			}

			const layers = layer !== null ? [layer] : SYSTEM_UNITS[system as keyof typeof SYSTEM_UNITS]

			return searchUnits(layers, debouncedQuery)
		},
		enabled: debouncedQuery.length >= minQueryLength
	}))

	const { results = [], remaining = 0 }: ResponseData = $derived(
		searchRequest.data || {}
	) as ResponseData

	const handleSelect = (item: SearchResult) => {
		onSelect({
			...item,
			bbox: item.bbox ? item.bbox.split(',').map(parseFloat) : null
		})
		query = ''
	}

	const handleKeyDown = (event: KeyboardEvent) => {
		const { key } = event
		if (key === 'Escape') {
			query = ''
			return
		}

		if (!(results && results.length > 0)) {
			return
		}

		if (key === 'ArrowUp') {
			event.preventDefault()
			event.stopPropagation()

			if (activeIndex === null) {
				activeIndex = results.length - 1
			} else {
				let nextIndex = activeIndex - 1
				if (nextIndex < 0) {
					nextIndex = results.length - 1
				}
				activeIndex = nextIndex
			}
		} else if (key === 'ArrowDown') {
			event.preventDefault()
			event.stopPropagation()

			if (activeIndex === null) {
				activeIndex = 0
			} else {
				let nextIndex = activeIndex + 1
				if (nextIndex > results.length - 1) {
					nextIndex = 0
				}
				activeIndex = nextIndex
			}
		}
	}
</script>

<div class={className}>
	<div>Search for a {searchLabel}:</div>

	<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
	<div onkeydown={handleKeyDown} role="search">
		<div class="mt-1">
			<SearchField
				bind:value={query}
				placeholder={`${searchLabel}${suffix}`}
				isLoading={searchRequest.isLoading}
			/>
		</div>

		{#if query.length > 0 && query.length < minQueryLength}
			<div class="italic text-muted-foreground text-sm mt-2">...keep typing...</div>
		{:else if searchRequest.error}
			<div class="flex gap-2 items-center text-accent">
				<WarningIcon class="size-5" />
				<div>Error retrieving results</div>
			</div>
		{:else if searchRequest.isSuccess}
			{#if results && results.length > 0}
				<div class="mt-2">
					{#each results as result, i (result.id)}
						{#if i > 0}
							<hr class="my-1" />
						{/if}

						<SearchResult
							{barrierType}
							{...result}
							{showID}
							{showCount}
							disabled={ignoreIds && ignoreIds.has(result.id)}
							focused={i === activeIndex}
							onClick={() => handleSelect(result)}
						/>
					{/each}
				</div>

				{#if remaining > 0}
					<div
						class="text-sm mt-2 pt-2 italic text-center text-muted-foreground border-t border-t-grey-1"
					>
						...and {formatNumber(remaining)} more...
					</div>
				{/if}
			{:else}
				<div class="italic text-muted-foreground mt-2 text-sm">No results match your search</div>
			{/if}
		{/if}
	</div>
</div>
