<script lang="ts">
	import { barrierTypeLabelSingular } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'

	const { barrierType, invasive, invasivenetwork } = $props()
	const barrierTypeLabel = $derived(barrierTypeLabelSingular[barrierType as BarrierTypePlural])
</script>

<section>
	<h3>Invasive species management</h3>

	<div>
		{#if invasive}
			This {barrierTypeLabel} is identified as a beneficial to restricting the movement of invasive species.
		{:else if invasivenetwork === 1}
			Upstream of a barrier identified as a beneficial to restricting the movement of invasive
			species.
		{/if}
	</div>
</section>
