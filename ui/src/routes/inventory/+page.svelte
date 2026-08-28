<script lang="ts">
	import ChartIcon from '@lucide/svelte/icons/chart-no-axes-combined'

	import { resolve } from '$app/paths'

	import DamIcon from '$lib/assets/icons/dam.svg'
	import { Button } from '$lib/components/ui/button'
	import { CONTACT_EMAIL, NACC_HOME_URL, SITE_NAME } from '$lib/env'
	import { formatNumber } from '$lib/util/format'
	import { HighlightBox } from '$lib/components/elements'
</script>

<svelte:head>
	<title>Aquatic Barrier Inventory | {SITE_NAME}</title>
</svelte:head>

<div class="max-h-64 overflow-hidden relative">
	<enhanced:img src="$lib/assets/images/zack-dutra-2d7Y5Yi3aq8-unsplash.jpg" alt="" />

	<div class="absolute bottom-0 right-0 py-1 px-2 bg-black/75 text-white text-xs">
		Photo: <a
			href="https://unsplash.com/photos/2d7Y5Yi3aq8"
			target="_blank"
			rel="external"
			class="text-white no-underline hover:underline">Zach Dutra</a
		>
	</div>
</div>

<div class="page-content">
	<h1 class="page-header">
		<img src={DamIcon} alt="Inventory icon" class="h-20" />

		<div>
			<div class="text-2xl italic">National</div>
			<div class="text-3xl md:text-4xl lg:text-5xl">Aquatic Barrier Inventory</div>
		</div>
	</h1>

	<p class="text-lg mt-8">
		This inventory is a growing and living database of dams, culverts, and other road crossings that
		spans all 50 states, Puerto Rico, and the US Virgin Islands, compiled by SARP with the generous
		support from many partners and funders. It integrates existing datasets from local, state, and
		federal partners with data collected from ongoing field surveys and local knowledge of specific
		structures.
	</p>

	<div class="grid sm:grid-cols-[1.5fr_1fr] gap-8 mt-8">
		<p class="text-lg">
			The inventory directly supports prioritization of barriers by including metrics that describe
			network connectivity, landscape condition, and presence of threatened and endangered aquatic
			organisms.
			<a href={resolve('/regions/southeast/use_cases', {})} target="_blank" rel="external">
				See an example of how the inventory can assist local partners to identify and prioritize
				barriers for removal.
			</a>
			<br /><br />
			In addition to state and local datasets, national barrier datasets used in this inventory include
			the
			<a href="https://nid.sec.usace.army.mil/#/" target="_blank" rel="external">
				National Inventory of Dams</a
			>,
			<a
				href="https://www.usgs.gov/data/waterfalls-and-rapids-conterminous-united-states-linked-national-hydrography-datasets-v20"
				target="_blank"
				rel="external"
			>
				USGS Waterfalls of the Conterminous U.S.
			</a>, and
			<a
				href="https://www.usgs.gov/data/database-stream-crossings-united-states"
				target="_blank"
				rel="external"
			>
				USGS Database of Stream Crossings in the U.S.
			</a>
			Barriers are snapped to aquatic networks derived from the
			<a
				href="https://www.usgs.gov/core-science-systems/ngp/national-hydrography/nhdplus-high-resolution"
				target="_blank"
				rel="external">USGS High Resolution National Hydrography Dataset</a
			>
			supplemented with additional information from the
			<a
				href="https://www.fws.gov/program/national-wetlands-inventory"
				target="_blank"
				rel="external">National Wetlands Inventory</a
			>.
		</p>
		<HighlightBox title="How to get the inventory?">
			<ul class="text-lg leading-snug list-none pl-0 [&_li]:not-first-of-type:mt-4">
				<li>
					<a href={resolve('/explore/', {})} class="font-bold">Summarize & download</a> aquatic barriers
					in the inventory.
				</li>
				<li>
					<a href={resolve('/priority/', {})} class="font-bold">Prioritize barriers for removal</a> and
					download results.
				</li>
				<li>
					<a href={resolve('/restoration/', {})} class="font-bold">Summarize & explore</a> removed and
					mitigated aquatic barriers.
				</li>
				<li>
					<a href={resolve('/statistics/', {})} class="font-bold">Explore</a> summary statistics about
					barriers in the inventory.
				</li>
			</ul>
		</HighlightBox>
	</div>

	<p class="text-lg mt-16"></p>
	<div class="grid sm:grid-cols-[1fr_2fr] gap-8 mt-8">
		<div>
			<enhanced:img
				src="$lib/assets/images/53366114257_3bbe03a419_o.jpg"
				alt="Culvert on Ammonoosuc River"
			/>
			<div class="text-xs text-grey-8 text-right">
				Photo: Culvert on Ammonoosuc River | <a
					href="https://www.flickr.com/photos/usfs_eastern_region/53366114257/"
					>Myles N. Sornborger, USDA Forest Service</a
				>
			</div>
		</div>
		<p class="text-lg">
			This inventory builds on regional and state efforts to collect barrier data using field
			surveys and other methods. This includes field data collected using rigorous protocols, such
			as those developed by the
			<a href="https://streamcontinuity.org/" target="_blank" rel="external"
				>North Atlantic Aquatic Connectivity Collaborative</a
			>
			(NAACC). These data are regularly updated in the inventory.
			<br /><br />
			Beginning in early 2026, field surveys coordinated and housed under the current NAACC protocol system
			will be consolidated under the new National Aquatic Connectivity Collaborative and available at
			this site.
			<br /><br />
			You can access field survey forms and manuals

			<a href={`${NACC_HOME_URL}/survey-forms/`}>here</a>.
		</p>
	</div>
	<div class="grid sm:grid-cols-[1.5fr_1fr] gap-8 mt-16">
		<p class="text-lg">
			To see a list of data sources as well as a link to submit a missing data source,
			<a
				href="https://docs.google.com/document/d/1mUwk9rHukmY1D_NInxjdIxbBVfILD1Y8Xr-lMqjV4xU/edit?usp=sharing"
				target="_blank"
				rel="external">click here</a
			>.
			<br /><br />
			<b>
				To help improve this inventory or participate in field surveys in your area, please
				<a href={`mailto:${CONTACT_EMAIL}`}>contact us</a>!
			</b>

			<br /><br />

			This inventory was originally developed within the Southeast as part of
			<a
				href="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act"
				target="_blank"
				rel="external">SARP's Aquatic Connectivity Program</a
			>, this inventory and tool have been expanded to a broader geographic area to empower
			state-level Aquatic Connectivity Teams and other collaborators with the best available
			information on aquatic barriers.
		</p>
		<div>
			<enhanced:img
				src="$lib/assets/images/8959617293_123e3f07b9_o.jpg"
				alt="T and Y Dam bypass channel"
			/>
			<div class="text-xs text-grey-8 text-right">
				Photo: T and Y dam, Montana | <a
					href="https://www.flickr.com/photos/usfwsmtnprairie/8959617293/in/album-72157633817428065"
					target="_blank"
					rel="external">Montana Fish, Wildlife, and Parks</a
				>
			</div>
		</div>
	</div>
</div>
