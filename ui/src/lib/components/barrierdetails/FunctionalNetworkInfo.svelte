<script lang="ts">
	import { barrierTypeLabelSingular } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { ExpandableParagraph } from '$lib/components/text'
	import { InfoTooltip } from '$lib/components/tooltip'
	import { cn } from '$lib/utils'

	import Entry from './Entry.svelte'

	import { formatNumber, formatPercent } from '$lib/util/format'

	const {
		barrierType,
		networkType,
		totalupstreammiles = 0,
		perennialupstreammiles = 0,
		alteredupstreammiles = 0,
		unalteredupstreammiles = 0,
		resilientupstreammiles = 0,
		coldupstreammiles = 0,
		freedownstreammiles = 0,
		freeperennialdownstreammiles = 0,
		freealtereddownstreammiles = 0,
		freeunaltereddownstreammiles = 0,
		freeresilientdownstreammiles = 0,
		freecolddownstreammiles = 0,
		percentresilient = 0,
		percentcold = 0,
		sizeclasses = 0,
		landcover = 0,
		invasive = false,
		unranked = false,
		removed = false,
		flowstoocean = 0,
		flowstogreatlakes = 0,
		totaldownstreamdams = 0,
		totaldownstreamsmallbarriers = 0,
		totaldownstreamwaterfalls = 0,
		unalteredwaterbodyacres = 0,
		unalteredwetlandacres = 0,
		upstreambarrier = null,
		upstreambarriersarpid = null,
		upstreambarriermiles = null,
		downstreambarrier = null,
		downstreambarriersarpid = null,
		downstreambarriermiles = null
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

	const networkStatsNote = $derived.by(() => {
		let note = `Statistics are based on aquatic networks cut by ${networkType === 'dams' ? 'waterfalls and dams' : 'waterfalls, dams, and road-related barriers'}`

		if (networkType === 'largefish_barriers') {
			note += ' based on their passability for large-bodied fish'
		} else if (networkType === 'smallfish_barriers') {
			note += ' based on their passability for small-bodied fish'
		}

		if (removed) {
			note += `, including any that were present at the time this
                ${barrierTypeLabel} was removed, with the exception of those
                directly upstream that were removed in the same year as this barrier.
                All barriers removed prior to 2000 or where the year they were
                removed was unknown were lumped together for this analysis`
		}

		return note + '.'
	})
</script>

<ExpandableParagraph
	snippet="Functional networks are the full upstream dendritic network..."
	class="text-xs text-muted-foreground mt-2  mb-4 mx-2"
>
	Functional networks are the full upstream dendritic network to the upstream-most points on the
	network or upstream barriers. The downstream network is the upstream functional network of the
	next barrier immediately downstream or downstream-most point on that network, and includes any
	tributaries up to their upstream-most points or other barriers.
</ExpandableParagraph>

<table cellpadding="0" cellspacing="0">
	<thead>
		<tr>
			<th class="w-44">Network metric</th>
			<th>Upstream</th>
			<th
				>Downstream
				<div class="text-xs text-muted-foreground font-normal">free-flowing <br /> miles only</div>
			</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>
				<InfoTooltip title="Total miles">
					Total miles upstream is the sum of all river and stream lengths in the upstream functional
					network.
					<br />
					<br />
					Total miles downstream is the sum of all river and stream lengths in the functional network
					immediately downstream of this network, excluding all lengths within altered waterbodies.
				</InfoTooltip>
			</td>
			<td class={cn({ 'font-bold': gainMilesSide === 'upstream' })}>
				{formatNumber(totalupstreammiles, 2, true)}
			</td>
			<td class={cn({ 'font-bold': gainMilesSide === 'downstream' })}>
				{formatNumber(freedownstreammiles, 2, true)}
			</td>
		</tr>

		<tr>
			<td>
				<InfoTooltip title="Perennial miles">
					Total perennial miles upstream is the sum of all perennial reach lengths in the upstream
					functional network. Perennial reaches are all those that are not specifically identified
					as ephemeral or intermittent. Perennial reaches are not necessarily contiguous.
					<br />
					<br />
					Total perennial miles downstream is the sum of all perennial reach lengths in the functional
					network immediately downstream of this network, excluding all lengths within altered waterbodies.
				</InfoTooltip>
			</td>
			<td class={cn({ 'font-bold': perennialGainMilesSide === 'upstream' })}>
				{formatNumber(perennialupstreammiles, 2, true)}
			</td>
			<td class={cn({ 'font-bold': perennialGainMilesSide === 'downstream' })}>
				{formatNumber(freeperennialdownstreammiles, 2, true)}
			</td>
		</tr>

		<tr>
			<td>
				<InfoTooltip title="Ephemeral / intermittent miles">
					Total ephemeral and intermittent miles upstream is the sum of all ephemeral and
					intermittent reach lengths in the upstream functional network.
					<br />
					<br />
					Total ephemeral and intermittent miles downstream is the sum of all ephemeral and intermittent
					reach lengths in the functional network immediately downstream of this network, excluding all
					lengths within altered waterbodies.
				</InfoTooltip>
			</td>
			<td>{formatNumber(intermittentupstreammiles, 2, true)}</td>
			<td>{formatNumber(freeintermittentdownstreammiles, 2, true)}</td>
		</tr>

		<tr>
			<td>
				<InfoTooltip title="Altered miles">
					Total altered miles upstream is the sum of all reach lengths specifically identified as
					altered (canal / ditch, within reservoir, or other channel alteration).
					<br />
					<br />
					Total altered miles downstream is the sum of all altered reach lengths in the functional network
					immediately downstream of this network, excluding all lengths within altered waterbodies.
				</InfoTooltip>
			</td>
			<td>{formatNumber(alteredupstreammiles, 2, true)}</td>
			<td>{formatNumber(freealtereddownstreammiles, 2, true)}</td>
		</tr>

		<tr>
			<td>
				<InfoTooltip title="Unaltered miles">
					Total unaltered miles upstream is the sum of all reach lengths not specifically identified
					as altered (canal / ditch, within reservoir, or other channel alteration).
					<br />
					<br />
					Total unaltered miles downstream is the sum of all unaltered reach lengths in the functional
					network immediately downstream of this network, excluding all lengths within altered waterbodies.
				</InfoTooltip>
			</td>
			<td>{formatNumber(unalteredupstreammiles, 2, true)}</td>
			<td>{formatNumber(freeunaltereddownstreammiles, 2, true)}</td>
		</tr>

		<tr>
			<td>
				<InfoTooltip title="Resilient miles">
					Total resilient miles upstream is the sum of all reach lengths that are within watersheds
					with above average or greater freshwater resilience within The Nature Conservancy&apos;s
					Freshwater Resilience dataset (v0.44).
					<br />
					<br />
					Total resilient miles downstream is the sum of all reach lengths in the functional network immediately
					downstream of this network that are within watersheds with above average or greater freshwater
					resilience, excluding all lengths within altered waterbodies.
				</InfoTooltip>
			</td>
			<td>{formatNumber(resilientupstreammiles, 2, true)}</td>
			<td>{formatNumber(freeresilientdownstreammiles, 2, true)}</td>
		</tr>

		<tr>
			<td>
				<InfoTooltip title="Coldwater habitat miles">
					Total coldwater habitat miles upstream is the sum of all reach lengths that are within
					watersheds with slighly above average or greater cold temperature scores within The Nature
					Conservancy's Freshwater Resilience dataset (March 2024).
					<br />
					<br />
					Total coldwater habitat miles downstream is the sum of all reach lengths in the functional network
					immediately downstream of this network that are within watersheds with slighly above average
					or greater cold temperature scores, excluding all lengths within altered waterbodies.
				</InfoTooltip>
			</td>
			<td>{formatNumber(coldupstreammiles, 2, true)}</td>
			<td>{formatNumber(freecolddownstreammiles, 2, true)}</td>
		</tr>

		{#if barrierType !== 'waterfalls'}
			<tr class="border-t-2 border-t-grey-4">
				<td>
					<InfoTooltip title="Total miles gained">
						The total miles that {removed ? 'were' : 'could be'} gained by removing this barrier is the
						lesser of the upstream or downstream total functional network miles.
					</InfoTooltip>
				</td>
				<td class={cn('invisible', { 'visible font-bold': gainMilesSide === 'upstream' })}>
					{formatNumber(totalupstreammiles, 2, true)}{#if alwaysUseUpstream}<sup>*</sup>{/if}
				</td>
				<td class={cn('invisible', { 'visible font-bold': gainMilesSide === 'downstream' })}>
					{formatNumber(freedownstreammiles, 2, true)}
				</td>
			</tr>

			<tr>
				<td>
					<InfoTooltip title="Perennial miles gained">
						The total perennial miles that
						{removed ? 'were' : 'could be'} gained by removing this barrier is the lesser of the upstream
						or downstream perennial miles.
					</InfoTooltip>
				</td>
				<td class={cn({ 'font-bold': perennialGainMilesSide === 'upstream' })}>
					{formatNumber(perennialupstreammiles, 2, true)}{#if alwaysUseUpstream}<sup>*</sup>{/if}
				</td>
				<td class={cn({ 'font-bold': perennialGainMilesSide === 'downstream' })}>
					{formatNumber(freeperennialdownstreammiles, 2, true)}
				</td>
			</tr>
		{/if}
	</tbody>
</table>

<div class="text-xs text-muted-foreground mt-4 mx-2">
	{#if barrierType !== 'waterfalls' && alwaysUseUpstream}
		<sup>*</sup>Upstream miles are used because the downstream network flows into the {flowstogreatlakes ===
		1
			? 'Great Lakes'
			: 'ocean'}
		and there are no barriers downstream.
		<br />
		<br />
	{/if}

	{networkStatsNote}
</div>

{#if totalupstreammiles > 0}
	<Entry label="Percent of the upstream network in unaltered stream channels">
		{formatPercent(percentUnaltered)}%
	</Entry>

	<Entry label="Percent of the upstream network in resilient watersheds">
		{formatPercent(percentresilient)}%
	</Entry>

	<Entry label="Percent of the upstream network in coldwater habitat watersheds">
		{formatPercent(percentcold)}%
	</Entry>
{/if}

<Entry
	label={barrierType === 'waterfalls'
		? 'Number of size classes upstream'
		: `Number of size classes that ${
				removed ? 'were' : 'could be'
			} gained by removing this barrier`}
>
	{sizeclasses}
</Entry>

<Entry label="Percent of upstream floodplain composed of natural landcover">
	{formatNumber(landcover, 0)}%
</Entry>

<Entry label="Total area of unaltered lakes and ponds">
	{formatNumber(unalteredwaterbodyacres)} acres

	<ExpandableParagraph
		snippet="Based on all unaltered lakes and ponds that
            intersect any stream reach in the upstream functional network..."
		class="text-xs text-muted-foreground mt-4"
	>
		Based on all unaltered lakes and ponds that intersect any stream reach in the upstream
		functional network, and exclude any specifically marked by their data provider as altered as
		well as any that are associated with dams in this inventory.
	</ExpandableParagraph>
</Entry>

<Entry label="Total area of unaltered freshwater wetlands">
	{formatNumber(unalteredwetlandacres)} acres

	<ExpandableParagraph
		snippet="Based on all unaltered freshwater wetlands that
            intersect any stream reach in the upstream functional network."
		class="text-xs text-muted-foreground mt-4"
	>
		Based on all unaltered freshwater wetlands that intersect any stream reach in the upstream
		functional network. Wetlands are derived from the National Wetlands Inventory (freshwater
		scrub-shrub, freshwater forested, freshwater emergent) and NHD (swamp/marsh) and exclude any
		specifically marked by their data provider as altered.
	</ExpandableParagraph>
</Entry>

{#if upstreambarrier}
	<Entry label="Nearest upstream barrier">
		<div class="leading-relaxed">
			{barrierTypeLabelSingular[`${upstreambarrier}s` as BarrierTypePlural]}

			(id: {upstreambarriersarpid})
			<br />
			distance: {formatNumber(upstreambarriermiles)} miles upstream
		</div>
	</Entry>
{/if}

{#if downstreambarrier}
	<Entry label="Downstream barrier">
		<div class="leading-relaxed">
			{barrierTypeLabelSingular[`${downstreambarrier}s` as BarrierTypePlural]}

			id: {downstreambarriersarpid}
			<br />
			distance: {formatNumber(downstreambarriermiles)} miles downstream
		</div>
	</Entry>
{/if}

{#if unranked && !invasive}
	<Entry>
		<div class="text-xs text-muted-foreground">
			This {barrierTypeLabel} excluded from ranking based on field reconnaissance, manual review of aerial
			imagery, or other information about this {barrierTypeLabel}.
		</div>
	</Entry>
{/if}
