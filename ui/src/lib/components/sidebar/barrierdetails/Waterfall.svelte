<script lang="ts">
	import { PASSABILITY, barrierTypeLabelSingular } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { isEmptyString } from '$lib/util/string'

	import Entry from './Entry.svelte'
	import Section from './Section.svelte'

	import DiadromousInfo from './DiadromousInfo.svelte'
	import FunctionalNetworkInfo from './FunctionalNetworkInfo.svelte'
	import IDInfo from './IDInfo.svelte'
	import LocationInfo from './LocationInfo.svelte'
	import MainstemNetworkInfo from './MainstemNetworkInfo.svelte'
	import NoNetworkInfo from './NoNetworkInfo.svelte'
	import SpeciesHabitatInfo from './SpeciesHabitatInfo.svelte'
	import SpeciesWatershedPresenceInfo from './SpeciesWatershedPresenceInfo.svelte'

	const { data } = $props()

	const {
		barrierType,
		falltype,
		flowstoocean,
		habitat,
		hasnetwork,
		milestooutlet,
		passability,
		totalmainstemupstreammiles,
		totalmainstemdownstreammiles,
		invasive,
		invasivenetwork
	} = $derived(data)

	const barrierTypeLabel = $derived(barrierTypeLabelSingular[barrierType as BarrierTypePlural])
</script>

<Section title="Location">
	<LocationInfo {...data} />

	{#if !isEmptyString(falltype)}
		<Entry label="Waterfall type">{falltype}</Entry>
	{/if}

	{#if passability !== null}
		<Entry label="Passability" isUnknown={passability === 0}>
			{PASSABILITY[passability as keyof typeof PASSABILITY]}
		</Entry>
	{/if}
</Section>

<Section title="Functional network information">
	{#if hasnetwork}
		<FunctionalNetworkInfo {...data} />
	{:else}
		<NoNetworkInfo {...data} />
	{/if}
</Section>

{#if hasnetwork}
	{#if habitat && habitat.length > 0}
		<Section title="Species habitat information for this network">
			<SpeciesHabitatInfo {...data} />
		</Section>
	{/if}

	{#if flowstoocean && milestooutlet < 500}
		<Section title="Marine connectivity">
			<DiadromousInfo {...data} />
		</Section>
	{/if}

	{#if totalmainstemupstreammiles > 0 || totalmainstemdownstreammiles > 0}
		<Section title="Mainstem network information">
			<MainstemNetworkInfo {...data} />
		</Section>
	{/if}
{/if}

<Section title="Species information for this subwatershed">
	<SpeciesWatershedPresenceInfo {...data} />
</Section>

{#if hasnetwork && invasive && invasivenetwork === 1}
	<Section title="Invasive species management">
		<Entry>
			{#if invasive}
				This {barrierTypeLabel} is identified as a beneficial to restricting the movement of invasive
				species and is not ranked.
			{:else if invasivenetwork === 1}
				Upstream of a barrier identified as a beneficial to restricting the movement of invasive
				species.
			{/if}
		</Entry>
	</Section>
{/if}

<Section title="Other information">
	<IDInfo {...data} />
</Section>
