<script lang="ts">
	import { untrack } from 'svelte'
	import { createQuery } from '@tanstack/svelte-query'

	import { CONTACT_EMAIL } from '$lib/env'
	import { SearchField } from '$lib/components/search'
	import { searchPlaces, getPlace } from './mapbox'
	import ListItem from './PlaceListItem.svelte'

	type PlaceResult = {
		id: string
		name: string
		address?: string
	}

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
			selectedId = null
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
		queryKey: ['search-places-by-name', debouncedQuery],
		queryFn: async () => {
			if (!(debouncedQuery && debouncedQuery.length >= MIN_QUERY_LENGTH)) {
				return {}
			}

			return searchPlaces(debouncedQuery)
		},
		enabled: debouncedQuery.length >= MIN_QUERY_LENGTH
	}))

	const placeRequest = createQuery(() => ({
		queryKey: ['get-place', selectedId],
		queryFn: async () => {
			const { latitude = null, longitude = null } = await getPlace(selectedId!)

			if (latitude !== null && longitude !== null) {
				onSubmit({ latitude, longitude })
			}

			return { latitude, longitude }
		},
		enabled: !!selectedId
	}))

	const results: PlaceResult[] | undefined = $derived(searchRequest.data)

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
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<div onkeydown={handleKeyDown} role="search">
	<SearchField
		bind:value
		bind:ref
		placeholder="Find a place by name / address"
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
					{#each results as place, i (place.id)}
						{#if i > 0}
							<hr class="my-0.5" />
						{/if}
						<ListItem
							{...place}
							focused={i === activeIndex}
							isActive={place.id === selectedId}
							onClick={() => {
								selectedId = place.id
							}}
						/>
					{/each}
				</div>
			</div>
		{:else}
			<div class="px-1 py-8 -ml-6 italic text-muted-foreground flex justify-center items-center">
				No results found...
			</div>
		{/if}
	{:else if value && value.length < MIN_QUERY_LENGTH}
		<div class="text-muted-foreground text-xs italic mt-2">keep typing...</div>
	{/if}
</div>
