<script lang="ts">
	import { formatNumber } from '$lib/util/format'

	import Entry from './Entry.svelte'

	const {
		barrierType,
		milestooutlet,
		totaldownstreamdams,
		totaldownstreamsmallbarriers,
		totaldownstreamwaterfalls
	} = $props()
</script>

<Entry label="Miles downstream to the ocean">
	{formatNumber(milestooutlet)}
</Entry>

{#if totaldownstreamdams !== null && totaldownstreamdams >= 0}
	<Entry label="Number of dams downstream">
		{formatNumber(totaldownstreamdams)}
	</Entry>
{/if}

{#if barrierType === 'small_barriers' && totaldownstreamsmallbarriers !== null && totaldownstreamsmallbarriers >= 0}
	<Entry label="Number of assessed road-related barriers downstream">
		{formatNumber(totaldownstreamsmallbarriers)}
	</Entry>
{/if}

{#if totaldownstreamwaterfalls !== null && totaldownstreamwaterfalls >= 0}
	<Entry label="Number of waterfalls downstream">
		{formatNumber(totaldownstreamwaterfalls)}
	</Entry>
{/if}
