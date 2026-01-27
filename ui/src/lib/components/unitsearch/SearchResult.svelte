<script lang="ts">
	import WarningIcon from '@lucide/svelte/icons/triangle-alert'

	import { STATES, barrierTypeLabels } from '$lib/config/constants'
	import { formatNumber, pluralize, singularOrPlural } from '$lib/util/format'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { Button } from '$lib/components/ui/button'
	import { cn } from '$lib/utils'

	const {
		barrierType,
		id,
		name,
		state: stateId = '',
		layer = '',
		rankedDams = 0,
		totalSmallBarriers = 0,
		rankedSmallBarriers = 0,
		rankedLargefishBarriersDams = 0,
		rankedLargefishBarriersSmallBarriers = 0,
		rankedSmallfishBarriersDams = 0,
		rankedSmallfishBarriersSmallBarriers = 0,
		totalRoadCrossings = 0,
		unsurveyedRoadCrossings = 0,
		showID = false,
		showCount = false,
		disabled = false,
		focused = false,
		onClick
	} = $props()

	const { warning, countMessage } = $derived.by(() => {
		if (!showCount || disabled) {
			return { warning: null, countMessage: null }
		}

		const totalRoadBarriers = totalSmallBarriers + unsurveyedRoadCrossings
		const insufficientBarriers = totalSmallBarriers < 10 && unsurveyedRoadCrossings > 10
		let outWarning = null
		let outCountMessage = null

		switch (barrierType) {
			case 'dams': {
				return {
					warning: rankedDams === 0 ? 'no dams available for prioritization' : null,
					countMessage:
						rankedDams > 0 ? `${formatNumber(rankedDams)} ${pluralize('dam', rankedDams)}` : null
				}
			}

			case 'small_barriers': {
				if (totalSmallBarriers === 0) {
					outWarning = `no road/stream crossings have been assessed in this area (${formatNumber(
						totalRoadBarriers
					)} road / stream ${pluralize('crossing', totalRoadBarriers)})`
				} else if (rankedSmallBarriers === 0) {
					outWarning = `no road-related barriers available for prioritization (${formatNumber(
						totalRoadBarriers
					)} road / stream ${pluralize('crossing', totalRoadBarriers)})`
				} else if (insufficientBarriers) {
					const prefix =
						totalSmallBarriers === 0
							? 'no assessed road/stream crossings'
							: `${formatNumber(totalSmallBarriers)} assessed road/stream ${pluralize(
									'crossing',
									totalSmallBarriers
								)} (${formatNumber(rankedSmallBarriers)} likely ${pluralize(
									'barrier',
									rankedSmallBarriers
								)})`

					outWarning = `${prefix} ${singularOrPlural(
						'has',
						'have',
						rankedSmallBarriers
					)} been assessed out of ${formatNumber(
						totalRoadBarriers
					)} total road / stream ${pluralize(
						'crossing',
						totalRoadBarriers
					)}; this may not result in useful priorities`
				} else {
					outCountMessage = `${formatNumber(rankedSmallBarriers)} ${pluralize(
						'barrier',
						rankedSmallBarriers
					)} (${formatNumber(totalSmallBarriers)} assessed road/stream ${pluralize(
						'crossing',
						totalSmallBarriers
					)} of ${formatNumber(totalRoadBarriers)} total road/stream ${pluralize(
						'crossing',
						totalRoadBarriers
					)})`
				}

				return {
					warning: outWarning,
					countMessage: outCountMessage
				}
			}

			case 'combined_barriers':
			case 'largefish_barrhers':
			case 'smallfish_barriers': {
				// extract counts specific to network type
				let rankedD = 0
				let rankedSB = 0
				if (barrierType === 'combined_barriers') {
					rankedD = rankedDams
					rankedSB = rankedSmallBarriers
				} else if (barrierType === 'largefish_barriers') {
					rankedD = rankedLargefishBarriersDams
					rankedSB = rankedLargefishBarriersSmallBarriers
				} else if (barrierType === 'smallfish_barriers') {
					rankedD = rankedSmallfishBarriersDams
					rankedSB = rankedSmallfishBarriersSmallBarriers
				}

				if (rankedD + rankedSB === 0) {
					outWarning = `no ${barrierTypeLabels[barrierType as BarrierTypePlural]} available for prioritization`
				} else if (rankedD > 0 && insufficientBarriers) {
					const prefix =
						totalSmallBarriers === 0
							? 'no assessed road/stream crossings'
							: `${formatNumber(totalSmallBarriers)} assessed road/stream ${pluralize(
									'crossing',
									totalSmallBarriers
								)} (${formatNumber(rankedSB)} likely ${pluralize('barrier', rankedSB)})`
					outWarning = `${prefix} ${singularOrPlural(
						'has',
						'have',
						totalSmallBarriers
					)} been assessed out of ${formatNumber(
						totalRoadBarriers
					)} total road / stream ${pluralize(
						'crossing',
						totalRoadBarriers
					)}; this may not result in useful priorities`

					outCountMessage = `${formatNumber(rankedD)} ${pluralize('dam', rankedD)}`
				} else if (rankedD > 0) {
					outCountMessage = `${formatNumber(rankedD)} ${pluralize(
						'dam',
						rankedD
					)} and ${formatNumber(rankedSB)} ${pluralize('likely barrier', rankedSB)} (${formatNumber(
						totalSmallBarriers
					)} assessed road/stream ${pluralize(
						'crossing',
						totalSmallBarriers
					)} of ${formatNumber(totalRoadBarriers)} road/stream ${pluralize(
						'crossing',
						totalRoadBarriers
					)})`
				}

				return { warning: outWarning, countMessage: outCountMessage }
			}

			case 'road_crossings': {
				return {
					warning:
						totalRoadCrossings === 0
							? `no road/stream crossings have been mapped in this area`
							: null,
					countMessage:
						totalRoadCrossings > 0
							? `${formatNumber(totalRoadCrossings)} total road/stream ${pluralize(
									'crossing',
									totalRoadCrossings
								)}`
							: null
				}
			}
		}
	}) as {
		warning: string | null
		countMessage: string | null
	}

	let node: HTMLButtonElement | null = $state(null)

	$effect(() => {
		if (node && focused) {
			node.focus()
		}
	})
</script>

<Button
	bind:ref={node}
	variant="ghost"
	{disabled}
	onclick={onClick}
	class={cn('block text-left h-auto m-0 p-1 w-full rounded-none', {
		'hover:bg-grey-0': !disabled,
		'italic text-muted-foreground': disabled
	})}
>
	<div class={cn({ 'font-bold': !disabled })}>
		{name}

		{#if stateId && layer !== 'CongressionalDistrict'}
			<span class="text-sm"
				>({stateId
					.split(',')
					.map((s: string) => STATES[s as keyof typeof STATES])
					.sort()
					.join(', ')})</span
			>
		{/if}

		{#if disabled}
			<span class="text-xs"> (already selected) </span>
		{/if}
	</div>

	{#if showID}
		<div class="text-xs text-muted-foreground whitespace-nowrap text-nowrap">
			{#if layer}
				{layer}:
			{/if}
			{id}
		</div>
	{/if}

	{#if countMessage}
		<div class="text-xs text-muted-foreground">
			{countMessage}
		</div>
	{/if}

	{#if warning}
		<div class="mt-1 text-accent">
			<WarningIcon class="size-4 flex-none inline mr-1" />
			<div class="flex-auto">
				{warning}
			</div>
		</div>
	{/if}
</Button>
