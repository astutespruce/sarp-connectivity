<script lang="ts">
	import { untrack } from 'svelte'
	import { createQuery } from '@tanstack/svelte-query'

	import { searchBarriers } from '$lib/api'
	import { CONTACT_EMAIL } from '$lib/env'
	import { SearchField } from '$lib/components/search'
	import { formatNumber } from '$lib/util/format'

	import ListItem from './BarrierListItem.svelte'

	type SearchResult = {
		sarpid: string
		name: string
		state: string
		river: string | null
		barriertype: string
		latitude: number
		longitude: number
	}
	type ResponseData = { results: SearchResult[]; remaining: number }

	const TIMEOUT = 250 // ms
	const MIN_QUERY_LENGTH = 3

	let { value = $bindable(''), ref = $bindable(), onSubmit } = $props()

	let debouncedQuery = $state(value)
	let activeIndex: number | null = $state(null)
	let selectedId: string | null = $state(null)
	let timeout = $state()

	$effect(() => {
		value

		untrack(() => {
			clearTimeout(timeout)
			activeIndex = null
		})

		if (!value) {
			debouncedQuery = ''
			return
		}

		timeout = setTimeout(() => {
			console.log('set debounced to', value)
			debouncedQuery = value
		}, TIMEOUT)
	})

	const searchRequest = createQuery(() => ({
		queryKey: ['search-barriers-by-name', debouncedQuery],
		queryFn: async () => {
			if (!(debouncedQuery && debouncedQuery.length >= MIN_QUERY_LENGTH)) {
				return {}
			}

			return searchBarriers(debouncedQuery)
		},
		enabled: debouncedQuery.length >= MIN_QUERY_LENGTH
	}))

	const { results = [], remaining = 0 } = $derived(searchRequest.data || {}) as ResponseData

	const handleKeyDown = ({ key }) => {
		if (key === 'Escape') {
			value = ''
			return
		}
		if (!(results && results.length > 0)) {
			return
		}
		if (key === 'ArrowUp') {
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

	const handleSelect = (barrier: SearchResult, index: number) => {
		selectedId = barrier.sarpid
		activeIndex = index
		onSubmit({ latitude: barrier.latitude, longitude: barrier.longitude })
	}
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<div onkeydown={handleKeyDown} role="search">
	<SearchField
		bind:value
		bind:ref
		placeholder="Find a barrier by name / ID"
		isLoading={searchRequest.isLoading}
	/>

	{#if searchRequest.error}
		<div class="flex gap-1 text-destructive">Error loading search results</div>
		<div class="mt-4 text-xs">
			Please try a different search term. If the error continues, please
			<a href={`mailto:${CONTACT_EMAIL}`}> let us know </a>.
		</div>
	{:else if searchRequest.isSuccess}
		{#if results && results.length > 0}
			<div class="mt-2 -mx-1.75 max-h-[50vh] overflow-y-auto">
				<div class="px-1.75">
					{#each results as barrier, i (barrier.sarpid)}
						{#if i > 0}
							<hr class="my-0.5" />
						{/if}
						<ListItem
							{...barrier}
							focused={i === activeIndex}
							isActive={barrier.sarpid === selectedId}
							onClick={() => {
								handleSelect(barrier, i)
							}}
						/>
					{/each}
				</div>
			</div>
			{#if remaining > 0}
				<div class="text-xs border-t border-t-grey-1 pt-2 italic text-center text-muted-foreground">
					...and {formatNumber(remaining)} more...
				</div>
			{/if}
		{:else}
			<div class="px-1 py-4 text-xs italic text-muted-foreground flex justify-center items-center">
				No results found...
			</div>
		{/if}
	{:else if value && value.length < MIN_QUERY_LENGTH}
		<div class="text-muted-foreground italic mt-2 text-xs">keep typing...</div>
	{/if}
</div>
