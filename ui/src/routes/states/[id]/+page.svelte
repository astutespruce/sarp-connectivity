<script lang="ts">
	import { createQuery } from '@tanstack/svelte-query'
	import LoadingIcon from '@lucide/svelte/icons/loader-circle'

	import { resolve } from '$app/paths'
	import { SITE_NAME } from '$lib/env'
	import { fetchUnitDetails } from '$lib/api'

	import { PageLoadingError } from '$lib/components/layout'
	import {
		ActionBar,
		BarrierStats,
		DataProviders,
		DownloadBar,
		GetInvolved
	} from '$lib/components/unitSummaryPage'

	const { params, data } = $props()
	const downloadConfig = $derived({
		scenario: 'NCWC',
		layer: 'State',
		summaryUnits: { State: [params.id] }
	})

	const statsRequest = createQuery(() => ({
		queryKey: ['State', params.id],
		queryFn: async () => fetchUnitDetails('State', params.id)
	}))

	const stats = $derived(statsRequest.data)
</script>

<svelte:head>
	<title>{data.name} | {SITE_NAME}</title>
</svelte:head>

<div class="container pt-8 pb-12">
	<div class="flex gap-8 justify-between items-baseline">
		<h1 class="leading-tight text-3xl md:text-4xl lg:text-5xl">
			{data.name}
		</h1>
		<div>
			Part of
			{#each data.regions as region, i (region.url)}
				{#if i > 0}
					,
				{/if}
				<a href={resolve(region.url)}>
					{region.name} region
				</a>
			{/each}
		</div>
	</div>

	{#if statsRequest.error}
		<PageLoadingError />
	{:else if statsRequest.isLoading}
		<div class="flex justify-center items-center gap-4 text-xl text-muted-foreground mt-12">
			<LoadingIcon class="size-12 motion-safe:animate-spin" />
			Loading...
		</div>
	{:else if statsRequest.isSuccess}
		<DownloadBar {stats} config={downloadConfig} areaName={data.name} />

		<BarrierStats areaName={data.name} map={data.map} {stats} />

		<ActionBar
			exploreURL={`/explore/?state=${params.id}`}
			restorationURL={`/restoration/?state=${params.id}`}
			prioritizeURL="/priority/"
		/>

		<DataProviders dataProviders={data.dataProviders} />

		<GetInvolved team={data.team} />
	{/if}
</div>
