<script lang="ts">
	import { Downloader } from '$lib/components/download'
	import { barrierTypeLabels } from '$lib/config/constants'
	const { stats, config, areaName = null } = $props()
</script>

<div
	class="bg-grey-1/75 border-t border-t-grey-3 border-b border-b-grey-3 p-2 text-sm flex justify-end items-center gap-4 mt-4 mb-8"
>
	<div class="flex-none">Download:</div>
	<Downloader label="dams" barrierType="dams" {areaName} disabled={stats.dams === 0} {config} />
	<Downloader
		label={`Download ${barrierTypeLabels.small_barriers}`}
		barrierType="small_barriers"
		{areaName}
		disabled={stats.totalSmallBarriers === 0}
		{config}
	/>
	<Downloader
		label="Download surveyed & unsurveyed road/stream crossings"
		triggerLabel="surveyed & unsurveyed crossings"
		barrierType="road_crossings"
		{areaName}
		disabled={stats.totalRoadCrossings === 0}
		{config}
	/>
</div>
