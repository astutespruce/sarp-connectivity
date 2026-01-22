<script lang="ts">
	import ScoreChart from './ScoreChart.svelte'

	const { nc, wc, ncwc, pnc, pwc, pncwc, mnc, mwc, mncwc } = $props()
</script>

<div>
	<div class="font-bold text-lg">Full networks</div>
	<div class="px-4">
		<ScoreChart label="Network Connectivity Tier" score={nc.score} tier={nc.tier} />
		<ScoreChart label="Watershed Condition Tier" score={wc.score} tier={wc.tier} />
		<ScoreChart
			label="Network Connectivity & Watershed Condition Tier"
			score={ncwc.score}
			tier={ncwc.tier}
		/>

		<div class="text-xs test-muted-foreground mt-4">
			Note: network connectivity is based on the total perennial length in a given network.
			Watershed condition is based on the percent of the total length of stream reaches in the
			network that are not altered (canals / ditches), the number of unique stream size classes, and
			the percent of natural landcover in the floodplains.
		</div>
	</div>
</div>

<div>
	<div class="font-bold text-lg">Perennial reaches only</div>
	<div class="px-4">
		<ScoreChart label="Perennial Network Connectivity Tier" score={pnc.score} tier={pnc.tier} />
		<ScoreChart label="Perennial Watershed Condition Tier" score={pwc.score} tier={pwc.tier} />
		<ScoreChart
			label="Perennial Network Connectivity & Watershed Condition Tier"
			score={pncwc.score}
			tier={pncwc.tier}
		/>
		<div class="text-xs text-muted-foreground mt-4">
			Note: perennial network connectivity is based on the total perennial (non-intermittent or
			ephemeral) length in a given network. Perennial watershed condition is based on the percent of
			the total length of perennial stream reaches that are not altered (canals / ditches), the
			number of unique stream size classes in perennial reaches, and the percent of natural
			landcover in the floodplains for the full network.
		</div>
	</div>
</div>

<div>
	<div class="font-bold text-lg">Mainstem networks</div>
	<div class="px-4">
		<ScoreChart label="Mainstem Network Connectivity Tier" score={mnc.score} tier={mnc.tier} />
		<ScoreChart label="Mainstem Watershed Condition Tier" score={mwc.score} tier={mwc.tier} />
		<ScoreChart
			label="Mainstem Network Connectivity & Watershed Condition Tier"
			score={mncwc.score}
			tier={mncwc.tier}
		/>
		<div class="text-xs text-muted-foreground">
			Note: mainstem network connectivity is based on the total mainstem network length in a given
			network. Mainstem watershed condition is based on the percent of the total length of stream
			reaches in the mainstem network that are not altered (canals / ditches), the number of unique
			stream size classes in the mainstem network, and the percent of natural landcover in the
			floodplains for the full network.
		</div>
	</div>
</div>
