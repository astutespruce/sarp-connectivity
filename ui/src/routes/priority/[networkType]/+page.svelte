<script lang="ts">
	import { SITE_NAME } from '#lib/config/constants.js'
	import { barrierTypeLabels } from '#lib/config/constants.js'
	import type { BarrierTypePlural } from '#lib/config/types.js'
	import { Workflow } from '#lib/components/priority/index.js'

	const { params } = $props()
</script>

<svelte:head>
	<title>
		Prioritize {barrierTypeLabels[params.networkType as BarrierTypePlural]} | {SITE_NAME}
	</title>
</svelte:head>

<Workflow networkType={params.networkType} />
