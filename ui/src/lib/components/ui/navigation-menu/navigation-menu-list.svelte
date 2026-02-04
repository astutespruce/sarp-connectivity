<script lang="ts">
	// style override: change gap-1 to gap-2
	import { NavigationMenu as NavigationMenuPrimitive } from 'bits-ui'
	import { cn } from '$lib/utils.js'

	let {
		ref = $bindable(null),
		class: className,
		...restProps
	}: NavigationMenuPrimitive.ListProps = $props()
</script>

<NavigationMenuPrimitive.List
	bind:ref
	data-slot="navigation-menu-list"
	class={cn('group flex flex-1 list-none items-center justify-center gap-2', className)}
	{...restProps}
/>
