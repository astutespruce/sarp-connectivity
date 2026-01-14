<script lang="ts">
	import { createQuery } from '@tanstack/svelte-query'
	import ExploreIcon from '@lucide/svelte/icons/map'
	import LoadingIcon from '@lucide/svelte/icons/loader-circle'
	import PrioritizeIcon from '@lucide/svelte/icons/search-check'
	import RestorationIcon from '@lucide/svelte/icons/chart-no-axes-combined'

	import { resolve } from '$app/paths'
	import { CONTACT_EMAIL, SITE_NAME } from '$lib/env'
	import { fetchUnitDetails } from '$lib/api'
	import { formatNumber, pluralize, singularOrPlural } from '$lib/util/format'

	import { Alert } from '$lib/components/alert'
	import { Button } from '$lib/components/ui/button'
	import { Downloader } from '$lib/components/download'
	import { Chart } from '$lib/components/restoration'
	import type { MetricOptionValue } from '$lib/components/restoration/types'

	const downloadConfig = { scenario: 'NCWC', layer: 'FishHabitatPartnership' }

	const { params, data } = $props()

	let metric: MetricOptionValue = $state('gainmiles')

	const fhpDataRequest = createQuery(() => ({
		queryKey: ['FishHabitatPartnership', params.id],
		queryFn: async () => fetchUnitDetails('FishHabitatPartnership', params.id)
	}))

	const fhpData = $derived(fhpDataRequest.data)

	const hasRemovedBarriers = $derived(
		fhpData && fhpData.removedBarriersByYear
			? fhpData.removedBarriersByYear.filter(
					({ dams: d, smallBarriers: sb }: { dams: number; smallBarriers: number }) => d + sb > 0
				).length > 0
			: false
	)
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

	{#if fhpDataRequest.error}
		<Alert title="Oh no!" class="text-lg mt-8">
			<p class="text-lg">
				We're sorry, there was an unexpected error loading this page. Please reload this page in
				your browser.
				<br /><br />
				If that doesn't fix the problem, please <a href={`mailto:${CONTACT_EMAIL}`}>contact us</a> to
				let us know!
			</p>
		</Alert>
	{:else if fhpDataRequest.isLoading}
		<div class="flex justify-center items-center gap-4 text-xl text-muted-foreground mt-12">
			<LoadingIcon class="size-12 motion-safe:animate-spin" />
			Loading...
		</div>
	{:else if fhpDataRequest.isSuccess}
		<div
			class="bg-grey-1/75 border-t border-t-grey-3 border-b border-b-grey-3 p-2 text-sm flex justify-end items-center gap-4 mt-4 mb-8"
		>
			<div class="flex-none">Download:</div>
			<Downloader
				label="dams"
				barrierType="dams"
				disabled={fhpData.dams === 0}
				config={{
					...downloadConfig,
					summaryUnits: { fishhabitatpartnership: [params.id] }
				}}
			/>
			<div>TODO: download small barriers</div>
		</div>

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

		<div class="grid sm:grid-cols-2 gap-16 mt-8">
			<figure>
				<enhanced:img src={data.map} alt={`${data.name} map`} class="border border-grey-3" />
				<figcaption class="text-sm leading-snug">
					Map of {formatNumber(fhpData.dams)} inventoried dams and
					{formatNumber(fhpData.smallBarriers)} road-related barriers likely to impact aquatic organisms
					in the
					{data.name} boundary.
				</figcaption>
			</figure>

			<div class="[&_ul]:list-disc [&_ul]:list-outside [&_ul]:pl-8 [&_ul_li+li]:mt-2">
				<div class="text-lg font-bold leading-tight">
					The inventory within the {data.name} boundary currently includes
				</div>
				<div class="mt-4">
					<b>{formatNumber(fhpData.dams)}</b> inventoried {pluralize('dam', fhpData.dams)},
					including:
				</div>
				<ul class="mt-2">
					<li>
						<b>{formatNumber(fhpData.rankedDams, 0)}</b> that
						{singularOrPlural('was', 'were', fhpData.rankedDams)} analyzed for impacts to aquatic connectivity
						in this tool
					</li>
					<li>
						<b>{formatNumber(fhpData.reconDams)}</b> that
						{singularOrPlural('was', 'were', fhpData.reconDams)} reconned for social feasibility of removal
					</li>
					{#if fhpData.removedDams > 0}
						<li>
							<b>{formatNumber(fhpData.removedDams, 0)}</b> that
							{singularOrPlural('was', 'were', fhpData.removedDams)}
							removed or mitigated, gaining
							<b>{formatNumber(fhpData.removedDamsGainMiles)} miles</b> of reconnected rivers and streams
						</li>
					{/if}
				</ul>

				<div class="mt-8">
					<b>{formatNumber(fhpData.totalSmallBarriers + fhpData.unsurveyedRoadCrossings, 0)}</b> or more
					road/stream crossings (potential barriers), including:
				</div>
				<ul class="mt-2">
					<li>
						<b>{formatNumber(fhpData.totalSmallBarriers, 0)}</b> that

						{singularOrPlural('was', 'were', fhpData.totalSmallBarriers)} assessed for impacts to aquatic
						organisms
					</li>
					<li>
						<b>{formatNumber(fhpData.smallBarriers, 0)}</b> that
						{singularOrPlural('is', 'are', fhpData.smallBarriers)}

						likely to impact aquatic organisms
					</li>
					<li>
						<b>{formatNumber(fhpData.rankedSmallBarriers, 0)}</b> that
						{singularOrPlural('was', 'were', fhpData.rankedSmallBarriers)}
						analyzed for impacts to aquatic connectivity in this tool
					</li>

					{#if fhpData.removedSmallBarriers}
						<li>
							<b>{formatNumber(fhpData.removedSmallBarriers, 0)}</b> that
							{singularOrPlural('was', 'were', fhpData.removedSmallBarriers)}
							removed or mitigated, gaining
							<b>{formatNumber(fhpData.removedSmallBarriersGainMiles)} miles</b> of reconnected rivers
							and streams
						</li>
					{/if}
				</ul>
			</div>
		</div>

		{#if hasRemovedBarriers}
			<div class="text-2xl font-bold mt-12">Progress toward restoring aquatic connectivity:</div>
			<Chart
				barrierType="combined_barriers"
				removedBarriersByYear={fhpData.removedBarriersByYear}
				{metric}
				onChangeMetric={(newMetric: MetricOptionValue) => {
					metric = newMetric
				}}
			/>
			<div class="text-sm text-muted-foreground mt-4">
				Note: counts above may include both completed as well as active barrier removal or
				mitigation projects.
			</div>
		{/if}

		<div
			class="grid sm:grid-cols-3 gap-0 bg-grey-1/75 mt-12 p-4 border-t border-t-grey-3 border-b border-b-grey-3 [&>div]:flex [&>div]:flex-col [&>div]:gap-4 [&>div+div]:border-t-2 sm:[&>div+div]:border-t-0 sm:[&>div+div]:border-l-2 [&>div]:border-white [&>div+div]:mt-6 sm:[&>div+div]:mt-0 [&>div+div]:pt-4 sm:[&>div+div]:pt-0 sm:[&>div]:px-6 [&>div]:w-full sm:[&>div]:h-full"
		>
			<div>
				<div class="flex-none">
					Explore how many dams or road-related barriers there are in a state, county, or watershed.
				</div>
				<div class="flex-auto flex justify-center items-end mt-4">
					<Button
						href={resolve(`/explore/?fishhabitatpartnership=${params.id}`)}
						class="no-underline"
					>
						<ExploreIcon class="size-6" />
						Start exploring
					</Button>
				</div>
			</div>

			<div>
				<div class="flex-none">
					Explore dams and road-related barriers that have been removed or mitigated by state,
					county, or watershed.
				</div>
				<div class="flex-auto flex justify-center items-end mt-4">
					<Button
						href={resolve(`/restoration/?fishhabitatpartnership=${params.id}`)}
						class="no-underline"
					>
						<RestorationIcon class="size-6" />
						See restoration progress
					</Button>
				</div>
			</div>

			<div>
				<div class="flex-none">
					Identify and rank dams or road-related barriers that reconnect the most high-quality
					aquatic networks.
				</div>
				<div class="flex-auto flex justify-center items-end mt-4">
					<Button href={resolve('/priority/')} class="no-underline">
						<PrioritizeIcon class="size-6" />
						Start prioritizing
					</Button>
				</div>
			</div>
		</div>

		<div class="text-2xl font-bold mt-24">You can help!</div>

		<p class="mt-2">
			You can help improve the inventory You can help improve the inventory by sharing data,
			assisting with field reconnaissance to evaluate the impact of aquatic barriers, or even by
			reporting issues with the inventory data in this tool. To join an aquatic connectivity team
			click
			<a
				href="https://www.americanrivers.org/aquatic-connectivity-groups/"
				target="_blank"
				rel="external"
			>
				here
			</a>.
			<br />
			<br />
			<a href={`mailto:${CONTACT_EMAIL}`}>Contact us</a> to learn more about how you can help
			improve aquatic connectivity in {data.name}.
		</p>
	{/if}
</div>
