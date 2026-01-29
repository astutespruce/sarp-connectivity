<script lang="ts">
	import { createQuery } from '@tanstack/svelte-query'
	import LoadingIcon from '@lucide/svelte/icons/loader-circle'
	import { SITE_NAME } from '$lib/env'
	import { fetchUnitDetails } from '$lib/api'

	import { PageLoadingError } from '$lib/components/layout'
	import {
		ActionBar,
		BarrierStats,
		DownloadBar,
		GetInvolved
	} from '$lib/components/unitSummaryPage'

	const { params, data } = $props()

	const areaName = $derived(`the ${data.name} boundary`)

	const downloadConfig = $derived({
		scenario: 'NCWC',
		layer: 'FishHabitatPartnership',
		summaryUnits: { fishhabitatpartnership: [params.id] }
	})

	const statsRequest = createQuery(() => ({
		queryKey: ['FishHabitatPartnership', params.id],
		queryFn: async () => fetchUnitDetails('FishHabitatPartnership', params.id)
	}))

	const stats = $derived(statsRequest.data)
</script>

<svelte:head>
	<title>{data.name} | {SITE_NAME}</title>
</svelte:head>

<div class="container pt-8 pb-12">
	<div class="flex gap-8 justify-between items-center">
		<h1 class="leading-tight text-3xl md:text-4xl lg:text-5xl">
			{data.name}
		</h1>
		{#if data.logo}
			<a href={data.url} target="_blank" rel="external" aria-label={`${data.name} website`}>
				<img
					src={data.logo}
					alt={`${data.name} logo`}
					class="block"
					style={`max-width: ${data.logoWidth}`}
				/>
			</a>
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
		<DownloadBar {stats} config={downloadConfig} {areaName} />

		<div class="grid sm:grid-cols-[2fr_1fr] gap-8">
			{#if data.description}
				<p>
					{data.description}
					<br />
					<br />
					Learn more about the <a href={data.url} target="_blank">{data.name}</a>.
				</p>
				<div class="bg-blue-1/50 p-4 rounded-lg">
					The {data.name} is one of the Fish Habitat Partnerships under the
					<a href="https://www.fishhabitat.org/" target="_blank" rel="external">
						National Fish Habitat Partnership
					</a>
					umbrella that works to conserve and protect the nation's fisheries and aquatic systems through
					a network of 20 Fish Habitat Partnerships.
				</div>
			{:else}
				<p>
					The {data.name} is one of the Fish Habitat Partnerships under the
					<a href="https://www.fishhabitat.org/" target="_blank" rel="external">
						National Fish Habitat Partnership
					</a>
					umbrella that works to conserve and protect the nation's fisheries and aquatic systems through
					a network of 20 Fish Habitat Partnerships.
					<br />
					<br />
					Learn more about the <a href={data.url} target="_blank">{data.name}</a>.
				</p>
			{/if}
		</div>

		<hr class="divider my-12" />

		<BarrierStats {areaName} map={data.map} {stats} />

		<ActionBar
			exploreURL={`/explore/${params.id}/`}
			restorationURL={`/restoration/${params.id}/`}
			prioritizeURL="/priority/"
		/>

		<GetInvolved />
	{/if}
</div>
