<script lang="ts">
	import type { ColumnTable as Table } from 'arquero'
	import LoadingIcon from '@lucide/svelte/icons/loader'
	import WarningIcon from '@lucide/svelte/icons/triangle-alert'
	import { SvelteSet } from 'svelte/reactivity'
	import { getQueryClientContext } from '@tanstack/svelte-query'
	import type { Map as MapboxGLMapType, LngLatBoundsLike } from 'mapbox-gl'

	import { fetchBarrierInfo, fetchBarrierRanks, fetchUnitDetails } from '$lib/api'
	import { CONTACT_EMAIL } from '$lib/env'
	import { getSingularUnitLabel } from '$lib/config/constants'
	import { summaryStats } from '$lib/config/summaryStats'
	import { Alert } from '$lib/components/alert'
	import { BarrierDetails } from '$lib/components/barrierdetails'
	import { Root as ButtonGroup } from '$lib/components/ui/button-group'
	import { Button } from '$lib/components/ui/button'
	import { Crossfilter } from '$lib/components/filter'
	import { TopBar } from '$lib/components/map'
	import { Sidebar } from '$lib/components/sidebar'
	import { Filters, LayerChooser, UnitChooser } from '$lib/components/workflow'
	import type { SummaryUnit, Status, Step } from '$lib/components/workflow/types'
	import { unitLayerConfig } from '$lib/components/workflow/config'
	import { trackPrioritize } from '$lib/util/analytics'
	import { captureException } from '$lib/util/log'
	import { cn } from '$lib/utils'

	import Map from './Map.svelte'
	import Results from './Results.svelte'
	import type { Option, ResultType } from './types'

	const queryClient = getQueryClientContext()

	const scenarioOptions: Option[] = [
		{ value: 'nc', label: 'network connectivity' },
		{ value: 'wc', label: 'watershed condition' },
		{ value: 'ncwc', label: 'combined' }
	]

	const resultTypeOptions: { value: ResultType; label: string }[] = [
		{
			value: 'full',
			label: 'full networks'
		},
		{
			value: 'perennial',
			label: 'perennial reaches'
		},
		{ value: 'mainstem', label: 'mainstem networks' }
	]

	const resultTypePrefix = {
		full: '',
		perennial: 'p',
		mainstem: 'm'
	}

	const { networkType } = $props()

	const crossfilter = $derived(new Crossfilter(networkType))
	$inspect('filters', crossfilter.filters).with(console.log)

	const { bounds: fullBounds } = summaryStats

	let status: Status = $state({ isLoading: true, error: null })
	let unitStatus: Status = $state({ isLoading: false, error: null })
	let map: MapboxGLMapType | undefined = $state.raw()

	let summaryUnitIds: SvelteSet<string> = new SvelteSet()
	let summaryUnits: SummaryUnit[] = $state([])
	let layer: string | null = $state(null)

	let rankData = $state.raw([])
	let scenario = $state('ncwc')
	let resultsType: ResultType = $state('full')
	let tierThreshold = $state(1)
	let bounds = $state.raw(fullBounds)
	let selectedBarrier = $state.raw(null)
	let step: Step = $state('select-layer')
	let zoom: number = $state(0)

	const handleStartOver = () => {
		crossfilter.data = null

		step = 'select-layer'
		selectedBarrier = null
		layer = null
		summaryUnits = []
		rankData = []
		scenario = 'ncwc'
		resultsType = 'full'
		tierThreshold = 1
		bounds = fullBounds
	}

	const handleCreateMap = async () => {
		// this function is used to prevent selecting units before map is ready
		status = { isLoading: false, error: null }
		zoom = map!.getZoom()
		map!.on('zoomend', () => {
			zoom = map!.getZoom()
		})
	}

	const handleZoomBounds = (newBounds: LngLatBoundsLike) => {
		if (!(map && newBounds)) {
			return
		}
		map.fitBounds(newBounds, { padding: 100 })
	}

	const handleUnitChooserBack = () => {
		step = 'select-layer'
		layer = null
	}

	const handleFilterBack = () => {
		step = 'select-units'
		crossfilter.data = null
	}

	const handleResultsBack = () => {
		step = 'filter'
		rankData = []
		scenario = 'ncwc'
		resultsType = 'full'
		tierThreshold = 1
	}

	// @ts-expect-error newLayer is valid; don't want to bother type checking
	const handleSelectLayer = (newLayer) => {
		layer = newLayer
		summaryUnits = []
		step = 'select-units'
	}

	const handleSelectUnit = async ({
		layer,
		id: selectedId,
		...preFetchedUnitData
	}: SummaryUnit) => {
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
					...preFetchedUnitData
				} as SummaryUnit
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

	const loadBarrierInfo = async () => {
		status = { isLoading: true, error: null }
		rankData = []

		// only select units with non-zero ranked barriers
		let nonzeroSummaryUnits: SummaryUnit[] = []
		switch (networkType) {
			case 'dams': {
				nonzeroSummaryUnits = summaryUnits.filter(({ rankedDams }) => rankedDams > 0)
				break
			}
			case 'small_barriers': {
				nonzeroSummaryUnits = summaryUnits.filter(
					({ rankedSmallBarriers }) => rankedSmallBarriers > 0
				)
				break
			}
			case 'combined_barriers': {
				nonzeroSummaryUnits = summaryUnits.filter(
					({ rankedDams = 0, rankedSmallBarriers = 0 }) => rankedDams + rankedSmallBarriers > 0
				)
				break
			}
			case 'largefish_barriers': {
				nonzeroSummaryUnits = summaryUnits.filter(
					({ rankedLargefishBarriersDams = 0, rankedLargefishBarriersSmallBarriers = 0 }) =>
						rankedLargefishBarriersDams + rankedLargefishBarriersSmallBarriers > 0
				)
				break
			}
			case 'smallfish_barriers': {
				nonzeroSummaryUnits = summaryUnits.filter(
					({ rankedSmallfishBarriersDams = 0, rankedSmallfishBarriersSmallBarriers = 0 }) =>
						rankedSmallfishBarriersDams + rankedSmallfishBarriersSmallBarriers > 0
				)
				break
			}
		}

		summaryUnits = nonzeroSummaryUnits

		const {
			error,
			data,
			bounds: newBounds = null
		} = await queryClient.fetchQuery({
			queryKey: [networkType, layer, nonzeroSummaryUnits.toString()],
			queryFn: async () =>
				fetchBarrierInfo(networkType, {
					[layer!]: nonzeroSummaryUnits.map(({ id }) => id)
				})
		})

		if (error || !data) {
			status = { isLoading: false, error: 'info loading error' }
		}

		crossfilter.data = data as Table

		step = 'filter'
		if (newBounds) {
			bounds = newBounds.split(',').map(parseFloat)
		}
		status = { isLoading: false, error: null }
	}

	const loadRankInfo = async () => {
		status = { isLoading: true, error: null }
		rankData = []

		const {
			error,
			data,
			bounds: newBounds = null
		} = await queryClient.fetchQuery({
			queryKey: [networkType, layer, summaryUnits.toString(), crossfilter.serializeFilters()],
			queryFn: async () =>
				fetchBarrierRanks(
					networkType,
					{ [layer!]: summaryUnits.map(({ id }) => id) },
					crossfilter.filters
				)
		})

		if (error || !data) {
			status = { isLoading: false, error: 'rank loading error' }
		}

		step = 'results'
		// @ts-expect-error assignment is valid, don't want to mess with typing
		rankData = data

		if (newBounds) {
			bounds = newBounds.split(',').map(parseFloat)
		}

		status = { isLoading: false, error: null }

		trackPrioritize({
			barrierType: networkType,
			unitType: layer!,
			details: `ids: [${summaryUnits ? summaryUnits.map(({ id }) => id) : 'none'}], filters: ${crossfilter.serializeFilters()}, scenario: ${scenario}`
		})
	}

	// @ts-expect-error feature is valid here; don't want to bother typing
	const handleSelectBarrier = (feature) => {
		selectedBarrier = feature
	}

	const handleBarrierDetailsClose = () => {
		selectedBarrier = null
	}
