<script lang="ts">
	import { Button } from '$lib/components/ui/button'
	import { cn } from '$lib/utils'

	const { snippet, children, class: className = null } = $props()

	let isOpen = $state(false)

	const toggle = () => {
		isOpen = !isOpen
	}
</script>

<div class={cn(className)}>
	{#if isOpen}
		{@render children()}
	{:else}
		<span>
			{snippet}
		</span>
	{/if}

	<Button variant="link" onclick={toggle}>
		Show {isOpen ? 'less' : 'more'}...
	</Button>
</div>
