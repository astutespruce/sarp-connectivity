<script lang="ts">
	const { children } = $props()
</script>

<div
	class="flex items-center p-2 absolute top-0 z-1000 l-3 bg-white text-sm shadow-md rounded-b-md [&_button]:lowercase [&:button]:py-1 [&:button]:px-2"
>
	{@render children()}
</div>
