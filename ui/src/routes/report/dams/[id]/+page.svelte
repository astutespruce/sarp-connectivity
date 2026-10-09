<script lang="ts">
	import { Report } from '#lib/components/report/index.js'

	const { params } = $props()
</script>

<Report sarpid={params.id} networkType="dams" />
