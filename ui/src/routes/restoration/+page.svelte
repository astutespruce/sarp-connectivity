<script lang="ts">
	import { summaryStats } from '$lib/config/summaryStats'
	import { RestorationPage } from '$lib/components/restoration'

	const coreData = {
		id: 'total',
		name: 'the full analysis region',
		layer: 'boundary'
	}
</script>

<RestorationPage name={coreData.name} type="Region" details={{ ...coreData, ...summaryStats }} />
