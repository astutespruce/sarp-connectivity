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
		percentresilient,
		percentcold,
		sizeclasses,
		landcover,
		invasive,
		unranked,
		removed,
		flowstoocean,
		flowstogreatlakes,
		totaldownstreamdams,
		totaldownstreamsmallbarriers,
		totaldownstreamwaterfalls,
		unalteredwaterbodyacres,
		unalteredwetlandacres,
		upstreambarrier,
		upstreambarriersarpid,
		upstreambarriermiles,
		downstreambarrier,
		downstreambarriersarpid,
		downstreambarriermiles
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
</script>

<div class="text-xs text-muted-foreground mx-2">
	Functional networks are the full upstream dendritic network to the upstream-most points on the
	network or upstream barriers. The downstream network is the upstream functional network of the
	next barrier immediately downstream or downstream-most point on that network, and includes any
	tributaries up to their upstream-most points or other barriers.
</div>

<table cellpadding="0" cellspacing="0">
	<thead>
		<tr>
			<th class="w-44">Network metric</th>
			<th>Upstream</th>
			<th
				>Downstream
				<div class="text-xs text-muted-foreground">free-flowing miles only</div>
			</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>
				Total miles
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
				Perennial miles
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
				Intermittent miles
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
				Altered miles
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
				Unaltered miles
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
				Resilient miles
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
				Coldwater habitat miles
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
					<b>Total miles gained</b>
					<InfoTooltip title="Total miles gained">
						The total miles that {removed ? 'were' : 'could be'} gained by removing this barrier is the
						lesser of the upstream or downstream total functional network miles.
					</InfoTooltip>
				</td>
				<td class={cn('invisible', { 'visible font-bold': gainMilesSide === 'upstream' })}>
					{formatNumber(totalupstreammiles, 2, true)}
					{#if alwaysUseUpstream}<sup>*</sup>{/if}
				</td>
				<td class={cn('invisible', { 'visible font-bold': gainMilesSide === 'downstream' })}>
					{formatNumber(freedownstreammiles, 2, true)}
				</td>
			</tr>

			<tr>
				<td>
					<b>Perennial miles gained</b>
					<InfoTooltip title="Perennial miles gained">
						The total perennial miles that
						{removed ? 'were' : 'could be'} gained by removing this barrier is the lesser of the upstream
						or downstream perennial miles.
					</InfoTooltip>
				</td>
				<td class={cn({ 'font-bold': perennialGainMilesSide === 'upstream' })}>
					{formatNumber(perennialupstreammiles, 2, true)}
					{#if alwaysUseUpstream}<sup>*</sup>{/if}
				</td>
				<td class={cn({ 'font-bold': perennialGainMilesSide === 'downstream' })}>
					{formatNumber(freeperennialdownstreammiles, 2, true)}
				</td>
			</tr>
		{/if}
	</tbody>
</table>

<div class="text-xs text-muted-foreground mt-8">
	{#if barrierType !== 'waterfalls' && alwaysUseUpstream}
		<sup>*</sup>upstream miles are used because the downstream network flows into the {flowstogreatlakes ===
		1
			? 'Great Lakes'
			: 'ocean'}
		and there are no barriers downstream.
		<br />
		<br />
	{/if}

	Note: statistics are based on aquatic networks cut by
	{networkType === 'dams' ? 'waterfalls and dams' : 'waterfalls, dams, and road-related barriers'}
	{networkType === 'largefish_barriers'
		? ' based on their passability for large-bodied fish'
		: null}
	{networkType === 'smallfish_barriers'
		? ' based on their passability for small-bodied fish'
		: null}
	{removed
		? `, including any that were present at the time this
                ${barrierTypeLabel} was removed, with the exception of those
                directly upstream that were removed in the same year as this barrier.
                All barriers removed prior to 2000 or where the year they were
                removed was unknown were lumped together for this analysis`
		: null}.
</div>

{#if totalupstreammiles > 0}
	<Entry label="Percent of the upstream network in unaltered stream channels">
		<b>{formatPercent(percentUnaltered)}%</b>
	</Entry>

	<Entry label="Percent of the upstream network in resilient watersheds">
		<b>{formatPercent(percentresilient)}%</b>
	</Entry>

	<Entry label="Percent of the upstream network in coldwater habitat watersheds">
		<b>{formatPercent(percentcold)}%</b>
	</Entry>
{/if}

<Entry
	label={barrierType === 'waterfalls'
		? 'Number of size classes upstream'
		: `Number of size classes that ${
				removed ? 'were' : 'could be'
			} gained by removing this barrier`}
>
	<div class={cn({ 'font-bold': sizeclasses > 0 })}>
		{sizeclasses}
	</div>
</Entry>

<Entry label="Percent of upstream floodplain composed of natural landcover">
	<b>{formatNumber(landcover, 0)}%</b>
</Entry>

<Entry label="Total area of unaltered lakes and ponds">
	<div class={cn({ 'font-bold': unalteredwaterbodyacres > 0 })}>
		{formatNumber(unalteredwaterbodyacres)} acres
	</div>
	<ExpandableParagraph
		snippet="Note: this metric is based on all unaltered lakes and ponds that
            intersect any stream reach in the upstream functional network..."
		class="text-xs text-muted-foreground mt-2"
	>
		Note: this metric is based on all unaltered lakes and ponds that intersect any stream reach in
		the upstream functional network, and exclude any specifically marked by their data provider as
		altered as well as any that are associated with dams in this inventory.
	</ExpandableParagraph>
</Entry>

<Entry label="Total area of unaltered freshwater wetlands">
	<div class={cn({ 'font-bold': unalteredwetlandacres > 0 })}>
		{formatNumber(unalteredwetlandacres)} acres
	</div>

	<ExpandableParagraph
		snippet="Note: this metric is based on all unaltered freshwater wetlands that
            intersect any stream reach in the upstream functional network."
		class="text-xs text-muted-foreground mt-2"
	>
		Note: this metric is based on all unaltered freshwater wetlands that intersect any stream reach
		in the upstream functional network. Wetlands are derived from the National Wetlands Inventory
		(freshwater scrub-shrub, freshwater forested, freshwater emergent) and NHD (swamp/marsh) and
		exclude any specifically marked by their data provider as altered.
	</ExpandableParagraph>
</Entry>

{#if upstreambarrier}
	<Entry label="Nearest upstream barrier">
		{barrierTypeLabelSingular[`${upstreambarrier}s` as BarrierTypePlural]}
		<br />
		id: {upstreambarriersarpid}
		<br />
		{formatNumber(upstreambarriermiles)} miles upstream
	</Entry>
{/if}

{#if downstreambarrier}
	<Entry label="Downstream barrier">
		{barrierTypeLabelSingular[`${downstreambarrier}s` as BarrierTypePlural]}
		<br />
		id: {downstreambarriersarpid}
		<br />
		{formatNumber(downstreambarriermiles)} miles downstream
	</Entry>
{/if}

{#if unranked && !invasive}
	<Entry>
		<div class="text-xs text-muted-foreground">
			Note: this {barrierTypeLabel} excluded from ranking based on field reconnaissance, manual review
			of aerial imagery, or other information about this {barrierTypeLabel}.
		</div>
	</Entry>
{/if}
