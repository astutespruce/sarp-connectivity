<script lang="ts">
	import ChevronsRightIcon from '@lucide/svelte/icons/chevrons-right'
	import CloseIcon from '@lucide/svelte/icons/circle-x'
	import { SvelteSet as Set } from 'svelte/reactivity'

	import { resolve } from '$app/paths'
	import { Button } from '$lib/components/ui/button'
	import { STATE_FIPS, STATES, shortBarrierTypeLabels } from '$lib/config/constants'
	import { formatNumber, pluralize, singularOrPlural } from '$lib/util/format'
	import { Downloader } from '$lib/components/download'
	import { summaryUnitLayers } from '$lib/components/explore/layers'
	import { Search } from '$lib/components/unitsearch'
	import { cn } from '$lib/utils'

	import Chart from './Chart.svelte'
	import ListItem from './UnitListItem.svelte'

	type SummaryUnit = {
		id: string
		layer: string
	}

	type RemovedBarriersByYear = {
		label: string
		totalCount: number
		totalNoNetworkCount: number
		totalGainMiles: number
		dams: number
		smallBarriers: number
		smallBarriersGainMiles: number
	}[]

	const {
		barrierType,
		system,
		metric,
		summaryUnits,
		onChangeMetric,
		onSelectUnit,
		onReset,
		onZoomBounds
	} = $props()

	const [{ id, name = '', layer }] = $derived(summaryUnits)
	const {
		title = null,
		subtitle = null,
		idInfo = null,
		ignoreIds = new Set()
	} = $derived.by(() => {
		if (summaryUnits.length === 1) {
			switch (layer) {
				case 'State': {
					return {
						title: STATES[id as keyof typeof STATES]
					}
				}
				case 'County': {
					return { title: name, subtitle: STATE_FIPS[id.slice(0, 2) as keyof typeof STATE_FIPS] }
				}
				case 'HUC2': {
					return { title: name, idInfo: `${layer}: ${id}` }
				}
				default: {
					// all remaining HUC cases
					const [{ title: layerTitle }] = laysummaryUnitLayersers.filter(
						({ id: lyrID }) => lyrID === layer
					)
					return {
						title: name,
						subtitle: layerTitle,
						idInfo: `${layer}: ${id}`
					}
				}
			}
		}

		// mark items to ignore
		const existingIds: Set<string> = new Set()
		if (system === 'ADM') {
			const statesPresent = new Set(
				(summaryUnits as SummaryUnit[])
					.filter(({ layer: l }) => l === 'State')
					.map(({ id: i }) => STATES[i as keyof typeof STATES])
			)

			summaryUnits
				.filter(({ layer: l }: SummaryUnit) => l === 'County')
				.forEach(({ id: i }: SummaryUnit) => {
					const state = STATE_FIPS[i.slice(0, 2) as keyof typeof STATE_FIPS]
					if (statesPresent.has(state)) {
						existingIds.add(i)
					}
				})
		} else {
			const hucsPresent = new Set(summaryUnits.map(({ id: huc }: SummaryUnit) => huc))
			const ids = [...hucsPresent]
			ids.forEach((parentHuc) => {
				ids.forEach((childHuc) => {
					if (parentHuc !== childHuc && childHuc.startsWith(parentHuc)) {
						existingIds.add(childHuc)
					}
				})
			})
		}

		return { title: 'Statistics for selected areas', ignoreIds: existingIds }
	})

	const stats = $derived.by(() => {
		let dams = 0
		let removedDams = 0
		let removedDamsGainMiles = 0
		let totalSmallBarriers = 0
		let removedSmallBarriers = 0
		let removedSmallBarriersGainMiles = 0
		let removedBarriersByYear: RemovedBarriersByYear = []

		summaryUnits
			.filter(({ id: i }: SummaryUnit) => !ignoreIds.has(i))
			.forEach(
				({
					dams: curDams = 0,
					removedDams: curRemovedDams = 0,
					removedDamsGainMiles: curRemovedDamsGainMiles = 0,
					totalSmallBarriers: curTotalSmallBarriers = 0,
					removedSmallBarriers: curRemovedSmallBarriers = 0,
					removedSmallBarriersGainMiles: curRemovedSmallBarriersGainMiles = 0,
					removedBarriersByYear: curRemovedBarriersByYear = []
				}) => {
					dams += curDams
					removedDams += curRemovedDams
					removedDamsGainMiles += curRemovedDamsGainMiles
					totalSmallBarriers += curTotalSmallBarriers
					removedSmallBarriers += curRemovedSmallBarriers
					removedSmallBarriersGainMiles += curRemovedSmallBarriersGainMiles

					if (removedBarriersByYear.length === 0) {
						removedBarriersByYear = curRemovedBarriersByYear
					} else if (curRemovedBarriersByYear.length > 0) {
						// splice together; entries are in same order
						removedBarriersByYear = removedBarriersByYear.map((prev, i) => {
							const cur = curRemovedBarriersByYear[i]
							return Object.fromEntries(
								Object.entries(prev).map(([key, value]) => [
									key,
									key === 'label' ? value : value + cur[key]
								])
							)
						}) as RemovedBarriersByYear
					}
				}
			)

		return {
			dams,
			removedDams,
			removedDamsGainMiles,
			totalSmallBarriers,
			removedSmallBarriers,
			removedSmallBarriersGainMiles,
			removedBarriersByYear
		}
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

	const summaryUnitsForDownload = $derived(
		summaryUnits.reduce(
			(prev, { layer: l, id: i }) =>
				Object.assign(prev, {
					[l]: prev[l] ? prev[l].concat([i]) : [i]
				}),
			{}
		)
	)

	const downloadConfig = $derived({
		// aggregate summary unit ids to list per summary unit layer
		summaryUnits: summaryUnitsForDownload,
		scenario: 'ncwc'
	})

	const handleZoomBounds = () => {
		if (summaryUnits.length !== 1) return
		onZoomBounds(summaryUnits[0].bbox)
	}
</script>

<div class="flex flex-col h-full">
	<div
		class="flex pt-3 pb-4 pl-4 pr-2 justify-center items-start border-b border-b-grey-4 bg-grey-1/50 leading-tight"
	>
		<div class="flex flex-auto">
			<h2 class="text-xl">
				{title}
				{#if subtitle && idInfo}
					<div class="font-normal text-[1rem]">
						{subtitle} <span class="text-muted text-sm">({idInfo})</span>
					</div>
				{:else if subtitle}
					<div class="font-normal text-[1rem]">{subtitle}</div>
				{:else if idInfo}
					<div class="text-muted text-sm">{idInfo}</div>
				{/if}
			</h2>
		</div>

		<div class="flex flex-none flex-col justify-between items-end h-full">
			<Button
				onclick={onReset}
				variant="ghost"
				aria-label={`unselect ${title}`}
				class="p-0! h-auto rounded-full text-muted-foreground hover:text-foreground"
			>
				<CloseIcon class="size-5" />
			</Button>
			{#if summaryUnits.length === 1 && summaryUnits[0].bbox}
				<Button
					variant="link"
					onclick={handleZoomBounds}
					aria-label={`zoom to ${title} on the map`}
					class="p-0! h-auto text-sm mt-1">zoom to</Button
				>
			{/if}
		</div>
	</div>

	<div bind:this={contentNode} class="px-4 pt-2 pb-8 flex-auto h-full overflow-y-auto">
		{#if summaryUnits.length === 1 && layer === 'State'}
			<a href={resolve(`/states/${id}`, { id })} class="flex gap-2 items-end pb-4">
				view state page for more information
				<ChevronsRightIcon class="size-5" />
			</a>
		{/if}

		<div class="[&_ul]:pl-5 [&_ul>li]:leading-snug [&_ul>li+li]:mt-2">
			<div>
				{singularOrPlural('This area contains', 'These areas contain', summaryUnits.length)}:
			</div>

			{#if barrierType === 'dams' || barrierType === 'combined_barriers'}
				<div class="mt-2">
					{#if stats.removedDams > 0}
						<b>
							{formatNumber(stats.removedDams, 0)}
							{pluralize('dam', stats.removedDams)}
						</b>
						that
						{stats.removedDams === 1
							? 'has been or is actively being'
							: 'have been or are actively being'}
						removed or mitigated, gaining
						<b>{formatNumber(stats.removedDamsGainMiles)} miles</b> of reconnected rivers and streams.
					{:else}
						<b>0</b> dams that are known to have been removed or mitigated.
					{/if}
				</div>
			{/if}

			{#if barrierType === 'small_barriers' || barrierType === 'combined_barriers'}
				<div class={cn({ 'mt-6': barrierType === 'combined_barriers' })}>
					{#if stats.removedSmallBarriers > 0}
						<b>{formatNumber(stats.removedSmallBarriers, 0)}</b>
						surveyed road/stream {pluralize('crossing', stats.removedSmallBarriers)} that
						{stats.removedSmallBarriers === 1
							? 'has been or is actively being'
							: 'have been or are actively being'}
						removed or mitigated, gaining
						<b>{formatNumber(stats.removedSmallBarriersGainMiles)} miles</b> of reconnected rivers and
						streams.
					{:else}
						<b>0</b> surveyed road/stream crossings that are known to have been removed or mitigated.
					{/if}
				</div>
			{/if}
		</div>

		<div class="mt-4">
			<Chart
				{barrierType}
				removedBarriersByYear={stats.removedBarriersByYear}
				{metric}
				{onChangeMetric}
			/>
		</div>

		{#if summaryUnits.length > 1}
			<div
				class="mt-8 bg-grey-1/50 py-1 px-4 -mx-4 border-t border-t-grey-2 border-b border-b-grey-2"
			>
				<b>Selected areas:</b>
			</div>

			<ul class="pl-0! list-none">
				{#each summaryUnits as unit (unit.id)}
					<ListItem
						{barrierType}
						{system}
						{unit}
						ignore={ignoreIds.has(unit.id)}
						onDelete={() => {
							onSelectUnit(unit)
						}}
						{onZoomBounds}
					/>
				{/each}
			</ul>
		{/if}

		<hr class="my-6" />

		<div class="text-sm text-muted-foreground mt-2 pb-6">
			Select {summaryUnits.length > 0 ? 'additional' : ''}
			{system === 'ADM' ? 'states / counties' : 'hydrologic units'} by clicking on them on the map or
			searching by name. You can then download data for all selected areas.
		</div>

		<Search
			{barrierType}
			{system}
			ignoreIds={summaryUnits && summaryUnits.length > 0
				? new Set(summaryUnits.map(({ id: unitId }: SummaryUnit) => unitId))
				: null}
			onSelect={onSelectUnit}
		/>

		<hr />

		{#if barrierType === 'dams'}
			<div class="text-sm text-muted-foreground">
				Note: These statistics are based on {formatNumber(stats.dams, 0)}
				inventoried {pluralize('dam', stats.dams)} and available information on dams that have been or
				are actively being removed or mitigated, including projects starting in 2026. Because the inventory
				is incomplete in many areas, areas with a high number of dams may simply represent areas that
				have a more complete inventory.
			</div>
		{:else if barrierType === 'small_barriers'}
			<div class="text-sm text-muted-foreground">
				Note: These statistics are based on
				{formatNumber(stats.totalSmallBarriers, 0)} road/stream crossings that have been surveyed for
				impacts to aquatic organisms and available information on barriers that have been removed or mitigated.
				Because the inventory is incomplete in many areas, areas with a high number of barriers may simply
				represent areas that have a more complete inventory.
			</div>
		{:else if barrierType === 'combined_barriers'}
			<div class="text-sm text-muted-foreground">
				Note: These statistics are based on {formatNumber(stats.dams, 0)}
				inventoried {pluralize('dam', stats.dams)} and
				{formatNumber(stats.totalSmallBarriers, 0)}
				road/stream {pluralize('crossing', stats.totalSmallBarriers)} that have been surveyed for impacts
				to aquatic organisms, and available information on barriers that have been or are actively being
				removed or mitigated, including projects starting in 2026. Because the inventory is incomplete
				in many areas, areas with a high number of barriers may simply represent areas that have a more
				complete inventory.
			</div>
		{/if}

		<div class="text-sm text-muted-foreground mt-4">
			Miles gained are based on aquatic networks cut by
			{barrierType === 'dams' ? 'waterfalls and dams' : 'waterfalls, dams, and surveyed crossings'}
			that were present at the time a given barrier was removed, with the exception of those directly
			upstream that were removed in the same year as a given barrier.
		</div>
	</div>

	<div
		class={cn(
			'flex gap-4 items-center flex-none pt-2 pb-4 px-2 border-t border-t-grey-4 bg-grey-1/50',
			{ 'flex-wrap': barrierType === 'small_barriers' }
		)}
	>
		<div class="leading-none flex-auto">Download:</div>
		<div class="flex gap-4 justify-between flex-none">
			{#if barrierType === 'dams'}
				<Downloader
					barrierType="dams"
					label={shortBarrierTypeLabels.dams}
					config={downloadConfig}
					disabled={stats.dams === 0}
					showOptions={false}
					includeUnranked
					triggerClass="text-sm h-auto py-1.5 px-2!"
				/>
			{:else if barrierType === 'small_barriers'}
				<Downloader
					barrierType="small_barriers"
					label={shortBarrierTypeLabels.small_barriers}
					config={downloadConfig}
					disabled={stats.totalSmallBarriers === 0}
					showOptions={false}
					includeUnranked
					triggerClass="text-sm h-auto py-1.5 px-2!"
				/>
			{:else if barrierType === 'combined_barriers'}
				<Downloader
					barrierType="combined_barriers"
					label={shortBarrierTypeLabels.combined_barriers}
					config={downloadConfig}
					disabled={stats.dams + stats.totalSmallBarriers === 0}
					showOptions={false}
					includeUnranked
					triggerClass="text-sm h-auto py-1.5 px-2!"
				/>
			{/if}
		</div>
	</div>
</div>
