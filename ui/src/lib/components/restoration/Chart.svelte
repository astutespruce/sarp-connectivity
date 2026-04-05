<script lang="ts">
	import { cn } from '$lib/utils'
	import { barrierTypeLabels } from '$lib/config/constants'
	import { sum } from '$lib/util/data'
	import { formatNumber } from '$lib/util/format'
	import { Button } from '$lib/components/ui/button'

	import type { MetricOption } from './types'

	const { barrierType, removedBarriersByYear, metric, onChangeMetric } = $props()

	type ChartEntry = {
		label: string
		totalCount: number
		totalNoNetworkCount: number
		totalUpstreamMiles: number
		totalDownstreamMiles: number
		dams: number
		smallBarriers: number
		smallBarriersUpstreamMiles: number
		smallBarriersDownstreamMiles: number
	}

	const entries = $derived(
		removedBarriersByYear
			.map(
				({
					label = '',
					dams = 0,
					damsNoNetwork = 0,
					damsUpstreamMiles = 0,
					damsDownstreamMiles = 0,
					smallBarriers = 0,
					smallBarriersNoNetwork = 0,
					smallBarriersUpstreamMiles = 0,
					smallBarriersDownstreamMiles = 0
				}) => {
					let totalCount = dams + smallBarriers

					let totalNoNetworkCount = damsNoNetwork + smallBarriersNoNetwork
					let totalUpstreamMiles = damsUpstreamMiles + smallBarriersUpstreamMiles
					let totalDownstreamMiles = damsDownstreamMiles + smallBarriersDownstreamMiles
					if (barrierType === 'dams') {
						totalCount = dams
						totalNoNetworkCount = damsNoNetwork
						totalUpstreamMiles = damsUpstreamMiles
						totalDownstreamMiles = damsDownstreamMiles
					} else if (barrierType === 'small_barriers') {
						totalCount = smallBarriers
						totalNoNetworkCount = smallBarriersNoNetwork
						totalUpstreamMiles = smallBarriersUpstreamMiles
						totalDownstreamMiles = smallBarriersDownstreamMiles
					}

					const out: ChartEntry = {
						label,
						totalCount,
						totalNoNetworkCount,
						totalUpstreamMiles,
						totalDownstreamMiles,
						dams,
						smallBarriers,
						smallBarriersUpstreamMiles,
						smallBarriersDownstreamMiles
					}

					if (metric === 'upstream') {
						out.dams = damsUpstreamMiles
						out.smallBarriers = smallBarriersUpstreamMiles
					} else if (metric === 'downstream') {
						out.dams = damsDownstreamMiles
						out.smallBarriers = smallBarriersDownstreamMiles
					}

					return out
				}
			)
			// only show unknown when present
			.filter(({ label, totalCount }: ChartEntry) => label !== 'unknown' || totalCount > 0)
	)

	const max = $derived(
		Math.max(
			...entries.map(({ totalCount, totalUpstreamMiles, totalDownstreamMiles }: ChartEntry) => {
				if (metric === 'upstream') {
					return totalUpstreamMiles
				} else if (metric === 'downstream') {
					return totalDownstreamMiles
				}
				return totalCount
			})
		)
	)

	const totalNoNetworkCount = $derived(
		sum(
			entries.map(({ totalNoNetworkCount: yearNoNetworkCount }: ChartEntry) => yearNoNetworkCount)
		)
	)

	const showDams = $derived(barrierType === 'dams' || barrierType === 'combined_barriers')
	const showSmallBarriers = $derived(
		barrierType === 'small_barriers' || barrierType === 'combined_barriers'
	)

	const metrics: MetricOption[] = [
		{ id: 'upstream', label: 'upstream' },
		{ id: 'downstream', label: 'downstream' },
		{ id: 'count', label: 'number removed' }
	]
</script>

{#if max > 0}
	<div class="flex items-center text-xs mt-2">
		<div class="pr-2 text-right basis-26 flex-none">year</div>
		<div class="flex gap-1 items-center border-l border-l-grey-2 pl-2">
			{#each metrics as metricOption, i (metricOption.id)}
				{#if i > 0}
					<div>|</div>
				{/if}
				<Button
					variant="link"
					class={cn('flex-none no-underline hover:no-underline text-foreground p-0! h-7', {
						'font-bold text-accent ': metricOption.id === metric,
						'hover:text-accent': metricOption.id !== metric
					})}
					onclick={() => {
						onChangeMetric(metricOption.id)
					}}
				>
					{metricOption.label}
				</Button>
			{/each}
		</div>
	</div>

	<div
		class="border-b border-b-grey-2 border-t border-t-grey-2"
		style={`padding-right: ${formatNumber(max).length * 0.8 + 2}em`}
	>
		{#each entries as entry (entry.label)}
			<div class="flex items-center leading-none group">
				<div class="text-right pr-2 basis-26 text-sm group-first:pt-1.5 group-last:pb-2.5">
					{entry.label}
				</div>
				<div
					class="flex flex-auto items-center border-l border-l-grey-2 py-1 group-first:pt-3 group-last:pb-3"
				>
					{#if showDams}
						<div class="h-4 bg-blue-8" style={`flex: 0 0 ${(100 * entry.dams) / max}%`}></div>
					{/if}

					{#if showSmallBarriers}
						<div
							class={cn('h-4 bg-blue-8', {
								'bg-blue-2': showDams
							})}
							style={`flex: 0 0 ${(100 * entry.smallBarriers) / max}%`}
						></div>
					{/if}

					<div class="flex-none text-xs text-muted-foreground pl-1">
						{#if metric === 'upstream'}
							{formatNumber(entry.totalUpstreamMiles)} miles
						{:else if metric === 'downstream'}
							{formatNumber(entry.totalDownstreamMiles)} miles
						{:else}
							{formatNumber(entry.totalCount)}
						{/if}
						{#if entry.totalNoNetworkCount}<sup>*</sup>{/if}
					</div>
				</div>
			</div>
		{/each}
	</div>

	{#if barrierType === 'combined_barriers'}
		<div class="mt-2 flex gap-8 text-xs justify-center">
			<div class="flex items-center gap-1">
				<div class="flex-auto size-4 bg-blue-8"></div>
				<div>{barrierTypeLabels.dams}</div>
			</div>
			<div class="flex items-center gap-1">
				<div class="flex-auto size-4 bg-blue-2"></div>
				<div>
					{barrierTypeLabels.small_barriers}
				</div>
			</div>
		</div>
	{/if}

	{#if totalNoNetworkCount}
		<div class="text-xs text-muted-foreground mt-8">
			<sup>*</sup> includes {formatNumber(totalNoNetworkCount)}
			{#if showDams}{barrierTypeLabels.dams}{/if}
			{#if showDams && showSmallBarriers}
				and / or
			{/if}
			{#if showSmallBarriers}{barrierTypeLabels.small_barriers}{/if}
			that could not be correctly located on the aquatic network or were otherwise excluded from the analysis;
			these contribute toward the count but not the upstream / downstream miles gained.
		</div>
	{/if}
{/if}
