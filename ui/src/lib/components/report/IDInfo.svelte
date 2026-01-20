<script lang="ts">
	import WarningIcon from '@lucide/svelte/icons/triangle-alert'

	import { CONTACT_EMAIL } from '$lib/env'
	import { dataVersion } from '$lib/config/constants'
	import { isEmptyString } from '$lib/util/string'

	const {
		sarpid,
		nidfederalid,
		nidid,
		source,
		sourceid,
		partnerid,
		sourcelink,
		nearestusgscrossingid,
		estimated
	} = $props()
</script>

<section>
	<h2>Data sources</h2>
	<div class="report-entries">
		<div>
			SARP ID: {sarpid} (data version: {dataVersion})
		</div>

		{#if !isEmptyString(nidfederalid) || !isEmptyString(nidid)}
			<div>
				{#if nidfederalid === nidid || (nidfederalid && isEmptyString(nidid))}
					National inventory of dams ID:
					<a
						href={`https://nid.sec.usace.army.mil/#/dams/system/${nidfederalid}/summary`}
						target="_blank"
						rel="external"
					>
						{nidfederalid}
					</a>
				{:else if !isEmptyString(nidfederalid) && !isEmptyString(nidid)}
					National inventory of dams ID:
					<a
						href={`https://nid.sec.usace.army.mil/#/dams/system/${nidfederalid}/summary`}
						target="_blank"
						rel="external"
					>
						{nidfederalid}
					</a>
					<br />
					legacy ID: {nidid}
				{:else}
					National inventory of dams ID: {nidid} (legacy ID)
				{/if}
			</div>
		{/if}

		{#if !isEmptyString(source)}
			<div>
				Source:
				{#if source.startsWith('OpenStreetMap')}
					<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>
				{:else}
					{source}
				{/if}
			</div>
		{/if}

		{#if !isEmptyString(sourceid)}
			<div>Source ID: {sourceid}</div>
		{/if}

		{#if !isEmptyString(sourcelink)}
			<div>
				More information:
				<a href={sourcelink} target="_blank" rel="external">{sourcelink}</a>
			</div>
		{/if}

		{#if !isEmptyString(nearestusgscrossingid)}
			<div>
				USGS Database of Stream Crossings ID: {nearestusgscrossingid}
				<div class="text-xs text-muted-foreground mt-2">
					Note: this crossing is close to the location of this barrier, but it may not represent
					exactly the same barrier that was inventoried due to methods used to snap barriers and
					crossings to the aquatic network.
				</div>
			</div>
		{/if}

		{#if !isEmptyString(partnerid)}
			<div>Local Partner ID: {partnerid}</div>
		{/if}

		{#if source}
			{#if source.startsWith('WDFW')}
				<div>
					Information about this barrier is maintained by the Washington State Department of Fish
					and Wildlife, Fish Passage Division. For more information about specific structures,
					please visit the
					<a
						href="https://geodataservices.wdfw.wa.gov/hp/fishpassage/index.html"
						target="_blank"
						rel="external"
					>
						fish passage web map
					</a>.
				</div>
			{:else if source.startsWith('ODFW')}
				<div>
					Information about this barrier is maintained by the
					<a
						href="https://www.dfw.state.or.us/fish/passage/inventories.asp"
						target="_blank"
						rel="external"
					>
						Oregon Department of Fish and Wildlife
					</a>.
				</div>
			{/if}
		{/if}

		{#if estimated}
			<div class="flex items-center mt-4 gap-2">
				<WarningIcon class="size-5 flex-none" />
				<div class="flex-none leading-tight">
					Dam is estimated from other data sources and may be incorrect; please
					<a
						href={`mailto:${CONTACT_EMAIL}?subject=Problem with Estimated Dam ${sarpid} (data version: ${dataVersion})`}
					>
						let us know
					</a>
					.
				</div>
			</div>
		{/if}
	</div>
</section>
