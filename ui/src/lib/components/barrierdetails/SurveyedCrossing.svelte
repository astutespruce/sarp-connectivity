<script lang="ts">
	import {
		SMALL_BARRIER_SEVERITY,
		CONDITION,
		CROSSING_TYPE,
		ROAD_TYPE,
		CONSTRICTION,
		PASSAGEFACILITY,
		barrierTypeLabelSingular
	} from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { formatNumber } from '$lib/util/format'
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
	import SurveyPhotos from './SurveyPhotos.svelte'

	export const classifySARPScore = (score: number) => {
		// assumes -1 (NODATA) already filtered out
		if (score < 0.2) {
			return 'severe barrier'
		}
		if (score < 0.4) {
			return 'significant barrier'
		}
		if (score < 0.6) {
			return 'moderate barrier'
		}
		if (score < 0.8) {
			return 'minor barrier'
		}
		if (score < 1) {
			return 'insignificant barrier'
		}
		if (score >= 1) {
			return 'no barrier'
		}
		return 'not calculated'
	}

	const { data } = $props()

	const {
		barrierType,
		barrierseverity,
		condition,
		constriction,
		crossingtype,
		flowstoocean,
		habitat,
		hasnetwork,
		invasive,
		invasivenetwork,
		milestooutlet,
		passagefacility,
		protocolused,
		removed,
		road,
		roadtype,
		sarp_score,
		totalmainstemupstreammiles,
		totalmainstemdownstreammiles,
		yearremoved
	} = $derived(data)

	const barrierTypeLabel = $derived(barrierTypeLabelSingular[barrierType as BarrierTypePlural])
</script>

<Section title="Location">
	<Entry label="Barrier type">
		{barrierTypeLabel}

		{#if invasive}
			,<br />invasive species barrier
		{/if}
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

	{#if condition !== null && condition >= 0}
		<Entry label="Condition" isUnknown={condition === 0}>
			{CONDITION[condition as keyof typeof CONDITION]}
		</Entry>
	{/if}

	{#if constriction !== null && constriction >= 0}
		<Entry label="Type of constriction" isUnknown={constriction === 0}>
			{CONSTRICTION[constriction as keyof typeof CONSTRICTION]}
		</Entry>
	{/if}

	{#if !removed && barrierseverity !== null}
		<Entry label="Severity" isUnknown={barrierseverity === 0}>
			{SMALL_BARRIER_SEVERITY[barrierseverity as keyof typeof SMALL_BARRIER_SEVERITY]}
		</Entry>
	{/if}

	{#if !removed && sarp_score >= 0}
		<Entry label="SARP Aquatic Organism Passage score">
			{formatNumber(sarp_score, 1)}
			<div class="text-xs text-muted-foreground">
				({classifySARPScore(sarp_score)})
			</div>
		</Entry>
		{#if isEmptyString(protocolused)}
			<Entry label="Protocol used">{protocolused}</Entry>
		{/if}
	{/if}

	{#if passagefacility !== null && passagefacility >= 0 && PASSAGEFACILITY[passagefacility as keyof typeof PASSAGEFACILITY]}
		<Entry label="Passage facility type" isUnknown={passagefacility === 0}>
			{PASSAGEFACILITY[passagefacility as keyof typeof PASSAGEFACILITY].toLowerCase()}
		</Entry>
	{/if}
</Section>

<Section title="Functional network information">
	{#if removed}
		<Entry>
			{yearremoved !== null && yearremoved > 0
				? `This barrier was removed or mitigated in ${yearremoved}.`
				: 'This barrier has been removed or mitigated.'}
		</Entry>
	{/if}

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

	{#if data.attachments && data.attachments.length > 0}
		<SurveyPhotos {...data} />
	{/if}
</Section>
