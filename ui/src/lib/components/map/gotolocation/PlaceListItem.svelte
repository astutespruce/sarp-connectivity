<script lang="ts">
	import { Button } from '$lib/components/ui/button'
	import { cn } from '$lib/utils'

	const { name, address = null, focused = false, isActive = false, onClick } = $props()

	let node: HTMLButtonElement | null = $state(null)

	$effect(() => {
		if (node && focused) {
			node.focus()
		}
	})
</script>

<Button
	bind:ref={node}
	variant="ghost"
	onclick={onClick}
	class={cn(
		'block text-left h-auto m-0 p-1 w-full rounded-none text-xs leading-tight hover:bg-grey-1/50 text-wrap break-all overflow-hidden',
		{ 'bg-grey-1/50': isActive }
	)}
>
	<div class={cn({ 'font-bold': isActive })}>
		{name}
	</div>
	{#if address}
		<div class="text-muted-foreground mt-0.5">
			{address}
		</div>
	{/if}
</Button>
