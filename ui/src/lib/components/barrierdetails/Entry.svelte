<script lang="ts">
	import { cn } from '$lib/utils'

	const { label = null, children, isUnknown = false } = $props()
</script>

<div class="px-2 not-first-of-type:mt-4 border-t border-t-grey-2">
	{#if label}
		<div
			class="text-sm bg-blue-1/40 border-b border-b-grey-1 -mx-2 px-2 py-1 font-bold leading-snug"
		>
			{label}:
		</div>
	{/if}

	<div
		class={cn('text-sm leading-tight mt-2 ml-4', {
			'text-muted-foreground italic': isUnknown,
			'mt-3': !label
		})}
	>
		{@render children()}
	</div>
</div>
