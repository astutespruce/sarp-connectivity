<script lang="ts">
	import ChevronsRightIcon from '@lucide/svelte/icons/chevrons-right'
	import CloseIcon from '@lucide/svelte/icons/circle-x'
	import { SvelteSet as Set } from 'svelte/reactivity'

	import { resolve } from '$app/paths'
	import { Button } from '$lib/components/ui/button'
	import { STATE_FIPS, STATES, barrierTypeLabels } from '$lib/config/constants'
	import { formatNumber, pluralize, singularOrPlural } from '$lib/util/format'
	import { Downloader } from '$lib/components/download'
	import { layers } from '$lib/components/explore/layers'
	import { Search } from '$lib/components/unitsearch'
	import { cn } from '$lib/utils'

	import ListItem from './UnitListItem.svelte'

	type SummaryUnit = {
		id: string
		layer: string
	}

	const { barrierType, system, summaryUnits, onSelectUnit, onReset, onZoomBounds } = $props()

	const [{ id, name = '', layer }] = $derived(summaryUnits)
	const {
		title = null,
		subtitle = null,
		idline = null,
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
					return { title: name, idline: `${layer}: ${id}` }
				}
				default: {
					// all remaining HUC cases
					const [{ title: layerTitle }] = layers.filter(({ id: lyrID }) => lyrID === layer)
					return {
						title: name,
						subtitle: layerTitle,
						idline: `${layer}: ${id}`
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

		summaryUnits
			.filter(({ id: i }) => !ignoreIds.has(i))
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
		if (summaryUnits.length !== 1) return
		onZoomBounds(summaryUnits[0].bbox)
	}

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
</script>

<div class="flex flex-col h-full">
	<div
		class="flex py-4 pl-4 pr-2 justify-center items-start border-b border-b-grey-4 bg-grey-0 leading-tight"
	>
		<div class="flex flex-auto">
			<h2>
				{title}
				{#if subtitle}
					<div class="font-normal">{subtitle}</div>
				{/if}
			</h2>
			{#if idline}
				<div class="text-muted-foreground">
					{idline}
				</div>
			{/if}
		</div>

		<div class="flex flex-none flex-col justify-between items-end h-full">
			<Button onclick={onReset} aria-label={`unselect ${title}`}>
				<CloseIcon class="size-5" />
			</Button>
			{#if summaryUnits.length === 1 && summaryUnits[0].bbox}
				<Button
					variant="link"
					class="text-sm"
					onclick={handleZoomBounds}
					aria-label={`zoom to ${title} on the map`}>zoom to</Button
				>
			{/if}
		</div>
	</div>

	<div
		bind:this={contentNode}
		class="p-4 flex-auto h-full overflow-y-auto [&_ul]:list-outside [&_ul]:list-disc [&_ul]:pl-4"
	>
		{#if summaryUnits.length === 1 && layer === 'State'}
			<a href={resolve(`/states/${id}`, { id })} class="block">
				view state page for more information
				<ChevronsRightIcon class="size-5" />
			</a>
		{/if}

		<p>
			{singularOrPlural('This area contains', 'These areas contain', summaryUnits.length)}:
		</p>

		{#if barrierType === 'dams' || barrierType === 'combined_barriers'}
			{#if stats.dams > 0}
				<p>
					<b>{stats.dams}</b> inventoried {pluralize('dam', stats.dams)} including:
				</p>
				<ul class="mt-2">
					<li>
						<b>{formatNumber(stats.rankedDams, 0)}</b> that
						{stats.rankedDams === 1 ? 'was ' : 'were '} analyzed for impacts to aquatic connectivity in
						this tool
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
				<p class="mt-2">
					<b>0</b> inventoried dams
				</p>
			{/if}
		{/if}

		{#if barrierType === 'small_barriers' || barrierType === 'combined_barriers'}
			{#if stats.totalRoadBarriers > 0}
				<p class={cn('mt-2', { 'mt-6': barrierType === 'combined_barriers' })}>
					<b>{formatNumber(stats.totalRoadBarriers, 0)}</b> or more road/stream crossings (potential aquatic
					barriers), including:
				</p>
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
				<p class="mt-2">
					<b>{formatNumber(stats.unsurveyedRoadCrossings, 0)}</b> that have not yet been surveyed
				</p>
			{/if}
		{/if}

		{#if summaryUnits.length > 1}
			<div
				class="mt-8 mb-2 -mx-4 px-4 py-1 bg-grey-0 border-t border-t-grey-2 border-b border-b-grey-2"
			>
				<b>Selected areas:</b>
				<ul class="pl-0 list-none">
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
			</div>
		{/if}

		<div
			class={cn('-mx-4 px-4  border-b-2 border-b-grey-2', {
				'mt-8 border-t-2 border-t-grey-2': summaryUnits.length === 1
			})}
		>
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
		</div>

		{#if barrierType === 'dams'}
			<div class="text-sm text-muted-foreground">
				Note: These statistics are based on <i>inventoried</i> dams. Because the inventory is
				incomplete in many areas, areas with a high number of dams may simply represent areas that
				have a more complete inventory.
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
				Note: These statistics are based on <i>inventoried</i> road-related barriers that have been
				assessed for impacts to aquatic organisms. Because the inventory is incomplete in many
				areas, areas with a high number of barriers may simply represent areas that have a more
				complete inventory.
				{#if stats.unrankedBarriers}
					{formatNumber(stats.unrankedBarriers, 0)} road-related
					{pluralize('barrier', stats.unrankedBarriers)}
					{stats.unrankedBarriers === 1 ? 'was' : 'were'} not analyzed because
					{stats.unrankedBarriers === 1 ? 'it was' : 'they were'} not on the aquatic network or could
					not be correctly located on the network
				{/if}
			</div>
		{:else if barrierType === 'combined_barriers'}
			<div class="text-sm text-muted-foreground">
				Note: These statistics are based on <i>inventoried</i> dams and road-related barriers that
				have been assessed for impacts to aquatic organisms. Because the inventory is incomplete in
				many areas, areas with a high number of barriers may simply represent areas that have a more
				complete inventory.
				{#if stats.unrankedDams > 0 || stats.unrankedBarriers > 0}
					<br />
					<br />
					{stats.unrankedDams > 0 ? `${formatNumber(stats.unrankedDams, 0)} dams` : null}
					{stats.unrankedDams > 0 && stats.unrankedBarriers > 0 ? ' and ' : null}
					{stats.unrankedBarriers > 0
						? `${formatNumber(stats.unrankedBarriers, 0)} road-related barriers`
						: null}
					{stats.unrankedDams + stats.unrankedBarriers === 1 ? 'was' : 'were'} not analyzed because
					{stats.unrankedDams + stats.unrankedBarriers === 1 ? 'it was' : 'they were'}
					not on the aquatic network or could not be correctly located on the network
				{/if}
			</div>
		{/if}
	</div>

	<div
		class={cn(
			'flex gap-4 items-center flex-none pt-2 px-1 pb-1 border-t border-t-grey-4 bg-grey-0',
			{ 'flex-wrap': barrierType === 'small_barriers' }
		)}
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
					label={barrierTypeLabels.dams}
					config={downloadConfig}
					disabled={stats.dams === 0}
					showOptions={false}
					includeUnranked
				/>
			{:else if barrierType === 'small_barriers'}
				<Downloader
					barrierType="small_barriers"
					label={barrierTypeLabels.small_barriers}
					config={downloadConfig}
					disabled={stats.totalSmallBarriers === 0}
					showOptions={false}
					includeUnranked
				/>

				<Downloader
					barrierType="road_crossings"
					label={barrierTypeLabels.road_crossings}
					config={{
						summaryUnits: summaryUnitsForDownload
					}}
					disabled={stats.totalRoadCrossings === 0}
					showOptions={false}
					includeUnranked
				/>
			{:else if barrierType === 'combined_barriers'}
				<Downloader
					barrierType="combined_barriers"
					label={barrierTypeLabels.combined_barriers}
					config={downloadConfig}
					disabled={stats.dams + stats.totalSmallBarriers === 0}
					showOptions={false}
					includeUnranked
				/>
			{/if}
		</div>
	</div>
</div>
