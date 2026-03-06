<script lang="ts">
	import type { ColumnTable as Table } from 'arquero'
	import LoadingIcon from '@lucide/svelte/icons/loader'
	import WarningIcon from '@lucide/svelte/icons/triangle-alert'
	import { getQueryClientContext } from '@tanstack/svelte-query'
	import type { Map as MapboxGLMapType, LngLatBoundsLike } from 'mapbox-gl'

	import { fetchBarrierInfo, fetchBarrierRanks } from '$lib/api'
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
	import { SummaryUnitManager } from '$lib/components/summaryunits'
	import type { SummaryUnit } from '$lib/components/summaryunits/types'
	import { Filters, LayerChooser, UnitChooser } from '$lib/components/workflow'
	import type { Status, Step } from '$lib/components/workflow/types'
	import { unitLayerConfig } from '$lib/components/workflow/config'
	import { trackPrioritize, logGAEvent } from '$lib/util/analytics'
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

	const summaryUnits = new SummaryUnitManager()

	const { networkType } = $props()

	const crossfilter = $derived(new Crossfilter(networkType))
	$inspect('filters', crossfilter.filters).with(console.log)

	const { bounds: fullBounds } = summaryStats

	let status: Status = $state({ isLoading: true, error: null })
	let map: MapboxGLMapType | undefined = $state.raw()
	let mapComponent = $state.raw()
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
		step = 'select-layer'
		selectedBarrier = null
		layer = null
		summaryUnits.clear()
		rankData = []
		scenario = 'ncwc'
		resultsType = 'full'
		tierThreshold = 1
		bounds = fullBounds
		crossfilter.data = null

		// @ts-expect-error clearSelectedBarrier is valid
		mapComponent.clearSelectedBarrier()
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
		summaryUnits.clear()
		step = 'select-units'

		logGAEvent(`prioritize ${networkType} - set layer`, newLayer)
	}

	const handleSelectUnit = async (item: SummaryUnit) => {
		selectedBarrier = null
		// @ts-expect-error clearSelectedBarrier is valid
		mapComponent.clearSelectedBarrier()

		await summaryUnits.toggleItem(item)

		if (item) {
			logGAEvent(`prioritize ${networkType} - select unit`, `${item.layer}: ${item.id}`)
		}
	}

	const loadBarrierInfo = async () => {
		status = { isLoading: true, error: null }
		rankData = []

		const {
			error,
			data,
			bounds: newBounds = null
		} = await queryClient.fetchQuery({
			queryKey: [networkType, layer, summaryUnits.ids.toString()],
			queryFn: async () =>
				fetchBarrierInfo(networkType, {
					[layer!]: summaryUnits.ids
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
				fetchBarrierRanks(networkType, { [layer!]: summaryUnits.ids }, crossfilter.filters)
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
			details: `ids: [${summaryUnits.ids.join(',')}], filters: ${crossfilter.serializeFilters()}, scenario: ${scenario}`
		})
	}

	// @ts-expect-error feature is valid here; don't want to bother typing
	const handleSelectBarrier = (feature) => {
		selectedBarrier = feature

		if (selectedBarrier) {
			logGAEvent(`prioritize ${networkType} - select barrier`, feature.sarpidname.split('|')[0])
		}
	}

	const handleBarrierDetailsClose = () => {
		selectedBarrier = null
		// @ts-expect-error clearSelectedBarrier is valid
		mapComponent.clearSelectedBarrier()
	}

	$effect(() => {
		crossfilter.filters

		if (Object.keys(crossfilter.filters).length > 0) {
			logGAEvent(`prioritize ${networkType} - set filters`, crossfilter.serializeFilters())
		}
	})
</script>

<div class="flex gap-0 h-full w-full">
	<Sidebar>
		{#if status.error || summaryUnits.error}
			<div class="flex flex-col p-4 mt-8 flex-auto">
				<Alert title="Whoops!">
					<div>
						There was an error loading these data. Please try clicking on a different area in the
						map or refresh this page in your browser. If it happens again, please
						<a href={`mailto:${CONTACT_EMAIL}`} target="_blank">contact us</a>.
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
					summaryUnits: { [layer!]: summaryUnits.ids },
					filters: crossfilter.filters,
					scenario
				}}
				onStartOver={handleStartOver}
				onBack={handleResultsBack}
			/>
		{/if}
	</Sidebar>

	<Map
		bind:this={mapComponent}
		bind:map
		{networkType}
		{crossfilter}
		{bounds}
		allowUnitSelect={step === 'select-units'}
		activeLayer={layer}
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
