<script lang="ts">
	import { resolve } from '$app/paths'
	import { barrierTypeLabelSingular } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { formatNumber } from '$lib/util/format'

	const { barrierType, diadromoushabitat, habitat } = $props()
	const sources = $derived(
		[...new Set(habitat.map(({ source }: { source: string }) => source))].join(', ')
	)
</script>

<section>
	<h2>Species habitat information for this network</h2>

	<table cellpadding="0" cellspacing="0" class="mt-4">
		<thead>
			<tr>
				<th>Species or group</th>
				<th class="max-w-48">upstream miles</th>
				<th class="max-w-48"
					>downstream miles
					<div class="text-xs text-muted-foreground font-normal">free-flowing miles only</div>
				</th>
			</tr>
		</thead>
		<tbody>
			{#each habitat as species (species.id)}
				<tr>
					<td
						>{species.label}
						{#if species.limit}
							<div class="text-xs text-muted-foreground">
								Data are known to be limited to {species.limit}.
							</div>
						{/if}
					</td>

					<td>
						{species.upstreammiles > 0 && species.upstreammiles < 0.1
							? '<0.1'
							: formatNumber(species.upstreammiles)}
					</td>
					<td
						>{species.downstreammiles > 0 && species.downstreammiles < 0.1
							? '<0.1'
							: formatNumber(species.downstreammiles)}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>

	{#if diadromoushabitat === 1}
		<div class="text-sm mt-8">
			This {barrierTypeLabelSingular[barrierType as BarrierTypePlural]} is located on a reach with anadromous
			/ catadromous species habitat.
		</div>

		<div class="text-xs text-muted-foreground mt-8">
			Note: instream habitat is estimated from data provided by regional partners ({sources}) and
			assigned to NHDPlusHR flowlines; these estimates do not fully account for elevation gradients
			or other natural barriers that may have been present in the source data. Habitat data are
			limited to available data sources and are not comprehensive and do not fully capture all
			current or potential habitat for a given species or group across its range. For more
			information, please see the
			<a href={resolve('/methods/habitat/', {})}>analysis methods</a>.
		</div>
	{/if}
</section>
