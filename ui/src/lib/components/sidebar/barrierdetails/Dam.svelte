<script lang="ts">
	import EmailIcon from '@lucide/svelte/icons/mail'
	import WarningIcon from '@lucide/svelte/icons/triangle-alert'

	import { CONTACT_EMAIL } from '$lib/env'
	import {
		HAZARD,
		CONDITION,
		CONSTRUCTION,
		PASSAGEFACILITY,
		PURPOSE,
		FEASIBILITYCLASS,
		RECON,
		PASSABILITY,
		barrierTypeLabelSingular,
		dataVersion
	} from '$lib/config/constants'

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
		sarpid,
		condition,
		construction,
		diversion,
		estimated,
		feasibilityclass,
		flowstoocean,
		habitat,
		hasnetwork,
		hazard,
		height,
		invasive,
		lowheaddam,
		milestooutlet,
		passability,
		passagefacility,
		purpose,
		recon,
		removed,
		totalmainstemupstreammiles,
		totalmainstemdownstreammiles,
		yearcompleted,
		yearremoved,
		invasivenetwork
	} = $derived(data)

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

<Section title="Location">
	<Entry label="Barrier type">
		{barrierTypeLabel}

		{#if estimated}
			<div class="flex mt-2 gap-1">
				<WarningIcon class="size-4" />
				<div class="text-xs text-muted-foreground">
					Dam is estimated from other data sources and may be incorrect; please
					<a
						href={`mailto:${CONTACT_EMAIL}subject=Problem with Estimated Dam ${sarpid} (data version: ${dataVersion})`}
					>
						let us know
					</a>
				</div>
			</div>
		{/if}
	</Entry>

	<LocationInfo {...data} />
</Section>

<Section title="Construction information">
	{#if purpose !== null && purpose >= 0 && PURPOSE[purpose as keyof typeof PURPOSE]}
		<Entry label="Purpose" isUnknown={purpose === 0}>
			{PURPOSE[purpose as keyof typeof PURPOSE].toLowerCase()}
		</Entry>
	{/if}

	{#if yearcompleted > 0}
		<Entry label="Construction completed">
			{yearcompleted}
		</Entry>
	{/if}

	{#if height > 0}
		<Entry label="Height">
			{height} feet
		</Entry>
	{/if}

	{#if construction !== null && construction >= 0 && CONSTRUCTION[construction as keyof typeof CONSTRUCTION]}
		<Entry label="Construction material" isUnknown={construction === 0}>
			{CONSTRUCTION[construction as keyof typeof CONSTRUCTION].toLowerCase()}
		</Entry>
	{/if}

	{#if hazard > 0 && HAZARD[hazard as keyof typeof HAZARD]}
		<Entry label="Hazard rating">
			{HAZARD[hazard as keyof typeof HAZARD].toLowerCase()}
		</Entry>
	{/if}

	{#if condition !== null && condition >= 0 && CONDITION[condition as keyof typeof CONDITION]}
		<Entry label="Structural condition" isUnknown={condition === 0}>
			{CONDITION[condition as keyof typeof CONDITION].toLowerCase()}
		</Entry>
	{/if}

	{#if !removed && passability !== null && PASSABILITY[passability as keyof typeof PASSABILITY]}
		<Entry label="Passability" isUnknown={passability === 0}>
			{PASSABILITY[passability as keyof typeof PASSABILITY].toLowerCase()}
		</Entry>
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
				? `This dam was removed or mitigated in ${yearremoved}.`
				: 'This dam has been removed or mitigated.'}
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

{#if !removed && feasibilityclass && feasibilityclass <= 10}
	<Section title="Feasibility & conservation benefit">
		<Entry label="Feasibility" isUnknown={feasibilityclass <= 1}>
			{FEASIBILITYCLASS[feasibilityclass as keyof typeof FEASIBILITYCLASS]}
			<br />
			<a
				href={`mailto:${CONTACT_EMAIL}?subject=Update feasibility for dam: ${sarpid} (data version: ${dataVersion})&body=The feasibility of this barrier should be: %0D%0A%0D%0A(choose one of the following options)%0D%0A%0D%0A${Object.entries(
					FEASIBILITYCLASS
				)
					.filter(([key]) => parseInt(key, 10) >= 1)
					.map(([_, value]) => value)
					.join('%0D%0A')})`}
				target="_blank"
				rel="external"
			>
				<div class="flex gap-1 items-center text-xs">
					<EmailIcon class="size-4" />
					submit {feasibilityclass > 1 ? 'new' : null} feasibility
				</div>
			</a>
		</Entry>

		{#if recon > 0}
			<Entry label="Field recon notes">{RECON[recon as keyof typeof RECON]}</Entry>
		{/if}
	</Section>
{/if}

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

	<!-- TODO: only show for small barriers if attachments.length>0
	<SurveyPhotos {...data} /> -->
</Section>
