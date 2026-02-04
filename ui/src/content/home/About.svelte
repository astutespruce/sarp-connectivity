<script lang="ts">
	import { NACC_HOME_URL } from '$lib/env'

	import NFHPLogo from '$lib/assets/images/nfhp_logo.svg'
	import SARPLogo from '$lib/assets/images/sarp_logo.png'
	import USFWSLogo from '$lib/assets/images/usfws_logo.svg'
	import USFSLogo from '$lib/assets/images/usfs_logo.svg'
	import TNCLogo from '$lib/assets/images/tnc_logo.svg'
	import AmericanRiversLogo from '$lib/assets/images/american_rivers_logo.svg'
	import TULogo from '$lib/assets/images/trout_unlimited_logo.svg'
</script>

<div class="mt-16 text-3xl font-bold leading-tight">
	Improve aquatic connectivity by prioritizing aquatic barriers for removal using the best available
	data
</div>

<p class="mt-4">
	Fish and other aquatic organisms depend on high quality, connected river networks. A legacy of
	human use of river networks have left them fragmented by barriers such as dams and culverts.
	Fragmentation prevents species from dispersing and accessing habitats required for their
	persistence through changing conditions.
	<br />
	<br />
	The <b>National Aquatic Barrier Inventory & Prioritization Tool</b> is part of the
	<b>
		<a href={NACC_HOME_URL} target="_blank" rel="external">
			National Aquatic Connectivity Collaborative
		</a>
	</b>
	(NACC), which is a national effort to build a community of practice of resource management partners
	working together to identify aquatic barriers, prioritize these barriers for removal or mitigation,
	and implement barrier removal projects across political boundaries. The NACC is coordinated by the
	<a href="https://www.fishhabitat.org/" target="_blank" rel="external"
		>National Fish Habitat Partnership</a
	>
	(NFHP) and works together with other fish habitat partnerships and organizations across the country.
	<br />
	<br />
	At the national scale, the National Aquatic Barrier Inventory and Prioritization Tool was originated
	by the
	<a
		href="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act"
		target="_blank"
		rel="external"
	>
		Southeast Aquatic Resources Partnership</a
	>
	(SARP) and is made possible by funding from the
	<a href="https://www.fws.gov/program/national-fish-passage" target="_blank" rel="external">
		U.S. Fish and Wildlife Service
	</a>,
	<a href="https://www.americanrivers.org/" target="_blank" rel="external"> American Rivers </a>,
	the
	<a href="https://www.nfwf.org/" target="_blank" rel="external">
		National Fish and Wildlife Foundation
	</a>,
	<a href="https://www.fs.usda.gov/" target="_blank" rel="external">
		U.S. Department of Agriculture, Forest Service
	</a>,
	<a href="https://www.nature.org/" target="_blank" rel="external"> The Nature Conservancy </a>,
	<a href="https://www.tu.org/" target="_blank" rel="external">Trout Unlimited</a>, and state
	wildlife grant funding from Florida and Texas. This effort would not be possible without the
	collaboration of our partners from numerous state, federal, and non profit organizations.
</p>

<div class="flex mt-8 gap-4 flex-wrap items-center justify-between">
	<div class="flex flex-col gap-2">
		<a href="https://www.fishhabitat.org/" class="block" target="_blank" rel="external">
			<img src={NFHPLogo} alt="NFHP logo" class="w-40" />
		</a>
		<a href="https://southeastaquatics.net" class="block" target="_blank" rel="external">
			<img src={SARPLogo} alt="SARP logo" class="w-35" /></a
		>
	</div>
	<a
		href="https://www.fws.gov/program/national-fish-passage"
		class="block"
		target="_blank"
		rel="external"
	>
		<img src={USFWSLogo} alt="USFWS logo" class="h-24" />
	</a>

	<a href="https://www.fs.usda.gov/" class="block" target="_blank" rel="external">
		<img src={USFSLogo} alt="USFS logo" class="h-24" />
	</a>

	<a href="https://www.nature.org/" class="block" target="_blank" rel="external">
		<img src={TNCLogo} alt="TNC logo" class="w-37.5" />
	</a>

	<a href="https://www.americanrivers.org/" class="block" target="_blank" rel="external">
		<img src={AmericanRiversLogo} alt="American Rivers logo" class="w-35" />
	</a>

	<a href="https://www.tu.org/" class="block" target="_blank" rel="external">
		<img src={TULogo} alt="Trout Unlimited logo" class="h-20" />
	</a>
