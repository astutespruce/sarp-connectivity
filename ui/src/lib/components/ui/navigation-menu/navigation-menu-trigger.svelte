<script lang="ts" module>
	// style overrides: change accent to white/20, change to ring-white
	// add gap-2 text-lg
	// remove bg-background text-accent usage text-sm
	// change chevron to size-5
	import { cn } from '$lib/utils.js'
	import { tv } from 'tailwind-variants'

	export const navigationMenuTriggerStyle = tv({
		base: 'text-white text-lg hover:bg-white/20 focus:bg-white/20 data-[state=open]:hover:bg-white/20 data-[state=open]:focus:bg-white/20 data-[state=open]:bg-white/10 data-[state=open]:ring-white data-[state=open]:ring-2 focus-visible:ring-white group inline-flex h-9 w-max items-center justify-center rounded-md p-2 font-medium transition-[color,box-shadow] outline-none focus-visible:ring-[2px] focus-visible:outline-1 disabled:pointer-events-none disabled:opacity-50 gap-2'
	})
</script>

<script lang="ts">
	import { NavigationMenu as NavigationMenuPrimitive } from 'bits-ui'
	import ChevronDownIcon from '@lucide/svelte/icons/chevron-down'

	let {
		ref = $bindable(null),
		class: className,
		children,
		...restProps
	}: NavigationMenuPrimitive.TriggerProps = $props()
</script>

<NavigationMenuPrimitive.Trigger
	bind:ref
	data-slot="navigation-menu-trigger"
	class={cn(navigationMenuTriggerStyle(), 'group', className)}
	{...restProps}
>
	{@render children?.()}

	<ChevronDownIcon
		class="relative top-px size-5 transition duration-300 group-data-[state=open]:rotate-180 -ml-1"
		aria-hidden="true"
	/>
</NavigationMenuPrimitive.Trigger>
