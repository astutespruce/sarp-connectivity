<script lang="ts">
	import LoadingIcon from '@lucide/svelte/icons/loader-circle'
	import type { Map as MapboxGLMapType, LngLatBoundsLike } from 'mapbox-gl'
	import { createQuery, QueryClient } from '@tanstack/svelte-query'
	import { SvelteSet } from 'svelte/reactivity'

	import { browser } from '$app/environment'
	import { CONTACT_EMAIL, SITE_NAME } from '$lib/env'
	import { Button } from '$lib/components/ui/button'

	import { fetchUnitDetails } from '$lib/api'
	import { Alert } from '$lib/components/alert'
	import { BarrierDetails } from '$lib/components/barrierdetails'
	import { Root as ButtonGroup } from '$lib/components/ui/button-group'
	import { Map, RegionSummary, UnitSummary } from '$lib/components/explore'
	import type { FocalBarrierType } from '$lib/components/explore/types'
	import { Legend, TopBar } from '$lib/components/map'
	import { Sidebar } from '$lib/components/sidebar'
	import { REGIONS, SYSTEMS, FISH_HABITAT_PARTNERSHIPS } from '$lib/config/constants'
	import { getQueryParams } from '$lib/util/dom'
	import { captureException } from '$lib/util/log'
	import { cn } from '$lib/utils'

	type System = 'ADM' | 'HUC'
	type Status = { isLoading: boolean; error: string | null }

	const focalBarrierTypeOptions: { value: FocalBarrierType; label: string }[] = [
		{ value: 'dams', label: 'dams' },
		{ value: 'small_barriers', label: 'surveyed crossings' },
		{ value: 'combined_barriers', label: 'both' }
	]

	const systemOptions: { value: System; label: string }[] = Object.entries(SYSTEMS)
		.filter(([key]) => key === 'ADM' || key === 'HUC')
		.map(([value, label]) => ({
			value: value as System,
			label
		}))

	const queryClient = new QueryClient()

	const { id = null, name, type, details } = $props()

	// FIXME: remove
	$inspect('incoming', id, name, type, details).with(console.log)

	let map: MapboxGLMapType | undefined = $state()
	let system: System = $derived(
		type === 'Region' || type === 'State' || type === 'FishHabitatPartnership' ? 'ADM' : 'HUC'
	)
	let focalBarrierType: FocalBarrierType = $state('dams')
	let summaryUnitIds: SvelteSet<string> = new SvelteSet()
	let summaryUnits: { layer: string; id: string }[] = $state([])
	let unitStatus: Status = $state({ isLoading: false, error: null })
	let selectedBarrier = $state(null)
	let barrierStatus: Status = $state({ isLoading: false, error: null })

	const handleSelectUnit = async ({
		layer,
		id: selectedId,
		...preFetchedUnitData
	}: {
		layer: string
		id: string
	}) => {
		if (summaryUnitIds.has(selectedId)) {
			// remove it
			summaryUnitIds.delete(selectedId)
			summaryUnits = summaryUnits.filter(({ id: unitId }) => unitId !== selectedId)
			unitStatus = { isLoading: false, error: null }
			return
		}

		// add it

		// assume if unitData are present it was from a search feature and already
		// has necessary data loaded
		if (Object.keys(preFetchedUnitData).length > 0) {
			summaryUnitIds.add(selectedId)
			summaryUnits = [
				...summaryUnits,
				{
					layer,
					id: selectedId,
					...preFetchedUnitData
				}
			]
			unitStatus = { isLoading: false, error: null }
			return
		}

		// otherwise fetch details for it
		unitStatus = { isLoading: true, error: null }

		try {
			const unitData = await queryClient.fetchQuery({
				queryKey: ['explore-unit-details', layer, selectedId],
				queryFn: async () => fetchUnitDetails(layer, selectedId)
			})

			// if multiple requests resolved with this id due to slow requests, ignore
			// subsequent requests
			if (!summaryUnitIds.has(selectedId)) {
				summaryUnitIds.add(selectedId)
				summaryUnits = [...summaryUnits, unitData]
			}
			unitStatus = { isLoading: false, error: null }
		} catch (ex) {
			captureException(ex as Error | string)
			unitStatus = { isLoading: false, error: ex as string }
		}
	}

	// TODO: derive url, urlLabel, layer from type
	// let regionData = $derived.by(() => {
	// 	switch (type) {
	// 		case 'Region': {
	// 			if (id === 'total') {
	// 				return { ...details, id, name: 'full analysis region', layer: 'boundary' }
	// 			}
	// 			return {
	// 				...details,
	// 				url: `/regions/${id}/`,
	// 				urlLabel: 'view region page for more information'
	// 			}
	// 		}
	// 	}
	// })

	// const dataRequest = createQuery(() => ({
	// 	// TODO: other params
	// 	queryKey: ['explore', type, id],
	// 	queryFn: async () => fetchUnitDetails(type, id),
	// 	enabled: false // FIXME:
	// }))

	const handleSelectBarrier = (feature) => {
		selectedBarrier: feature
		summaryUnitIds.clear()
		summaryUnits = []
	}

	const handleBarrierDetailsClose = () => {
		selectedBarrier = null
	}

	const handleReset = () => {
		summaryUnitIds.clear()
		summaryUnits = []
		selectedBarrier = null
		// bounds = null // FIXME: where is this getting set?
		unitStatus = {
			isLoading: false,
			error: null
		}
	}

	const handleZoomBounds = (newBounds: LngLatBoundsLike) => {
		if (!(map && newBounds)) {
			return
		}
		map.fitBounds(newBounds, { padding: 100 })
	}
