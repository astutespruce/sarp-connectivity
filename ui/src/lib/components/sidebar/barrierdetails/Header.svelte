<script lang="ts">
	import PriorityBarrierIcon from '@lucide/svelte/icons/map-plus'
	import RemovedBarrierIcon from '@lucide/svelte/icons/waves'
	import SurveyedIcon from '@lucide/svelte/icons/drafting-compass'
	import CloseIcon from '@lucide/svelte/icons/circle-x'
	import ReportIcon from '@lucide/svelte/icons/file-input'

	import { resolve } from '$app/paths'
	import { Button } from '$lib/components/ui/button'
	import { STATES } from '$lib/config/constants'
	import { formatNumber } from '$lib/util/format'

	import { isEmptyString } from '$lib/util/string'

	const {
		barrierType,
		networkType,
		sarpid,
		name,
		county,
		state,
		lat,
		lon,
		removed,
		yearremoved,
		isPriority,
		isSurveyed,
		onClose
	} = $props()
</script>

<div class="py-2 px-2 border-b-4 border-b-blue-2">
	<div class="flex justify-between">
		<div class="flex-auto">
			<div class="text-lg font-bold">
				{name}
			</div>
			{#if removed}
				<div class="flex mt-1 gap-2 items-center">
					<RemovedBarrierIcon class="text-blue-8 size-5" />
				</div>
				{#if yearremoved && yearremoved !== 0}
					<div class="text-sm font-bold">Removed / mitigated in {yearremoved}</div>
				{:else}
					<div class="font-bold font-sm">
						Removed / mitigated
						<span class="text-xs font-normal">(year unknown)</span>
					</div>
				{/if}
			{:else if isPriority}
				<div class="flex items-center gap-2 mt-1">
					<PriorityBarrierIcon class="text-blue-8 size-5" />
					<div class="font-bold">Identified as a priority by resource managers</div>
				</div>
			{/if}

			{#if isSurveyed}
				<div class="flex items-center mt-1 gap-2">
					<SurveyedIcon class="size-5" />
					<div class="font-bold text-sm">
						Likely surveyed
						<span class="text-xs font-normal"> (close to a surveyed barrier) </span>
					</div>
				</div>
			{/if}
		</div>
		<Button
			variant="ghost"
			onclick={onClose}
			class="p-0 flex-none"
			aria-label="close barrier details"><CloseIcon class="size-5" /></Button
		>
	</div>

	<div class="flex text-muted-foreground text-sm">
		<div class="flex-auto">
			{!isEmptyString(state) ? `${county} County, ${STATES[state as keyof typeof STATES]}` : ''}
		</div>
		<div class="flex-none text-right">
			{formatNumber(lat, 3)}
			&deg; N, {formatNumber(lon, 3)}
			&deg; E
		</div>
	</div>

	{#if barrierType === 'dams' || barrierType === 'small_barriers'}
		<a
			href={resolve(
				`/report/${networkType === 'small_barriers' ? 'combined_barriers' : networkType}/${sarpid}`,
				{ id: sarpid }
			)}
			target="_blank"
			class="block mt-6"
		>
			<div class="flex items-baseline">
				<ReportIcon class="size-5" />
				<div>Create PDF report</div>
			</div>
		</a>
	{/if}
</div>
