<script lang="ts">
	import { barrierTypeLabelSingular, EPA_CAUSE_CODES } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { formatNumber, formatPercent } from '$lib/util/format'
	import { cn } from '$lib/utils'

	const {
		barrierType,
		networkType,
		totalmainstemupstreammiles,
		perennialmainstemupstreammiles,
		alteredmainstemupstreammiles,
		unalteredmainstemupstreammiles,
		mainstemsizeclasses,
		freemainstemdownstreammiles,
		freeperennialmainstemdownstreammiles,
		freealteredmainstemdownstreammiles,
		freeunalteredmainstemdownstreammiles,
		mainstemupstreamimpairment,
		mainstemdownstreamimpairment,
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

	const numCols = $derived(totalmainstemupstreammiles > 0 ? 3 : 2)
</script>

<section>
	<h2>Mainstem network information</h2>
	<div class="text-xs text-muted-foreground">
		Upstream mainstem networks include the stream reaches upstream that are the same stream order as
		the one associated with this barrier (excludes smaller tributaries) with at least 1 square mile
		of drainage area. Downstream mainstem networks are based on the linear flow direction through
		the same stream order to the next barrier downstream, a change in stream order, or the
		downstream-most point on the network.
	</div>

	<div
		class={`grid sm:grid-cols-${numCols} gap-4 mt-4 text-sm leading-snug sm:[&>div]:py-2 sm:[&>div+div]:border-l sm:[&>div+div]:border-l-grey-2 sm:[&>div+div]:pl-4`}
	>
		<div>
			<b>{formatNumber(mainstemGainMiles, 2, true)} total miles</b>
			{removed ? 'were' : 'could be'} gained by removing this
			{barrierTypeLabel} including
			<b>{formatNumber(perennialMainstemGainMiles, 2, true)} miles</b> of perennial reaches.
		</div>

		{#if totalmainstemupstreammiles > 0}
			<div>
				<b>
					{formatPercent(percentUnaltered)}% of the upstream mainstem network
				</b>
				is in unaltered stream reaches.
			</div>
		{/if}

		<div>
			<b>
				{mainstemsizeclasses} mainstem river size
				{mainstemsizeclasses === 1 ? 'class' : 'classes'}
			</b>
			{removed ? 'were' : 'could be'} gained by removing this
			{barrierTypeLabel}.
		</div>
	</div>

	<table cellpadding="0" cellspacing="0" class="mt-12">
		<thead>
			<tr>
				<th>Mainstem network metric</th>
				<th>upstream network</th>
				<th>downstream network</th>
			</tr>
		</thead>
		<tbody>
			<tr>
				<td>Total miles</td>
				<td class={cn({ 'font-bold': mainstemGainMilesSide === 'upstream' })}>
					{formatNumber(totalmainstemupstreammiles, 2, true)}
				</td>
				<td class={cn({ 'font-bold': mainstemGainMilesSide === 'downstream' })}>
					{formatNumber(freemainstemdownstreammiles, 2, true)}
				</td>
			</tr>

			<tr>
				<td>Perennial miles</td>
				<td class={cn({ 'font-bold': perennialMainstemGainMilesSide === 'upstream' })}>
					{formatNumber(perennialmainstemupstreammiles, 2, true)}
				</td>
				<td class={cn({ 'font-bold': perennialMainstemGainMilesSide === 'downstream' })}>
					{formatNumber(freeperennialmainstemdownstreammiles, 2, true)}
				</td>
			</tr>

			<tr>
				<td>Ephemeral / intermittent miles</td>
				<td>
					{formatNumber(intermittentmainstemupstreammiles, 2, true)}
				</td>
				<td>
					{formatNumber(freeintermittentmainstemdownstreammiles, 2, true)}
				</td>
			</tr>

			<tr>
				<td>Altered miles</td>
				<td>{formatNumber(alteredmainstemupstreammiles, 2, true)}</td>
				<td>
					{formatNumber(freealteredmainstemdownstreammiles, 2, true)}
				</td>
			</tr>

			<tr>
				<td>Unaltered miles</td>
				<td>{formatNumber(unalteredmainstemupstreammiles, 2, true)}</td>
				<td>
					{formatNumber(freeunalteredmainstemdownstreammiles, 2, true)}
				</td>
			</tr>

			{#if mainstemupstreamimpairment || mainstemdownstreamimpairment}
				<tr>
					<td>
						Water quality impairments
						<br />
						present:
					</td>
					<td>
						{#each mainstemupstreamimpairment.split(',') as code (code)}
							<div>{EPA_CAUSE_CODES[code as keyof typeof EPA_CAUSE_CODES]}</div>
						{/each}
					</td>
					<td>
						{#each mainstemdownstreamimpairment.split(',') as code (code)}
							<div>{EPA_CAUSE_CODES[code as keyof typeof EPA_CAUSE_CODES]}</div>
						{/each}
					</td>
				</tr>
			{/if}
		</tbody>
	</table>

	<div class="text-xs text-muted-foreground mt-8">
		{#if alwaysUseUpstream}
			Note: upstream miles are used because the downstream network flows into the {flowstogreatlakes ===
			1
				? 'Great Lakes'
				: 'ocean'} and there are no barriers downstream.
			<br />
			<br />
		{/if}

		Note: Statistics are based on aquatic networks cut by
		{networkType === 'dams'
			? 'waterfalls and dams'
			: 'waterfalls, dams, and road-related barriers'}{networkType === 'largefish_barriers'
			? ' based on their passability for large-bodied fish'
			: null}{networkType === 'smallfish_barriers'
			? ' based on their passability for small-bodied fish'
			: null}{removed
			? `, including any that were present at the time this
            ${barrierTypeLabel} was removed, with the exception of those directly
            upstream that were removed in the same year as this barrier.
            All barriers removed prior to 2000 or where the year they were removed
            was unknown were lumped together for this analysis`
			: null}.

		{#if mainstemupstreamimpairment || mainstemdownstreamimpairment}
			<br />
			<br />
			Water quality impairments based on based on
			<a href="https://www.epa.gov/waterdata/attains" target="_blank" rel="external">
				EPA ATTAINS
			</a>
			water quality data within the mainstem network.
		{/if}
	</div>
</section>
