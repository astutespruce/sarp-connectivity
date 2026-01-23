<script lang="ts">
	import CloseIcon from '@lucide/svelte/icons/circle-x'
	import { resolve } from '$app/paths'

	import { Button } from '$lib/components/ui/button'
	import { STATE_FIPS, STATES } from '$lib/config/constants'
	import { formatNumber, pluralize } from '$lib/util/format'
	import { cn } from '$lib/utils'

	const { barrierType, system, unit, ignore, onDelete, onZoomBounds } = $props()

	const {
		id,
		layer,
		bbox = null,
		dams = 0,
		totalSmallBarriers = 0,
		unsurveyedRoadCrossings = 0
	} = $derived(unit)

	const name = $derived(layer === 'State' ? STATES[id as keyof typeof STATES] : unit.name)

	const { count, countMessage } = $derived.by(() => {
		const totalRoadBarriers = totalSmallBarriers + unsurveyedRoadCrossings

		switch (barrierType) {
			case 'dams': {
				return {
					count: dams,
					countMessage: `${formatNumber(dams)} ${pluralize('dam', dams)}`
				}
			}
			case 'small_barriers': {
				return {
					count: totalSmallBarriers,
					countMessage: `${formatNumber(totalSmallBarriers)} assessed road/stream ${pluralize(
						'crossing',
						totalSmallBarriers
					)} (out of ${formatNumber(totalRoadBarriers)} total ${pluralize(
						'crossing',
						totalRoadBarriers
					)})`
				}
			}
			case 'combined_barriers': {
				return {
					count: dams + totalSmallBarriers,
					countMessage: `${formatNumber(dams)} ${pluralize('dam', dams)} and ${formatNumber(
						totalSmallBarriers
					)} assessed road/stream ${pluralize(
						'crossing',
						totalSmallBarriers
					)} (out of ${formatNumber(totalRoadBarriers)} total ${pluralize(
						'crossing',
						totalRoadBarriers
					)})`
				}
			}
		}
	}) as { count: number; countMessage: string }
</script>

<li
	class="gird grid-cols-[1fr_3.5fr] gap-4 -mx-4 px-4 py-2 not-first-of-type:border-t not-first-of-type:border-t-grey-1 last-of-type:border-b last-of-type:border-b-grey-1"
>
	<div>
		<div
			class={cn('text-sm', {
				'font-bold': count > 0 && !ignore,
				'italic text-muted-foreground': count === 0 || ignore
			})}
		>
			{name}

			{#if layer === 'State'}
				<span class="font-normal text-xs text-muted-foreground">
					(
					<a href={resolve(`/states/${id}`, { id })}> view state details </a>
					)</span
				>
			{:else if layer === 'County'}
				, {STATE_FIPS[id.slice(0, 2) as keyof typeof STATE_FIPS]}
			{/if}
		</div>

		{#if system === 'HUC'}
			<div class={cn('text-xs', { 'italic text-muted-foreground': count === 0 })}>
				{layer}: {id}
			</div>
		{/if}

		<div class="text xs text-muted-foreground">
			{countMessage}
			{#if ignore}
				(already counted in larger selected area)
			{/if}
		</div>
	</div>

	<div class="flex flex-col justify-between items-end h-full">
		<Button
			variant="ghost"
			onclick={() => onDelete(unit)}
			class="p-0 flex-none"
			aria-label={`remove ${name} from list`}
		>
			<CloseIcon class="size-4" />
		</Button>

		{#if bbox}
			<Button
				variant="link"
				onclick={() => onZoomBounds(bbox)}
				class="p-0 text-xs"
				aria-label={`zoom to ${name} on the map`}
			>
				zoom to
			</Button>
		{/if}
	</div>
</li>
