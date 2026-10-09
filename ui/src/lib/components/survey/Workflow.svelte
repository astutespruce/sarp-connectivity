<script lang="ts">
	import type { ColumnTable as Table } from 'arquero'
	import LoadingIcon from '@lucide/svelte/icons/loader'
	import WarningIcon from '@lucide/svelte/icons/triangle-alert'
	import { getQueryClientContext } from '@tanstack/svelte-query'
	import type { Map as MapboxGLMapType, LngLatBoundsLike } from 'mapbox-gl/esm'

	import { fetchBarrierInfo } from '#lib/api/index.js'
	import { CONTACT_EMAIL } from '#lib/env.js'
	import { getSingularUnitLabel } from '#lib/config/constants.js'
	import { summaryStats } from '#lib/config/summaryStats.js'
	import { Alert } from '#lib/components/alert/index.js'
	import { BarrierDetails } from '#lib/components/barrierdetails/index.js'
	import { Crossfilter } from '#lib/components/filter/index.js'
	import { TopBar } from '#lib/components/map/index.js'
	import { Sidebar } from '#lib/components/sidebar/index.js'
	import { SummaryUnitManager } from '#lib/components/summaryunits/index.js'
	import type { SummaryUnit } from '#lib/components/summaryunits/types.js'
	import { Filters, LayerChooser, UnitChooser } from '#lib/components/workflow/index.js'
	import type { Status, Step } from '#lib/components/workflow/types.js'
	import { unitLayerConfig } from '#lib/components/workflow/config.js'
	import { logGAEvent } from '#lib/util/analytics.js'

	import Map from './Map.svelte'
	import Results from './Results.svelte'

	const MAX_DOWNLOAD_COUNT = 1500000

	const queryClient = getQueryClientContext()

	const networkType = 'road_crossings'

	const summaryUnits = new SummaryUnitManager()

	const crossfilter = new Crossfilter(networkType)

	// oxlint-disable-next-line
	$inspect('filters', crossfilter.filters).with(console.log)

	const { bounds: fullBounds } = summaryStats

	let status: Status = $state({ isLoading: true, error: null })
	let map: MapboxGLMapType | undefined = $state.raw()
	let mapComponent = $state.raw()
	let layer: string | null = $state(null)

	let bounds = $state(fullBounds)
	let selectedBarrier = $state.raw(null)
	let step: Step = $state('select-layer')
	let zoom: number = $state(0)

	const handleStartOver = () => {
		step = 'select-layer'
		selectedBarrier = null
		layer = null
		summaryUnits.clear()
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

	const handleFilterNext = () => {
		step = 'results'
	}

	const handleResultsBack = () => {
		step = 'filter'
	}

	// @ts-expect-error newLayer is valid; don't want to bother type checking
	const handleSelectLayer = (newLayer) => {
		layer = newLayer
		summaryUnits.clear()
		step = 'select-units'

		logGAEvent(`survey ${networkType} - set layer`, newLayer)
	}

	const handleSelectUnit = async (item: SummaryUnit) => {
		selectedBarrier = null
		// @ts-expect-error clearSelectedBarrier is valid
		mapComponent.clearSelectedBarrier()

		await summaryUnits.toggleItem(item)

		if (item) {
			logGAEvent(`survey ${networkType} - select unit`, `${item.layer}: ${item.id}`)
		}
	}

	// @ts-expect-error feature is valid here; don't want to bother typing
	const handleSelectBarrier = (feature) => {
		selectedBarrier = feature

		if (selectedBarrier) {
			logGAEvent(`survey ${networkType} - select barrier`, feature.sarpidname.split('|')[0])
		}
	}

	const handleBarrierDetailsClose = () => {
		selectedBarrier = null
		// @ts-expect-error clearSelectedBarrier is valid
		mapComponent.clearSelectedBarrier()
	}

	const loadBarrierInfo = async () => {
		status = { isLoading: true, error: null }

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

	$effect(() => {
		// oxlint-disable-next-line no-unused-expressions
		crossfilter.filters

		if (Object.keys(crossfilter.filters).length > 0) {
			logGAEvent('survey road crossings - set filters', crossfilter.serializeFilters())
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
				{crossfilter}
				title="Filter crossings"
				nextStepLabel="Select crossings"
				maxAllowed={MAX_DOWNLOAD_COUNT}
				onBack={handleFilterBack}
				onStartOver={handleStartOver}
				onSubmit={handleFilterNext}
			/>
		{:else if step === 'results'}
			<Results
				{networkType}
				{crossfilter}
				config={{
					summaryUnits: { [layer!]: summaryUnits.ids },
					filters: crossfilter.filters
				}}
				onStartOver={handleStartOver}
				onBack={handleResultsBack}
			/>
		{/if}
	</Sidebar>

	<Map
		bind:this={mapComponent}
		bind:map
		focalBarrierType={networkType}
		{crossfilter}
		{bounds}
		allowUnitSelect={step === 'select-units'}
		activeLayer={layer}
		{summaryUnits}
		onSelectUnit={handleSelectUnit}
		onSelectBarrier={handleSelectBarrier}
		onCreateMap={handleCreateMap}
	>
		{#if step === 'select-units' && zoom < unitLayerConfig[layer! as keyof typeof unitLayerConfig].minzoom}
			<TopBar>
				<div class="text-sm text-accent flex gap-2 items-center">
					<WarningIcon class="size-4" />
					Zoom in further to select a {getSingularUnitLabel(layer!)}
				</div>
			</TopBar>
		{/if}
	</Map>
</div>
