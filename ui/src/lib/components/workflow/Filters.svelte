<script lang="ts">
	import ResetIcon from '@lucide/svelte/icons/circle-x'
	import WarningIcon from '@lucide/svelte/icons/triangle-alert'
	import { op } from 'arquero'
	import type { RowObject } from 'arquero/dist/types/table/types'

	import { barrierTypeLabels } from '$lib/config/constants'
	import { Alert } from '$lib/components/alert'
	import { Button } from '$lib/components/ui/button'
	import { FilterGroup } from '$lib/components/filter'
	import { Header, Footer } from '$lib/components/sidebar'
	import { ExpandableParagraph } from '$lib/components/text'
	import { reduceToObject } from '$lib/util/data'
	import { formatNumber, pluralize } from '$lib/util/format'
	import { cn } from '$lib/utils'

	import BackButton from './BackButton.svelte'
	import StartOverButton from './StartOverButton.svelte'
	import NextButton from './NextButton.svelte'
	import type { BarrierTypePlural } from '$lib/config/types'

	const {
		networkType,
		title = null,
		crossfilter,
		maxAllowed = Infinity,
		nextStepLabel,
		onBack,
		onStartOver,
		onSubmit
	} = $props()

	const barrierTypeLabel = $derived(barrierTypeLabels[networkType as BarrierTypePlural])

	const countMessage = $derived.by(() => {
		// since filters are a deep object, we have to snapshot them here to detect change
		$state.snapshot(crossfilter.filters)

		switch (networkType) {
			case 'dams': {
				return `${formatNumber(crossfilter.filteredCount)} ${pluralize('dam', crossfilter.filteredCount)}`
			}
			case 'small_barriers': {
				return `${formatNumber(crossfilter.filteredCount)} surveyed road/stream ${pluralize('crossing', crossfilter.filteredCount)}`
			}
			case 'combined_barriers':
			case 'largefish_barriers':
			case 'smallfish_barriers': {
				// during transitions between views, crossfilter.data may be briefly null
				const { dams = 0, small_barriers: smallBarriers = 0 } = crossfilter.filteredData
					? crossfilter.filteredData
							.groupby('barriertype')
							.rollup({ _count: (d: RowObject) => op.sum(d._count) })
							.derive({ row: op.row_object() })
							.array('row')
							.reduce(...reduceToObject('barriertype', (d: RowObject) => d._count))
					: {}

				return `${formatNumber(dams || 0)} ${pluralize(
					'dam',
					dams
				)} and ${formatNumber(smallBarriers)} surveyed road/stream ${pluralize('crossing', smallBarriers)}`
			}
			case 'road_crossings': {
				return `${formatNumber(crossfilter.filteredCount)} road/stream ${pluralize('crossing', crossfilter.filteredCount)}`
			}
		}
	})

	const handleBack = () => {
		crossfilter.resetFilters()
		onBack()
	}

	const handleReset = () => {
		crossfilter.resetFilters()
	}
</script>

<div class="flex flex-col h-full">
	<Header class="pt-2 pb-1 px-4">
		<BackButton label="modify area of interest" onClick={handleBack} />

		<div class="flex justify-between items-baseline">
			<h2 class="flex-auto text-2xl leading-none">
				{title || `Filter ${barrierTypeLabel}`}
			</h2>

			<Button
				variant="link"
				class={cn(
					'p-0! flex-none items-center justify-end text-accent no-underline hover:no-underline leading-none',
					{ invisible: !crossfilter.hasFilters }
				)}
				onclick={handleReset}
			>
				<ResetIcon class="size-4" />
				reset filters
			</Button>
		</div>
	</Header>

	<div class="flex-auto px-4 pt-2 pb-4 overflow-y-auto overflow-x-hidden">
		<div class="text-muted-foreground text-xs">
			<ExpandableParagraph
				snippet={`[OPTIONAL] Use the filters below to select the ${barrierTypeLabel} that meet
        your needs. Click on a bar to select ${barrierTypeLabel} with that value.`}
			>
				[OPTIONAL] Use the filters below to select the {barrierTypeLabel}
				that meet your needs. Click on a bar to select {barrierTypeLabel}
				with that value. Click on the bar again to unselect. You can combine multiple values across multiple
				filters to select the
				{barrierTypeLabel} that match ANY of those values within a filter and also have the values selected
				across ALL filters.
			</ExpandableParagraph>
		</div>

		<div class="-mx-4 mt-2">
			{#each crossfilter.filterConfig.filter(({ id }: { id: string }) => !crossfilter.emptyGroups.has(id)) as group (group.id)}
				<FilterGroup {...group} {crossfilter} />
			{/each}
		</div>
	</div>

	<Footer class="pt-4">
		<div class="text-sm text-right mr-1 -mt-2 mb-3">
			selected: {countMessage}
		</div>

		{#if crossfilter.filteredCount > maxAllowed}
			<div class="mb-4">
				<Alert title="Too many barriers!">
					You have selected too many barriers for analysis. The limit is {formatNumber(maxAllowed)}.
					Please choose a smaller area of interest or filter your barriers of interest further.
				</Alert>
			</div>
		{:else if crossfilter.filteredCount === 0}
			<div class="mt-1 mb-3 text-xs flex gap-2">
				<WarningIcon class="size-4 flex-none" />
				No barriers selected. Please choose a different area of interest or adjust your filters to select
				barriers for analysis.
			</div>
		{/if}

		<div class="flex justify-between items-center gap-4">
			<StartOverButton {onStartOver} />

			<NextButton
				disabled={crossfilter.filteredCount === 0}
				label={nextStepLabel}
				onClick={onSubmit}
			/>
		</div>
	</Footer>
</div>
