<script lang="ts">
	import { cn } from '$lib/utils'

	const { author = null, url = null, children, class: className = null } = $props()
</script>

<div class={cn('max-h-64 overflow-hidden relative', className)}>
	{@render children()}

	{#if author}
		<div class="absolute bottom-0 right-0 py-1 px-2 bg-black/75 text-white text-xs">
			Photo:

			{#if url}
				<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
				<a href={url} target="_blank" rel="external" class="text-white no-underline hover:underline"
					>{author}</a
				>
			{:else}
				{author}
			{/if}
		</div>
	{/if}
</div>
