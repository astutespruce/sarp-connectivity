<script lang="ts">
	// style override: change bg to white, text to foreground, update arrow config
	import { Tooltip as TooltipPrimitive } from 'bits-ui'
	import { cn } from '$lib/utils.js'

	let {
		ref = $bindable(null),
		class: className,
		sideOffset = 0,
		side = 'top',
		children,
		arrowClasses,
		...restProps
	}: TooltipPrimitive.ContentProps & {
		arrowClasses?: string
	} = $props()
</script>

<TooltipPrimitive.Portal>
	<TooltipPrimitive.Content
		bind:ref
		data-slot="tooltip-content"
		{sideOffset}
		{side}
		class={cn(
			'bg-white border border-grey-4 drop-shadow-md origin-(--bits-tooltip-content-transform-origin) z-10000 w-fit text-balance rounded-md px-3 py-1.5 text-xs data-[side=bottom]:-mt-1',
			className
		)}
		{...restProps}
	>
		{@render children?.()}
		<TooltipPrimitive.Arrow>
			{#snippet child({ props })}
				<div
					class={cn(
						'z-50 size-0 border-8 border-transparent',
						'data-[side=right]:border-l-grey-9 data-[side=right]:border-b-grey-9 data-[side=right]:-rotate-45 data-[side=right]:-mt-1',
						'data-[side=bottom]:border-b-grey-9 data-[side=bottom]:border-r-grey-9 data-[side=bottom]:rotate-45 data-[side=bottom]:-ml-2 data-[side=bottom]:mt-1.25',
						arrowClasses
					)}
					{...props}
				></div>
			{/snippet}
		</TooltipPrimitive.Arrow>
	</TooltipPrimitive.Content>
</TooltipPrimitive.Portal>
