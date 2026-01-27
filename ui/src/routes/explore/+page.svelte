<script lang="ts">
	import { summaryStats } from '$lib/config/summaryStats'
	import { ExplorePage } from '$lib/components/explore'

	const coreData = {
		id: 'total',
		name: 'full analysis region',
		layer: 'boundary'
	}
</script>

<ExplorePage name={coreData.name} type="Region" details={{ ...coreData, ...summaryStats }} />
