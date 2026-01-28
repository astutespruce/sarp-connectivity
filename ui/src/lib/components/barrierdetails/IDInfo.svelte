<script lang="ts">
	import { attachmentKeywords } from '$lib/config/constants'
	import { isEmptyString } from '$lib/util/string'

	import Entry from './Entry.svelte'

	const {
		barrierType,
		sarpid = '',
		nidfederalid = '',
		nidid = '',
		source = '',
		sourceid = '',
		partnerid = '',
		nearestusgscrossingid = null,
		sourcelink = null,
		lat,
		lon
	} = $props()
</script>

{#if !isEmptyString(sarpid)}
	<Entry label="SARP ID">{sarpid}</Entry>
{/if}

{#if !isEmptyString(nidfederalid) || !isEmptyString(nidid)}
	<Entry label="National inventory of dams ID">
		{#if nidfederalid === nidid || (!isEmptyString(nidfederalid) && isEmptyString(nidid))}
			<a
				href={`https://nid.sec.usace.army.mil/#/dams/system/${nidfederalid}/summary`}
				target="_blank"
				rel="external"
			>
				{nidfederalid}
			</a>
		{:else if !isEmptyString(nidfederalid) && !isEmptyString(nidid)}
			<div class="flex flex-col">
				<a
					href={`https://nid.sec.usace.army.mil/#/dams/system/${nidfederalid}/summary`}
					target="_blank"
					rel="external"
				>
					{nidfederalid}
				</a>
				<div class="text-xs">legacy ID: {nidid}</div>
			</div>
		{:else}
			<a href="https://nid.sec.usace.army.mil/#/" target="_blank" rel="external">
				{nidid}
			</a>
			(legacy ID)
		{/if}
	</Entry>
{/if}

{#if !isEmptyString(source)}
	<Entry label="Source">
		<div class="leading-relaxed">
			{#if source.startsWith('OpenStreetMap')}
				<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="external">
					OpenStreetMap
				</a>
			{:else}
				{source}
				{#if !isEmptyString(sourceid)}
					<br />
					ID: {sourceid}
				{/if}
				{#if !isEmptyString(sourcelink)}
					<a href={sourcelink} target="_blank" rel="external" class="block mt-2">
						Click here for more information about this barrier
					</a>
				{/if}
			{/if}
		</div>

		{#if source.startsWith('WDFW')}
			<div class="mt-4">
				Information about this barrier is maintained by the Washington State Department of Fish and
				Wildlife, Fish Passage Division. For more information about specific structures, please
				visit the
				<a
					href="https://geodataservices.wdfw.wa.gov/hp/fishpassage/index.html"
					target="_blank"
					rel="external"
				>
					fish passage web map
				</a>.
			</div>
		{:else if source.startsWith('ODFW')}
			<div class="mt-4">
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
	</Entry>
{/if}

{#if !isEmptyString(partnerid)}
	<Entry label="Local Partner ID">{partnerid}</Entry>
{/if}

{#if !isEmptyString(nearestusgscrossingid)}
	<Entry label="USGS Database of Stream Crossings ID">
		{nearestusgscrossingid}

		<div class="text-xs text-muted-foreground mt-2">
			Note: this crossing is close to the location of this barrier, but it may not represent exactly
			the same barrier that was inventoried due to methods used to snap barriers and crossings to
			the aquatic network.
		</div>
	</Entry>
{/if}

<Entry label="View location in Google Maps">
	<div class="flex gap-2">
		<div class="flex-none">
			<a
				href={`https://www.google.com/maps/search/?api=1&query=${lat},${lon}`}
				target="_blank"
				rel="external"
			>
				map
			</a>
		</div>
		{#if barrierType === 'small_barriers' || barrierType === 'road_crossings'}
			<div class="flex-none border-l border-l-grey-3 pl-2">
				<a
					href={`https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}&fov=100`}
					target="_blank"
					rel="external"
				>
					street view
				</a>
			</div>
		{/if}
	</div>
</Entry>
