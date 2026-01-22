<script lang="ts">
	import { CROSSING_TYPE, ROAD_TYPE, barrierTypeLabelSingular } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { isEmptyString } from '$lib/util/string'

	import Entry from './Entry.svelte'
	import Section from './Section.svelte'

	import IDInfo from './IDInfo.svelte'
	import LocationInfo from './LocationInfo.svelte'
	import NoNetworkInfo from './NoNetworkInfo.svelte'
	import SpeciesWatershedPresenceInfo from './SpeciesWatershedPresenceInfo.svelte'

	const { data } = $props()

	const { barrierType, crossingtype, diadromoushabitat, intermittent, road, roadtype } =
		$derived(data)

	const barrierTypeLabel = $derived(barrierTypeLabelSingular[barrierType as BarrierTypePlural])
</script>

<Section title="Location">
	<Entry label="Barrier type">
		{barrierTypeLabel}
	</Entry>

	{#if !isEmptyString(road)}
		<Entry label="Road">{road}</Entry>
	{/if}

	<LocationInfo {...data} />
</Section>

<Section title="Barrier information">
	{#if roadtype !== null && roadtype >= 0}
		<Entry label="Road type" isUnknown={roadtype === 0}>
			{ROAD_TYPE[roadtype as keyof typeof ROAD_TYPE]}
		</Entry>
	{/if}

	{#if crossingtype !== null && crossingtype >= 0}
		<Entry label="Crossing type" isUnknown={crossingtype === 0}>
			{CROSSING_TYPE[crossingtype as keyof typeof CROSSING_TYPE]}
		</Entry>
	{/if}

	{#if intermittent === 1}
		<Entry>On a reach that has intermittent or ephemeral flow</Entry>
	{/if}
</Section>

{#if diadromoushabitat === 1}
	<Section title="Species habitat information for this network">
		<Entry>
			This {barrierTypeLabel} is located on a reach with anadromous / catadromous species habitat.
			<div class="text-xs text-muted-foreground">
				Note: species habitat network statistics are not available for this
				{barrierTypeLabel}.
			</div>
		</Entry>
	</Section>
{/if}

<Section title="Functional network information">
	<NoNetworkInfo {...data} />
</Section>

<Section title="Species information for this subwatershed">
	<SpeciesWatershedPresenceInfo {...data} />
</Section>

<Section title="Other information">
	<IDInfo {...data} />
</Section>
