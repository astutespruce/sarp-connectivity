<script lang="ts">
	import PriorityBarrierIcon from '@lucide/svelte/icons/map-plus'
	import RemovedBarrierIcon from '@lucide/svelte/icons/waves'
	import PlannedProjectIcon from '@lucide/svelte/icons/waves-arrow-up'

	import { barrierTypeLabelSingular, STATES } from '$lib/config/constants'
	import { formatNumber } from '$lib/util/format'

	const {
		barrierType,
		name,
		county,
		state,
		lat,
		lon,
		removed,
		yearremoved,
		plannedproject,
		yearsurveyed,
		resurveyed,
		ispriority,
		lowheaddam,
		diversion,
		invasive,
		estimated
	} = $props()

	const barrierTypeLabel = $derived.by(() => {
		let defaultLabel =
			barrierTypeLabelSingular[barrierType as keyof typeof barrierTypeLabelSingular]
		if (estimated) {
			defaultLabel = `estimated ${defaultLabel}`
		}

		const labelParts = []
		if (lowheaddam === 1) {
			labelParts.push('lowhead dam')
		} else if (lowheaddam === 2) {
			labelParts.push('likely lowhead dam')
		}
		if (diversion === 2) {
			labelParts.push('likely water diversion')
		} else if (diversion >= 1) {
			labelParts.push('water diversion')
		}

		if (labelParts.length === 0) {
			labelParts.push(defaultLabel)
		}

		if (invasive) {
			labelParts.push('invasive species barrier')
		}

		return labelParts.join(', ')
	})
</script>

<div class="leading-tight">
	<h1 class="font-bold text-xl sm:text-[1.75rem] leading-tight">{name}</h1>
	{#if removed}
		<div class="flex items-center gap-2 mt-1 mb-4">
			<RemovedBarrierIcon class="text-blue-8 size-5" />
			<div class="font-bold">
				Removed / mitigated
				{yearremoved !== null && yearremoved !== 0 ? `in ${yearremoved}` : `(year unknown)`}
			</div>
		</div>
	{:else if ispriority}
		<div class="flex items-center gap-2 mt-1 mb-4">
			<PriorityBarrierIcon class="text-blue-8 size-5" />
			<div class="font-bold">Identified as a priority by resource managers</div>
		</div>
	{:else if plannedproject}
		<div class="flex items-center gap-2 mt-1 mb-4">
			<PlannedProjectIcon class="text-blue-8 size-5" />
			<div class="font-bold">Planned for removal / mitigation</div>
		</div>
	{/if}

	<div class="flex flex-wrap text-muted-foreground justify-between gap-2 sm:gap-8 mt-2">
		<div class="flex-auto">
			Barrier type: {barrierTypeLabel}
		</div>

		{#if yearsurveyed !== 0}
			<div class="flex-none">
				Surveyed in {yearsurveyed}
				{resurveyed !== 0 ? ' (resurveyed)' : null}
			</div>
		{/if}
	</div>

	<div class="flex flex-wrap justify-between gap-2 sm:gap-8 mt-4 text-muted-foreground">
		<div class="flex-auto">
			{county} County, {STATES[state as keyof typeof STATES]}
		</div>
		<div class="flex-none">
			Located at {formatNumber(lat, 5)}
			&deg; N / {formatNumber(lon, 5)}
			&deg; E
		</div>
	</div>
</div>
