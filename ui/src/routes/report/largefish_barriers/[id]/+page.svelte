<script lang="ts">
	import { Report } from '$lib/components/report'

	const { params } = $props()
</script>

<Report sarpid={params.id} networkType="largefish_barriers" />
