<script lang="ts">
	import { cn } from '$lib/utils'

	const { children, class: className = null } = $props()
</script>

<div class={cn('flex-none pt-2 pb-4 px-2 border-t border-t-grey-4 bg-grey-1/50', className)}>
	{@render children()}
</div>
