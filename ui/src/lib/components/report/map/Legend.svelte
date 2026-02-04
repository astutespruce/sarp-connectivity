<script lang="ts">
	import { cn } from '$lib/utils'
	import { getLegendEntries } from './layers'
	import type { LegendSymbol } from './layers'

	const { networkType, name, visibleLayers } = $props()
	const entries = $derived(getLegendEntries({ networkType, name, visibleLayers }))

	const haveSymbols = $derived(entries.some(({ symbols }) => !!symbols))
</script>

{#snippet Symbol(symbol: LegendSymbol & { type: 'circle' | 'line' })}
	{#if symbol.type === 'line'}
		<div class="flex items-center flex-none">
			<div
				class="w-4"
				style="border-top:{symbol.borderWidth}px {symbol.borderStyle || 'solid'} {symbol.color};"
			></div>
		</div>
	{:else if symbol.type === 'circle'}
		<div
			class="flex-none mt-1 rounded-full"
			style="width:{(symbol.radius || 8) * 2.5}px; height:{(symbol.radius || 8) *
				2.5}px; background-color:{symbol.color}; border: {symbol.borderWidth ||
				0}px solid {symbol.borderColor};"
		></div>
	{/if}
{/snippet}

<div
	class={cn('text-sm', {
		'grid sm:grid-cols-2': entries.length >= 6
	})}
>
	{#each entries as entry, i (entry.label)}
		<div class="flex gap-2 leading-tight not-first:mt-0.75">
			<div
				class={cn('flex-none flex gap-0.5 w-3 basis-4 items-start', {
					'basis-7': haveSymbols,
					'items-center': entry.type === 'line',
					'items-baseline': entry.symbols
				})}
			>
				{#if entry.symbols}
					{#each entry.symbols as symbol, i (`${symbol.color}-${symbol.borderColor}-${i}`)}
						{@render Symbol({ ...symbol, type: entry.type })}
					{/each}
				{:else}
					{@render Symbol(entry)}
				{/if}
			</div>

			<div class={cn('pt-1 text-xs', { 'font-bold': i === 0 })}>{entry.label}</div>
		</div>
	{/each}
</div>
