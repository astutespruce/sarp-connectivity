<script lang="ts">
	import { barrierTypeLabels, STATES } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { cn } from '$lib/utils'

	const {
		barrierType,
		networkType,
		state,
		invasive,
		state_nc_tier,
		state_wc_tier,
		state_ncwc_tier,
		state_pnc_tier,
		state_pwc_tier,
		state_pncwc_tier,
		state_mnc_tier,
		state_mwc_tier,
		state_mncwc_tier,
		huc8_nc_tier,
		huc8_wc_tier,
		huc8_ncwc_tier,
		huc8_pnc_tier,
		huc8_pwc_tier,
		huc8_pncwc_tier,
		huc8_mnc_tier,
		huc8_mwc_tier,
		huc8_mncwc_tier
	} = $props()

	const hasStateTiers = $derived(networkType === 'dams' && state_ncwc_tier !== -1)
	const hasHUC8Tiers = $derived(huc8_ncwc_tier !== -1)
	const barrierTypeLabel = $derived(barrierTypeLabels[barrierType as BarrierTypePlural])
</script>

<section>
	<h2>Connectivity ranks</h2>

	{#if invasive}
		This {barrierTypeLabel} was excluded from prioritization because it provides an ecological benefit
		by restricting the movement of invasive aquatic species.
	{:else}
		<div class="text-xs text-muted-foreground text-center">
			connectivity tiers range from 20 (lowest) to 1 (highest)
		</div>

		{#if hasStateTiers}
			<table cellpadding="0" cellspacing="0" class="mt-8">
				<thead>
					<tr>
						<th>
							Compared to other {barrierTypeLabel} in {STATES[state as keyof typeof STATES]}
						</th>
						<th>full network</th>
						<th>perennial reaches</th>
						<th>mainstem network</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td>Network connectivity tier</td>
						<td>{state_nc_tier}</td>
						<td>{state_pnc_tier}</td>
						<td>{state_mnc_tier}</td>
					</tr>
					<tr>
						<td>Watershed condition tier</td>
						<td>{state_wc_tier}</td>
						<td>{state_pwc_tier}</td>
						<td>{state_mwc_tier}</td>
					</tr>
					<tr>
						<td>
							Combined network connectivity &amp;
							<br />
							watershed condition tier
						</td>
						<td>{state_ncwc_tier}</td>
						<td>{state_pncwc_tier}</td>
						<td>{state_mncwc_tier}</td>
					</tr>
				</tbody>
			</table>
		{/if}

		{#if hasHUC8Tiers}
			<table
				cellpadding="0"
				cellspacing="0"
				class={cn('mt-8', {
					'mt-12': hasStateTiers
				})}
			>
				<thead>
					<tr>
						<th>
							Compared to other {barrierTypeLabel} in this subbasin
						</th>
						<th>full network</th>
						<th>perennial reaches</th>
						<th>mainstem network</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td>Network connectivity tier</td>
						<td>{huc8_nc_tier}</td>
						<td>{huc8_pnc_tier}</td>
						<td>{huc8_mnc_tier}</td>
					</tr>
					<tr>
						<td>Watershed condition tier</td>
						<td>{huc8_wc_tier}</td>
						<td>{huc8_pwc_tier}</td>
						<td>{huc8_mwc_tier}</td>
					</tr>
					<tr>
						<td>
							Combined network connectivity &amp;
							<br />
							watershed condition tier
						</td>
						<td>{huc8_ncwc_tier}</td>
						<td>{huc8_pncwc_tier}</td>
						<td>{huc8_mncwc_tier}</td>
					</tr>
				</tbody>
			</table>

			<div class="text-xs text-muted-foreground mt-8">
				Note: network connectivity is based on the total perennial length in a given network.
				Watershed condition is based on the percent of the total length of stream reaches in the
				network that are not altered (canals / ditches), the number of unique stream size classes,
				and the percent of natural landcover in the floodplains. Perennial network connectivity is
				based on the total perennial (non-intermittent or ephemeral) length in a given network.
				Perennial watershed condition is based on the percent of the total length of perennial
				stream reaches that are not altered (canals / ditches), the number of unique stream size
				classes in perennial reaches, and the percent of natural landcover in the floodplains for
				the full network. Mainstem network connectivity is based on the total mainstem network
				length in a given network. Mainstem watershed condition is based on the percent of the total
				length of stream reaches in the mainstem network that are not altered (canals / ditches),
				the number of unique stream size classes in the mainstem network, and the percent of natural
				landcover in the floodplains for the full network.
			</div>
		{/if}
	{/if}
</section>
