<script lang="ts">
	import PrintIcon from '@lucide/svelte/icons/file-input'

	import { browser } from '$app/environment'
	import { resolve } from '$app/paths'
	import NACCLogo from '$lib/assets/images/nacc_logo.svg'
	import { SITE_URL, NACC_HOME_URL } from '$lib/env'
	import { Button } from '$lib/components/ui/button'
	import { HeaderImage } from '$lib/components/image'
	import { summaryStats } from '$lib/config/summaryStats'
	import { formatNumber } from '$lib/util/format'
	import { dataDate, dataVersion } from '$lib/config/constants'

	const {
		dams,
		reconDams,
		rankedDams,
		removedDams,
		removedDamsGainMiles,
		lowheadDams,
		fatalityDams,
		hydroDams,
		highHazardDams,
		poorConditionDams,
		teSppDams,
		diadromousHabitatDams,
		noDownstreamBarrierDams,
		totalDamUpstreamMiles,
		estimatedDams,
		smallBarriers,
		rankedSmallBarriers,
		totalSmallBarriers,
		removedSmallBarriers,
		removedSmallBarriersGainMiles,
		noDownstreamBarrierSmallBarriers,
		totalSmallBarrierUpstreamMiles,
		unsurveyedRoadCrossings,
		teSppRoadCrossings,
		diadromousHabitatRoadCrossings,
		waterfalls,
		passabilityWaterfalls,
		passableWaterfalls,
		teSppWaterfalls,
		diadromousHabitatWaterfalls
	} = summaryStats

	const handlePrint = () => {
		window.print()
	}
</script>

<HeaderImage
	author="Jessica Smith"
	url="https://unsplash.com/photos/a-large-waterfall-with-water-coming-out-of-it-EL7cnhBw5rs"
>
	<enhanced:img src="$lib/assets/images/jessica-smith-EL7cnhBw5rs-unsplash.jpg" alt="" />
</HeaderImage>

<div
	class=" page-content print:[&_section]:break-inside-avoid print:[&_section]:not-first-of-type:mt-12 [&_section]:not-first-of-type:mt-20 [&_ul]:list-none [&_ul]:pl-0 [&_ul]:text-lg [&_h2]:bg-grey-1/75 [&_h2]:py-2 [&_h2]:text-center [&_h2]:text-4xl"
