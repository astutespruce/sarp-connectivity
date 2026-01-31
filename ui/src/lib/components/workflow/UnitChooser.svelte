<script lang="ts">
	import { barrierTypeLabels } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { Search } from '$lib/components/unitsearch'
	import { Header, Footer } from '$lib/components/sidebar'
	import { formatNumber, pluralize } from '$lib/util/format'

	import BackButton from './BackButton.svelte'
	import StartOverButton from './StartOverButton.svelte'
	import NextButton from './NextButton.svelte'
	import ListItem from './UnitListItem.svelte'
	import type { SummaryUnit } from './types'

	const {
		networkType,
		layer,
		summaryUnits,
		onSelectUnit,
		onBack,
		onSubmit,
		onStartOver,
		onZoomBounds
	} = $props()

	const barrierTypeLabel = $derived(barrierTypeLabels[networkType as BarrierTypePlural])

	const pluralUnitsLabel = $derived.by(() => {
		switch (layer) {
			case 'State':
				return 'states'
			case 'County':
				return 'counties'
			case 'CongressionalDistrict':
				return 'congressional districts'
			case 'HUC6':
				return 'basins'
			case 'HUC8':
				return 'subbasins'
			case 'HUC10':
				return 'watersheds'
			case 'HUC12':
				return 'subwatersheds'
			default:
				return 'areas'
		}
	})

	const {
		total = 0,
		countMessage = null,
		offNetworkCount = 0
	} = $derived.by(() => {
		if (summaryUnits.length > 0) {
			switch (networkType) {
				case 'dams': {
					const numDams = summaryUnits.reduce(
						(out: number, v: SummaryUnit) => out + v.rankedDams,
						0
					)
					return {
						offNetworkCount: summaryUnits.reduce(
							(out: number, v: SummaryUnit) => out + (v.dams - v.rankedDams),
							0
						),
						total: numDams,
						countMessage: `${formatNumber(numDams)} ${pluralize('dam', numDams)}`
					}
				}
				case 'small_barriers': {
					const numBarriers = summaryUnits.reduce(
						(out: number, v: SummaryUnit) => out + v.rankedSmallBarriers,
						0
					)
					return {
						offNetworkCount: summaryUnits.reduce(
							(out: number, v: SummaryUnit) => out + (v.smallBarriers - v.rankedSmallBarriers),
							0
						),
						total: numBarriers,
						countMessage: `${formatNumber(numBarriers)} surveyed ${pluralize('crossing', numBarriers)}`
					}
				}
				case 'combined_barriers':
				case 'largefish_barriers':
				case 'smallfish_barriers': {
					let damField = null
					let smallBarrierField = null
					if (networkType === 'combined_barriers') {
						damField = 'rankedDams'
						smallBarrierField = 'rankedSmallBarriers'
					} else if (networkType === 'largefish_barriers') {
						damField = 'rankedLargefishBarriersDams'
						smallBarrierField = 'rankedLargefishBarriersSmallBarriers'
					} else if (networkType === 'smallfish_barriers') {
						damField = 'rankedSmallfishBarriersDams'
						smallBarrierField = 'rankedSmallfishBarriersSmallBarriers'
					}

					let dams = 0
					let smallBarriers = 0

					summaryUnits.forEach(
						// @ts-expect-error damField, smallBarrierField are valid
						({ [damField]: damCount = 0, [smallBarrierField]: smallBarrierCount = 0 }) => {
							dams += damCount
							smallBarriers += smallBarrierCount
						}
					)
					let numBarriers = dams + smallBarriers

					return {
						total: numBarriers,
						countMessage: `${formatNumber(dams)} ${pluralize(
							'dam',
							dams
						)} and ${formatNumber(smallBarriers)} road-related ${pluralize(
							'barrier',
							smallBarriers
						)}`,
						// always use plain ranked barriers vs count to determine off-network values
						offNetworkCount: summaryUnits.reduce(
							(out: number, v: SummaryUnit) =>
								out + (v.dams - v.rankedDams) + (v.smallBarriers - v.rankedSmallBarriers),
							0
						)
					}
				}
				case 'road_crossings': {
					let numCrossings = summaryUnits.reduce(
						(out: number, v: SummaryUnit) => out + v.totalRoadCrossings,
						0
					)
					return {
						offNetworkCount: 0,
						total: numCrossings,
						countMessage: `${formatNumber(numCrossings)} road/stream ${pluralize('crossing', numCrossings)}`
					}
				}
			}
		}

		return {}
	})

	$inspect('summaryUnits', summaryUnits).with(console.log)
</script>

<div class="flex flex-col h-full pb-8">
	<Header class="pt-2 pb-3 px-4">
		<BackButton label="choose a different type of area" onClick={onBack} />
		<h2 class="text-2xl">
			Choose {pluralUnitsLabel}
		</h2>
	</Header>

	<div class="flex-auto p-4 overflow-y-auto overflow-x-hidden">
		<div class="text-muted-foreground text-sm">
			Select {summaryUnits.length > 0 ? 'additional' : ''}
			{pluralUnitsLabel} by clicking on them on the map or using the search below.
		</div>

		{#if summaryUnits.length}
			<h3 class="font-bold mt-8 text-lg">
				Selected {pluralUnitsLabel}:
			</h3>
			<ul class="list-none pl-0!">
				{#each summaryUnits as unit (unit.id)}
					<ListItem
						barrierType={networkType}
						{layer}
						{unit}
						onDelete={onSelectUnit}
						{onZoomBounds}
					/>
				{/each}
			</ul>
		{/if}

		<Search
			barrierType={networkType}
			{layer}
			ignoreIds={summaryUnits && summaryUnits.length > 0
				? new Set(summaryUnits.map(({ id }: SummaryUnit) => id))
				: null}
			showCount
			minQueryLength={layer === 'StateWRA' ? 1 : 3}
			onSelect={onSelectUnit}
			class="mt-8"
		/>

		{#if summaryUnits.length > 0 && offNetworkCount > 0}
			<div class="text-muted-foreground mt-8 pb-8 text-sm">
				Note: only {barrierTypeLabel} that have been evaluated for aquatic network connectivity are available
				for prioritization. There are
				<b>{formatNumber(offNetworkCount, 0)}</b>
				{barrierTypeLabel} not available for prioritization in your selected area.
			</div>
		{/if}
	</div>
</div>

<Footer class="pt-4">
	{#if countMessage}
		<div class="text-sm text-right mr-1 -mt-2 mb-3">
			selected: {countMessage}
		</div>
	{/if}
	<div class="flex items-center justify-between">
		<StartOverButton {onStartOver} />
		<NextButton
			disabled={summaryUnits.size === 0 || total === 0}
			onClick={onSubmit}
			label="Configure filters"
			title={summaryUnits.size === 0 || total === 0
				? `you must select at least one area that has ${barrierTypeLabel} available`
				: null}
		/>
	</div>
</Footer>
