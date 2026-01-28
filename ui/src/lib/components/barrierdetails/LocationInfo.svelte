<script lang="ts">
	import {
		barrierTypeLabelSingular,
		OWNERTYPE,
		BARRIEROWNERTYPE,
		FERC_REGULATED,
		STATE_REGULATED,
		WATER_RIGHT,
		STREAM_SIZECLASS,
		STREAM_SIZECLASS_DRAINAGE_AREA,
		WATERBODY_SIZECLASS,
		FISH_HABITAT_PARTNERSHIPS,
		STATES,
		TNC_COLDWATER_STATUS,
		TNC_RESILIENCE,
		TU_BROOK_TROUT_PORTFOLIO,
		WILDSCENIC_RIVER_LONG_LABELS
	} from '$lib/config/constants'
	import type { BarrierTypePlural } from '$lib/config/types'

	import Entry from './Entry.svelte'
	import { formatNumber } from '$lib/util/format'
	import { isEmptyString } from '$lib/util/string'

	const {
		annualflow = null,
		barrierType,
		river = null,
		huc12,
		basin,
		subwatershed,
		congressionaldistrict = null,
		ownertype = null,
		barrierownertype = null,
		fercregulated = null,
		stateregulated = null,
		nrcsdam = null,
		fedregulatoryagency = null,
		waterright = null,
		costlower = null,
		costmean = null,
		costupper = null,
		ejtract = null,
		ejtribal = null,
		fishhabitatpartnership = null,
		nativeterritories = null,
		intermittent = null,
		canal = null,
		storagevolume = null,
		streamorder = null,
		streamsizeclass = null,
		waterbodysizeclass = null,
		waterbodyacres = null,
		wilderness = null,
		wildscenicriver = null,
		yearsurveyed = null,
		resurveyed = null,
		fatality = null,
		cold = null,
		resilience = null,
		brooktroutportfolio = null,
		hasnetwork = false,
		invasivenetwork = null,
		invasive = null
	} = $props()

	const barrierTypeLabel = $derived(barrierTypeLabelSingular[barrierType as BarrierTypePlural])
</script>

