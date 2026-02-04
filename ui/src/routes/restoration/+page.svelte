<script lang="ts">
	import { summaryStats } from '$lib/config/summaryStats'
	import { RestorationPage } from '$lib/components/restoration'
</script>

<RestorationPage
	type="Region"
	data={{
		id: 'total',
		name: 'the full analysis region',
		boundaryLayer: 'boundary',
		...summaryStats
	}}
/>
