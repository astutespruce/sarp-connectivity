<script lang="ts">
	import ChevronsRightIcon from '@lucide/svelte/icons/chevrons-right'
	import CloseIcon from '@lucide/svelte/icons/circle-x'
	import { SvelteSet } from 'svelte/reactivity'

	import { resolve } from '$app/paths'
	import { Button } from '$lib/components/ui/button'
	import { STATE_FIPS, STATES, shortBarrierTypeLabels } from '$lib/config/constants'
	import { formatNumber, pluralize, singularOrPlural } from '$lib/util/format'
	import { Downloader } from '$lib/components/download'
	import { summaryUnitLayers } from '$lib/components/explore/layers'
	import type { SummaryUnit } from '$lib/components/summaryunits/types'
	import { Search } from '$lib/components/unitsearch'
	import { Header, Footer } from '$lib/components/sidebar'
	import { cn } from '$lib/utils'

	import ListItem from './UnitListItem.svelte'

	const { barrierType, system, summaryUnits, onSelectUnit, onReset, onZoomBounds } = $props()

	const [{ id, name = '', layer }] = $derived(summaryUnits.items)
	const {
		title = null,
		subtitle = null,
		idInfo = null,
		ignoreIds = new SvelteSet()
	} = $derived.by(() => {
		if (summaryUnits.count === 1) {
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
					const [{ title: layerTitle }] = summaryUnitLayers.filter(
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
		const existingIds: SvelteSet<string> = new SvelteSet()
		if (system === 'ADM') {
			const statesPresent = new Set(
				summaryUnits.items
					.filter(({ layer: l }: SummaryUnit) => l === 'State')
					.map(({ id: i }: SummaryUnit) => STATES[i as keyof typeof STATES])
			)

			summaryUnits.items
				.filter(({ layer: l }: SummaryUnit) => l === 'County')
				.forEach(({ id: i }: SummaryUnit) => {
					const state = STATE_FIPS[i.slice(0, 2) as keyof typeof STATE_FIPS]
					if (statesPresent.has(state)) {
						existingIds.add(i)
					}
				})
		} else {
			const hucsPresent = new Set(summaryUnits.items.map(({ id: huc }: SummaryUnit) => huc))
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
		let rankedDams = 0
		let removedDams = 0
		let removedDamsGainMiles = 0
		let smallBarriers = 0
		let totalSmallBarriers = 0
		let rankedSmallBarriers = 0
		let removedSmallBarriers = 0
		let removedSmallBarriersGainMiles = 0
		let totalRoadCrossings = 0
		let unsurveyedRoadCrossings = 0

		summaryUnits.items
			.filter(({ id: i }: SummaryUnit) => !ignoreIds.has(i))
			.forEach(
				({
					dams: curDams = 0,
					rankedDams: curRankedDams = 0,
					removedDams: curRemovedDams = 0,
					removedDamsGainMiles: curRemovedDamsGainMiles = 0,
					smallBarriers: curSmallBarriers = 0,
					totalSmallBarriers: curTotalSmallBarriers = 0,
					rankedSmallBarriers: curRankedSmallBarriers = 0,
					removedSmallBarriers: curRemovedSmallBarriers = 0,
					removedSmallBarriersGainMiles: curRemovedSmallBarriersGainMiles = 0,
					totalRoadCrossings: curRoadCrossings = 0,
					unsurveyedRoadCrossings: curUnsurveyedCrossings = 0
				}) => {
					dams += curDams
					rankedDams += curRankedDams
					removedDams += curRemovedDams
					removedDamsGainMiles += curRemovedDamsGainMiles
					smallBarriers += curSmallBarriers
					totalSmallBarriers += curTotalSmallBarriers
					rankedSmallBarriers += curRankedSmallBarriers
					removedSmallBarriers += curRemovedSmallBarriers
					removedSmallBarriersGainMiles += curRemovedSmallBarriersGainMiles
					totalRoadCrossings += curRoadCrossings
					unsurveyedRoadCrossings += curUnsurveyedCrossings
				}
			)

		return {
			dams,
			rankedDams,
			unrankedDams: dams - rankedDams,
			removedDams,
			removedDamsGainMiles,
			smallBarriers,
			totalSmallBarriers,
			rankedSmallBarriers,
			unrankedBarriers: smallBarriers - rankedSmallBarriers,
			removedSmallBarriers,
			removedSmallBarriersGainMiles,
			totalRoadCrossings,
			unsurveyedRoadCrossings,
			totalRoadBarriers: totalSmallBarriers + unsurveyedRoadCrossings
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

	const handleZoomBounds = () => {
		if (summaryUnits.count !== 1) return

		onZoomBounds(summaryUnits.items[0].bbox)
	}

	const summaryUnitsForDownload = $derived(summaryUnits.getUnitIdsByLayer())

	const downloadConfig = $derived({
		// aggregate summary unit ids to list per summary unit layer
		summaryUnits: summaryUnitsForDownload,
		scenario: 'ncwc'
	})
</script>

<div class="flex flex-col h-full">
	<Header class="flex justify-center items-start leading-tight px-4 pt-2 pb-4">
		<div class="flex-auto">
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
			<Button variant="close" onclick={onReset} aria-label={`unselect ${title}`}>
				<CloseIcon class="size-5" />
			</Button>
			{#if summaryUnits.count === 1 && summaryUnits.items[0].bbox}
				<Button
					variant="link"
					class="p-0! h-auto text-sm mt-1"
					onclick={handleZoomBounds}
					aria-label={`zoom to ${title} on the map`}>zoom to</Button
				>
			{/if}
		</div>
	</Header>

	<div bind:this={contentNode} class="px-4 pt-2 pb-8 flex-auto h-full overflow-y-auto">
		{#if summaryUnits.count === 1 && layer === 'State'}
			<a href={resolve(`/states/${id}`, { id })} class="flex gap-2 items-end pb-4">
				view state page for more information
				<ChevronsRightIcon class="size-5" />
			</a>
		{/if}

		<div class="[&_ul]:pl-5 [&_ul>li]:leading-snug [&_ul>li+li]:mt-2">
			<div class="pb-2">
				{singularOrPlural('This area contains', 'These areas contain', summaryUnits.count)}:
			</div>

			{#if barrierType === 'dams' || barrierType === 'combined_barriers'}
				{#if stats.dams > 0}
					<div>
						<b>{formatNumber(stats.dams)}</b> inventoried {pluralize('dam', stats.dams)}, including:
					</div>
					<ul class="mt-2">
						<li>
							<b>{formatNumber(stats.rankedDams, 0)}</b> that
							{stats.rankedDams === 1 ? 'was ' : 'were '} analyzed for impacts to aquatic connectivity
							in this tool
						</li>
						{#if stats.removedDams > 0}
							<li>
								<b>{formatNumber(stats.removedDams, 0)}</b> that have been removed or mitigated,
								gaining
								<b>{formatNumber(stats.removedDamsGainMiles)} miles</b> of reconnected rivers and streams
							</li>
						{/if}
					</ul>
				{:else}
					<div class="mt-2">
						<b>0</b> inventoried dams
					</div>
				{/if}
			{/if}

			{#if barrierType === 'small_barriers' || barrierType === 'combined_barriers'}
				{#if stats.totalRoadBarriers > 0}
					<div class={cn({ 'mt-6': barrierType === 'combined_barriers' })}>
						<b>{formatNumber(stats.totalRoadBarriers, 0)}</b> or more road/stream crossings (potential
						aquatic barriers), including:
					</div>
					<ul class="mt-2">
						<li>
							<b>
								{formatNumber(stats.totalSmallBarriers - stats.removedSmallBarriers, 0)}
							</b>
							that
							{stats.totalSmallBarriers - stats.removedSmallBarriers === 1 ? 'has ' : 'have '}
							been surveyed for impacts to aquatic organisms.
						</li>
						<li>
							<b>
								{formatNumber(stats.smallBarriers - stats.removedSmallBarriers, 0)}
							</b>
							that
							{stats.smallBarriers - stats.removedSmallBarriers === 1 ? 'is' : 'are'}
							likely to impact aquatic organisms
						</li>
						<li>
							<b>{formatNumber(stats.rankedSmallBarriers, 0)}</b> that
							{stats.rankedSmallBarriers === 1 ? 'was ' : 'were '} analyzed for impacts to aquatic connectivity
							in this tool
						</li>
						{#if stats.removedSmallBarriers > 0}
							<li>
								<b>{formatNumber(stats.removedSmallBarriers, 0)}</b> that have been removed or
								mitigated, gaining
								<b>{formatNumber(stats.removedSmallBarriersGainMiles)} miles</b>
								of reconnected rivers and streams
							</li>
						{/if}
						<li>
							<b>{formatNumber(stats.unsurveyedRoadCrossings, 0)}</b> that have not yet been surveyed
						</li>
					</ul>
				{:else}
					<div class="mt-2">
						<b>{formatNumber(stats.unsurveyedRoadCrossings, 0)}</b> that have not yet been surveyed
					</div>
				{/if}
			{/if}

			{#if summaryUnits.count > 1}
				<div
					class="mt-8 bg-grey-1/50 py-1 px-4 -mx-4 border-t border-t-grey-2 border-b border-b-grey-2"
				>
					<b>Selected areas:</b>
				</div>
				<ul class="pl-0! list-none">
					{#each summaryUnits.items as unit (unit.id)}
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
		</div>

		<hr class="my-6" />

		<div class="text-sm text-muted-foreground mt-2 pb-6">
			Select {summaryUnits.count > 0 ? 'additional' : ''}
			{system === 'ADM' ? 'states / counties' : 'hydrologic units'} by clicking on them on the map or
			searching by name. You can then download data for all selected areas.
		</div>

		<Search
			{barrierType}
			{system}
			ignoreIds={summaryUnits.count > 0
				? new Set(summaryUnits.items.map(({ id: unitId }: SummaryUnit) => unitId))
				: null}
			onSelect={onSelectUnit}
		/>

		<hr />

		{#if barrierType === 'dams'}
			<div class="text-sm text-muted-foreground">
				Note: These statistics are based on inventoried dams. Because the inventory is incomplete in
				many areas, areas with a high number of dams may simply represent areas that have a more
				complete inventory.
				{#if stats.unrankedDams > 0}
					<br />
					<br />
					{formatNumber(stats.unrankedDams, 0)}
					{pluralize('dam', stats.unrankedDams)}
					{stats.unrankedDams === 1 ? 'was' : 'were'} not analyzed because
					{stats.unrankedDams === 1 ? 'it was' : 'they were'} not on the aquatic network or could not
					be correctly located on the network.
				{/if}
			</div>
		{:else if barrierType === 'small_barriers'}
			<div class="text-sm text-muted-foreground">
				Note: These statistics are based on surveyed crossings that have been assessed for impacts
				to aquatic organisms. Because the inventory is incomplete in many areas, areas with a high
				number of barriers may simply represent areas that have a more complete inventory.
				{#if stats.unrankedBarriers}
					{formatNumber(stats.unrankedBarriers, 0)} surveyed
					{pluralize('crossing', stats.unrankedBarriers)}
					{stats.unrankedBarriers === 1 ? 'was' : 'were'} not analyzed because
					{stats.unrankedBarriers === 1 ? 'it was' : 'they were'} not on the aquatic network or could
					not be correctly located on the network
				{/if}
			</div>
		{:else if barrierType === 'combined_barriers'}
			<div class="text-sm text-muted-foreground">
				Note: These statistics are based on inventoried dams and surveyed crossings that have been
				assessed for impacts to aquatic organisms. Because the inventory is incomplete in many
				areas, areas with a high number of barriers may simply represent areas that have a more
				complete inventory.
				{#if stats.unrankedDams > 0 || stats.unrankedBarriers > 0}
					<br />
					<br />
					{stats.unrankedDams > 0 ? `${formatNumber(stats.unrankedDams, 0)} dams` : null}
					{stats.unrankedDams > 0 && stats.unrankedBarriers > 0 ? ' and ' : null}
					{stats.unrankedBarriers > 0
						? `${formatNumber(stats.unrankedBarriers, 0)} surveyed crossings`
						: null}
					{stats.unrankedDams + stats.unrankedBarriers === 1 ? 'was' : 'were'} not analyzed because
					{stats.unrankedDams + stats.unrankedBarriers === 1 ? 'it was' : 'they were'}
					not on the aquatic network or could not be correctly located on the network
				{/if}
			</div>
		{/if}
	</div>

	<Footer
		class={cn('flex gap-4 items-center pt-4', { 'flex-wrap': barrierType === 'small_barriers' })}
	>
		<div class="leading-none flex-auto">Download:</div>
		<div
			class={cn('flex gap-4 justify-between flex-none', {
				'w-full': barrierType === 'small_barriers'
			})}
		>
			{#if barrierType === 'dams'}
				<Downloader
					barrierType="dams"
					label={`Download ${shortBarrierTypeLabels.dams}`}
					config={downloadConfig}
					disabled={stats.dams === 0}
					showOptions={false}
					includeUnranked
					triggerClass="text-sm h-auto py-1.5 px-2!"
				/>
			{:else if barrierType === 'small_barriers'}
				<Downloader
					barrierType="small_barriers"
					label={`Download ${shortBarrierTypeLabels.small_barriers}`}
					config={downloadConfig}
					disabled={stats.totalSmallBarriers === 0}
					showOptions={false}
					includeUnranked
					triggerClass="text-sm h-auto py-1.5 px-2!"
				/>

				<Downloader
					barrierType="road_crossings"
					label={`Download ${shortBarrierTypeLabels.road_crossings}`}
					config={{
						summaryUnits: summaryUnitsForDownload
					}}
					disabled={stats.totalRoadCrossings === 0}
					showOptions={false}
					includeUnranked
					triggerClass="text-sm h-auto py-1.5 px-2!"
				/>
			{:else if barrierType === 'combined_barriers'}
				<Downloader
					barrierType="combined_barriers"
					label={`Download ${shortBarrierTypeLabels.combined_barriers}`}
					config={downloadConfig}
					disabled={stats.dams + stats.totalSmallBarriers === 0}
					showOptions={false}
					includeUnranked
					triggerClass="text-sm h-auto py-1.5 px-2!"
				/>
			{/if}
		</div>
	</Footer>
</div>
