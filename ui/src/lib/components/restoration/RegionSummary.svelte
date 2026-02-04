<script lang="ts">
	import ChevronsRightIcon from '@lucide/svelte/icons/chevrons-right'

	import { resolve } from '$app/paths'
	import { STATES, shortBarrierTypeLabels } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { formatNumber, pluralize } from '$lib/util/format'
	import { Downloader } from '$lib/components/download'
	import { Search } from '$lib/components/unitsearch'
	import { Footer } from '$lib/components/sidebar'
	import { cn } from '$lib/utils'

	import Chart from './Chart.svelte'

	const downloadConfig = {
		summaryUnits: { State: Object.keys(STATES).sort() },
		filters: {
			removed: new Set([true])
		}
	}

	const {
		barrierType,
		system,
		metric,
		id,
		type,
		name,
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

	const { url, urlLabel }: { url?: string; urlLabel?: string } = $derived.by(() => {
		switch (type) {
			case 'Region': {
				if (id === 'total') {
					return {}
				}
				return {
					url: resolve(`/regions/${id}/`, { id }),
					urlLabel: 'view region page for more information'
				}
			}
			case 'FishHabitatPartnership': {
				return {
					url: resolve(`/fhp/${id}/`, { id }),
					urlLabel: 'view the FHP page for more information'
				}
			}
			case 'State': {
				return {
					url: resolve(`/states/${id}/`, { id }),
					urlLabel: 'view state page for more information'
				}
			}
		}
		return {}
	})

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
		class="pt-2 pb-8 px-4 flex-auto overflow-y-auto h-full [&_ul]:list-outside [&_ul]:list-disc [&_ul]:pl-5 [&_ul>li+li]:mt-2 [&_ul>li]:leading-snug"
	>
		{#if url}
			<a href={url} class="flex gap-1 items-end mb-4">
				{urlLabel}
				<ChevronsRightIcon class="size-5" />
			</a>
		{/if}

		<p class="text-2xl leading-tight mb-4">
			Across {name}, there are:
		</p>

		{#if barrierType === 'dams' || barrierType === 'combined_barriers'}
			<div class="mt-2">
				{#if removedDams > 0}
					<b>{formatNumber(removedDams, 0)}</b>
					{pluralize('dam', removedDams)} that
					{removedDams === 1 ? 'has been or is actively being' : 'have been or are actively being'}
					removed or mitigated, gaining
					<b>{formatNumber(removedDamsGainMiles)} miles</b> of reconnected rivers and streams.
				{:else}
					<b>0</b> dams that are known to have been removed or mitigated.
				{/if}
			</div>
		{/if}

		{#if barrierType === 'small_barriers' || barrierType === 'combined_barriers'}
			<div class={cn('mt-2', { 'mt-6': barrierType === 'combined_barriers' })}>
				{#if removedSmallBarriers > 0}
					<b>{formatNumber(removedSmallBarriers, 0)}</b>
					surveyed road/stream {pluralize('crossing', removedSmallBarriers)} that
					{removedSmallBarriers === 1 ? 'has been or is being' : 'have been or are being'}
					removed or mitigated, gaining
					<b>{formatNumber(removedSmallBarriersGainMiles)} miles</b> of reconnected rivers and streams.
				{:else}
					<b>0</b> surveyed road/stream crossings that are known to have been removed or mitigated.
				{/if}
			</div>
		{/if}

		<div class="mt-4">
			<Chart {barrierType} {removedBarriersByYear} {metric} {onChangeMetric} />
		</div>

		<hr class="my-6" />

		<div class="text-sm text-muted-foreground mt-2 pb-6">
			Select {system === 'ADM' ? 'states / counties' : 'hydrologic units'}
			by clicking on them on the map or searching by name.
		</div>

		<Search {barrierType} {system} onSelect={onSelectUnit} />

		<hr />

		{#if barrierType === 'dams'}
			<div class="mt-12 text-sm text-muted-foreground">
				Note: These statistics are based on <b>{formatNumber(dams, 0)}</b>
				inventoried {pluralize('dam', dams)}, and available information on dams that have been or
				are actively being removed or mitigated, including projects starting in 2026. Because the
				inventory is incomplete in many areas, areas with a high number of dams may simply represent
				areas that have a more complete inventory.
			</div>
		{:else if barrierType === 'small_barriers'}
			<div class="mt-12 text-sm text-muted-foreground">
				Note: These statistics are based on
				<b>{formatNumber(totalSmallBarriers, 0)}</b> surveyed {pluralize(
					'crossing',
					totalSmallBarriers
				)}, and available information on barriers that have been or are actively being removed or
				mitigated, including projects starting in 2026. Because the inventory is incomplete in many
				areas, areas with a high number of surveyed crossings may simply represent areas that have a
				more complete inventory.
			</div>
		{:else if barrierType === 'combined_barriers'}
			<div class="mt-12 text-sm text-muted-foreground">
				Note: These statistics are based on <b>{formatNumber(dams, 0)}</b>
				inventoried {pluralize('dam', dams)} and
				<b>{formatNumber(totalSmallBarriers, 0)}</b> surveyed {pluralize(
					'crossing',
					totalSmallBarriers
				)}, and available information on dams and barriers that have been or are actively being
				removed or mitigated, including projects starting in 2026. Because the inventory is
				incomplete in many areas, areas with a high number of dams or surveyed crossings may simply
				represent areas that have a more complete inventory.
			</div>
		{/if}

		<div class="mt-4 text-sm text-muted-foreground">
			Miles gained are based on aquatic networks cut by
			{barrierType === 'dams'
				? 'waterfalls and dams'
				: 'waterfalls, dams, and surveyed road/stream crossings'}
			that were present at the time a given barrier was removed, with the exception of those directly
			upstream that were removed in the same year as a given barrier.
		</div>
	</div>

	{#if id === 'total'}
		<Footer class="flex gap-4 items-center pt-4">
			<div class="leading-none flex-auto">Download:</div>
			<div class="flex-none">
				<Downloader
					{barrierType}
					label={`Download removed ${shortBarrierTypeLabels[barrierType as BarrierTypePlural]}`}
					config={downloadConfig}
					showOptions={false}
					includeUnranked
					triggerClass="text-sm h-auto py-1.5 px-2!"
				/>
			</div>
		</Footer>
	{/if}
</div>
