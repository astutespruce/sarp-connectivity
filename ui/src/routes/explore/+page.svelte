<script lang="ts">
	import { summaryStats } from '$lib/config/summaryStats'
	import { ExplorePage } from '$lib/components/explore'
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
