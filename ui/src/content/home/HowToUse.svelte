<script lang="ts">
	import ExploreIcon from '@lucide/svelte/icons/chart-column'
	import PrioritizeIcon from '@lucide/svelte/icons/search-check'

	import { resolve } from '$app/paths'
	import { MAP_SERVICES } from '$lib/config/constants'
	import { Button } from '$lib/components/ui/button'
</script>

<h2 class="text-2xl sm:text-3xl">Get started using this tool</h2>

<p>
	This inventory and prioritization tool is designed to guide users in identifying high priority
	barrier removal projects. To access information about to funding sources for barrier removal,
	please visit the
	<a
		href="https://interagency-bil-fish-passage-project-1-fws.hub.arcgis.com/"
		target="_blank"
		rel="external"
	>
		Fish Passage Portal
	</a>. The portal is a "one-stop shop" for anyone who needs information, funding, or resources to
	improve fish passage and aquatic connectivity projects. It provides landowners and public lands
	managers the tools to find funding across the federal government, as well as access to data,
	planning, and geospatial information.
</p>

<div class="grid sm:grid-cols-[5fr_3fr] gap-16 mt-12">
	<div>
		<h3 class="text-xl sm:text-2xl">Summarize the inventory</h3>
		<p class="mt-4">
			Explore summaries of the inventory by state, county, or different levels of watersheds.
			<br />
			<br />
			These summaries are a good way to become familiar with the level of aquatic fragmentation for many
			states across the U.S. Find out how many aquatic barriers have already been inventoried in your
			area! Just remember, the inventory is a living database, and is not yet comprehensive across these
			states.
		</p>
	</div>

	<div>
		<div class="flex justify-end">
			<Button href={resolve('/explore/', {})} class="text-base">
				<ExploreIcon />
				Start exploring
			</Button>
		</div>
		<div>
			<a href={resolve('/explore/', {})} aria-label="explore page">
				<enhanced:img
					src="$lib/assets/images/summarize.png"
					alt="explore map screenshot"
					class="border border-grey-2 mt-4"
				/>
			</a>
		</div>
	</div>
</div>

<div class="grid sm:grid-cols-[5fr_3fr] gap-16 mt-24">
	<div>
		<h3 class="text-xl sm:text-2xl">Prioritize aquatic barriers for removal</h3>
		<p class="mt-4">
			Identify barriers for further investigation based on the criteria that matter to you.
			<br />
			<br />
			You can select specific geographic areas for prioritization, including counties, states, and watersheds.
			You can filter the available barriers based on criteria such as likely feasibility for removal,
			height, and more. Once you have prioritized aquatic barriers, you can download a CSV file for further
			analysis.
		</p>
	</div>

	<div>
		<div class="flex justify-end">
			<Button href={resolve('/priority/', {})} class="text-base">
				<PrioritizeIcon />
				Start prioritizing
			</Button>
		</div>
		<div>
			<a href={resolve('/priority/', {})} aria-label="prioritize page">
				<enhanced:img
					src="$lib/assets/images/prioritize.png"
					alt="prioritize map screenshot"
					class="border border-grey-2 mt-4"
				/>
			</a>
		</div>
	</div>
</div>

<h4 class="text-xl mt-12">Map services</h4>

<p class="mt-2">
	If you would like to access map services of a recent version of the aquatic barriers and
	connectivity results (may not match the exact version here), you can import one of the following
	connectivity analysis map services into your GIS tool of choice:
</p>

<ul class="list-disc list-outside pl-8 mt-2 [&>li+li]:mt-2">
	<li>
		<a href={MAP_SERVICES.dams} target="_blank" rel="external">Dams</a> based on networks that are cut
		by dams and waterfalls.
	</li>
	<li>
		<a href={MAP_SERVICES.small_barriers} target="_blank" rel="external">
			Surveyed road crossings
		</a>
		based on networks that are cut by dams, waterfalls, and surveyed crossings.
	</li>
	<li>
		<a href={MAP_SERVICES.combined_barriers} target="_blank" rel="external">
			Dams & surveyed road crossings
		</a>
		based on networks that are cut by dams, waterfalls, and surveyed crossings.
	</li>
</ul>
