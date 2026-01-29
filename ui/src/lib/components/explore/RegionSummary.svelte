<script lang="ts">
	import ChevronsRightIcon from '@lucide/svelte/icons/chevrons-right'
	import { SvelteSet } from 'svelte/reactivity'

	import { resolve } from '$app/paths'
	import { MAP_SERVICES, shortBarrierTypeLabels } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { formatNumber } from '$lib/util/format'
	import { Downloader } from '$lib/components/download'
	import { Search } from '$lib/components/unitsearch'
	import { cn } from '$lib/utils'

	const {
		barrierType,
		system,
		id,
		type,
		name,
		dams = 0,
		reconDams = 0,
		rankedDams = 0,
		removedDams = 0,
		removedDamsGainMiles = 0,
		totalSmallBarriers = 0,
		smallBarriers = 0,
		rankedSmallBarriers = 0,
		removedSmallBarriers = 0,
		removedSmallBarriersGainMiles = 0,
		unsurveyedRoadCrossings = 0,
		onSelectUnit
	} = $props()

	const ignoreIds = $derived(new SvelteSet([id]))

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

	const unrankedDams = $derived(dams - rankedDams)
	const unrankedBarriers = $derived(smallBarriers - rankedSmallBarriers)
	const totalRoadBarriers = $derived(totalSmallBarriers + unsurveyedRoadCrossings)

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

		<div class="text-2xl leading-tight mb-4">
			Across {name}, there are:
		</div>

		{#if barrierType === 'dams' || barrierType === 'combined_barriers'}
			<div class="mt-2">
				<b>{formatNumber(dams, 0)}</b> inventoried dams, including:
			</div>
			<ul class="mt-2">
				<li>
					<b>{formatNumber(reconDams)}</b> that have been reconned for social feasibility of removal
				</li>
				<li>
					<b>{formatNumber(rankedDams, 0)}</b> that have been analyzed for their impacts to aquatic connectivity
					in this tool
				</li>

				{#if removedDams > 0}
					<li>
						<b>{formatNumber(removedDams, 0)}</b> that have been removed or mitigated, gaining
						<b>{formatNumber(removedDamsGainMiles)} miles</b> of reconnected rivers and streams
					</li>
				{/if}
			</ul>
		{/if}

		{#if barrierType === 'small_barriers' || barrierType === 'combined_barriers'}
			<div class={cn('mt-2', { 'mt-6': barrierType === 'combined_barriers' })}>
				<b>{formatNumber(totalRoadBarriers, 0)}</b> or more road/stream crossings (potential aquatic barriers),
				including:
			</div>

			<ul class="mt-2">
				<li>
					<b>
						{formatNumber(totalSmallBarriers - removedSmallBarriers, 0)}
					</b>
					that have been surveyed for impacts to aquatic organisms
				</li>
				<li>
					<b>{formatNumber(smallBarriers - removedSmallBarriers, 0)}</b>
					surveyed crossings are likely to impact aquatic organisms
				</li>
				<li>
					<b>{formatNumber(rankedSmallBarriers, 0)}</b> that have been analyzed for their impacts to aquatic
					connectivity in this tool
				</li>
				{#if removedSmallBarriers > 0}
					<li>
						<b>{formatNumber(removedSmallBarriers, 0)}</b> that have been removed or mitigated,
						gaining
						<b>{formatNumber(removedSmallBarriersGainMiles)} miles</b> of reconnected rivers and streams
					</li>
				{/if}
				<li>
					<b>{formatNumber(unsurveyedRoadCrossings, 0)}</b> unsurveyed road/stream crossings
				</li>
			</ul>
		{/if}

		<hr class="my-6" />

		<div class="text-sm mt-2 pb-6 text-muted-foreground">
			Select {system === 'ADM' ? 'states / counties' : 'hydrologic units'}
			by clicking on them on the map or searching by name. You can then download data for all selected
			areas.
		</div>

		<Search {barrierType} {system} onSelect={onSelectUnit} {ignoreIds} />

		<hr />

		{#if barrierType === 'dams'}
			<div class="text-sm text-muted-foreground mt-12">
				Note: These statistics are based on <i>inventoried</i> dams. Because the inventory is
				incomplete in many areas, areas with a high number of dams may simply represent areas that
				have a more complete inventory.
				<br />
				<br />
				{formatNumber(unrankedDams, 0)} dams were not analyzed because they could not be correctly located
				on the aquatic network or were otherwise excluded from the analysis.
			</div>
		{:else if barrierType === 'small_barriers'}
			<div class="text-sm text-muted-foreground mt-12">
				Note: These statistics are based on <i>inventoried</i> road-related barriers. Because the
				inventory is incomplete in many areas, areas with a high number of road-related barriers may
				simply represent areas that have a more complete inventory.
				<br />
				<br />
				{formatNumber(unrankedBarriers, 0)} road-related barriers could not be correctly located on the
				aquatic network or were otherwise excluded from the analysis.
			</div>
		{:else if barrierType === 'combined_barriers'}
			<div class="text-sm text-muted-foreground mt-12">
				Note: These statistics are based on <i>inventoried</i> dams and road-related barriers.
				Because the inventory is incomplete in many areas, areas with a high number of dams or
				road-related barriers may simply represent areas that have a more complete inventory.
				<br />
				<br />
				{formatNumber(unrankedDams, 0)} dams and
				{formatNumber(unrankedBarriers, 0)} road-related barriers could not be correctly located on the
				aquatic network or were otherwise excluded from the analysis.
			</div>
		{/if}

		{#if id === 'total'}
			<div class="mt-8">
				To access an ArcGIS map service of a recent version of these barriers and associated
				connectivity results,
				<a href={MAP_SERVICES[barrierType as keyof typeof MAP_SERVICES]}> click here </a>.
				<div class="text-sm mt-2 text-muted-foreground">
					Note: may not match the exact version available for download in this tool
				</div>
			</div>
		{/if}
	</div>

	{#if id === 'total'}
		<div
			class={cn(
				'flex gap-4 items-center flex-none pt-2 pb-4 px-2 border-t border-t-grey-4 bg-grey-1/50',
				{ 'flex-wrap': barrierType === 'small_barriers' }
			)}
		>
			<div class="leading-none flex-auto">Download:</div>
			<div
				class={cn('flex gap-4 justify-between flex-none', {
					'w-full': barrierType === 'small_barriers'
				})}
			>
				<Downloader
					{barrierType}
					label={shortBarrierTypeLabels[barrierType as BarrierTypePlural]}
					showOptions={false}
					triggerClass="text-sm h-auto py-1.5 px-2!"
				/>

				{#if barrierType === 'small_barriers'}
					<Downloader
						barrierType="road_crossings"
						label={shortBarrierTypeLabels.road_crossings}
						showOptions={false}
						triggerClass="text-sm h-auto py-1.5 px-2!"
					/>
				{/if}
			</div>
		</div>
	{/if}
</div>
