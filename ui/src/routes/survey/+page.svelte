<script lang="ts">
	import { SITE_NAME } from '$lib/env'
	import { Workflow } from '$lib/components/survey'
</script>

<svelte:head>
	<title>
		Select road crossings to survey | {SITE_NAME}
	</title>
</svelte:head>

<Workflow />
