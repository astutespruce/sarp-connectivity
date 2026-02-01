<script lang="ts">
	import { Button } from '$lib/components/ui/button'
	import { STATES, barrierTypeLabelSingular } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { cn } from '$lib/utils'

	const {
		sarpid,
		name = '',
		state: stateId,
		river = null,
		barriertype,
		isActive = false,
		focused = false,
		onClick
	} = $props()

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
		'block text-left h-auto p-1 w-full rounded-none text-xs leading-tight hover:bg-grey-1/50',
		{ 'bg-grey-1/50': isActive }
	)}
>
	<div class="grid grid-cols-[4fr_1fr] gap-4 text-wrap">
		<div>
			<div class={cn('text-[0.8rem]', { 'font-bold': isActive })}>
				{name ||
					// barrierNameWhenUnknown[barriertype as keyof typeof barrierNameWhenUnknown] ||
					'Unknown name'}
				<span class="text-muted-foreground text-xs">
					({sarpid})
				</span>
			</div>
			<div class="text-muted-foreground">
				{#if river}
					located on {river},
				{/if}
				{STATES[stateId as keyof typeof STATES]}
			</div>
		</div>

		<div class="text-muted-foreground flex-none text-right">
			{barrierTypeLabelSingular[barriertype as BarrierTypePlural]}
		</div>
	</div>
</Button>
