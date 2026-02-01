<script lang="ts">
	import LoadingIcon from '@lucide/svelte/icons/loader-circle'
	import type { Map as MapboxGLMapType, LngLatBoundsLike } from 'mapbox-gl'
	import { getQueryClientContext } from '@tanstack/svelte-query'
	import { SvelteSet } from 'svelte/reactivity'

	import { CONTACT_EMAIL, SITE_NAME } from '$lib/env'
	import { Button } from '$lib/components/ui/button'

	import { fetchUnitDetails } from '$lib/api'
	import { Alert } from '$lib/components/alert'
	import { BarrierDetails } from '$lib/components/barrierdetails'
	import { Root as ButtonGroup } from '$lib/components/ui/button-group'
	import { Map, RegionSummary, UnitSummary } from '$lib/components/restoration'
	import type { FocalBarrierType } from '$lib/config/types'
	import { TopBar } from '$lib/components/map'
	import { Sidebar } from '$lib/components/sidebar'
	import { SYSTEMS } from '$lib/config/constants'
	import { captureException } from '$lib/util/log'
	import { extractYearRemovedStats } from '$lib/util/stats'
	import { cn } from '$lib/utils'
	import type { MetricOptionValue } from './types'

	type System = 'ADM' | 'HUC'
	type Status = { isLoading: boolean; error: string | null }
	type SummaryUnit = {
		layer: string
		id: string
		removedBarriersByYear: {
			label: string
			dams: number
			damsNoNetwork: number
			damsGainMiles: number
			smallBarriers: number
			smallBarriersNoNetwork: number
			smallBarriersGainMiles: number
		}[]
	}

	const focalBarrierTypeOptions: { value: FocalBarrierType; label: string }[] = [
		{ value: 'dams', label: 'dams' },
		{ value: 'small_barriers', label: 'surveyed crossings' },
		{ value: 'combined_barriers', label: 'both' }
	]

	const systemOptions: { value: System; label: string }[] = Object.entries(SYSTEMS)
		.filter(([key]) => key === 'ADM' || key === 'HUC')
		.map(([value, label]) => ({
			value: value as System,
			label: label.toLowerCase()
		}))

	const queryClient = getQueryClientContext()

	const { type, data: regionData } = $props()

	let map: MapboxGLMapType | undefined = $state.raw()
	let system: System = $derived(
		type === 'Region' || type === 'State' || type === 'FishHabitatPartnership' ? 'ADM' : 'HUC'
	)
	let metric: MetricOptionValue = $state('gainmiles')
	let focalBarrierType: FocalBarrierType = $state('dams')
	let summaryUnitIds: SvelteSet<string> = new SvelteSet()
	let summaryUnits: SummaryUnit[] = $state([])
	let unitStatus: Status = $state({ isLoading: false, error: null })
	let selectedBarrier = $state.raw(null)

	const handleSetSystem = (newSystem: System) => {
		system = newSystem
		summaryUnitIds.clear()
		summaryUnits = []
		unitStatus = {
			isLoading: false,
			error: null
		}
	}

	const handleSelectUnit = async ({
		layer,
		id: selectedId,
		...preFetchedUnitData
	}: {
		layer: string
		id: string
	}) => {
		selectedBarrier = null

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
					...preFetchedUnitData,
					removedBarriersByYear: extractYearRemovedStats(
						// @ts-expect-error removedDamsByYear exists
						preFetchedUnitData.removedDamsByYear,
						// @ts-expect-error removedSmallBarriersByYear exists
						preFetchedUnitData.removedSmallBarriersByYear
					)
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

	const handleSelectBarrier = (feature) => {
		selectedBarrier = feature
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
	<title>Restoring aquatic connectivity | {SITE_NAME}</title>
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
		{:else if selectedBarrier}
			<BarrierDetails data={selectedBarrier} onClose={handleBarrierDetailsClose} />
		{:else if summaryUnits.length > 0}
			<UnitSummary
				barrierType={focalBarrierType}
				{system}
				{metric}
				{summaryUnits}
				onSelectUnit={handleSelectUnit}
				onReset={handleReset}
				onZoomBounds={handleZoomBounds}
				onChangeMetric={(newMetric: MetricOptionValue) => {
					metric = newMetric
				}}
			/>
		{:else}
			<RegionSummary
				barrierType={focalBarrierType}
				{...regionData}
				{system}
				{metric}
				onSelectUnit={handleSelectUnit}
				onChangeMetric={(newMetric: MetricOptionValue) => {
					metric = newMetric
				}}
			/>
		{/if}
	</Sidebar>
	<Map
		bind:map
		region={regionData}
		{focalBarrierType}
		{system}
		{summaryUnits}
		{selectedBarrier}
		onSelectUnit={handleSelectUnit}
		onSelectBarrier={handleSelectBarrier}
	>
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
							handleSetSystem(option.value)
						}}>{option.label}</Button
					>
				{/each}
			</ButtonGroup>
		</TopBar>
	</Map>
</div>
