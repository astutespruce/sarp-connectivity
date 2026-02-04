<script lang="ts">
	import { SALMONID_ESU, TROUT } from '$lib/config/constants'
	import { formatNumber } from '$lib/util/format'

	const { barrierType, tespp, statesgcnspp, regionalsgcnspp, trout, salmonidesu } = $props()
	const troutSpp = $derived(
		trout ? trout.split(',').map((code: keyof typeof TROUT) => TROUT[code]) : []
	)
</script>

<section>
	<h2>Species information for this subwatershed</h2>

	<div class="text-sm">
		Data sources in the subwatershed containing this
		{barrierType === 'dams' ? 'dam' : 'road/stream crossing'} have recorded:
	</div>

	<div
		class="grid sm:grid-cols-3 gap-4 text-sm mt-4 leading-snug sm:[&>div]:py-2 sm:[&>div+div]:border-l sm:[&>div+div]:border-l-grey-2 sm:[&>div+div]:pl-4"
	>
		<div>
			<b>{formatNumber(tespp)}</b> federally-listed threatened and endangered aquatic species
		</div>
		<div>
			<b>{statesgcnspp}</b> state-listed aquatic Species of Greatest Conservation Need (SGCN)
		</div>
		<div>
			<b>{regionalsgcnspp}</b> regionally-listed aquatic Species of Greatest Conservation Need
		</div>
	</div>

	<div class="mt-6 text-sm">
		{#if trout}This subwatershed includes recorded observations of {troutSpp.join(
				troutSpp.length === 2 ? ' and ' : ', '
			)}.
		{:else}
			No interior or eastern native trout species have been recorded in this subwatershed.
		{/if}
	</div>

	{#if salmonidesu}
		<div class="mt-6 text-sm">
			This subwatershed falls within the following salmon Evolutionarily Significant Units (ESU) /
			steelhead trout Discrete Population Segments (DPS):
			<ul class="list-disc list-outside mt-1 pl-8">
				{#each salmonidesu.split(',') as code (code)}
					<li>{SALMONID_ESU[code as keyof typeof SALMONID_ESU]}</li>
				{/each}
			</ul>
		</div>
	{/if}

	<div class="text-xs text-muted-foreground mt-8">
		Note: State and regionally listed species of greatest conservation need may include state-listed
		threatened and endangered species. Trout species presence is based on occurrences of Apache,
		brook, bull, cutthroat, Gila, lake, and redband trout species. Species information is very
		incomplete and only includes species that have been identified by available data sources for
		this subwatershed. These species may or may not be directly impacted by this barrier. The
		absence of species in the available data does not necessarily indicate the absence of species in
		the subwatershed.
	</div>
</section>
