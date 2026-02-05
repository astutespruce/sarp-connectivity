<script lang="ts">
	import { formatNumber, pluralize, singularOrPlural } from '$lib/util/format'
	import type { MetricOptionValue } from '$lib/components/restoration/types'
	import { Chart } from '$lib/components/restoration'

	const { areaName, map, stats } = $props()

	let metric: MetricOptionValue = $state('gainmiles')

	const hasRemovedBarriers = $derived(
		stats && stats.removedBarriersByYear
			? stats.removedBarriersByYear.filter(
					({ dams: d, smallBarriers: sb }: { dams: number; smallBarriers: number }) => d + sb > 0
				).length > 0
			: false
	)
</script>

<div class="grid sm:grid-cols-2 gap-16 mt-8">
	<figure>
		<enhanced:img src={map} alt={`${areaName} map`} class="border border-grey-3" />
		<figcaption class="text-sm leading-snug">
			Map of {formatNumber(stats.dams)} inventoried dams and
			{formatNumber(stats.smallBarriers)} surveyed road/stream crossings likely to impact aquatic organisms
			in
			{areaName}.
		</figcaption>
	</figure>
	<div class="[&_ul]:list-disc [&_ul]:list-outside [&_ul]:pl-8 [&_ul_li+li]:mt-2">
		<div class="text-lg font-bold leading-tight">
			The inventory within {areaName} currently includes
		</div>
		<div class="mt-4">
			<b>{formatNumber(stats.dams)}</b> inventoried {pluralize('dam', stats.dams)}, including:
		</div>
		<ul class="mt-2">
			<li>
				<b>{formatNumber(stats.rankedDams, 0)}</b> that
				{singularOrPlural('was', 'were', stats.rankedDams)} analyzed for impacts to aquatic connectivity
				in this tool
			</li>
			<li>
				<b>{formatNumber(stats.reconDams)}</b> that
				{singularOrPlural('was', 'were', stats.reconDams)} reconned for social feasibility of removal
			</li>
			{#if stats.removedDams > 0}
				<li>
					<b>{formatNumber(stats.removedDams, 0)}</b> that
					{singularOrPlural('was', 'were', stats.removedDams)}
					removed or mitigated, gaining
					<b>{formatNumber(stats.removedDamsGainMiles)} miles</b> of reconnected rivers and streams
				</li>
			{/if}
		</ul>

		<div class="mt-8">
			<b>{formatNumber(stats.totalSmallBarriers + stats.unsurveyedRoadCrossings, 0)}</b> or more road/stream
			crossings (potential barriers), including:
		</div>
		<ul class="mt-2">
			<li>
				<b>{formatNumber(stats.totalSmallBarriers, 0)}</b> that

				{singularOrPlural('was', 'were', stats.totalSmallBarriers)} surveyed for impacts to aquatic organisms
			</li>
			<li>
				<b>{formatNumber(stats.smallBarriers, 0)}</b> that
				{singularOrPlural('is', 'are', stats.smallBarriers)}

				likely to impact aquatic organisms
			</li>
			<li>
				<b>{formatNumber(stats.rankedSmallBarriers, 0)}</b> that
				{singularOrPlural('was', 'were', stats.rankedSmallBarriers)}
				analyzed for impacts to aquatic connectivity in this tool
			</li>

			{#if stats.removedSmallBarriers}
				<li>
					<b>{formatNumber(stats.removedSmallBarriers, 0)}</b> that
					{singularOrPlural('was', 'were', stats.removedSmallBarriers)}
					removed or mitigated, gaining
					<b>{formatNumber(stats.removedSmallBarriersGainMiles)} miles</b> of reconnected rivers and streams
				</li>
			{/if}
		</ul>

		<div class="mt-6">
			<b>{formatNumber(stats.waterfalls)}</b> or more waterfalls.
		</div>
	</div>
</div>

{#if hasRemovedBarriers}
	<div class="text-2xl font-bold mt-16">Progress toward restoring aquatic connectivity:</div>
	<Chart
		barrierType="combined_barriers"
		removedBarriersByYear={stats.removedBarriersByYear}
		{metric}
		onChangeMetric={(newMetric: MetricOptionValue) => {
			metric = newMetric
		}}
	/>
	<div class="text-sm text-muted-foreground mt-4">
		Note: counts above may include both completed as well as active barrier removal or mitigation
		projects.
	</div>
{/if}
