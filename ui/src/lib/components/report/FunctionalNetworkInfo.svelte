<script lang="ts">
	import { CONTACT_EMAIL } from '$lib/env'
	import { barrierTypeLabelSingular, dataVersion } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { formatNumber, formatPercent } from '$lib/util/format'
	import { cn } from '$lib/utils'

	const {
		barrierType,
		networkType,
		sarpid,
		totalupstreammiles,
		perennialupstreammiles,
		alteredupstreammiles,
		unalteredupstreammiles,
		resilientupstreammiles,
		coldupstreammiles,
		freedownstreammiles,
		freeperennialdownstreammiles,
		freealtereddownstreammiles,
		freeunaltereddownstreammiles,
		freeresilientdownstreammiles,
		freecolddownstreammiles,
		sizeclasses,
		landcover,
		excluded,
		hasnetwork,
		in_network_type,
		onloop,
		invasive,
		unranked,
		removed,
		yearremoved,
		flowstoocean,
		flowstogreatlakes,
		totaldownstreamdams,
		totaldownstreamsmallbarriers,
		totaldownstreamwaterfalls,
		unalteredwaterbodyacres,
		unalteredwetlandacres
	} = $props()

	const barrierTypeLabel = $derived(barrierTypeLabelSingular[barrierType as BarrierTypePlural])

	const totaldownstreambarriers = $derived(
		networkType === 'dams'
			? totaldownstreamdams + totaldownstreamwaterfalls
			: totaldownstreamdams + totaldownstreamwaterfalls + totaldownstreamsmallbarriers
	)

	const alwaysUseUpstream = $derived(
		(flowstoocean === 1 || flowstogreatlakes === 1) && totaldownstreambarriers === 0
	)

	const gainmiles = $derived(Math.min(totalupstreammiles, freedownstreammiles))
	const gainMilesSide = $derived(
		alwaysUseUpstream || gainmiles === totalupstreammiles ? 'upstream' : 'downstream'
	)

	const perennialGainMiles = $derived(
		Math.min(perennialupstreammiles, freeperennialdownstreammiles)
	)

	const perennialGainMilesSide = $derived(
		alwaysUseUpstream || perennialGainMiles === perennialupstreammiles ? 'upstream' : 'downstream'
	)

	const intermittentupstreammiles = $derived(totalupstreammiles - perennialupstreammiles)
	const freeintermittentdownstreammiles = $derived(
		freedownstreammiles - freeperennialdownstreammiles
	)

	const percentUnaltered = $derived(
		totalupstreammiles ? (100 * unalteredupstreammiles) / totalupstreammiles : 0
	)

	const numCols = $derived(totalupstreammiles > 0 ? 4 : 3)
</script>

