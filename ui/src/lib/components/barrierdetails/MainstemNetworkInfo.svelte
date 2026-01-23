<script lang="ts">
	import { barrierTypeLabelSingular, EPA_CAUSE_CODES } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { formatNumber, formatPercent } from '$lib/util/format'
	import { InfoTooltip } from '$lib/components/tooltip'
	import { cn } from '$lib/utils'
	import Entry from './Entry.svelte'

	const {
		barrierType,
		networkType,
		totalmainstemupstreammiles,
		perennialmainstemupstreammiles,
		alteredmainstemupstreammiles,
		unalteredmainstemupstreammiles,
		freemainstemdownstreammiles,
		freeperennialmainstemdownstreammiles,
		freealteredmainstemdownstreammiles,
		freeunalteredmainstemdownstreammiles,
		mainstemupstreamimpairment,
		mainstemdownstreamimpairment,
		mainstemsizeclasses,
		removed,
		flowstoocean,
		flowstogreatlakes,
		totaldownstreamdams,
		totaldownstreamsmallbarriers,
		totaldownstreamwaterfalls
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

	const mainstemGainMiles = $derived(
		Math.min(totalmainstemupstreammiles, freemainstemdownstreammiles)
	)

	const mainstemGainMilesSide = $derived(
		alwaysUseUpstream || mainstemGainMiles === totalmainstemupstreammiles
			? 'upstream'
			: 'downstream'
	)

	const perennialMainstemGainMiles = $derived(
		Math.min(perennialmainstemupstreammiles, freeperennialmainstemdownstreammiles)
	)

	const perennialMainstemGainMilesSide = $derived(
		alwaysUseUpstream || perennialMainstemGainMiles === perennialmainstemupstreammiles
			? 'upstream'
			: 'downstream'
	)

	const intermittentmainstemupstreammiles = $derived(
		totalmainstemupstreammiles - perennialmainstemupstreammiles
	)

	const freeintermittentmainstemdownstreammiles = $derived(
		freemainstemdownstreammiles - freeperennialmainstemdownstreammiles
	)

	const percentUnaltered = $derived(
		totalmainstemupstreammiles
			? (100 * unalteredmainstemupstreammiles) / totalmainstemupstreammiles
			: 0
	)
</script>

<div class="text-xs text-muted-foreground mx-2">
	Upstream mainstem networks include the stream reaches upstream that are the same stream order as
	the one associated with this barrier (excludes smaller tributaries) with at least 1 square mile of
	drainage area. Downstream mainstem networks are based on the linear flow direction through the
	same stream order to the next barrier downstream, a change in stream order, or the downstream-most
	point on that network.
</div>

<Entry>
	<table>
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
						Total mainstem miles upstream is the sum of all river and stream lengths in contiguous
						stream reaches of the same stream order order as this
						{barrierTypeLabel} and with drainage area ≥ 1 square mile.
						<br />
						<br />
						Total mainstem miles downstream is the sum of all river and stream lengths in the linear flow
						direction network immediately downstream of this network extending to the next barrier downstream
						or downstream-most point of the network, excluding all lengths within altered waterbodies.
					</InfoTooltip>
				</td>
				<td class={cn({ 'font-bold': mainstemGainMilesSide === 'upstream' })}>
					{formatNumber(totalmainstemupstreammiles, 2, true)}
				</td>
				<td class={cn({ 'font-bold': mainstemGainMilesSide === 'downstream' })}>
					{formatNumber(freemainstemdownstreammiles, 2, true)}
				</td>
			</tr>

			<tr>
				<td>
					Perennial miles
					<InfoTooltip title="Perennial miles">
						Total perennial mainstem miles upstream is the sum of all perennial reach lengths in the
						upstream mainstem network. Perennial reaches are all those that are not specifically
						identified as ephemeral or intermittent. Perennial reaches are not necessarily
						contiguous.
						<br />
						<br />
						Total perennial miles downstream is the sum of all perennial reach lengths in the linear flow
						direction network immediately downstream of this network, excluding all lengths within altered
						waterbodies.
					</InfoTooltip>
				</td>
				<td class={cn({ 'font-bold': perennialMainstemGainMilesSide === 'upstream' })}>
					{formatNumber(perennialmainstemupstreammiles, 2, true)}
				</td>
				<td class={cn({ 'font-bold': perennialMainstemGainMilesSide === 'downstream' })}>
					{formatNumber(freeperennialmainstemdownstreammiles, 2, true)}
				</td>
			</tr>

			<tr>
				<td>
					Intermittent miles
					<InfoTooltip title="Ephemeral / intermittent miles">
						Total ephemeral and intermittent mainstem miles upstream is the sum of all ephemeral and
						intermittent reach lengths in the upstream mainstem network.
						<br />
						<br />
						Total ephemeral and intermittent miles downstream is the sum of all ephemeral and intermittent
						reach lengths in the downstream mainstem network in the linear flow direction immediately
						downstream of this network, excluding all lengths within altered waterbodies.
					</InfoTooltip>
				</td>
				<td>
					{formatNumber(intermittentmainstemupstreammiles, 2, true)}
				</td>
				<td>
					{formatNumber(freeintermittentmainstemdownstreammiles, 2, true)}
				</td>
			</tr>

			<tr>
				<td
					>Altered miles
					<InfoTooltip title="Altered miles">
						Total altered mainstem miles upstream is the sum of all reach lengths specifically
						identified as altered (canal / ditch, within reservoir, or other channel alteration)
						within the upstream mainstem network.
						<br />
						<br />
						Total altered miles downstream is the sum of all altered reach lengths in the downstream mainstem
						network in the linear flow direction immediately downstream of this network, excluding all
						lengths within altered waterbodies.
					</InfoTooltip>
				</td>
				<td>{formatNumber(alteredmainstemupstreammiles, 2, true)}</td>
				<td>
					{formatNumber(freealteredmainstemdownstreammiles, 2, true)}
				</td>
			</tr>

			<tr>
				<td>
					Unaltered miles
					<InfoTooltip title="Unaltered miles">
						Total unaltered mainstem miles upstream is the sum of all reach lengths not specifically
						identified as altered (canal / ditch, within reservoir, or other channel alteration)
						within the upstream mainstem network.
						<br />
						<br />
						Total unaltered miles downstream is the sum of all unaltered reach lengths in the downstream
						mainstem network in the linear flow direction immediately downstream of this network, excluding
						all lengths within altered waterbodies.
					</InfoTooltip>
				</td>
				<td>{formatNumber(unalteredmainstemupstreammiles, 2, true)}</td>
				<td>
					{formatNumber(freeunalteredmainstemdownstreammiles, 2, true)}
				</td>
			</tr>

			{#if barrierType !== 'waterfalls'}
				<tr class="border-t-2 border-t-grey-4">
					<td>
						<b>Total mainstem miles gained</b>
						<InfoTooltip title="Total mainstem miles gained">
							The total mainstem miles that
							{removed ? 'were' : 'could be'} gained by removing this barrier is the lesser of the upstream
							mainstem network miles or free-flowing downstream mainstem network miles.
						</InfoTooltip>
					</td>
					<td
						class={cn('invisible', { 'visible font-bold': mainstemGainMilesSide === 'upstream' })}
					>
						{formatNumber(totalmainstemupstreammiles, 2, true)}
						{#if alwaysUseUpstream}<sup>*</sup>{/if}
					</td>
					<td
						class={cn('invisible', { 'visible font-bold': mainstemGainMilesSide === 'downstream' })}
					>
						{formatNumber(freemainstemdownstreammiles, 2, true)}
					</td>
				</tr>

				<tr>
					<td>
						<b>Perennial mainstem miles gained</b>
						<InfoTooltip title="Perennial mainstem miles gained">
							The total perennial mainstem miles that
							{removed ? 'were' : 'could be'} gained by removing this barrier is the lesser of the upstream
							perennial mainstem network miles or free-flowing downstream mainstem network perennial miles.
						</InfoTooltip>
					</td>
					<td
						class={cn('invisible', {
							'visible font-bold': perennialMainstemGainMilesSide === 'upstream'
						})}
					>
						{formatNumber(perennialmainstemupstreammiles, 2, true)}
						{#if alwaysUseUpstream}<sup>*</sup>{/if}
					</td>
					<td
						class={cn('invisible', {
							'visible font-bold': perennialMainstemGainMilesSide === 'downstream'
						})}
					>
						{formatNumber(freeperennialmainstemdownstreammiles, 2, true)}
					</td>
				</tr>
			{/if}
		</tbody>
	</table>

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
</Entry>

{#if totalmainstemupstreammiles}
	<Entry label="Percent of the upstream network in unaltered stream channels">
		<b>{formatPercent(percentUnaltered)}%</b>
	</Entry>

	<Entry
		label={barrierType === 'waterfalls'
			? 'Number of mainstem size classes upstream'
			: `Number of mainstem size classes that ${
					removed ? 'were' : 'could be'
				} gained by removing this barrier`}
	>
		<div class={cn({ 'font-bold': mainstemsizeclasses > 0 })}>
			{mainstemsizeclasses}
		</div>
	</Entry>
{/if}

{#if mainstemupstreamimpairment || mainstemdownstreamimpairment}
	<Entry label="Water quality impairments present">
		{#if mainstemupstreamimpairment}
			<div class="ml-2">
				upstream:
				{mainstemupstreamimpairment
					.split(',')
					.map((code: keyof typeof EPA_CAUSE_CODES) => EPA_CAUSE_CODES[code])
					.join(', ')}
			</div>
		{/if}

		{#if mainstemdownstreamimpairment}
			<div class="ml-2">
				{mainstemdownstreamimpairment
					.split(',')
					.map((code: keyof typeof EPA_CAUSE_CODES) => EPA_CAUSE_CODES[code])
					.join(', ')}
			</div>
		{/if}

		<div class="text-xs text-muted-foreground mt-1 ml-2">
			based on
			<a href="https://www.epa.gov/waterdata/attains" target="_blank" rel="external">
				EPA ATTAINS
			</a>
			water quality data within the mainstem network
		</div>
	</Entry>
{/if}
