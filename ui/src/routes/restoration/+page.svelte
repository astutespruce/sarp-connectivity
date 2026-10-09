<script lang="ts">
	import { summaryStats } from '#lib/config/summaryStats.js'
	import { RestorationPage } from '#lib/components/restoration/index.js'
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
