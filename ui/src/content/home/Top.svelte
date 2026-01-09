<script lang="ts">
	import { summaryStats } from '$lib/config/summaryStats'
	import { formatNumber } from '$lib/util/format'

	const {
		dams,
		removedDams,
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
				<b>{formatNumber(removedDams)}</b> removed for conservation
			</div>
		</div>
		<div class="bg-blue-0 py-2 sm:py-1 px-4">
			<div>
				<span class="text-lg sm:text-xl md:text-2xl">
					<b>{formatNumber(totalSmallBarriers + unsurveyedRoadCrossings)}</b>
				</span> <span class="text-lg">road/stream crossings</span>
			</div>
			<div class="mt-1 text-sm text-muted-foreground">
				<b>{formatNumber(totalSmallBarriers)}</b> assessed for impacts to aquatic organisms
				<br />
				<b>{formatNumber(smallBarriers - removedSmallBarriers)}</b>
				assessed barriers likely to impact aquatic organisms
				<br />
				<b>{formatNumber(removedSmallBarriers)}</b> removed for conservation
			</div>
		</div>
	</div>
</div>
