<script lang="ts">
	import Bar from './FilterBar.svelte'

	const { bars, max, onValueClick } = $props()
</script>

{#each bars as bar (bar.value)}
	<Bar {...bar} {max} onClick={onValueClick} />
{/each}
