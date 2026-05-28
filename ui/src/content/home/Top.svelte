<script lang="ts">
	import ChartIcon from '@lucide/svelte/icons/chart-no-axes-combined'

	import { resolve } from '$app/paths'
	import { Button } from '$lib/components/ui/button'
	import { summaryStats } from '$lib/config/summaryStats'
	import { formatNumber } from '$lib/util/format'

	const {
		dams,
		removedDams,
		lowheadDams,
		highHazardDams,
		poorConditionDams,
		smallBarriers,
		totalSmallBarriers,
		removedSmallBarriers,
		unsurveyedRoadCrossings
	} = summaryStats
</script>

<div class="bg-blue-0 border-b border-b-grey-2 py-2">
	<div class="container grid sm:grid-cols-2 gap-px bg-grey-1 px-0">
		<div class="bg-blue-0 py-2 sm:py-1 px-4">
			<div>
				<span class="text-lg sm:text-xl md:text-2xl">
					<b>{formatNumber(dams)}</b>
				</span> <span class="text-lg">inventoried dams</span>
			</div>
			<div class="mt-1 text-sm text-muted-foreground">
				<b>{formatNumber(highHazardDams)}</b> are rated as high hazards
				<br />
				<b>{formatNumber(poorConditionDams)}</b> dams are in poor condition
				<br />
				<b>{formatNumber(lowheadDams)}</b> known and likely lowhead dams
				<br />
				<b>{formatNumber(removedDams)}</b> dams removed for conservation
			</div>
		</div>
		<div class="bg-blue-0 py-2 sm:py-1 px-4">
			<div>
				<span class="text-lg sm:text-xl md:text-2xl">
					<b>{formatNumber(totalSmallBarriers + unsurveyedRoadCrossings)}</b>
				</span> <span class="text-lg">road/stream crossings</span>
			</div>
			<div class="mt-1 text-sm text-muted-foreground">
				<b>{formatNumber(totalSmallBarriers)}</b> surveyed for impacts to aquatic organisms
				<br />
				<b>{formatNumber(smallBarriers - removedSmallBarriers)}</b>
				surveyed crossings likely to impact aquatic organisms
				<br />
				<b>{formatNumber(removedSmallBarriers)}</b> surveyed crossings removed for conservation
			</div>
		</div>
	</div>
</div>
<div class="flex justify-center py-2 bg-grey-1 border-b border-b-grey-2">
	<Button href={resolve('/statistics', {})} class="">
		<ChartIcon class="size-4" />
		See more statistics here</Button
	>
</div>
