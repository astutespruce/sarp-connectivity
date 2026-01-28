<script lang="ts">
	import { CONTACT_EMAIL } from '$lib/env'
	import { barrierTypeLabels, barrierTypeLabelSingular } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'

	import Entry from './Entry.svelte'

	const {
		barrierType,
		networkType,
		snapped = 0,
		excluded = 0,
		in_network_type = false,
		onloop = false
	} = $props()

	const typeLabel = $derived(barrierTypeLabelSingular[barrierType as BarrierTypePlural])
</script>

<Entry>
	{#if barrierType === 'road_crossings'}
		This road-related barrier has not yet been assessed as a potential barrier for aquatic
		organisms, and has not been analyzed for aquatic network connectivity.
	{:else if !snapped}
		This {typeLabel} is off-network and has no functional network information.
		<div class="text-xs text-muted-foreground mt-4">
			Not all {barrierTypeLabels[barrierType as BarrierTypePlural]} could be correctly snapped to the
			aquatic network for analysis. Please <a href={`mailto:${CONTACT_EMAIL}`}>contact us</a> to report
			an error or for assistance interpreting these results.
		</div>
	{:else if excluded}
		This {typeLabel} was excluded from the connectivity analysis based on field reconnaissance, manual
		review of aerial imagery, or other information about this {typeLabel}.
	{:else if onloop}
		This {typeLabel} was excluded from the connectivity analysis based on its position within the aquatic
		network.
		<div class="text-xs text-muted-foreground mt-4">
			This {typeLabel} was snapped to a secondary channel within the aquatic network according to the
			way that primary versus secondary channels are identified within the NHD High Resolution Plus dataset.
			This dam may need to be repositioned to occur on the primary channel in order to be included within
			the connectivity analysis. Please
			<a href={`mailto:${CONTACT_EMAIL}`}>contact us</a> to report an issue with this barrier.
		</div>
	{:else if !in_network_type}
		This {typeLabel} is not included in this network scenario based on its passability
		{networkType === 'largefish_barriers' ? ' for large-bodied fish ' : null}
		{networkType === 'smallfish_barriers' ? ' for small-bodied fish ' : null}
		and has no functional network information.
	{:else}
		No network information is available.
	{/if}
</Entry>
