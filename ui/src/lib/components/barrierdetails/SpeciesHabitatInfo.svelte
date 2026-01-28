<script lang="ts">
	import { resolve } from '$app/paths'
	import { barrierTypeLabelSingular } from '$lib/config/constants'
	import { ExpandableParagraph } from '$lib/components/text'
	import { InfoTooltip } from '$lib/components/tooltip'
	import { formatNumber } from '$lib/util/format'

	import Entry from './Entry.svelte'
	import type { BarrierTypePlural } from '$lib/config/types'

	const { barrierType, diadromoushabitat = null, habitat = [] } = $props()
</script>

<ExpandableParagraph
	snippet="Instream habitat is estimated from data provided by regional
        partners and assigned to NHDPlusHR flowlines..."
	class="text-xs text-muted-foreground mt-2 mb-4 mx-2"
>
	Instream habitat is estimated from data provided by regional partners and assigned to NHDPlusHR
	flowlines; these estimates do not fully account for elevation gradients or other natural barriers
	that may have been present in the source data. Habitat data are limited to available data sources
	and are not comprehensive and do not fully capture all current or potential habitat for a given
	species or group across its range. For more information, please see the
	<a href={resolve('/methods/habitat/')}>analysis methods</a>.
</ExpandableParagraph>

<table cellpadding="0" cellspacing="0">
	<thead>
		<tr>
			<th class="w-48">Species or group</th>
			<th>Upstream miles</th>
			<th>
				Downstream miles
				<div class="text-xs text-muted-foreground font-normal">
					free-flowing
					<br />
					miles only
				</div>
			</th>
		</tr>
	</thead>
	<tbody>
		{#each habitat as species (species.id)}
			<tr>
				<td>
					<InfoTooltip title={species.label}>
						Estimated instream habitat based on data provided by
						{species.source}.
						{#if species.limit}
							<br />
							Data are known to be limited to {species.limit}.
						{/if}
					</InfoTooltip>
				</td>
				<td
					>{species.upstreammiles > 0 && species.upstreammiles < 0.1
						? '<0.1'
						: formatNumber(species.upstreammiles)}</td
				>
				<td>
					{species.downstreammiles > 0 && species.downstreammiles < 0.1
						? '<0.1'
						: formatNumber(species.downstreammiles)}
				</td>
			</tr>
		{/each}
	</tbody>
</table>

{#if diadromoushabitat === 1}
	<Entry>
		This {barrierTypeLabelSingular[barrierType as BarrierTypePlural]} is located on a reach with anadromous
		/ catadromous species habitat.
	</Entry>
{/if}
