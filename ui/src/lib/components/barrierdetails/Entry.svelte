<script lang="ts">
	import { cn } from '$lib/utils'

	const { label = null, children, isUnknown = false } = $props()
</script>

<div
	class="px-2 not-first-of-type:mt-2 not-first-of-type:pt-1 not-first-of-type:border-t not-first-of-type:border-t-grey-1"
>
	{#if label}
		<div>
			{label}
		</div>
	{/if}

	<div class={cn({ 'text-xs text-muted-foreground': isUnknown })}>
		{@render children()}
	</div>
</div>
