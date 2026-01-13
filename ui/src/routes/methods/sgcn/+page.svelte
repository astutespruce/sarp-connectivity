<script lang="ts">
	import { resolve } from '$app/paths'
	import { Alert } from '$lib/components/alert'
	import { HighlightBox } from '$lib/components/elements'
	import { HeaderImage } from '$lib/components/image'
	import { SITE_NAME } from '$lib/env'
</script>

<svelte:head>
	<title>Listed species and Species of Greatest Conservation Need | {SITE_NAME}</title>
</svelte:head>

<HeaderImage
	author="Appalachian elktoe. Photo: U.S. Fish & Wildlife Service Southeast Region."
	url="https://www.flickr.com/photos/usfwssoutheast/33643109826/"
>
	<enhanced:img src="$lib/assets/images/33643109826_51296358b0_k.jpg" alt="" />
</HeaderImage>

<div class="page-content">
	<h1>Listed species and Species of Greatest Conservation Need</h1>

	<p class="mt-8">
		The presence of federally-listed threatened and endangered aquatic species and state and
		regionally-listed aquatic Species of Greatest Conservation Need (SGCN) is an important factor in
		evaluating the priority of a given barrier for removal or mitigation.
		<br />
		<br />
		We compiled information on the location of these species using element occurrence data obtained from
		state natural heritage programs or similar organizations. These data were limited to aquatic species,
		specifically fishes, crayfishes, mussels, snails, and amphibians.
	</p>

	<h2 class="mt-12">Methods</h2>

	<p class="mt-2">We summarized species data to the subwatershed level based on:</p>

	<ol class="mt-2">
		<li>
			Presence of federally-listed species using data managed by the state programs or species lists
			from the U.S. Fish and Wildlife Service.
		</li>
		<li>
			Presence of state-listed Species of Greatest Conservation Need using species lists from
			<a href="https://www1.usgs.gov/csas/swap/" target="_blank" rel="external">
				State Wildlife Action Plan species lists
			</a>
			compiled by the U.S. Geological Survey.
		</li>
		<li>
			Presence of regionally-listed Species of Greatest Conservation Need using a species list from
			the Southeast Association of Fish and Wildlife Agencies.
		</li>
		<li>
			Presence of trout species using a combination of data provided from natural heritage programs
			and NatureServe, as well as data from the Eastern Brook Trout Joint Venture (
			<a
				href="https://easternbrooktrout.org/about/reports/ebtjv-salmonid-catchment-assessment-and-habitat-patch-layers"
				target="_blank"
				rel="external"
			>
				EBTJV Habitat Patch Dataset
			</a>, brook trout only).
		</li>
		<li>
			Overlap with salmon and steelhead Evolutionarily Significant Units / Discrete Population
			Segment data provided by the National Oceanic and Atmospheric Administration (NOAA)
			<a
				href="https://www.fisheries.noaa.gov/about/northwest-fisheries-science-center"
				target="_blank"
				rel="external"
			>
				Northwest Fisheries Science Center
			</a>.
		</li>
	</ol>

	<h2 class="mt-12">Caveats</h2>

	<ul class="mt-2">
		<li>
			The presence of one or more of these species in the same subwatershed as a barrier does not
			necessarily mean that the species is directly impacted by that barrier. Likewise, it does not
			necessarily imply that the species will directly benefit by removal or mitigation of the
			barrier.
		</li>
		<li>
			Information on these species is limited and comprehensive information has not been provided
			for all states at this time.
		</li>
		<li>
			Due to variations in taxonomic representation of a given species or subspecies, not all
			species are necessarily correctly categorized according to the above breakdown.
		</li>
	</ul>
</div>