</script>

<div class="flex gap-0 h-full w-full">
	<Sidebar>
		{#if status.error || unitStatus.error}
			<div class="flex flex-col p-4 mt-8 flex-auto">
				<Alert title="Whoops!">
					<div>
						There was an error loading these data. Please try clicking on a different area in the
						map or refresh this page in your browser. If it happens again, please
						<a href={`mailto:${CONTACT_EMAIL}`}>contact us</a>.
					</div>
				</Alert>
			</div>
		{:else if status.isLoading}
			<div class="flex justify-center items-center gap-4 text-md text-muted-foreground mt-8 p-4">
				<LoadingIcon class="size-8 motion-safe:animate-spin" />
				Loading...
			</div>
		{:else if selectedBarrier}
			<BarrierDetails data={selectedBarrier} onClose={handleBarrierDetailsClose} />
		{:else if step === 'select-layer'}
			<LayerChooser onSetLayer={handleSelectLayer} />
		{:else if step === 'select-units'}
			<UnitChooser
				{networkType}
				{layer}
				{summaryUnits}
				onSelectUnit={handleSelectUnit}
				onBack={handleUnitChooserBack}
				onSubmit={loadBarrierInfo}
				onStartOver={handleStartOver}
				onZoomBounds={handleZoomBounds}
			/>
		{:else if step === 'filter'}
			<Filters
				{networkType}
				title={networkType.endsWith('_barriers') ? 'Filter barriers' : null}
				{crossfilter}
				nextStepLabel="Prioritize selected barriers"
				onBack={handleFilterBack}
				onStartOver={handleStartOver}
				onSubmit={loadRankInfo}
			/>
		{:else if step === 'results'}
			<Results
				{networkType}
				{rankData}
				bind:tierThreshold
				{scenario}
				{resultsType}
				config={{
					summaryUnits: { [layer!]: summaryUnits.map(({ id }) => id) },
					filters: crossfilter.filters,
					scenario
				}}
				onStartOver={handleStartOver}
				onBack={handleResultsBack}
			/>
		{/if}
	</Sidebar>

	<Map
		bind:map
		{networkType}
		{crossfilter}
		{bounds}
		allowUnitSelect={step === 'select-units'}
		activeLayer={layer}
		{selectedBarrier}
		{summaryUnits}
		rankedBarriers={rankData}
		{tierThreshold}
		scenario={resultTypePrefix[resultsType] + scenario}
		onSelectUnit={handleSelectUnit}
		onSelectBarrier={handleSelectBarrier}
		onCreateMap={handleCreateMap}
		class={step === 'results' ? 'has-top-bar' : null}
	>
		{#if step === 'results'}
			<TopBar>
				<div class="text-sm">Show:</div>
				<ButtonGroup>
					{#each scenarioOptions as option (option.value)}
						<Button
							class={cn('px-2 py-1 h-auto not-first:ml-px', {
								'bg-blue-1 hover:bg-blue-2 text-foreground': option.value !== scenario
							})}
							onclick={() => {
								scenario = option.value
							}}>{option.label}</Button
						>
					{/each}
				</ButtonGroup>

				<div class="text-sm">for</div>

				<ButtonGroup>
					{#each resultTypeOptions as option (option.value)}
						<Button
							class={cn('px-2 py-1 h-auto not-first:ml-px', {
								'bg-blue-1 hover:bg-blue-2 text-foreground': option.value !== resultsType
							})}
							onclick={() => {
								resultsType = option.value
							}}>{option.label}</Button
						>
					{/each}
				</ButtonGroup>
			</TopBar>
		{:else if step === 'select-units' && zoom < unitLayerConfig[layer! as keyof typeof unitLayerConfig].minzoom}
			<TopBar>
				<div class="text-sm text-accent flex gap-2 items-center">
					<WarningIcon class="size-4" />
					Zoom in further to select a {getSingularUnitLabel(layer)}
				</div>
			</TopBar>
		{/if}
	</Map>
</div>
