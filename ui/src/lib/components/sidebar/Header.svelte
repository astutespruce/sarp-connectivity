<script lang="ts">
	import { cn } from '$lib/utils'

	const { children, class: className = null } = $props()
</script>

<div class={cn('flex-none border-b border-b-grey-4 bg-grey-1/50', className)}>
	{@render children()}
</div>
