<script lang="ts">
	import {
		STREAM_SIZECLASS,
		STREAM_SIZECLASS_DRAINAGE_AREA,
		WATERBODY_SIZECLASS,
		WILDSCENIC_RIVER_LONG_LABELS,
		barrierTypeLabelSingular
	} from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'

	import { formatNumber } from '$lib/util/format'

	const {
		barrierType,
		annualflow,
		river,
		intermittent,
		canal,
		subbasin,
		subwatershed,
		huc12,
		streamorder,
		streamsizeclass,
		waterbodyacres,
		waterbodysizeclass,
		wilderness,
		wildscenicriver
	} = $props()

	const barrierTypeLabel = $derived(barrierTypeLabelSingular[barrierType as BarrierTypePlural])

	const hasRiver = $derived(
		river &&
			river !== '"' &&
			river !== 'null' &&
			river.toLowerCase() !== 'unknown' &&
			river.toLowerCase() !== 'unnamed'
	)
</script>

<section>
	<h3>Location within the aquatic network</h3>

	<div class="report-entries">
		<div>
			{hasRiver ? `On ${river} in` : 'Within'}
			{subwatershed} Subwatershed,
			{subbasin} Subbasin
			<br />
			HUC12: {huc12}
		</div>

		{#if wildscenicriver}
			<div>
				{WILDSCENIC_RIVER_LONG_LABELS[wildscenicriver as keyof typeof WILDSCENIC_RIVER_LONG_LABELS]}
			</div>
		{/if}

		{#if wilderness}
			<div>Within a designated wilderness area</div>
		{/if}

		{#if intermittent === 1}
			<div>
				This {barrierTypeLabel} is located on a reach that has intermittent or ephemeral flow
			</div>
		{/if}

		{#if canal === 1}
			<div>This {barrierTypeLabel} is located on a canal or ditch</div>
		{/if}

		{#if streamorder > 0}
			<div>
				Stream order (NHD modified Strahler): {streamorder}
			</div>
		{/if}

		{#if streamsizeclass}
			<div>
				Stream size class: {STREAM_SIZECLASS[streamsizeclass as keyof typeof STREAM_SIZECLASS]} (drainage
				area:
				{STREAM_SIZECLASS_DRAINAGE_AREA[
					streamsizeclass as keyof typeof STREAM_SIZECLASS_DRAINAGE_AREA
				]})
			</div>
		{/if}

		{#if annualflow !== null && annualflow >= 0}
			<div>
				Stream reach annual flow rate: {formatNumber(annualflow)} CFS
			</div>
		{/if}

		{#if barrierType === 'dams' && waterbodysizeclass !== null && waterbodysizeclass > 0}
			<div>
				This {barrierTypeLabel} is associated with a
				{WATERBODY_SIZECLASS[waterbodysizeclass as keyof typeof WATERBODY_SIZECLASS]
					.split(' (')[0]
					.toLowerCase()}
				({formatNumber(waterbodyacres)} acres)
			</div>
		{/if}
	</div>
</section>
