<script lang="ts">
	import { SITE_NAME } from '#lib/config/constants.js'
	import { Workflow } from '#lib/components/survey/index.js'
</script>

<svelte:head>
	<title>
		Select road crossings to survey | {SITE_NAME}
	</title>
</svelte:head>

<Workflow />
