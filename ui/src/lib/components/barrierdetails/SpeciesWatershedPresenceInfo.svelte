<script lang="ts">
	import { resolve } from '$app/paths'
	import { SALMONID_ESU, TROUT, barrierTypeLabelSingular } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { cn } from '$lib/utils'

	import Entry from './Entry.svelte'

	const {
		barrierType,
		tespp = 0,
		regionalsgcnspp = 0,
		statesgcnspp = 0,
		trout = 0,
		salmonidesu = null
	} = $props()

	const typeLabel = $derived(barrierTypeLabelSingular[barrierType as BarrierTypePlural])
</script>

<div class="text-xs text-muted-foreground mx-2 mt-2">
	Note: species information is very incomplete and is limited to the subwatershed level. These
	species may or may not be directly impacted by this {typeLabel}.
	<a href={resolve('/methods/sgcn/')} target="_blank"> Read more. </a>
</div>

{#if tespp + regionalsgcnspp + statesgcnspp > 0 || trout || salmonidesu}
	<Entry label="Number of federally-listed threatened and endangered aquatic species">
		<div class={cn('font-bold', { 'font-normal text-muted-foreground': tespp === 0 })}>{tespp}</div>
	</Entry>

	<Entry
		label="Number of state-listed aquatic Species of Greatest
          Conservation Need (including state-listed threatened and
          endangered species)"
	>
		<div class={cn('font-bold', { 'font-normal text-muted-foreground': statesgcnspp === 0 })}>
			{statesgcnspp}
		</div>
	</Entry>

	<Entry
		label="Number of regionally-listed aquatic Species of Greatest
          Conservation Need"
	>
		<div class={cn('font-bold', { 'font-normal text-muted-foreground': regionalsgcnspp === 0 })}>
			{regionalsgcnspp}
		</div>
	</Entry>

	<Entry label="Trout species present">
		{#if trout}
			{trout
				.split(',')
				.map((code: keyof typeof TROUT) => TROUT[code])
				.join(', ')}
		{:else}
			<div class="text-muted-foreground">none recorded</div>
		{/if}
	</Entry>

	{#if salmonidesu}
		<Entry
			label="Salmon Evolutionarily Significant Units / Steelhead trout Discrete Population Segments present"
		>
			<ul class="list-disc list-outside pl-4 [&>li+li]:mt-1">
				{#each salmonidesu.split(',') as code (code)}
					<li>{SALMONID_ESU[code as keyof typeof SALMONID_ESU]}</li>
				{/each}
			</ul>
		</Entry>
	{/if}
{:else}
	<div class="text-muted-foreground mt-4 mr-2m px-2 text-sm">
		Data sources in the subwatershed containing this {typeLabel} have not recorded any federally-listed
		threatened and endangered aquatic species, state-listed aquatic Species of Greatest Conservation Need,
		regionally-listed aquatic Species of Greatest Conservation Need, trout species, or salmon ESU / steelhead
		trout DPS.
	</div>
{/if}
