<script lang="ts">
	import { resolve } from '$app/paths'
	import { barrierTypeLabels } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { Button } from '$lib/components/ui/button'
	import { Root as ButtonGroup } from '$lib/components/ui/button-group'
	import { cn } from '$lib/utils'

	import ScoresList from './ScoresList.svelte'

	type TabId = 'custom' | 'state' | 'huc8'

	const tabs: { id: TabId; label: string }[] = [
		{ id: 'custom', label: 'Selected Area' },
		{ id: 'state', label: 'State' },
		{ id: 'huc8', label: 'Subbasin' }
	]

	const tabLabels = Object.fromEntries(tabs.map(({ id, label }) => [id, label]))

	const { networkType, scores } = $props()

	const availableTabs = $derived.by(() => {
		const out = []
		if (scores.custom && scores.custom.ncwc) {
			out.push(tabs[0])
		}
		if (scores.state && scores.state.ncwc) {
			out.push(tabs[1])
		}
		if (scores.huc8 && scores.huc8.ncwc) {
			out.push(tabs[2])
		}

		return out
	})

	let view: TabId | undefined = $derived(availableTabs.length > 0 ? availableTabs[0].id : undefined)
</script>

<div class="h-full overflow-auto pb-8">
	{#if availableTabs.length > 0}
		<div>
			{#if availableTabs.length > 1}
				<div class="mx-2 mt-4 font-bold">
					Compared to other
					{barrierTypeLabels[networkType as BarrierTypePlural]} in the
				</div>

				<ButtonGroup class="mx-2 mt-1">
					{#each availableTabs as tab (tab.id)}
						<Button
							variant="ghost"
							onclick={() => {
								view = tab.id
							}}
							class={cn(' h-auto px-4 py-0.5! not-first:ml-0.5', {
								' bg-primary text-white border-b-transparent hover:text-white hover:bg-primary/90':
									view === tab.id,
								'bg-blue-1 hover:bg-blue-2 text-muted-foreground': view !== tab.id
							})}>{tab.label}</Button
						>
					{/each}
				</ButtonGroup>
			{/if}

			<ScoresList {...scores[view!]} />
		</div>
	{:else}
		<div class="mx-2 mt-4 text-muted-foreground text-sm">
			State-level ranks are not available for this network type because there are not yet sufficient
			assessed road-related barriers at the state level for all states. Instead, you can <a
				href={resolve('/priority/')}>prioritize</a
			>
			barriers to calculate ranks for a selected area.
		</div>
	{/if}
</div>
