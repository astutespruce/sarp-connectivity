<script lang="ts">
	import SearchIcon from '@lucide/svelte/icons/search'
	import { Marker as MapboxGLMarker } from 'mapbox-gl'
	import type { Marker } from 'mapbox-gl'

	import { Button } from '$lib/components/ui/button'
	import { truncate } from '$lib/util/format'
	import { cn } from '$lib/utils'

	import BarrierSearch from './BarrierSearch.svelte'
	import PlacenameSearch from './PlacenameSearch.svelte'
	import LatLonField from './LatLonField.svelte'

	type Location = { latitude: number; longitude: number }

	type ViewOption = 'barrier' | 'placename' | 'latlon'
	const viewOptions: { id: ViewOption; label: string }[] = [
		{ id: 'barrier', label: 'barrier' },
		{ id: 'placename', label: 'place' },
		{ id: 'latlon', label: 'lat/lon' }
	]

	const { map } = $props()

	let isOpen = $state(false)
	let view: ViewOption = $state(viewOptions[0].id)

	let barrierQuery = $state('')
	let barrierNode: HTMLElement | null = $state(null)
	let placenameQuery = $state('')
	let placenameNode: HTMLElement | null = $state(null)
	let latLonValue = $state('')
	let latLonNode: HTMLElement | null = $state(null)
	let marker: Marker | null = $state(null)
	let location: Location | null = $state(null)

	// clear out search values on chaneg of view
	$effect(() => {
		view

		latLonValue = ''
		placenameQuery = ''
		barrierQuery = ''
		marker = null
	})

	// focus on input node when open and when change between views
	$effect(() => {
		if (isOpen) {
			let focusNode = null
			switch (view) {
				case 'barrier': {
					focusNode = barrierNode
					break
				}
				case 'placename': {
					focusNode = placenameNode
					break
				}
				case 'latlon': {
					focusNode = latLonNode
					break
				}
			}

			if (focusNode) {
				focusNode.focus()
			}
		}
	})

	// reset location on change of queries
	$effect(() => {
		barrierQuery
		placenameQuery
		latLonValue

		location = null
	})

	$effect(() => {
		if (!map) {
			return
		}

		if (location === null) {
			if (marker) {
				marker.remove()
				marker = null
			}
		} else {
			const { latitude, longitude } = location
			map.jumpTo({ center: [longitude, latitude], zoom: 14 })
			if (!marker) {
				marker = new MapboxGLMarker().setLngLat([longitude, latitude]).addTo(map)
			} else {
				marker.setLngLat([longitude, latitude])
			}
		}
	})

	const handleToggleOpen = () => {
		isOpen = !isOpen
	}

	const handleKeyDown = ({ key }) => {
		if (key === 'Escape') {
			isOpen = false
		}
	}

	const handleSetLocation = (nextLocation: Location) => {
		isOpen = false

		location = nextLocation
	}
</script>

<div
	class={cn('hidden absolute left-0 right-0 bottom-0 top-0 z-1000', {
		block: isOpen
	})}
	onclick={() => {
		isOpen = false
	}}
	aria-hidden="true"
></div>

<Button
	tabindex={0}
	variant="outline"
	class={cn(
		'block invisible opacity-0 transition-opacity absolute leading-none bg-white z-2001 top-2 right-2 rounded-md p-1.75 hover:grey-0 w-36 h-10 border-none',
		{ 'visible opacity-100': !isOpen }
	)}
	style="box-shadow:0 0 0 2px #0000001a"
	title="Show map search options"
	aria-label="Search for barriers, places, or enter coodinates"
	onclick={handleToggleOpen}
>
	<div
		class="flex items-center gap-1 border border-grey-2 py-1 px-2 rounded text-muted-foreground/75 text-sm leading-none overflow-hidden"
	>
		<SearchIcon class="size-4" />
		{#if view === 'barrier'}
			{truncate(barrierQuery || 'Search for...', 14)}
		{:else if view === 'placename'}
			{truncate(placenameQuery || 'Search for...', 14)}
		{:else if view === 'latlon'}
			{truncate(latLonValue || 'Go to...', 14)}
		{:else}
			Search for...
		{/if}
	</div>
</Button>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<div
	class={cn(
		'invisible transition-opacity opacity-0 absolute leading-none bg-white z-2001 top-3 right-2 p-1.75 rounded-lg hover:grey-0 border border-text-foreground shadow-lg shadow-grey-8 w-75 overflow-hidden',
		{ 'visible opacity-100': isOpen }
	)}
	onkeydown={handleKeyDown}
	role="search"
>
	<div class="flex gap-1 items-center text-sm leading-none pt-1 pb-3">
		find:
		{#each viewOptions as option (option.id)}
			<Button
				variant="link"
				onclick={() => (view = option.id)}
				class={cn('px-2 py-1 h-auto', { 'text-accent underline': view === option.id })}
				>{option.label}</Button
			>
		{/each}
	</div>

	{#if view === 'barrier'}
		<BarrierSearch bind:value={barrierQuery} bind:ref={barrierNode} onSubmit={handleSetLocation} />
	{:else if view === 'placename'}
		<PlacenameSearch
			bind:value={placenameQuery}
			bind:ref={placenameNode}
			onSubmit={handleSetLocation}
		/>
	{:else if view === 'latlon'}
		<LatLonField bind:value={latLonValue} bind:ref={latLonNode} onSubmit={handleSetLocation} />
	{/if}
</div>
