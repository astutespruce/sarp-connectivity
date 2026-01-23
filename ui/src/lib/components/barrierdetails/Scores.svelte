<script lang="ts">
	import { resolve } from '$app/paths'
	import { barrierTypeLabels } from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { Button } from '$lib/components/ui/button'

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

{#if availableTabs.length > 0}
	<div>
		<div class="text-xs text-muted-foreground text-center">
			Tiers range from 20 (lowest) to 1 (highest).
		</div>

		{#if availableTabs.length > 1}
			<div>
				Compared to other {barrierTypeLabels[networkType as BarrierTypePlural]} in the
				{tabLabels[view!]}
			</div>
			<div class="flex">
				{#each availableTabs as tab (tab.id)}
					<Button
						variant="ghost"
						onclick={() => {
							view = tab.id
						}}>{tab.label}</Button
					>
				{/each}
			</div>
		{/if}

		<ScoresList {...scores[view!]} />
	</div>
{:else}
	State-level ranks are not available for this network type because there are not yet sufficient
	assessed road-related barriers at the state level for all states. Instead, you can <a
		href={resolve('/priority/')}>prioritize</a
	>
	barriers to calculate ranks for a selected area.
{/if}
