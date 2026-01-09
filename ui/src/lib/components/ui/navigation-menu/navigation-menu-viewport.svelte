<script lang="ts">
	// style override: add border-grey-5
	// remove animation, zoom
	import { NavigationMenu as NavigationMenuPrimitive } from 'bits-ui'
	import { cn } from '$lib/utils.js'

	let {
		ref = $bindable(null),
		class: className,
		...restProps
	}: NavigationMenuPrimitive.ViewportProps = $props()

</script>

<div class={cn('absolute start-0 top-full isolate z-50 flex justify-center')}>
	<NavigationMenuPrimitive.Viewport
		bind:ref
		data-slot="navigation-menu-viewport"
		class={cn(
			'origin-top-center bg-popover text-popover-foreground  relative mt-1.5 h-[var(--bits-navigation-menu-viewport-height)] overflow-hidden rounded-md border border-grey-5 shadow w-[var(--bits-navigation-menu-viewport-width)]',
			className
		)}
		{...restProps}
	/>
</div>
