<script lang="ts">
	import { pointColors } from '$lib/config/constants'
	import { formatNumber } from '$lib/util/format'
	import { cn } from '$lib/utils'

	const { counts, threshold } = $props()

	const max = $derived(Math.max(...counts))

	const labelWidth = $derived(max.toString().length * 0.75)
</script>

<div class="flex-auto text-xs leading-none text-muted-foreground">
	{#each counts as count, i (`${i}-${count}`)}
		<div
			class={cn('grid grid-cols-[4rem_1fr] gap-1 items-center text-muted-foreground', {
				'font-bold': i + 1 <= threshold
			})}
			style="color: {i + 1 <= threshold ? pointColors.topRank.color : 'inherit'}"
		>
			<div class="text-right flex-none py-1">
				Tier {i + 1}
			</div>

			<div class="flex gap-1 items-center border-l border-l-grey-2 py-1">
				<div
					class="h-4"
					style="background-color:{i + 1 <= threshold
						? pointColors.topRank.color
						: pointColors.lowerRank.color}; width: calc({(100 * count) / max}% - {labelWidth}em)"
				></div>
				<div class="w-16 flex-none">
					{formatNumber(count, 0)}
				</div>
			</div>
		</div>
	{/each}
</div>
