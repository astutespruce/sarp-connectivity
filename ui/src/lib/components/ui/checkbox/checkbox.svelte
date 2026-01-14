<script lang="ts">
	// style override: change size-4 to size-5, add cursor-pointer
	// change icon size to 4.5
	import { Checkbox as CheckboxPrimitive } from 'bits-ui'
	import CheckIcon from '@lucide/svelte/icons/check'
	import MinusIcon from '@lucide/svelte/icons/minus'
	import { cn, type WithoutChildrenOrChild } from '$lib/utils.js'

	let {
		ref = $bindable(null),
		checked = $bindable(false),
		indeterminate = $bindable(false),
		class: className,
		...restProps
	}: WithoutChildrenOrChild<CheckboxPrimitive.RootProps> = $props()
</script>

<CheckboxPrimitive.Root
	bind:ref
	data-slot="checkbox"
	class={cn(
		'cursor-pointer border-input dark:bg-input/30 data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground dark:data-[state=checked]:bg-primary data-[state=checked]:border-primary focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive peer flex size-5 shrink-0 items-center justify-center rounded-[4px] border shadow-xs transition-shadow outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50',
		className
	)}
	bind:checked
	bind:indeterminate
	{...restProps}
>
	{#snippet children({ checked, indeterminate })}
		<div data-slot="checkbox-indicator" class="text-current transition-none">
			{#if checked}
				<CheckIcon class="size-4.5" />
			{:else if indeterminate}
				<MinusIcon class="size-4.5" />
			{/if}
		</div>
	{/snippet}
</CheckboxPrimitive.Root>
