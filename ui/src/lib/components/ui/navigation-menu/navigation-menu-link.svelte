<script lang="ts">
	// style override: change bg-accent to bg-white/20
	// remove flex-col text-sm text-accent usage
	// add text-white no-underline items-center leading-none
	import { NavigationMenu as NavigationMenuPrimitive } from 'bits-ui'
	import { cn } from '$lib/utils.js'

	let {
		ref = $bindable(null),
		class: className,
		...restProps
	}: NavigationMenuPrimitive.LinkProps = $props()
</script>

<NavigationMenuPrimitive.Link
	bind:ref
	data-slot="navigation-menu-link"
	class={cn(
		"text-white items-center leading-none no-underline data-[active=true]:focus:bg-white/20 data-[active=true]:hover:bg-white/20 data-[active=true]:bg-white/20 data-[is-active=true]:bg-white/20 data-[is-active=true]:ring-white data-[is-active=true]:ring-2 hover:bg-white/20 focus:bg-white/20 focus-visible:ring-white [&_svg:not([class*='text-'])]:text-muted-foreground flex gap-1 rounded-sm p-2 transition-all outline-none focus-visible:ring-2 focus-visible:outline-1 [&_svg:not([class*='size-'])]:size-4",
		className
	)}
	{...restProps}
/>
