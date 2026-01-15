<script lang="ts">
	import { createQuery } from '@tanstack/svelte-query'
	import LoadingIcon from '@lucide/svelte/icons/loader-circle'

	import { SITE_NAME } from '$lib/env'
	import { fetchUnitDetails, fetchUnitList } from '$lib/api'

	import { PageLoadingError } from '$lib/components/layout'
	import {
		ActionBar,
		BarrierStats,
		DataProviders,
		GetInvolved,
		StateDownloadTable,
		SARPConnectivityProgram
	} from '$lib/components/unitSummaryPage'

	const { params, data } = $props()

	const areaName = $derived(`the ${data.name} region`)

	const statsRequest = createQuery(() => ({
		queryKey: ['Region', params.id],
		queryFn: async () => {
			const [regionStats, stateStats] = await Promise.all([
				fetchUnitDetails('Region', params.id),
				fetchUnitList('State', data.states)
			])

			return {
				region: regionStats,
				states: stateStats.sort(({ name: left }, { name: right }) => (left < right ? -1 : 1))
			}
		}
	}))

	const stats = $derived(statsRequest.data)
</script>

<svelte:head>
	<title>{data.name} region | {SITE_NAME}</title>
</svelte:head>

<div class="container pt-8 pb-12">
	<div class="flex gap-8 justify-between items-baseline border-b border-b-grey-2">
		<h1 class="leading-tight text-3xl md:text-4xl lg:text-5xl">
			{data.name}
		</h1>
		{#if data.inDevelopment}
			<div class="text-muted-foreground flex-none">(in development)</div>
		{/if}
	</div>

	{#if statsRequest.error}
		<PageLoadingError />
	{:else if statsRequest.isLoading}
		<div class="flex justify-center items-center gap-4 text-xl text-muted-foreground mt-12">
			<LoadingIcon class="size-12 motion-safe:animate-spin" />
			Loading...
		</div>
	{:else if statsRequest.isSuccess}
		<BarrierStats {areaName} map={data.map} stats={stats!.region} />

		<ActionBar
			exploreURL={`/explore/?region=${params.id}`}
			restorationURL={`/restoration/?region=${params.id}`}
			prioritizeURL="/priority/"
		/>

		{#if params.id === 'southeast'}
			<SARPConnectivityProgram />
		{/if}

		<StateDownloadTable total={stats!.region} states={stats!.states} {areaName} />

		<DataProviders dataProviders={data.dataProviders} />

		<GetInvolved teams={data.teams} />
	{/if}
</div>
