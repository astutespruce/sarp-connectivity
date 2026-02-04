<script lang="ts">
	import LoadingIcon from '@lucide/svelte/icons/loader-circle'
	import { createQuery } from '@tanstack/svelte-query'

	import { fetchBarrierDetails } from '$lib/api'
	import { CONTACT_EMAIL } from '$lib/env'
	import { Alert } from '$lib/components/alert'
	import { Button } from '$lib/components/ui/button'
	import { METRICS } from '$lib/config/constants'

	import Dam from './Dam.svelte'
	import Footer from './Footer.svelte'
	import Header from './Header.svelte'
	import Scores from './Scores.svelte'
	import SurveyedCrossing from './SurveyedCrossing.svelte'
	import UnsurveyedCrossing from './UnsurveyedCrossing.svelte'
	import Waterfall from './Waterfall.svelte'
	import { cn } from '$lib/utils'

	type Score = { score: number; tier: number }
	type Scores = {
		state?: { [key: string]: Score }
		huc8?: { [key: string]: Score }
		custom?: { [key: string]: Score }
	}

	// IMPORTANT: due to rendering lags, this component appears to render even when
	// data prop is null (should not render due to #if in parent)
	const { data: coreData, onClose } = $props()

	let view: 'details' | 'scores' = $state('details')

	// SARPID is packed for tile data
	const sarpid = $derived(coreData ? coreData.sarpidname.split('|')[0] : null)

	const requestNetworkType = $derived(
		coreData.networkType === 'small_barriers' ? 'combined_barriers' : coreData.networkType
	)
	const dataRequest = createQuery(() => ({
		queryKey: ['barrier-details', requestNetworkType, sarpid],
		queryFn: async () => fetchBarrierDetails(requestNetworkType, sarpid),
		enabled: sarpid !== null
	}))

	const data = $derived({ ...coreData, ...dataRequest.data })

	const hasTabs = $derived(
		data.ranked && (data.barrierType !== 'waterfalls' || data.barrierType === 'road_crossings')
	)

	const scores = $derived.by(() => {
		const tierToPercent = (tier: number) => (100 * (19 - (tier - 1))) / 20

		const out: Scores = {}

		if (
			data.networkType === 'dams' &&
			data.state_ncwc_tier !== null &&
			data.state_ncwc_tier !== undefined &&
			data.state_ncwc_tier !== -1
		) {
			out.state = Object.fromEntries(
				METRICS.map((metric) => {
					const tier = data[`state_${metric}_tier`]
					return [
						metric,
						{
							score: tierToPercent(tier),
							tier
						}
					]
				})
			)
		}

		if (
			data.huc8_ncwc_tier !== null &&
			data.huc8_ncwc_tier !== undefined &&
			data.huc8_ncwc_tier !== -1
		) {
			out.huc8 = Object.fromEntries(
				METRICS.map((metric) => {
					const tier = data[`huc8_${metric}_tier`]
					return [
						metric,
						{
							score: tierToPercent(tier),
							tier
						}
					]
				})
			)
		}

		// add in custom results if available
		if (data.tiers) {
			out.custom = Object.fromEntries(
				METRICS.map((metric) => {
					const tier = data.tiers[metric]
					return [
						metric,
						{
							score: tierToPercent(tier),
							tier
						}
					]
				})
			)
		}

		return out
	})

	$inspect('selectedBarrier', sarpid, data.barrierType, data).with(console.log)
</script>

<!-- data request null indicates 404 type error -->

{#if dataRequest.isSuccess && dataRequest.data}
	<div class="flex flex-col h-full">
		<Header {...data} {onClose} />

		{#if hasTabs}
			<div class="grid grid-cols-2 gap-0 bg-blue-1 flex-none border-t-4 border-t-blue-2">
				<Button
					variant="ghost"
					class={cn('rounded-none', {
						'bg-white font-bold': view === 'details'
					})}
					onclick={() => {
						view = 'details'
					}}
				>
					Overview
				</Button>
				<Button
					variant="ghost"
					class={cn('rounded-none', { 'bg-white font-bold': view === 'scores' })}
					onclick={() => {
						view = 'scores'
					}}>Connectivity ranks</Button
				>
			</div>
		{/if}

		{#if view === 'details'}
			<div
				class={cn('sidebar-barrier-details flex-auto overflow-auto h-full', {
					'pt-4': hasTabs,
					'border-t-2 border-t-blue-8': !hasTabs
				})}
			>
				{#if data.barrierType === 'dams'}
					<Dam {data} />
				{:else if data.barrierType === 'small_barriers'}
					<SurveyedCrossing {data} />
				{:else if data.barrierType === 'road_crossings'}
					<UnsurveyedCrossing {data} />
				{:else if data.barrierType === 'waterfalls'}
					<Waterfall {data} />
				{/if}
			</div>
		{:else}
			<Scores {...data} {scores} />
		{/if}

		<Footer {...data} />
	</div>
{:else if dataRequest.isLoading}
	<div class="container">
		<div class="flex justify-center items-center gap-4 text-xl text-muted-foreground mt-16">
			<LoadingIcon class="size-8 motion-safe:animate-spin" />
			Loading...
		</div>
	</div>
{:else}
	<Alert title="Whoops!">
		There was an error loading these data. Please try clicking on a different barrier or refresh
		this page in your browser.
		<div class="text-sm">
			If it happens again, please
			<a href={`mailto:${CONTACT_EMAIL}`}>contact us</a>.
		</div>
	</Alert>
{/if}