>
	<div>
		<div class="flex gap-8 justify-between items-end">
			<h1 class="page-header pb-0 mb-0 border-none block">
				<div class="hidden print:block font-bold text-xl leading-none">
					National Aquatic Barrier Inventory
				</div>

				Aquatic Barrier Statistics
			</h1>

			<Button onclick={handlePrint} disabled={!browser} class="flex-none print:hidden">
				<PrintIcon class="size-5" />
				Print / Save PDF
			</Button>

			<div>
				<img src={NACCLogo} alt="NACC logo" class="hidden print:block w-50 h-auto" />
			</div>
		</div>

		<div class="mt-2">As of {dataDate} (version {dataVersion})</div>
	</div>

	<section class="mt-6">
		<h2 class="bg-grey-1 py-2 text-center text-5xl">Dams</h2>

		<p class="text-xl mt-4">
			<b>{formatNumber(dams)}</b>
			dams have been inventoried so far, impacting at least
			<b>{formatNumber(totalDamUpstreamMiles)}</b> upstream miles, including:
		</p>
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-4 mt-4">
			<div>
				<ul>
					<li><b>{formatNumber(hydroDams)}</b> primarily used for hydropower</li>
					<li><b>{formatNumber(highHazardDams)}</b> rated as high hazards</li>
					<li><b>{formatNumber(poorConditionDams)}</b> rated in poor condition</li>
					<li><b>{formatNumber(lowheadDams)}</b> known or likely lowhead dams</li>
					<li><b>{formatNumber(fatalityDams)}</b> that have had at least one fatality</li>
					<li>
						<b>{formatNumber(reconDams)}</b> that have been reconned for social feasibility of removal
					</li>
				</ul>
			</div>
			<div class="sm:border-l sm:border-l-grey-2 sm:pl-4">
				<ul>
					<li>
						<b>{formatNumber(teSppDams)}</b> in subwatersheds with at least one T&E species
					</li>

					<li>
						<b>{formatNumber(diadromousHabitatDams)}</b> on a reach with anadromous / catadromous species
						habitat
					</li>

					<li>
						<b>{formatNumber(noDownstreamBarrierDams)}</b> that have no other downstream barriers
					</li>
					<li>
						<b>{formatNumber(estimatedDams)}</b> that have been estimated from other data sources
					</li>
				</ul>
			</div>
		</div>

		<div class="py-4 px-4 bg-blue-1/75 text-lg mt-4 text-center">
			<b>{formatNumber(removedDams)}</b> dams have been removed or improved for conservation,
			<br />
			gaining <b>{formatNumber(removedDamsGainMiles)} miles</b> of reconnected rivers and streams
		</div>

		<p class="text-muted-foreground text-sm mt-6">
			Note: These statistics are based on inventoried dams. Because the inventory is incomplete in
			many areas, areas with a high number of dams may simply represent areas that have a more
			complete inventory.
			<a href={resolve('/methods/inventory/', {})}
				>Learn more about aquatic barrier inventory methods here</a
			>.
			<br />
			<br />
			{formatNumber(dams - rankedDams, 0)} dams were not analyzed for prioritization because they could
			not be correctly located on the aquatic network or were otherwise excluded from the analysis.
		</p>
	</section>

	<section>
		<h2>Road/stream crossings</h2>

		<p class="text-xl mt-4">
			At least <b>{formatNumber(totalSmallBarriers + unsurveyedRoadCrossings)}</b> road/stream crossings
			have been identified, including:
		</p>

		<div class="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-4 mt-4">
			<div>
				<ul>
					<li>
						<b>{formatNumber(totalSmallBarriers)}</b> that have been surveyed for impacts to aquatic organisms
					</li>
					<li>
						<b>{formatNumber(smallBarriers - removedSmallBarriers)}</b>
						surveyed crossings that are likely to impact aquatic organisms based on their barrier severity,
						impacting at least <b>{formatNumber(totalSmallBarrierUpstreamMiles)}</b> upstream miles
					</li>
					<li>
						<b>{formatNumber(rankedSmallBarriers, 0)}</b> that have been analyzed for their impacts to
						aquatic connectivity in this tool
					</li>
				</ul>
			</div>
			<div class="sm:border-l sm:border-l-grey-2 sm:pl-4">
				<ul>
					<li>
						<b>{formatNumber(teSppRoadCrossings)}</b> surveyed & unsurveyed crossings in subwatersheds
						with at least one T&E species
					</li>
					<li>
						<b>{formatNumber(diadromousHabitatRoadCrossings)}</b> surveyed & unsurveyed crossings on a
						reach with anadromous / catadromous species habitat
					</li>
					<li>
						<b>{formatNumber(noDownstreamBarrierSmallBarriers)}</b> that have no other surveyed downstream
						barriers
					</li>
				</ul>
			</div>
		</div>

		<div class="py-4 px-4 bg-blue-1/75 text-lg mt-4 text-center">
			<b>{formatNumber(removedSmallBarriers)}</b> surveyed crossings have been removed or improved
			for conservation
			<br />
			gaining <b>{formatNumber(removedSmallBarriersGainMiles)} miles</b> of reconnected rivers and streams
		</div>

		<p class="text-muted-foreground text-sm mt-6">
			Note: These statistics are based on surveyed road/stream crossings. Because the inventory is
			incomplete in many areas, areas with a high number of surveyed crossings may simply represent
			areas that have a more complete inventory. <a href={resolve('/methods/inventory/', {})}
				>Learn more about aquatic barrier inventory methods here</a
			>.
			<br />
			<br />
			{formatNumber(smallBarriers - rankedSmallBarriers, 0)} surveyed road/stream crossings were not analyzed
			for prioritization because they could not be correctly located on the aquatic network or were otherwise
			excluded from the analysis.
		</p>
	</section>

	<section>
		<h2>Waterfalls</h2>
		<p class="text-xl mt-4">
			At least <b>{formatNumber(waterfalls)}</b> waterfalls have been identified, including:
		</p>
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-4 mt-4">
			<div>
				<ul>
					<li>
						<b>{formatNumber(passabilityWaterfalls)}</b> that have been reviewed for passability to aquatic
						organisms
					</li>
					<li>
						<b>{formatNumber(passableWaterfalls)}</b>
						with at least partial passability
					</li>
				</ul>
			</div>
			<div class="sm:border-l sm:border-l-grey-2 sm:pl-4">
				<ul>
					<li>
						<b>{formatNumber(teSppWaterfalls)}</b> are in subwatersheds with at least one T&E species
					</li>
					<li>
						<b>{formatNumber(diadromousHabitatWaterfalls)}</b> are on a reach with anadromous / catadromous
						species habitat
					</li>
				</ul>
			</div>
		</div>
	</section>

	<section class="border-t border-t-grey-2 pt-8">
		<p class="text-xs">
			This report was created on {new Date().toLocaleDateString()} using the
			<a href={SITE_URL} target="_blank" rel="external">
				National Aquatic Barrier Inventory & Prioritization Tool
			</a>, part of the
			<a href={NACC_HOME_URL} target="_blank" rel="external">
				National Aquatic Connectivity Collaborative
			</a>
			(NACC), led by the
			<a
				href="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act"
				target="_blank"
				rel="external"
			>
				Southeast Aquatic Resources Partnership
			</a>
			and the
			<a href="https://www.fishhabitat.org/" target="_blank" rel="external">
				National Fish Habitat Partnership
			</a>.

			<br /><br />
			This project is made possible by funding from the
			<a href="https://www.fws.gov/program/national-fish-passage" target="_blank" rel="external">
				U.S. Fish and Wildlife Service
			</a>,
			<a href="https://www.americanrivers.org/" target="_blank" rel="external">
				American Rivers
			</a>, the
			<a href="https://www.nfwf.org/" target="_blank" rel="external">
				National Fish and Wildlife Foundation
			</a>,
			<a href="https://www.fs.usda.gov/" target="_blank" rel="external">
				U.S. Department of Agriculture, Forest Service
			</a>,
			<a href="https://www.nature.org/" target="_blank" rel="external"> The Nature Conservancy </a>,
			<a href="https://www.tu.org/" target="_blank" rel="external">Trout Unlimited</a>, and state
			wildlife grant funding from Florida and Texas. This effort would not be possible without the
			collaboration of NACC partners from numerous state, federal, and non profit organizations.
		</p>
	</section>
</div>
