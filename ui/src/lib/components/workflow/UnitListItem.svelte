<script lang="ts">
	import CloseIcon from '@lucide/svelte/icons/circle-x'
	import WarningIcon from '@lucide/svelte/icons/triangle-alert'

	import { STATE_FIPS, STATES, barrierTypeLabels } from '$lib/config/constants'
	import { Button } from '$lib/components/ui/button'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { formatNumber, pluralize } from '$lib/util/format'
	import { cn } from '$lib/utils'

	const { barrierType, layer, unit, onDelete, onZoomBounds } = $props()

	const {
		id,
		bbox = null,
		rankedDams = 0,
		totalSmallBarriers = 0,
		rankedSmallBarriers = 0,
		rankedLargefishBarriersDams = 0,
		rankedLargefishBarriersSmallBarriers = 0,
		rankedSmallfishBarriersDams = 0,
		rankedSmallfishBarriersSmallBarriers = 0,
		totalRoadCrossings = 0,
		unsurveyedRoadCrossings = 0
	} = $derived(unit)

	const name = $derived.by(() => {
		if (layer === 'State') {
			return STATES[id as keyof typeof STATES]
		}
		if (layer === 'County') {
			return `${unit.name}, ${STATE_FIPS[id.slice(0, 2) as keyof typeof STATE_FIPS]}`
		}

		return unit.name || id
	})

	const totalRoadBarriers = $derived(totalSmallBarriers + unsurveyedRoadCrossings)
	const insufficientBarriers = $derived(totalSmallBarriers < 10 && totalRoadBarriers > 10)

	const {
		count = 0,
		warning = null,
		countMessage = null
	} = $derived.by(() => {
		switch (barrierType) {
			case 'dams': {
				if (rankedDams === 0) {
					return {
						count: rankedDams,
						warning: 'no dams available for prioritization'
					}
				}
				return {
					count: rankedDams,
					countMessage: `${formatNumber(rankedDams)} ${pluralize('dam', rankedDams)}`
				}
			}
			case 'small_barriers': {
				if (totalSmallBarriers === 0) {
					return {
						count: totalSmallBarriers,
						warning: `no road/stream crossings have been surveyed in this area (${formatNumber(
							totalRoadBarriers
						)} road/stream ${pluralize('crossing', totalRoadBarriers)})`
					}
				} else if (rankedSmallBarriers === 0) {
					return {
						count: totalSmallBarriers,
						warning: `no surveyed road/stream crossings available for prioritization (${formatNumber(
							totalRoadBarriers
						)} road/stream ${pluralize('crossing', totalRoadBarriers)})`
					}
				} else if (insufficientBarriers) {
					const prefix =
						totalSmallBarriers === 0
							? 'no road/stream crossings'
							: `${formatNumber(totalSmallBarriers)} road/stream ${pluralize(
									'crossing',
									totalSmallBarriers
								)} (${formatNumber(rankedSmallBarriers)} likely ${pluralize(
									'barrier',
									rankedSmallBarriers
								)})`

					return {
						count: totalSmallBarriers,
						warning: `${prefix} ${
							rankedSmallBarriers === 1 ? 'has' : 'have'
						} been surveyed out of ${formatNumber(totalRoadBarriers)} total road/stream ${pluralize(
							'crossing',
							totalRoadBarriers
						)}; this may not result in useful priorities`
					}
				}
				return {
					count: totalSmallBarriers,
					countMessage: `${formatNumber(rankedSmallBarriers)} ${pluralize(
						'barrier',
						rankedSmallBarriers
					)} (${formatNumber(totalSmallBarriers)} surveyed road/stream ${pluralize(
						'crossing',
						totalSmallBarriers
					)} of ${formatNumber(totalRoadBarriers)} total road/stream ${pluralize(
						'crossing',
						totalRoadBarriers
					)})`
				}
			}
			case 'combined_barriers':
			case 'largefish_barriers':
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

				const rankedCount = rankedD + rankedSB

				if (rankedCount === 0) {
					return {
						count: rankedCount,
						warning: `no ${barrierTypeLabels[barrierType as BarrierTypePlural]} available for prioritization`
					}
				} else if (rankedD > 0 && insufficientBarriers) {
					const prefix =
						totalSmallBarriers === 0
							? 'no surveyed road/stream crossings'
							: `${formatNumber(totalSmallBarriers)} surveyed road/stream ${pluralize(
									'crossing',
									totalSmallBarriers
								)} (${formatNumber(rankedSB)} likely ${pluralize('barrier', rankedSB)})`
					return {
						count: rankedCount,
						warning: `${prefix} ${
							totalSmallBarriers === 1 ? 'has' : 'have'
						} been surveyed out of ${formatNumber(totalRoadBarriers)} total road/stream ${pluralize(
							'crossing',
							totalRoadBarriers
						)}; this may not result in useful priorities`,

						countMessage: `${formatNumber(rankedD)} ${pluralize('dam', rankedD)}`
					}
				} else if (rankedD > 0) {
					return {
						count: rankedCount,
						countMessage: `${formatNumber(rankedD)} ${pluralize(
							'dam',
							rankedDams
						)} and ${formatNumber(rankedSB)} surveyed road/stream ${pluralize(
							'barrier',
							rankedSB
						)} (${formatNumber(totalSmallBarriers)} surveyed road/stream ${pluralize(
							'crossing',
							totalSmallBarriers
						)} of ${formatNumber(totalRoadBarriers)} total road/stream ${pluralize(
							'crossing',
							totalRoadBarriers
						)})`
					}
				}

				break
			}
			case 'road_crossings': {
				if (totalRoadCrossings === 0) {
					return {
						count: totalRoadCrossings,
						warning: `no road/stream crossings have been mapped in this area`
					}
				}
				return {
					count: totalRoadCrossings,
					countMessage: `${formatNumber(totalRoadCrossings)} road/stream ${pluralize(
						'crossing',
						totalRoadCrossings
					)} (${formatNumber(
						unsurveyedRoadCrossings
					)} have not yet been surveyed; ${formatNumber(totalSmallBarriers)} surveyed ${pluralize('crossing', totalSmallBarriers)} have been surveyed)`
				}
			}
		}
		return {}
	})
</script>

<li
	class="grid grid-cols-[1fr_3.5rem] gap-2 border-b border-b-grey-1 -mx-4 px-4 py-2 first-of-type:border-t first-of-type:border-t-grey-1"
>
	<div>
		<div
			class={cn('text-base', {
				'font-bold': count > 0,
				'italic text-muted-foreground': count === 0
			})}
		>
			{name}
		</div>

		{#if layer.startsWith('HUC')}
			<div
				class={cn('text-xs', {
					'italic text-muted-foreground': count === 0
				})}
			>
				{layer}: {id}
			</div>
		{/if}

		{#if countMessage}
			<div class="text-xs text-muted-foreground mt-1">
				{countMessage}
			</div>
		{/if}

		{#if warning}
			<div class="flex mt-1 text-destructive text-sm gap-2 leading-tight">
				<WarningIcon class="size-4 flex-none" />
				<div class="flex-auto">
					{warning}
				</div>
			</div>
		{/if}
	</div>
	<div class="flex flex-none flex-col gap-2 items-end">
		<Button variant="close" onclick={() => onDelete(unit)} aria-label={`remove ${name} from list`}
			><CloseIcon class="size-5" />
		</Button>

		{#if bbox}
			<Button
				variant="link"
				class="text-right p-0! h-auto flex-none text-xs no-underline hover:no-underline"
				onclick={() => onZoomBounds(bbox)}
			>
				zoom to
			</Button>
		{/if}
	</div>
</li>
