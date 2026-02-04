<script lang="ts">
	const { children } = $props()
</script>

<div
	class="flex items-center gap-2 p-2 absolute top-0 z-10 left-3 bg-white text-xs shadow-md shadow-grey-8 rounded-b-md"
>
	{@render children()}
</div>
