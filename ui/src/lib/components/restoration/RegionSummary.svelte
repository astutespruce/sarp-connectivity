<script lang="ts">
	import ChevronsRightIcon from '@lucide/svelte/icons/chevrons-right'

	import { resolve } from '$app/paths'
	import { STATES, barrierTypeLabels } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { formatNumber, pluralize } from '$lib/util/format'
	import { Downloader } from '$lib/components/download'
	import { Search } from '$lib/components/unitsearch'
	import { cn } from '$lib/utils'

	import Chart from './Chart.svelte'

	const downloadConfig = {
		summaryUnits: { State: Object.keys(STATES).sort() },
		filters: {
			removed: new Set([true])
		}
	}

	const {
		region = null,
		url = null,
		urlLabel = null,
		name,
		barrierType,
		system,
		metric,
		dams = 0,
		removedDams = 0,
		removedDamsGainMiles = 0,
		totalSmallBarriers = 0,
		removedSmallBarriers = 0,
		removedSmallBarriersGainMiles = 0,
		removedBarriersByYear = null,
		onSelectUnit,
		onChangeMetric
	} = $props()

	// reset scroll of content node on change
	let contentNode: Element | null = $state(null)
	$effect(() => {
		barrierType
		system

		if (contentNode) {
			contentNode.scrollTop = 0
		}
	})
</script>

<div class="flex flex-col h-full">
	<div
		bind:this={contentNode}
		class="pt-2 pb-1 px-1 flex-auto overflow-y-auto h-full [&_ul]:list-outside [&_ul]:list-disc [&_ul]:pl-4"
	>
		{#if url}
			<a href={resolve(url)} class="block">
				{urlLabel}
				<ChevronsRightIcon class="size-5" />
			</a>
		{/if}

		<p class="text-lg">
			Across {name}, there are:
		</p>

		{#if barrierType === 'dams' || barrierType === 'combined_barriers'}
			<p class="mt-2">
				{#if removedDams > 0}
					<b>{formatNumber(removedDams, 0)}</b>
					{pluralize('dam', removedDams)} that
					{removedDams === 1 ? 'has been or is actively being' : 'have been or are actively being'}
					removed or mitigated, gaining
					<b>{formatNumber(removedDamsGainMiles)} miles</b> of reconnected rivers and streams
				{:else}
					<b>0</b> dams that are known to have been removed or mitigated
				{/if}
			</p>
		{/if}

		{#if barrierType === 'small_barriers' || barrierType === 'combined_barriers'}
			<p class={cn('mt-2', { 'mt-6': barrierType === 'combined_barriers' })}>
				{#if removedSmallBarriers > 0}
					<b>{formatNumber(removedSmallBarriers, 0)}</b>
					{pluralize('road-related barrier', removedSmallBarriers)} that
					{removedSmallBarriers === 1 ? 'has been or is being' : 'have been or are being'}
					removed or mitigated, gaining
					<b>{formatNumber(removedSmallBarriersGainMiles)} miles</b> of reconnected rivers and streams
				{:else}
					<b>0</b> road-related barriers that are known to have been removed or mitigated
				{/if}
			</p>
		{/if}

		<div class="mt-8">
			<Chart {barrierType} {removedBarriersByYear} {metric} {onChangeMetric} />
		</div>

		<hr />

		<div class="text-sm text-muted-foreground mt-2 pb-6">
			Select {system === 'ADM' ? 'states / counties' : 'hydrologic units'}
			by clicking on them on the map or searching by name.
		</div>

		<Search {barrierType} {system} onSelect={onSelectUnit} />

		<hr />

		{#if barrierType === 'dams'}
			<p class="mt-12 text-sm text-muted-foreground">
				Note: These statistics are based on <b>{formatNumber(dams, 0)}</b>
				inventoried {pluralize('dam', dams)}, and available information on dams that have been or
				are actively being removed or mitigated, including projects starting in 2024. Because the
				inventory is incomplete in many areas, areas with a high number of dams may simply represent
				areas that have a more complete inventory.
			</p>
		{:else if barrierType === 'small_barriers'}
			<p class="mt-12 text-sm text-muted-foreground">
				Note: These statistics are based on
				<b>{formatNumber(totalSmallBarriers, 0)}</b> inventoried
				{pluralize('road-related barrier', totalSmallBarriers)}, and available information on
				barriers that have been or are actively being removed or mitigated, including projects
				starting in 2024. Because the inventory is incomplete in many areas, areas with a high
				number of road-related barriers may simply represent areas that have a more complete
				inventory.
			</p>
		{:else if barrierType === 'combined_barriers'}
			<p class="mt-12 text-sm text-muted-foreground">
				Note: These statistics are based on <b>{formatNumber(dams, 0)}</b>
				inventoried {pluralize('dam', dams)} and
				<b>{formatNumber(totalSmallBarriers, 0)}</b> inventoried
				{pluralize('road-related barrier', totalSmallBarriers)}, and available information on dams
				and barriers that have been or are actively being removed or mitigated, including projects
				starting in 2024. Because the inventory is incomplete in many areas, areas with a high
				number of dams or road-related barriers may simply represent areas that have a more complete
				inventory.
			</p>
		{/if}

		<p class="mt-4 text-sm text-muted-foreground">
			Miles gained are based on aquatic networks cut by
			{barrierType === 'dams'
				? 'waterfalls and dams'
				: 'waterfalls, dams, and road-related barriers'}
			that were present at the time a given barrier was removed, with the exception of those directly
			upstream that were removed in the same year as a given barrier.
		</p>

		{#if !region}
			<div
				class="flex flex-none gap-4 items-center pt-2 px-4 pb-4 border-top border-top-grey-4 bg-grey-0"
			>
				<div class="leading-none flex-auto">Download:</div>
				<div class="flex-none">
					<Downloader
						{barrierType}
						label={barrierTypeLabels[barrierType as BarrierTypePlural]}
						config={downloadConfig}
						showOptions={false}
						includeUnranked
					/>
				</div>
			</div>
		{/if}
	</div>
</div>
