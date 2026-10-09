<script lang="ts">
	import { summaryStats } from '#lib/config/summaryStats.js'
	import { ExplorePage } from '#lib/components/explore/index.js'
</script>

<ExplorePage
	type="Region"
	data={{
		id: 'total',
		name: 'the full analysis region',
		boundaryLayer: 'boundary',
		...summaryStats
	}}
/>
