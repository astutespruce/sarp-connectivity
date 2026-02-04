<script lang="ts">
	import { formatNumber } from '$lib/util/format'

	import Entry from './Entry.svelte'

	const {
		barrierType,
		milestooutlet = 0,
		totaldownstreamdams = 0,
		totaldownstreamsmallbarriers = 0,
		totaldownstreamwaterfalls = 0
	} = $props()
</script>

<Entry label="Miles downstream to the ocean">
	{formatNumber(milestooutlet)} miles
</Entry>

{#if totaldownstreamdams !== null && totaldownstreamdams >= 0}
	<Entry label="Number of dams downstream">
		{formatNumber(totaldownstreamdams)}
	</Entry>
{/if}

{#if barrierType === 'small_barriers' && totaldownstreamsmallbarriers !== null && totaldownstreamsmallbarriers >= 0}
	<Entry label="Number of surveyed road/stream crossings downstream">
		{formatNumber(totaldownstreamsmallbarriers)}
	</Entry>
{/if}

{#if totaldownstreamwaterfalls !== null && totaldownstreamwaterfalls >= 0}
	<Entry label="Number of waterfalls downstream">
		{formatNumber(totaldownstreamwaterfalls)}
	</Entry>
{/if}
