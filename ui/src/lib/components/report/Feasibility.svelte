<script lang="ts">
	import { RECON, FEASIBILITYCLASS } from '$lib/config/constants'
	const { recon, feasibilityclass } = $props()
</script>

<section>
	<h3>Feasibility & conservation benefit</h3>

	<div class="report-entries">
		<div>
			Feasibility: {FEASIBILITYCLASS[feasibilityclass as keyof typeof FEASIBILITYCLASS]}
		</div>
		{#if recon > 0}
			<div>Field recon notes: {RECON[recon as keyof typeof RECON]}</div>
		{/if}
	</div>
</section>