<section>
	<h3>Functional network information</h3>

	{#if excluded}
		<div class="text-sm">
			This {barrierTypeLabel} was excluded from the connectivity analysis based on field reconnaissance
			or manual review of aerial imagery.
		</div>
	{:else if onloop}
		<div class="text-sm">
			This {barrierTypeLabel} was excluded from the connectivity analysis based on its position within
			the aquatic network.

			<div class="text-xs text-muted-foreground mt-2">
				This {barrierTypeLabel} was snapped to a secondary channel within the aquatic network according
				to the way that primary versus secondary channels are identified within the NHD High Resolution
				Plus dataset. This {barrierTypeLabel} may need to be repositioned to occur on the primary channel
				in order to be included within the connectivity analysis. Please
				<a
					href={`mailto:${CONTACT_EMAIL}?subject=Problem with National Aquatic Barrier Inventory for ${barrierTypeLabel}: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
				>
					contact us
				</a>
				to report an error.
			</div>
		</div>
	{:else if !in_network_type}
		<div class="text-sm">
			This {barrierTypeLabel} is not included in this network scenario based on its passability
			{networkType === 'largefish_barriers' ? ' for large-bodied fish ' : null}
			{networkType === 'smallfish_barriers' ? ' for small-bodied fish ' : null}
			and has no functional network information.
		</div>
	{:else if !hasnetwork}
		<div class="text-sm">
			This {barrierTypeLabel} is off-network and has no functional network information.
			<div class="text-xs text-muted-foreground mt-2">
				Not all dams could be correctly snapped to the aquatic network for analysis. Please
				<a
					href={`mailto:${CONTACT_EMAIL}?subject=Problem with National Aquatic Barrier Inventory for ${barrierTypeLabel}: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
				>
					contact us
				</a>
				to report an error or for assistance interpreting these results.
			</div>
		</div>
	{:else}
		<div class="text-xs text-muted-foreground">
			Functional networks are the full upstream dendritic network to the upstream-most points on the
			network or upstream barriers. The downstream network is the upstream functional network of the
			next barrier immediately downstream or downstream-most point on that network, and includes any
			tributaries up to their upstream-most points or other barriers.
		</div>

		{#if removed}
			<div class="text-sm">
				{#if yearremoved !== null && yearremoved > 0}
					This barrier was removed or mitigated in ${yearremoved}.
				{:else}
					This barrier has been removed or mitigated.
				{/if}
			</div>
		{/if}

		<div
			class={`grid sm:grid-cols-${numCols} gap-4 text-sm mt-4 leading-snug sm:[&>div]:py-2 sm:[&>div+div]:border-l sm:[&>div+div]:border-l-grey-2 sm:[&>div+div]:pl-4`}
		>
			<div>
				<b>{formatNumber(gainmiles, 2, true)} total miles</b>
				{removed ? 'were' : 'could be'} reconnected by removing this
				{barrierTypeLabel} including
				<b>{formatNumber(perennialGainMiles, 2, true)} miles</b> of perennial reaches.
			</div>

			{#if totalupstreammiles > 0}
				<div>
					<b>{formatPercent(percentUnaltered)}% of the upstream network</b> is in unaltered stream reaches.
				</div>
			{/if}

			<div>
				<b>
					{sizeclasses} river size {sizeclasses === 1 ? 'class' : 'classes'}
				</b>
				{removed ? 'were' : 'could be'} gained by removing this
				{barrierTypeLabel}.
			</div>

			<div>
				<b>{formatNumber(landcover, 0)}% of the upstream floodplain</b> is composed of natural landcover.
			</div>
		</div>

		<table cellpadding="0" cellspacing="0" class="mt-12">
			<thead>
				<tr>
					<th class="font-bold"> Network metric </th>
					<th class="font-bold max-w-48"> upstream network </th>
					<th class="font-bold max-w-48"> downstream network </th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Total miles</td>
					<td class={cn({ 'font-bold': gainMilesSide === 'upstream' })}>
						{formatNumber(totalupstreammiles, 2, true)}
					</td>
					<td class={cn({ 'font-bold': gainMilesSide === 'downstream' })}>
						{formatNumber(freedownstreammiles, 2, true)}
					</td>
				</tr>

				<tr>
					<td>Perennial miles</td>
					<td class={cn({ 'font-bold': perennialGainMilesSide === 'upstream' })}>
						{formatNumber(perennialupstreammiles, 2, true)}
					</td>
					<td class={cn({ 'font-bold': perennialGainMilesSide === 'downstream' })}>
						{formatNumber(freeperennialdownstreammiles, 2, true)}
					</td>
				</tr>

				<tr>
					<td>Ephemeral / intermittent miles</td>
					<td>{formatNumber(intermittentupstreammiles, 2, true)}</td>
					<td>{formatNumber(freeintermittentdownstreammiles, 2, true)}</td>
				</tr>

				<tr>
					<td>Altered miles</td>
					<td>{formatNumber(alteredupstreammiles, 2, true)}</td>
					<td>{formatNumber(freealtereddownstreammiles, 2, true)}</td>
				</tr>

				<tr>
					<td>Unaltered miles</td>
					<td>{formatNumber(unalteredupstreammiles, 2, true)}</td>
					<td>{formatNumber(freeunaltereddownstreammiles, 2, true)}</td>
				</tr>

				<tr>
					<td>Resilient miles</td>
					<td>{formatNumber(resilientupstreammiles, 2, true)}</td>
					<td>{formatNumber(freeresilientdownstreammiles, 2, true)}</td>
				</tr>

				<tr>
					<td>Coldwater habitat miles</td>
					<td>{formatNumber(coldupstreammiles, 2, true)}</td>
					<td>{formatNumber(freecolddownstreammiles, 2, true)}</td>
				</tr>
			</tbody>
		</table>

		<div class="mt-8 text-sm">
			This network intersects
			<b>{formatNumber(unalteredwaterbodyacres)} acres</b> of unaltered lakes and ponds and
			<b>{formatNumber(unalteredwetlandacres)} acres</b> of unaltered freshwater wetlands.
		</div>

		<div class="text-xs text-muted-foreground mt-8">
			{#if unranked && !invasive}
				Note: this {barrierTypeLabel} excluded from ranking based on field reconnaissance, manual review
				of aerial imagery, or other information about this {barrierTypeLabel}.
				<br />
				<br />
			{/if}

			{#if alwaysUseUpstream}
				Note: upstream miles are used because the downstream network flows into the {flowstogreatlakes ===
				1
					? 'Great Lakes'
					: 'ocean'} and there are no barriers downstream.
				<br />
				<br />
			{/if}

			Note: Statistics are based on aquatic networks cut by{' '}
			{networkType === 'dams'
				? 'waterfalls and dams'
				: 'waterfalls, dams, and road-related barriers'}
			{networkType === 'largefish_barriers'
				? ' based on their passability for large-bodied fish'
				: null}
			{networkType === 'smallfish_barriers'
				? ' based on their passability for small-bodied fish'
				: null}
			{removed
				? `, including any that were present at the time this
            ${barrierTypeLabel} was removed, with the exception of those directly
            upstream that were removed in the same year as this barrier.
            All barriers removed prior to 2000 or where the year they were removed
            was unknown were lumped together for this analysis`
				: null}
			. Downstream lengths are limited to free-flowing reaches only; these exclude lengths within waterbodies
			in the downstream network. Perennial miles are the sum of lengths of all reaches not specifically
			coded as ephemeral or intermittent within the functional network. Perennial reaches are not necessarily
			contiguous. Altered miles are the total length of stream reaches that are specifically identified
			in NHD or the National Wetlands Inventory as altered (canal / ditch, within a reservoir, or other
			channel alteration), and do not necessarily include all forms of alteration of the stream channel.
			Resilient miles are the total length of stream reaches that are within watersheds with above average
			or greater freshwater resilience within
			<a href="https://www.maps.tnc.org/resilientrivers/#/explore" target="_blank" rel="external">
				The Nature Conservancy's Freshwater Resilience
			</a>
			dataset (v0.44). Coldwater habitat miles are the total length of stream reaches that are within
			watersheds with slighly above average or greater cold temperature scores (TNC, March 2024).
			<br />
			<br />
			Unaltered lakes and ponds include any that intersect a stream reach in the upstream functional network,
			and exclude any specifically marked by their data provider as altered as well as any that are associated
			with dams in this inventory. Unaltered freshwater wetlands are derived from the National Wetlands
			Inventory (freshwater scrub-shrub, freshwater forested, freshwater emergent) and NHD (swamp/marsh)
			and exclude any specifically marked by their data provider as altered.
		</div>
	{/if}
</section>