</script>

<svelte:head>
	<title>Explore & download barriers | {SITE_NAME}</title>
</svelte:head>

<div class="flex gap-0 w-full h-full">
	<Sidebar>
		{#if unitStatus.error}
			<div class="flex flex-col p-4 mt-8 flex-auto">
				<Alert title="Whoops!">
					<div>
						There was an error loading these data. Please try clicking on a different area in the
						map or refresh this page in your browser. If it happens again, please
						<a href={`mailto:${CONTACT_EMAIL}`}>contact us</a>.
					</div>
				</Alert>
			</div>
		{:else if unitStatus.isLoading}
			<div class="flex justify-center items-center gap-4 text-md text-muted-foreground mt-8 p-4">
				<LoadingIcon class="size-8 motion-safe:animate-spin" />
				Loading...
			</div>
		{:else if selectedBarrier !== null}
			<BarrierDetails data={selectedBarrier} onClose={handleBarrierDetailsClose} />
		{:else if summaryUnits.length > 0}
			<UnitSummary
				barrierType={focalBarrierType}
				{system}
				{summaryUnits}
				onSelectUnit={handleSelectUnit}
				onReset={handleReset}
				onZoomBounds={handleZoomBounds}
			/>
		{:else}
			<RegionSummary
				barrierType={focalBarrierType}
				region={id}
				{...details}
				{system}
				onSelectUnit={handleSelectUnit}
			/>
		{/if}
	</Sidebar>
	<!-- <Map {map} region="" focalBarrierType="dams" system="ADM"> -->
	<div class="relative h-full w-full flex-auto">
		<TopBar>
			<div class="flex-none">Show networks for:</div>

			<ButtonGroup class="flex-none">
				{#each focalBarrierTypeOptions as option (option.value)}
					<Button
						class={cn('px-2 py-1 h-auto not-first:ml-px', {
							'bg-blue-1 hover:bg-blue-2 text-foreground': option.value !== focalBarrierType
						})}
						onclick={() => {
							focalBarrierType = option.value
						}}>{option.label}</Button
					>
				{/each}
			</ButtonGroup>

			<div class="text-muted-foreground flex-none">by</div>

			<ButtonGroup class="flex-none">
				{#each systemOptions as option (option.value)}
					<Button
						class={cn('px-2 py-1 h-auto not-first:ml-px', {
							'bg-blue-1 hover:bg-blue-2 text-foreground': option.value !== system
						})}
						onclick={() => {
							system = option.value
						}}>{option.label}</Button
					>
				{/each}
			</ButtonGroup>

			{#if summaryUnits.length === 0}
				<div class="ml-1 text-muted-foreground leading-none max-w-40">
					Click on a summary unit for more information
				</div>
			{/if}
		</TopBar>
		<!-- </Map> -->
	</div>
</div>