</div>

<div class="grid sm:grid-cols-[2fr_1fr] gap-8 mt-16">
	<p>
		This inventory is a growing and living database of dams, culverts, and other road crossings that
		spans all 50 states, Puerto Rico, and the US Virgin Islands, compiled by SARP with the generous
		support from many partners and funders. It integrates existing datasets from local, state, and
		federal partners with data collected from ongoing field surveys and local knowledge of specific
		structures.
	</p>
	<figure>
		<enhanced:img src="$lib/assets/images/28274676694_1840f44362_o.jpg" alt="Flock Process dam" />
		<figcaption>
			Flock Process Dam, Connecticut. Removed in 2018, restoring over 4 miles of stream access to
			diadromous species. Photo:
			<a
				href="https://www.flickr.com/photos/usfwsnortheast/28274676694/in/album-72157650009434305"
				target="_blank"
				rel="external"
			>
				U.S. Fish and Wildlife Service Northeast Region
			</a>.
		</figcaption>
	</figure>
</div>

<div class="grid sm:grid-cols-3 mt-8 gap-4">
	<figure>
		<enhanced:img src="$lib/assets/images/53188100355_4ac3d174a8_o.jpg" alt="Numana Dam" />
		<figcaption>
			Numana Dam, Nevada. Fish passage structure project underway. Photo:
			<a
				href="https://www.flickr.com/photos/usfws_pacificsw/53188100355/in/album-72177720310798426"
				target="_blank"
				rel="external"
			>
				N. Hurner, U.S. Fish and Wildlife Service
			</a>.
		</figcaption>
	</figure>
	<figure>
		<enhanced:img
			src="$lib/assets/images/54791618987_56ea39a5db_o.jpg"
			alt="Culvert near Graham, WA"
		/>
		<figcaption>
			Culvert near Graham, WA replaced in 2025 for fish passage. Photo:
			<a
				href="https://www.flickr.com/photos/wsdot/54791618987/in/album-72177720329098004"
				target="_blank"
				rel="external"
			>
				Washington State Department of Transportation
			</a>.
		</figcaption>
	</figure>
	<figure>
		<enhanced:img
			src="$lib/assets/images/Roaring_River_dam_removal_partners_small.jpg"
			alt="Roaring River Dam Removal"
		/>
		<figcaption>
			Roaring River Dam Removal, Tennessee, 2017. Photo: Mark Thurman, Tennessee Wildlife Resources
			Agency.
		</figcaption>
	</figure>
</div>

<p class="mt-8">
	In order to fill data gaps, partners have been inventorying barriers in the field from the bottom
	up, using a standardized protocol developed by the
	<a href="https://streamcontinuity.org/" target="_blank" rel="external">
		North Atlantic Aquatic Connectivity Collaborative
	</a>
	(NAACC). The North Atlantic Aquatic Connectivity Collaborative (NAACC) is a network of individuals from
	universities, conservation organizations, and state and federal natural resource and transportation
	departments focused on improving aquatic connectivity across a thirteen-state region, from Maine to
	West Virginia. As this protocol has expanded across the country, partners from fifteen states within
	the southeastern region, as well as additional states in the Great Plains and Intermountain West have
	adopted this protocol, which will now be coordinated and managed at the National scale by the National
	Fish Habitat Partnership, now called the National Aquatic Connectivity Collaborative.
</p>