{#if yearsurveyed !== null && yearsurveyed !== 0}
	<Entry label="Year surveyed">
		{yearsurveyed}
		{resurveyed !== 0 ? ' (resurveyed)' : null}
	</Entry>
{/if}

<Entry label="Watershed">
	{#if !(isEmptyString(river) && river?.toLowerCase() === 'unknown' && river?.toLowerCase() === 'unnamed')}
		On {river} in
	{:else}
		Within
	{/if}
	{subwatershed} Subwatershed, {basin} Subbasin
	<br />
	<div class="mt-2">
		HUC12: {huc12}
	</div>
</Entry>

{#if wildscenicriver}
	<Entry label="Wild & Scenic River status">
		{WILDSCENIC_RIVER_LONG_LABELS[wildscenicriver as keyof typeof WILDSCENIC_RIVER_LONG_LABELS]}
	</Entry>
{/if}

{#if wilderness}
	<Entry label="Wilderness status">Within a designated wilderness area</Entry>
{/if}

{#if intermittent === 1}
	<Entry label="Stream permanence">
		This {barrierTypeLabel} is on an intermittent reach
	</Entry>
{/if}

{#if canal === 1}
	<Entry label="Canal / ditch position">This {barrierTypeLabel} is on canal or ditch</Entry>
{/if}

{#if storagevolume !== null}
	<Entry label="Normal storage volume">
		{formatNumber(storagevolume)} acre/feet
	</Entry>
{/if}

{#if waterbodysizeclass > 0}
	<Entry label="Related waterbody">
		This {barrierTypeLabel} is associated with a
		{WATERBODY_SIZECLASS[waterbodysizeclass as keyof typeof WATERBODY_SIZECLASS]
			.split(' (')[0]
			.toLowerCase()}
		({formatNumber(waterbodyacres)} acres)
	</Entry>
{/if}

{#if streamorder > 0}
	<Entry label="Stream order (NHD modified Strahler)">
		{streamorder}
	</Entry>
{/if}

{#if streamsizeclass}
	<Entry label="Stream size class">
		{STREAM_SIZECLASS[streamsizeclass as keyof typeof STREAM_SIZECLASS]} ({STREAM_SIZECLASS_DRAINAGE_AREA[
			streamsizeclass as keyof typeof STREAM_SIZECLASS_DRAINAGE_AREA
		]})
	</Entry>
{/if}

{#if annualflow !== null && annualflow >= 0}
	<Entry label="Stream reach annual flow rate">
		{formatNumber(annualflow)} CFS
	</Entry>
{/if}

{#if ownertype > 0}
	<Entry label="Conservation land type">{OWNERTYPE[ownertype as keyof typeof OWNERTYPE]}</Entry>
{/if}

{#if barrierownertype !== null && barrierType !== 'waterfalls'}
	<Entry label="Barrier ownership type" isUnknown={barrierownertype === 0}>
		{BARRIEROWNERTYPE[barrierownertype as keyof typeof BARRIEROWNERTYPE].toLowerCase()}
	</Entry>
{/if}

{#if fercregulated !== null && fercregulated > 0}
	<Entry
		label="Regulated by the Federal Energy Regulatory Commission"
		isUnknown={fercregulated === 0}
	>
		{FERC_REGULATED[fercregulated as keyof typeof FERC_REGULATED].toLowerCase()}
	</Entry>
{/if}

{#if stateregulated !== null && stateregulated !== -1}
	<Entry label="Regulated at the state level" isUnknown={stateregulated === 0}>
		{STATE_REGULATED[stateregulated as keyof typeof STATE_REGULATED].toLowerCase()}
	</Entry>
{/if}

{#if fedregulatoryagency}
	<Entry label="Federal regulatory agency">{fedregulatoryagency}</Entry>
{/if}

{#if nrcsdam === 1}
	<Entry label="NRCS flood control dam status">This is a NRCS flood control dam</Entry>
{/if}

{#if waterright > 0}
	<Entry label="Has an associated water right">
		{WATER_RIGHT[waterright as keyof typeof WATER_RIGHT].toLowerCase()}
	</Entry>
{/if}

{#if hasnetwork && invasive && invasivenetwork === 1}
	<Entry label="Invasive species management">
		{#if invasive}
			This {barrierTypeLabel} is identified as a beneficial to restricting the movement of invasive species
			and is not ranked for removal or mitigation.
		{:else if invasivenetwork === 1}
			Upstream of a barrier identified as a beneficial to restricting the movement of invasive
			species.
		{/if}
	</Entry>
{/if}

{#if fatality > 0}
	<Entry label="Number of fatalities recorded">
		{formatNumber(fatality)}

		<div class="text-xs text-muted-foreground mt-2">
			Based on data provided by
			<a href="https://krcproject.groups.et.byu.net/browse.php" target="_blank" rel="external">
				Fatalities at Submerged Hydraulic Jumps
			</a>
		</div>
	</Entry>
{/if}

{#if costmean > 0}
	<Entry label="Estimated cost of removal">
		<div class="leading-relaxed">
			average: ${formatNumber(costmean)}
			<br />
			range: ${formatNumber(costlower)} - ${formatNumber(costupper)}
		</div>

		<div class="text-xs text-muted-foreground mt-4">
			Costs are modeled based on dam characteristics (Jumani et. al. in prep) and are a veryrough
			estimate only; please use with caution
		</div>
	</Entry>
{/if}

{#if cold}
	<Entry label="Ability of the watershed to maintain cold water habitat">
		{TNC_COLDWATER_STATUS[cold as keyof typeof TNC_COLDWATER_STATUS]}

		<div class="text-xs text-muted-foreground mt-4">
			Based on The Nature Conservancy's cold water temperature score where this barrier occurs (TNC;
			March 2024).
		</div>
	</Entry>
{/if}

{#if resilience}
	<Entry label="Freshwater resilience">
		{TNC_RESILIENCE[resilience as keyof typeof TNC_RESILIENCE]}
		<div class="text-xs text-muted-foreground mt-4">
			Based on the The Nature Conservancy's freshwater resilience category of the watershed where
			this barrier occurs (v0.44).
		</div>
	</Entry>
{/if}

{#if brooktroutportfolio}
	<Entry label="Eastern brook trout conservation portfolio">
		{TU_BROOK_TROUT_PORTFOLIO[brooktroutportfolio as keyof typeof TU_BROOK_TROUT_PORTFOLIO]}

		<div class="text-xs text-muted-foreground mt-4">
			Based on the
			<a
				href="https://www.tu.org/science/conservation-planning-and-assessment/conservation-portfolio/"
				target="_blank"
				rel="external"
			>
				brook trout conservation portfolio
			</a>
			category of the watershed where this barrier occurs, as identified by Trout Unlimited (7/4/2022).
		</div>
	</Entry>
{/if}

{#if ejtract || ejtribal}
	<Entry label="Climate and environmental justice">
		{ejtract ? 'within a disadvantaged census tract' : null}
		{ejtract && ejtribal ? ', ' : null}
		{ejtribal ? 'within a tribal community' : null}
	</Entry>
{/if}

{#if fishhabitatpartnership}
	<Entry label="Fish Habitat Partnerships working in this area">
		{#each fishhabitatpartnership.split(',') as fhp, i (fhp)}
			{#if i > 0},
			{/if}
			<a
				href={FISH_HABITAT_PARTNERSHIPS[fhp as keyof typeof FISH_HABITAT_PARTNERSHIPS].url}
				target="_blank"
				rel="external"
			>
				{FISH_HABITAT_PARTNERSHIPS[fhp as keyof typeof FISH_HABITAT_PARTNERSHIPS].name}
			</a>
		{/each}
	</Entry>
{/if}

{#if nativeterritories}
	<Entry label="Within the following native territories">
		<div class="ml">
			{nativeterritories}
			<div class="text-xs text-muted-foreground mt-2">
				Based on data provided by
				<a href="https://native-land.ca/" target="_blank" rel="external">Native Land Digital</a>
			</div>
		</div>
	</Entry>
{/if}

{#if congressionaldistrict}
	<Entry label="Congressional district">
		{STATES[congressionaldistrict.slice(0, 2) as keyof typeof STATES]} Congressional District
		{congressionaldistrict.slice(2)}
		<span class="text-xs text-muted-foreground"> (119th congress) </span>
	</Entry>
{/if}
