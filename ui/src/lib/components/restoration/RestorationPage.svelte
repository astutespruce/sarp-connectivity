<script lang="ts">
	import LoadingIcon from '@lucide/svelte/icons/loader-circle'
	import type { Map as MapboxGLMapType, LngLatBoundsLike } from 'mapbox-gl'

	import { CONTACT_EMAIL, SITE_NAME } from '$lib/env'
	import { Button } from '$lib/components/ui/button'

	import { Alert } from '$lib/components/alert'
	import { BarrierDetails } from '$lib/components/barrierdetails'
	import { Root as ButtonGroup } from '$lib/components/ui/button-group'
	import { Map, RegionSummary, UnitSummary } from '$lib/components/restoration'
	import type { FocalBarrierType } from '$lib/config/types'
	import { TopBar } from '$lib/components/map'
	import { Sidebar } from '$lib/components/sidebar'
	import { SummaryUnitManager } from '$lib/components/summaryunits'
	import type { SummaryUnit } from '$lib/components/summaryunits/types'
	import { SYSTEMS } from '$lib/config/constants'
	import { logGAEvent } from '$lib/util/analytics'
	import { cn } from '$lib/utils'
	import type { MetricOptionValue } from './types'

	type System = 'ADM' | 'HUC'

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

	const summaryUnits = new SummaryUnitManager()

	const { type, data: regionData } = $props()

	let map: MapboxGLMapType | undefined = $state.raw()
	let mapComponent = $state.raw()
	let system: System = $derived(
		type === 'Region' || type === 'State' || type === 'FishHabitatPartnership' ? 'ADM' : 'HUC'
	)
	let metric: MetricOptionValue = $state('upstream')
	let focalBarrierType: FocalBarrierType = $state('dams')
	let selectedBarrier = $state.raw(null)

	const handleSetFocalBarrierType = (newType: FocalBarrierType) => {
		focalBarrierType = newType

		logGAEvent(`restoration - set barrier type`, newType)
	}

	const handleSetSystem = (newSystem: System) => {
		system = newSystem
		summaryUnits.clear()

		logGAEvent(`restoration ${focalBarrierType} - set system`, newSystem)
	}

	const handleSelectUnit = async (item: SummaryUnit) => {
		selectedBarrier = null
		await summaryUnits.toggleItem(item)

		if (item) {
			logGAEvent(`restoration ${focalBarrierType} - select unit`, `${item.layer}: ${item.id}`)
		}
	}

	// @ts-expect-error ignore typing here
	const handleSelectBarrier = (feature) => {
		selectedBarrier = feature
		summaryUnits.clear()

		if (selectedBarrier) {
			logGAEvent(
				`restoration ${focalBarrierType} - select barrier`,
				feature.sarpidname.split('|')[0]
			)
		}
	}

	const handleBarrierDetailsClose = () => {
		selectedBarrier = null
		// @ts-expect-error clearSelectedBarrier is valid
		mapComponent.clearSelectedBarrier()
	}

	const handleReset = () => {
		summaryUnits.clear()
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
		{#if summaryUnits.error}
			<div class="flex flex-col p-4 mt-8 flex-auto">
				<Alert title="Whoops!">
					<div>
						There was an error loading these data. Please try clicking on a different area in the
						map or refresh this page in your browser. If it happens again, please
						<a href={`mailto:${CONTACT_EMAIL}`} target="_blank">contact us</a>.
					</div>
				</Alert>
			</div>
		{:else if summaryUnits.isLoading}
			<div class="flex justify-center items-center gap-4 text-md text-muted-foreground mt-8 p-4">
				<LoadingIcon class="size-8 motion-safe:animate-spin" />
				Loading...
			</div>
		{:else if selectedBarrier}
			<BarrierDetails data={selectedBarrier} onClose={handleBarrierDetailsClose} />
		{:else if summaryUnits.count > 0}
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
		bind:this={mapComponent}
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
						onclick={() => handleSetFocalBarrierType(option.value)}>{option.label}</Button
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
