<script lang="ts">
	import { formatNumber, pluralize } from '$lib/util/format'

	const {
		barrierType,
		milestooutlet,
		totaldownstreamdams,
		totaldownstreamsmallbarriers,
		totaldownstreamwaterfalls
	} = $props()

	const numCols = $derived(
		1 +
			Number(totaldownstreamdams >= 0) +
			Number(barrierType === 'small_barriers' && totaldownstreamsmallbarriers >= 0) +
			Number(totaldownstreamwaterfalls >= 0)
	)
</script>

<section>
	<h2>Marine connectivity</h2>

	<div
		class={`grid sm:grid-cols-${numCols} gap-4 mt-4 leading-snug sm:[&>div]:py-2 sm:[&>div+div]:border-l sm:[&>div+div]:border-l-grey-2 sm:[&>div+div]:pl-4`}
	>
		<div>
			<b>{formatNumber(milestooutlet)}</b>
			{pluralize('mile', milestooutlet)} downstream to the ocean
		</div>

		{#if totaldownstreamdams >= 0}
			<div>
				<b>{formatNumber(totaldownstreamdams)}</b>
				{pluralize('dam', totaldownstreamdams)} downstream
			</div>
		{/if}

		{#if barrierType === 'small_barriers' && totaldownstreamsmallbarriers >= 0}
			<div>
				<b>{formatNumber(totaldownstreamsmallbarriers)}</b> surveyed road/stream crossings {pluralize(
					'barrier',
					totaldownstreamsmallbarriers
				)}
				downstream
			</div>
		{/if}

		{#if totaldownstreamwaterfalls >= 0}
			<div>
				<b>{formatNumber(totaldownstreamwaterfalls)}</b>
				{pluralize('waterfall', totaldownstreamwaterfalls)} downstream
			</div>
		{/if}
	</div>
</section>
