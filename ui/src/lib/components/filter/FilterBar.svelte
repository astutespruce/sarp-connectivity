<script lang="ts">
	import { Button } from '$lib/components/ui/button'
	import { formatNumber } from '$lib/util/format'
	import { cn } from '$lib/utils'

	const {
		value,
		label,
		quantity,
		max,
		isFiltered = false, // true if filter is set on this bar
		isExcluded = false, // true if filters are set on others but not this one
		onClick
	} = $props()

	const position = $derived((100 * quantity) / max)
</script>

<Button
	variant="ghost"
	class={cn(
		'block w-full text-sm leading-none p-0! rounded-none text-left transition-opacity mb-3 opacity-100 group',
		{
			'opacity-30 hover:opacity-50': isExcluded
		}
	)}
	onclick={() => {
		onClick(value)
	}}
>
	<div class="flex justify-between items-end text-xs">
		<div class={cn('flex-none', { 'font-bold': isFiltered })}>
			{label}
		</div>
		<div class="flex-none">
			{formatNumber(quantity)}
		</div>
	</div>

	<div class="flex w-full mt-1 h-3 rounded-full bg-grey-2/75 group-hover:bg-grey-2 overflow-hidden">
		<div
			class={cn('bg-primary border-primary group-hover:bg-primary/75 transition-all', {
				'bg-accent': isFiltered
			})}
			style="flex-basis:{position}%;"
		></div>
	</div>
</Button>
